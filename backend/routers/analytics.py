"""
Analytics Router - same-origin ingest endpoint for the frontend tracking SDK.

The browser posts here (same origin as the rest of the API), the server enriches with
context it can actually trust, and the events are forwarded to the back office
collector in the background. Nothing about the collector - its URL, its API key - is
ever exposed to the client.

These endpoints are intentionally unauthenticated: most of the funnel happens before
anyone logs in, and refusing anonymous events would defeat the entire purpose. A
bearer token is read opportunistically when present so authenticated events carry the
real ``user_id`` instead of one the client asserted.
"""
import logging
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

from services.analytics_service import (
    analytics_enabled,
    forward_events,
    forward_identify,
)
from services.analytics_taxonomy import EVENT_NAMES, SERVER_ONLY_EVENTS
from utils.client_context import extract_country, is_bot, parse_user_agent

logger = logging.getLogger(__name__)

router = APIRouter()
optional_security = HTTPBearer(auto_error=False)

MAX_BATCH = 50
MAX_PROPERTY_KEYS = 40
MAX_PROPERTY_STRING = 500

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{6,64}$")
_EVENT_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{2,79}$")

# Property keys that are dropped before anything is stored, whatever the caller sends.
# The SDK never sets them; this is the backstop that keeps credentials and card data
# out of the analytics store even if someone instruments a form carelessly.
_FORBIDDEN_PROPERTY_KEYS = {
    "password", "passwd", "pass", "new_password", "old_password",
    "token", "access_token", "refresh_token", "id_token", "temp_token",
    "api_key", "apikey", "secret", "client_secret", "authorization", "auth",
    "card", "card_number", "cardnumber", "cvv", "cvc", "pan", "iban",
    "ssn", "otp", "two_factor_code", "2fa", "backup_code",
    "session_token", "cookie", "jwt",
}


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class _AnalyticsRateLimiter:
    """
    Per-IP sliding window over analytics batches.

    Generous by design - a busy session legitimately produces a lot of events - but
    enough to stop a single client from flooding the collector. In-memory only: this
    guards a best-effort pipeline, so it is not worth a Redis round trip per beacon.
    """

    def __init__(self, limit: int = 120, window: int = 60):
        self._limit = limit
        self._window = window
        self._lock = Lock()
        self._hits: Dict[str, List[float]] = defaultdict(list)
        self._last_sweep = time.time()

    def allow(self, ip: str) -> bool:
        now = time.time()
        with self._lock:
            if now - self._last_sweep > self._window * 5:
                cutoff = now - self._window
                self._hits = defaultdict(
                    list,
                    {
                        key: [t for t in times if t > cutoff]
                        for key, times in self._hits.items()
                        if any(t > cutoff for t in times)
                    },
                )
                self._last_sweep = now

            times = self._hits[ip]
            times[:] = [t for t in times if now - t < self._window]
            if len(times) >= self._limit:
                return False
            times.append(now)
            return True


_limiter = _AnalyticsRateLimiter()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TrackedEvent(BaseModel):
    """One event as sent by the browser SDK."""

    event_id: str = Field(..., min_length=6, max_length=64)
    event_name: str = Field(..., min_length=3, max_length=80)
    anonymous_id: str = Field(..., min_length=6, max_length=64)
    session_id: Optional[str] = Field(None, max_length=64)
    timestamp: Optional[str] = Field(None, max_length=40)

    page_url: Optional[str] = Field(None, max_length=1000)
    page_path: Optional[str] = Field(None, max_length=500)
    page_title: Optional[str] = Field(None, max_length=255)
    referrer: Optional[str] = Field(None, max_length=1000)

    utm_source: Optional[str] = Field(None, max_length=120)
    utm_medium: Optional[str] = Field(None, max_length=120)
    utm_campaign: Optional[str] = Field(None, max_length=160)
    utm_content: Optional[str] = Field(None, max_length=160)
    utm_term: Optional[str] = Field(None, max_length=160)

    properties: Optional[Dict[str, Any]] = None

    @field_validator("event_id", "anonymous_id")
    @classmethod
    def _check_id(cls, v: str) -> str:
        if not _ID_RE.match(v):
            raise ValueError("invalid identifier")
        return v

    @field_validator("session_id")
    @classmethod
    def _check_session(cls, v: Optional[str]) -> Optional[str]:
        if v and not _ID_RE.match(v):
            raise ValueError("invalid session id")
        return v

    @field_validator("event_name")
    @classmethod
    def _check_name(cls, v: str) -> str:
        v = v.strip().lower()
        if not _EVENT_NAME_RE.match(v):
            raise ValueError("event names must be lower_snake_case object_action")
        return v


class TrackBatch(BaseModel):
    events: List[TrackedEvent] = Field(..., min_length=1, max_length=MAX_BATCH)


