"""
Analytics forwarding service for the main ZedReq app.

The browser posts events same-origin to ``/api/analytics/events``; this service
enriches them with context only the server can be trusted for (device, browser, OS,
country) and forwards them to the back office collector using the shared
``COLLECTOR_API_KEY``. The key therefore never reaches the JS bundle, and the browser
never talks to a second origin - which also means ad blockers and third-party-cookie
policies have nothing to block.

The hard rule everywhere in this module: **analytics must never affect the product**.
Every network call is fire-and-forget with a short timeout, and every failure path
ends in a debug log. If the back office is down, ZedReq keeps working and the events
are dropped.
"""
import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

BACKOFFICE_COLLECTOR_URL = os.getenv(
    "BACKOFFICE_COLLECTOR_URL", "http://localhost:5001/api/collect"
)
COLLECTOR_API_KEY = os.getenv("COLLECTOR_API_KEY", "")

# Short enough that a slow back office cannot hold a request handler open. Forwarding
# happens off the request path anyway, but a hung socket still costs a task slot.
FORWARD_TIMEOUT_SECONDS = 3.0

MAX_BATCH = 50


def analytics_enabled() -> bool:
    """
    Analytics is active only when the collector key is configured.

    Without it the back office collector refuses requests (it is fail-secure), so
    forwarding would be pure waste. Returning False here makes the whole pipeline a
    cheap no-op rather than a stream of failing HTTP calls.
    """
    return bool(COLLECTOR_API_KEY)


def new_event_id() -> str:
    """Idempotency key for a server-emitted event."""
    return uuid.uuid4().hex


async def forward_events(events: List[Dict[str, Any]]) -> None:
    """
    Ship a batch to the back office collector. Never raises.

    Called as a background task, so nothing awaits the result and no user-facing
    request can be delayed or failed by it.
    """
    if not events or not analytics_enabled():
        return

    payload = {"events": events[:MAX_BATCH]}
    headers = {"X-API-Key": COLLECTOR_API_KEY, "Content-Type": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=FORWARD_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{BACKOFFICE_COLLECTOR_URL}/analytics",
                json=payload,
                headers=headers,
            )
            if response.status_code >= 400:
                logger.debug(
                    "analytics: collector rejected batch (%s): %s",
                    response.status_code,
                    response.text[:300],
                )
    except httpx.TimeoutException:
        logger.debug("analytics: collector timed out, dropping %d events", len(events))
    except Exception as exc:  # noqa: BLE001 - analytics must never surface an error
        logger.debug("analytics: forward failed (%s), dropping %d events", exc, len(events))


async def forward_identify(
    anonymous_id: str,
    user_id: int,
    traits: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Tell the back office that an anonymous visitor is now a known user. Never raises.

    This is the identity-stitching call. Everything the visitor did before the account
    existed stays attributable to them once this lands.
    """
    if not anonymous_id or not user_id or not analytics_enabled():
        return

    headers = {"X-API-Key": COLLECTOR_API_KEY, "Content-Type": "application/json"}
    payload = {
        "anonymous_id": anonymous_id,
        "user_id": int(user_id),
        "traits": traits or {},
    }

    try:
        async with httpx.AsyncClient(timeout=FORWARD_TIMEOUT_SECONDS) as client:
            await client.post(
                f"{BACKOFFICE_COLLECTOR_URL}/analytics/identify",
                json=payload,
                headers=headers,
            )
    except Exception as exc:  # noqa: BLE001
        logger.debug("analytics: identify forward failed: %s", exc)


def build_server_event(
    event_name: str,
    *,
    user_id: Optional[int] = None,
    anonymous_id: Optional[str] = None,
    session_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    page_path: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Build a trusted, server-emitted event.

    Used for anything a browser must not be able to claim - signup and login success,
    payments, subscription changes. ``anonymous_id`` falls back to a stable
    user-derived value so the event still has the required identifier when the caller
    (a webhook, say) has no browser context at all.
    """
    if anonymous_id:
        resolved_anon = anonymous_id
    elif user_id:
        # Stable per-user fallback so webhook-emitted events still carry the required
        # identifier. It never collides with a real SDK id, which is always a hex uuid.
        resolved_anon = f"srv-user-{user_id}"
    else:
        resolved_anon = "srv-system-0"

    return {
        "event_id": new_event_id(),
        "event_name": event_name,
        "anonymous_id": resolved_anon,
        "session_id": session_id,
        "user_id": user_id,
        "authenticated": bool(user_id),
        "timestamp": (timestamp or datetime.utcnow()).isoformat(),
        "page_path": page_path,
        "properties": properties or {},
        "source": "server",
    }


def track_server_event(
    event_name: str,
    *,
    user_id: Optional[int] = None,
    anonymous_id: Optional[str] = None,
    session_id: Optional[str] = None,
    properties: Optional[Dict[str, Any]] = None,
    page_path: Optional[str] = None,
) -> None:
    """
    Fire-and-forget a trusted server event from synchronous code.

    Safe to call from anywhere, including inside a request handler or a webhook: it
    schedules the send on the running loop and returns immediately. If there is no
    running loop (a background thread, a script), the event is dropped rather than
    blocking the caller.
    """
    if not analytics_enabled():
        return

    try:
        event = build_server_event(
            event_name,
            user_id=user_id,
            anonymous_id=anonymous_id,
            session_id=session_id,
            properties=properties,
            page_path=page_path,
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("analytics: could not build server event %s: %s", event_name, exc)
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        logger.debug("analytics: no running loop, dropping %s", event_name)
        return

    task = loop.create_task(forward_events([event]))
    # Retain a reference so the task is not garbage collected mid-flight, and
    # swallow any exception it produces rather than letting it hit the loop handler.
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)


def stitch_identity(
    anonymous_id: Optional[str],
    user_id: int,
    traits: Optional[Dict[str, Any]] = None,
) -> None:
    """Fire-and-forget identity stitching from synchronous code."""
    if not anonymous_id or not analytics_enabled():
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return

    task = loop.create_task(forward_identify(anonymous_id, user_id, traits))
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)


# Strong references to in-flight background tasks. Without this, asyncio only holds a
# weak reference and a task can be collected before it finishes sending.
_BACKGROUND_TASKS: set = set()
