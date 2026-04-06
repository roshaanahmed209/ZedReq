"""
Map Paddle Billing subscription / transaction payloads into payment + user_subscriptions.
Used by webhooks and optionally after API calls.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.orm import User
from models.orm.payment import Payment
from models.orm.subscription_plan import SubscriptionPlan
from models.orm.user_subscription import UserSubscription

logger = logging.getLogger(__name__)


def price_id_to_plan_name(price_id: Optional[str], price_pro: Optional[str], price_premium: Optional[str]) -> Optional[str]:
    if not price_id:
        return None
    if price_pro and price_id == price_pro.strip():
        return "pro"
    if price_premium and price_id == price_premium.strip():
        return "premium"
    return None


def _first_recurring_price_id(items: Any) -> Optional[str]:
    if not items or not isinstance(items, list):
        return None
    for it in items:
        if not isinstance(it, dict):
            continue
        price = it.get("price")
        if isinstance(price, dict):
            pid = price.get("id")
            if pid:
                return str(pid)
        pid = it.get("price_id")
        if pid:
            return str(pid)
    return None


def _parse_rfc3339(dt: Optional[str]) -> Optional[datetime]:
    if not dt or not isinstance(dt, str):
        return None
    try:
        if dt.endswith("Z"):
            dt = dt[:-1] + "+00:00"
        return datetime.fromisoformat(dt.replace("Z", "+00:00"))
    except ValueError:
        return None


def resolve_user_id_for_paddle(
    db: Session,
    custom_data: Any,
    customer_id: Optional[str],
) -> Optional[int]:
    if isinstance(custom_data, dict):
        raw = custom_data.get("zedreq_user_id")
        if raw is not None:
            try:
                return int(raw)
            except (TypeError, ValueError):
                pass
    if customer_id:
        pay = (
            db.query(Payment)
            .filter(Payment.provider_customer_id == customer_id)
            .first()
        )
        if pay:
            return pay.uid
    return None


def apply_free_plan(
    db: Session,
    user_id: int,
    *,
    clear_paddle_subscription: bool = False,
) -> None:
    """Set user to free tier (active entitlement, inactive billing)."""
    free_plan = db.query(SubscriptionPlan).filter_by(plan_name="free", is_active=True).first()
    if not free_plan:
        logger.error("apply_free_plan: free plan missing from subscription_plans")
        return

    user = db.query(User).filter(User.uid == user_id).first()
    if not user:
        return

    if user.pay_id:
        payment = db.query(Payment).filter(Payment.pay_id == user.pay_id).first()
    else:
        payment = db.query(Payment).filter(Payment.uid == user_id).first()

    if payment:
        payment.subscription_plan = "free"
        payment.subscription_status = "inactive"
        if clear_paddle_subscription:
            payment.paddle_subscription_id = None
            payment.paddle_price_id = None
        payment.payment_provider = payment.payment_provider or "paddle"
    else:
        payment = Payment(
            uid=user_id,
            payment_provider="paddle",
            subscription_plan="free",
            subscription_status="inactive",
        )
        db.add(payment)
        db.flush()
        user.pay_id = payment.pay_id

    user_sub = db.query(UserSubscription).filter_by(user_id=user_id).first()
    if user_sub:
        user_sub.plan_id = free_plan.plan_id
        user_sub.status = "active"
        user_sub.assigned_by = "paddle"
    else:
        user_sub = UserSubscription(
            user_id=user_id,
            plan_id=free_plan.plan_id,
            status="active",
            assigned_by="paddle",
            started_at=datetime.now(timezone.utc),
        )
        db.add(user_sub)
        db.flush()

    payment.subscription_id = user_sub.subscription_id
    db.commit()
    logger.info("apply_free_plan user_id=%s clear_paddle=%s", user_id, clear_paddle_subscription)


def apply_paid_plan(
    db: Session,
    user_id: int,
    plan_name: str,
    *,
    paddle_subscription_id: str,
    customer_id: Optional[str],
    price_id: Optional[str],
    subscription_start: Optional[datetime] = None,
    subscription_end: Optional[datetime] = None,
) -> None:
    if plan_name not in ("pro", "premium"):
        logger.warning("apply_paid_plan: unsupported plan %s", plan_name)
        return

    plan_obj = (
        db.query(SubscriptionPlan)
        .filter_by(plan_name=plan_name, is_active=True)
        .first()
    )
    if not plan_obj:
        logger.error("apply_paid_plan: plan %s not found", plan_name)
        return

    user = db.query(User).filter(User.uid == user_id).first()
    if not user:
        return

    if user.pay_id:
        payment = db.query(Payment).filter(Payment.pay_id == user.pay_id).first()
    else:
        payment = db.query(Payment).filter(Payment.uid == user_id).first()

    if payment:
        payment.subscription_plan = plan_name
        payment.subscription_status = "active"
        payment.payment_provider = "paddle"
        payment.paddle_subscription_id = paddle_subscription_id
        if price_id:
            payment.paddle_price_id = price_id
        if customer_id:
            payment.provider_customer_id = customer_id
        if subscription_start:
            payment.subscription_start = subscription_start
        if subscription_end:
            payment.subscription_end = subscription_end
    else:
        payment = Payment(
            uid=user_id,
            payment_provider="paddle",
            subscription_plan=plan_name,
            subscription_status="active",
            paddle_subscription_id=paddle_subscription_id,
            paddle_price_id=price_id,
            provider_customer_id=customer_id,
            subscription_start=subscription_start,
            subscription_end=subscription_end,
        )
        db.add(payment)
        db.flush()
        user.pay_id = payment.pay_id

    user_sub = db.query(UserSubscription).filter_by(user_id=user_id).first()
    if user_sub:
        user_sub.plan_id = plan_obj.plan_id
        user_sub.status = "active"
        user_sub.assigned_by = "paddle"
        if subscription_end:
            user_sub.expires_at = subscription_end
    else:
        user_sub = UserSubscription(
            user_id=user_id,
            plan_id=plan_obj.plan_id,
            status="active",
            assigned_by="paddle",
            started_at=subscription_start or datetime.now(timezone.utc),
            expires_at=subscription_end,
        )
        db.add(user_sub)
        db.flush()

    payment.subscription_id = user_sub.subscription_id
    db.commit()
    logger.info(
        "apply_paid_plan user_id=%s plan=%s paddle_sub=%s",
        user_id,
        plan_name,
        paddle_subscription_id,
    )


def sync_subscription_entity(
    db: Session,
    sub: Dict[str, Any],
    *,
    price_pro: Optional[str],
    price_premium: Optional[str],
) -> None:
    """
    Apply Paddle subscription object to local DB.
    """
    paddle_sub_id = sub.get("id")
    if not paddle_sub_id:
        logger.warning("sync_subscription_entity: missing id")
        return

    customer_id = sub.get("customer_id")
    custom_data = sub.get("custom_data")
    status = (sub.get("status") or "").lower()
    items = sub.get("items")

    user_id = resolve_user_id_for_paddle(db, custom_data, customer_id)
    if user_id is None:
        logger.warning(
            "sync_subscription_entity: cannot resolve user for sub %s customer %s",
            paddle_sub_id,
            customer_id,
        )
        return

    # Enterprise must remain admin-assigned; do not downgrade from enterprise via Paddle
    existing_sub = db.query(UserSubscription).filter_by(user_id=user_id).first()
    if existing_sub and existing_sub.plan and existing_sub.plan.plan_name == "enterprise":
        logger.info("sync_subscription_entity: skip Paddle sync for enterprise user_id=%s", user_id)
        return

    started = _parse_rfc3339(sub.get("started_at") or sub.get("first_billed_at"))
    period = sub.get("current_billing_period") or {}
    ends = _parse_rfc3339(period.get("ends_at")) if isinstance(period, dict) else None
    canceled_at = _parse_rfc3339(sub.get("canceled_at"))

    if status == "canceled" or canceled_at:
        apply_free_plan(db, user_id, clear_paddle_subscription=False)
        pay = _get_payment_for_user(db, user_id)
        if pay:
            pay.paddle_subscription_id = str(paddle_sub_id)
            db.commit()
        return

    if status == "paused":
        price_id = _first_recurring_price_id(items)
        plan_name = price_id_to_plan_name(price_id, price_pro, price_premium)
        if plan_name:
            apply_paid_plan(
                db,
                user_id,
                plan_name,
                paddle_subscription_id=str(paddle_sub_id),
                customer_id=str(customer_id) if customer_id else None,
                price_id=price_id,
                subscription_start=started,
                subscription_end=ends,
            )
        pay = _get_payment_for_user(db, user_id)
        if pay:
            pay.subscription_status = "paused"
            pay.paddle_subscription_id = str(paddle_sub_id)
            db.commit()
        elif not plan_name:
            logger.warning("paused subscription: no local payment row user_id=%s", user_id)
        return

    price_id = _first_recurring_price_id(items)
    plan_name = price_id_to_plan_name(price_id, price_pro, price_premium)
    if not plan_name:
        logger.warning(
            "sync_subscription_entity: unknown price_id=%s for sub %s",
            price_id,
            paddle_sub_id,
        )
        return

    apply_paid_plan(
        db,
        user_id,
        plan_name,
        paddle_subscription_id=str(paddle_sub_id),
        customer_id=str(customer_id) if customer_id else None,
        price_id=price_id,
        subscription_start=started,
        subscription_end=ends,
    )


def _get_payment_for_user(db: Session, user_id: int) -> Optional[Payment]:
    user = db.query(User).filter(User.uid == user_id).first()
    if not user:
        return None
    if user.pay_id:
        return db.query(Payment).filter(Payment.pay_id == user.pay_id).first()
    return db.query(Payment).filter(Payment.uid == user_id).first()


def sync_transaction_entity(
    db: Session,
    tx: Dict[str, Any],
) -> None:
    """Update payment row from transaction.completed / billed."""
    tx_id = tx.get("id")
    customer_id = tx.get("customer_id")
    subscription_id = tx.get("subscription_id")
    if not customer_id and not subscription_id:
        return

    pay = None
    if subscription_id:
        pay = (
            db.query(Payment)
            .filter(Payment.paddle_subscription_id == str(subscription_id))
            .first()
        )
    if pay is None and customer_id:
        pay = (
            db.query(Payment)
            .filter(Payment.provider_customer_id == str(customer_id))
            .first()
        )
    if pay is None:
        return

    if tx_id:
        pay.transaction_id = str(tx_id)[:255]
    pay.last_payment_date = datetime.now(timezone.utc)
    details = tx.get("details") or {}
    if isinstance(details, dict):
        totals = details.get("totals") or {}
        if isinstance(totals, dict):
            grand = totals.get("grand_total")
            if grand is not None:
                try:
                    pay.amount = grand
                except Exception:
                    pass
    db.commit()