class IdentifyRequest(BaseModel):
    anonymous_id: str = Field(..., min_length=6, max_length=64)

    @field_validator("anonymous_id")
    @classmethod
    def _check_anon(cls, v: str) -> str:
        if not _ID_RE.match(v):
            raise ValueError("invalid anonymous id")
        return v


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_user_id(credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[int]:
    """
    Read the user id from a bearer token if one was sent, else None.

    Never raises: an expired or malformed token simply means the event is recorded as
    anonymous. Analytics must not be the thing that logs somebody out.
    """
    if not credentials or not credentials.credentials:
        return None
    try:
        from dependencies.auth import verify_token

        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        return int(user_id) if user_id is not None else None
    except Exception:  # noqa: BLE001
        return None


def _clean_properties(props: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Strip sensitive keys, cap breadth and depth, coerce to JSON-safe scalars."""
    if not props or not isinstance(props, dict):
        return {}

    cleaned: Dict[str, Any] = {}
    for key, value in list(props.items())[:MAX_PROPERTY_KEYS]:
        if not isinstance(key, str):
            continue
        if key.lower() in _FORBIDDEN_PROPERTY_KEYS:
            continue
        if isinstance(value, str):
            cleaned[key[:60]] = value[:MAX_PROPERTY_STRING]
        elif isinstance(value, (int, float, bool)) or value is None:
            cleaned[key[:60]] = value
        elif isinstance(value, (list, tuple)):
            cleaned[key[:60]] = [
                v[:MAX_PROPERTY_STRING] if isinstance(v, str) else v
                for v in list(value)[:20]
                if isinstance(v, (str, int, float, bool))
            ]
        # Nested dicts are deliberately dropped: they encourage dumping whole API
        # payloads into analytics, which is how sensitive data leaks in.
    return cleaned


def _parse_timestamp(raw: Optional[str]) -> str:
    """Normalise the client timestamp, pinning anything implausible to server time."""
    now = datetime.now(timezone.utc)
    if not raw:
        return now.isoformat()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        if parsed > now + timedelta(minutes=5) or parsed < now - timedelta(days=7):
            return now.isoformat()
        return parsed.isoformat()
    except (ValueError, TypeError):
        return now.isoformat()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
async def track_events(
    batch: TrackBatch,
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
):
    """
    Accept a batch of events from the browser SDK.

    Always returns 202, even when nothing is stored. The SDK treats this endpoint as
    fire-and-forget, and an error response would only cause pointless retries; the
    caller has no useful way to react to an analytics failure anyway.
    """
    if not analytics_enabled():
        return {"accepted": 0, "enabled": False}

    user_agent = request.headers.get("user-agent")

    # Drop bot traffic at the door. Counting crawlers as visitors would quietly
    # inflate every denominator in the funnel.
    if is_bot(user_agent):
        return {"accepted": 0}

    client_ip = request.client.host if request.client else "unknown"
    if not _limiter.allow(client_ip):
        return {"accepted": 0, "throttled": True}

    user_id = _resolve_user_id(credentials)
    context = parse_user_agent(user_agent)
    country = extract_country(request.headers)

    enriched: List[Dict[str, Any]] = []
    for event in batch.events:
        # Unknown names are dropped here so a stale deploy or a typo cannot pollute
        # the taxonomy. The back office enforces the same list independently.
        if event.event_name not in EVENT_NAMES:
            logger.debug("analytics: unknown event name %s", event.event_name)
            continue

        # A browser cannot claim a conversion. These only count from the server.
        if event.event_name in SERVER_ONLY_EVENTS:
            logger.debug("analytics: refused client-side %s", event.event_name)
            continue

        enriched.append(
            {
                "event_id": event.event_id,
                "event_name": event.event_name,
                "anonymous_id": event.anonymous_id,
                "session_id": event.session_id,
                "user_id": user_id,
                "authenticated": bool(user_id),
                "timestamp": _parse_timestamp(event.timestamp),
                "page_url": event.page_url,
                "page_path": event.page_path,
                "page_title": event.page_title,
                "referrer": event.referrer,
                # Derived server-side - never taken from the client.
                "device_type": context["device_type"],
                "browser": context["browser"],
                "operating_system": context["operating_system"],
                "country": country,
                "utm_source": event.utm_source,
                "utm_medium": event.utm_medium,
                "utm_campaign": event.utm_campaign,
                "utm_content": event.utm_content,
                "utm_term": event.utm_term,
                "properties": _clean_properties(event.properties),
                "source": "client",
            }
        )

    if enriched:
        background_tasks.add_task(forward_events, enriched)

    return {"accepted": len(enriched)}


@router.post("/identify", status_code=status.HTTP_202_ACCEPTED)
async def identify(
    payload: IdentifyRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
):
    """
    Stitch the caller's anonymous id to their authenticated account.

    The ``user_id`` comes from the bearer token, never from the request body - a
    client must not be able to attach someone else's anonymous history to its own
    account, or to claim another user's journey.
    """
    if not analytics_enabled():
        return {"stitched": False, "enabled": False}

    user_id = _resolve_user_id(credentials)
    if not user_id:
        return {"stitched": False}

    background_tasks.add_task(forward_identify, payload.anonymous_id, user_id, {})
    return {"stitched": True}
