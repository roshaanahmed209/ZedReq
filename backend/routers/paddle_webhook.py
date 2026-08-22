"""Paddle Billing webhook receiver (raw body + signature verification)."""
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from config.database_orm import get_db
from config.settings import get_settings
from models.orm.paddle_webhook_event import PaddleWebhookEvent
from services.paddle_billing_sync import (
    resolve_user_id_for_paddle,
    sync_subscription_entity,
    sync_transaction_entity,
)
from services.analytics_service import track_server_event
from utils.paddle_signature import verify_paddle_signature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])


_SUBSCRIPTION_EVENT_MAP = {
    "subscription.created": "subscription_started",
    "subscription.activated": "subscription_started",
    "subscription.canceled": "subscription_cancelled",
    "subscription.updated": "subscription_renewed",
    "subscription.resumed": "subscription_renewed",
}


def _track_billing_event(db: Session, event_type: str, root: Dict[str, Any]) -> None:
    """
    Emit the analytics event for one Paddle webhook.

    Only non-sensitive commercial attributes are recorded: plan, billing period,
    amount, currency and the provider's own ids. Card numbers, CVVs, payment methods
    and customer addresses are never touched - Paddle holds them and they have no
    place in an analytics store.
    """
    user_id = resolve_user_id_for_paddle(
        db, root.get("custom_data"), root.get("customer_id")
    )
    if not user_id:
        return

    if event_type.startswith("subscription."):
        event_name = _SUBSCRIPTION_EVENT_MAP.get(event_type)
        if not event_name:
            return

        items = root.get("items") or []
        price_id = None
        billing_period = None
        if isinstance(items, list) and items:
            price = (items[0] or {}).get("price") or {}
            price_id = price.get("id")
            cycle = price.get("billing_cycle") or {}
            if isinstance(cycle, dict) and cycle.get("interval"):
                billing_period = cycle.get("interval")

        track_server_event(
            event_name,
            user_id=user_id,
            properties={
                "plan_id": price_id,
                "billing_period": billing_period,
                "status": root.get("status"),
                "paddle_subscription_id": root.get("id"),
            },
        )
        return

    if event_type in ("transaction.completed", "transaction.paid"):
        totals = (root.get("details") or {}).get("totals") or {}
        amount_raw = totals.get("grand_total") or totals.get("total")
        try:
            # Paddle sends minor units as a string ("4999" = $49.99).
            amount = round(int(amount_raw) / 100, 2) if amount_raw is not None else None
        except (TypeError, ValueError):
            amount = None

        track_server_event(
            "payment_succeeded",
            user_id=user_id,
            properties={
                "amount": amount,
                "currency": root.get("currency_code"),
                "transaction_id": root.get("id"),
                "paddle_subscription_id": root.get("subscription_id"),
            },
        )
    elif event_type in ("transaction.payment_failed", "transaction.past_due"):
        track_server_event(
            "payment_failed",
            user_id=user_id,
            properties={
                "transaction_id": root.get("id"),
                "currency": root.get("currency_code"),
                # A category, never the provider's raw decline text.
                "failure_category": "payment_declined",
            },
        )


def _event_payload_root(body: Dict[str, Any]) -> Dict[str, Any]:
    """Paddle wraps entity in `data`; tolerate flat bodies."""
    data = body.get("data")
    if isinstance(data, dict):
        return data
    return body


@router.post("/paddle/webhook")
async def paddle_webhook(request: Request, db: Session = Depends(get_db)):
    settings = get_settings()
    secret = settings.PADDLE_WEBHOOK_SECRET
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Paddle webhooks are not configured",
        )

    raw = await request.body()
    sig = request.headers.get("Paddle-Signature") or request.headers.get("paddle-signature")
    if not verify_paddle_signature(
        raw,
        sig,
        secret,
        max_age_seconds=int(getattr(settings, "PADDLE_WEBHOOK_MAX_AGE_SECONDS", 3600) or 3600),
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid webhook signature",
        )

    try:
        body = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON body",
        )

    event_id = body.get("event_id") or body.get("id")
    event_type = (body.get("event_type") or body.get("type") or "").strip()
    if not event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing event id",
        )

    eid = str(event_id)[:128]
    if db.query(PaddleWebhookEvent).filter_by(event_id=eid).first():
        return {"success": True, "duplicate": True}

    price_pro = settings.PADDLE_PRICE_PRO
    price_premium = settings.PADDLE_PRICE_PREMIUM

    root = _event_payload_root(body)

    if event_type.startswith("subscription."):
        sync_subscription_entity(db, root, price_pro=price_pro, price_premium=price_premium)
    elif event_type.startswith("transaction."):
        sync_transaction_entity(db, root)
    else:
        logger.info("paddle_webhook unhandled event_type=%s", event_type)

    # Monetisation analytics. Emitted here rather than inside the sync services so it
    # sits behind the same signature check and the same event_id deduplication that
    # already protects the billing writes: a replayed webhook cannot create a second
    # conversion. Wrapped so a tracking failure can never fail the webhook, which
    # would make Paddle retry a payment that was in fact applied successfully.
    try:
        _track_billing_event(db, event_type, root)
    except Exception as exc:  # noqa: BLE001
        logger.debug("paddle_webhook analytics failed: %s", exc)

    db.add(PaddleWebhookEvent(event_id=eid, event_type=event_type[:128] or "unknown"))
    db.commit()

    return {"success": True}
