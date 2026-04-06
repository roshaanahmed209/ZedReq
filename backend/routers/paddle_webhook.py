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
from services.paddle_billing_sync import sync_subscription_entity, sync_transaction_entity
from utils.paddle_signature import verify_paddle_signature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing"])


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

    db.add(PaddleWebhookEvent(event_id=eid, event_type=event_type[:128] or "unknown"))
    db.commit()

    return {"success": True}
