"""User-initiated Paddle subscription cancel and plan changes."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from config.settings import get_settings
from models.orm import User
from models.orm.payment import Payment
from models.orm.user_subscription import UserSubscription
from services.paddle_api import cancel_subscription, update_subscription_items
from services.subscription_service import SubscriptionService
from utils.errors import ValidationError

logger = logging.getLogger(__name__)


def _payment_for_user(db: Session, user_id: int) -> Optional[Payment]:
    user = db.query(User).filter(User.uid == user_id).first()
    if not user:
        return None
    if user.pay_id:
        return db.query(Payment).filter(Payment.pay_id == user.pay_id).first()
    return db.query(Payment).filter(Payment.uid == user_id).first()


def _is_enterprise(db: Session, user_id: int) -> bool:
    sub = (
        db.query(UserSubscription)
        .filter(UserSubscription.user_id == user_id, UserSubscription.status == "active")
        .first()
    )
    return bool(sub and sub.plan and sub.plan.plan_name == "enterprise")


class SubscriptionBillingService:
    def __init__(self, db: Session):
        self.db = db

    def cancel_paddle_subscription(
        self,
        user_id: int,
        effective_from: str = "next_billing_period",
    ) -> Dict[str, Any]:
        if _is_enterprise(self.db, user_id):
            raise ValidationError("Enterprise subscriptions are managed by your administrator.")
        pay = _payment_for_user(self.db, user_id)
        if not pay or not pay.paddle_subscription_id:
            raise ValidationError(
                "No Paddle subscription on file. If you subscribed recently, wait a moment; "
                "otherwise use checkout to subscribe or contact support."
            )
        settings = get_settings()
        if not settings.PADDLE_API_KEY:
            raise ValidationError("Billing integration is not configured.")

        if effective_from not in ("immediately", "next_billing_period"):
            raise ValidationError("effective_from must be immediately or next_billing_period")

        try:
            cancel_subscription(pay.paddle_subscription_id, effective_from=effective_from)
        except Exception as e:
            logger.exception("Paddle cancel API failed: %s", e)
            raise ValidationError("Could not cancel subscription with Paddle. Try again or contact support.")

        return {
            "success": True,
            "message": "Cancellation submitted. Your plan will update when Paddle confirms (usually within a minute).",
            "effective_from": effective_from,
        }

    def change_paddle_plan(
        self,
        user_id: int,
        target_plan: str,
        proration_billing_mode: str = "prorated_immediately",
    ) -> Dict[str, Any]:
        if target_plan not in ("pro", "premium"):
            raise ValidationError("Only pro and premium are supported for self-serve changes.")
        if _is_enterprise(self.db, user_id):
            raise ValidationError("Enterprise subscriptions are managed by your administrator.")

        pay = _payment_for_user(self.db, user_id)
        if not pay or not pay.paddle_subscription_id:
            raise ValidationError(
                "No active Paddle subscription to change. Use checkout to subscribe first."
            )

        settings = get_settings()
        if not settings.PADDLE_API_KEY:
            raise ValidationError("Billing integration is not configured.")

        price_pro = settings.PADDLE_PRICE_PRO
        price_premium = settings.PADDLE_PRICE_PREMIUM
        target_price = price_pro if target_plan == "pro" else price_premium
        if not target_price or not str(target_price).strip():
            raise ValidationError("Server is missing PADDLE_PRICE_PRO / PADDLE_PRICE_PREMIUM configuration.")

        svc = SubscriptionService(self.db)
        current = svc.get_user_plan(user_id)
        current_name = (current.get("plan_name") or "free").lower()
        if current_name == "free":
            raise ValidationError("Use checkout to start a paid subscription.")
        if current_name == target_plan:
            raise ValidationError(f"You are already on the {target_plan} plan.")

        items = [{"price_id": str(target_price).strip(), "quantity": 1}]
        try:
            update_subscription_items(
                pay.paddle_subscription_id,
                items,
                proration_billing_mode=proration_billing_mode,
            )
        except Exception as e:
            logger.exception("Paddle update subscription failed: %s", e)
            raise ValidationError("Could not update subscription with Paddle. Try again or contact support.")

        return {
            "success": True,
            "message": "Plan change submitted. Your entitlements will update when Paddle confirms.",
            "target_plan": target_plan,
        }
