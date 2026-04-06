"""Paddle Billing REST API client (server-side)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from config.settings import get_settings

logger = logging.getLogger(__name__)

PADDLE_API_BASE_PROD = "https://api.paddle.com"
PADDLE_API_BASE_SANDBOX = "https://sandbox-api.paddle.com"


def _base_url() -> str:
    s = get_settings()
    return PADDLE_API_BASE_SANDBOX if getattr(s, "PADDLE_SANDBOX", False) else PADDLE_API_BASE_PROD


def _headers() -> Dict[str, str]:
    key = get_settings().PADDLE_API_KEY
    if not key:
        raise RuntimeError("PADDLE_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def cancel_subscription(
    paddle_subscription_id: str,
    effective_from: str = "next_billing_period",
) -> Dict[str, Any]:
    """
    POST /subscriptions/{id}/cancel
    effective_from: next_billing_period | immediately
    """
    url = f"{_base_url()}/subscriptions/{paddle_subscription_id}/cancel"
    payload = {"effective_from": effective_from}
    with httpx.Client(timeout=60.0) as client:
        r = client.post(url, headers=_headers(), json=payload)
        if r.status_code >= 400:
            logger.error("Paddle cancel failed: %s %s", r.status_code, r.text)
            r.raise_for_status()
        return r.json()


def update_subscription_items(
    paddle_subscription_id: str,
    items: List[Dict[str, Any]],
    proration_billing_mode: str = "prorated_immediately",
) -> Dict[str, Any]:
    """
    PATCH /subscriptions/{id} — send full items list (replace catalog items).
    """
    url = f"{_base_url()}/subscriptions/{paddle_subscription_id}"
    payload = {
        "items": items,
        "proration_billing_mode": proration_billing_mode,
    }
    with httpx.Client(timeout=120.0) as client:
        r = client.patch(url, headers=_headers(), json=payload)
        if r.status_code >= 400:
            logger.error("Paddle update subscription failed: %s %s", r.status_code, r.text)
            r.raise_for_status()
        return r.json()


def get_subscription(paddle_subscription_id: str) -> Dict[str, Any]:
    url = f"{_base_url()}/subscriptions/{paddle_subscription_id}"
    with httpx.Client(timeout=30.0) as client:
        r = client.get(url, headers=_headers())
        if r.status_code >= 400:
            r.raise_for_status()
        return r.json()
