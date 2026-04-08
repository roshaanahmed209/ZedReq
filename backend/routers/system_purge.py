"""Internal endpoint for backoffice-triggered full user purge (archive + DB + Firebase)."""
import hashlib
import hmac
import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.database_orm import get_db
from config.settings import get_settings
from dependencies.rate_limit import RateLimiter
from services.messaging_service import MessagingService
from services.user_deletion_service import UserDeletionService
from utils.errors import NotFoundError
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(tags=["System"])

# Rate limit for the purge endpoint — keyed by target user_id to prevent
# rapid-fire account deletion with a compromised key.
_purge_limiter = RateLimiter(requests_per_minute=10)


class PurgeUserRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    source: str = "admin"
    admin_id: Optional[int] = None
    reason: Optional[str] = None


def _verify_hmac_signature(
    key: str,
    user_id: int,
    timestamp: Optional[str],
    signature: Optional[str],
) -> None:
    """Verify HMAC-SHA256 signature and reject requests older than 60 seconds."""
    if not timestamp or not signature:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    try:
        ts = int(timestamp)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    if abs(time.time() - ts) > 60:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request expired",
        )

    expected_sig = hmac.new(
        key.encode(),
        f"{user_id}:{timestamp}".encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_sig, signature):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


@router.post("/purge-user")
async def purge_user_internal(
    request: Request,
    body: PurgeUserRequest,
    x_purge_sig: Optional[str] = Header(None, alias="X-Purge-Sig"),
    x_timestamp: Optional[str] = Header(None, alias="X-Timestamp"),
    db: Session = Depends(get_db),
):
    settings = get_settings()
    purge_key = getattr(settings, "BACKOFFICE_USER_PURGE_KEY", None) or ""
    if not purge_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User purge API is not configured (BACKOFFICE_USER_PURGE_KEY)",
        )

    _verify_hmac_signature(purge_key, body.user_id, x_timestamp, x_purge_sig)

    if not _purge_limiter.is_allowed(body.user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many purge requests for this user — retry later.",
            headers={"Retry-After": "60"},
        )

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")

    source = body.source if body.source in ("admin", "user_self") else "admin"
    try:
        svc = UserDeletionService(db)
        email = svc.purge_user(
            body.user_id,
            deletion_source=source,
            admin_id=body.admin_id,
            reason=body.reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        logger.error("purge_user_internal failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purge user",
        )

    messaging = MessagingService()
    purged = await messaging.purge_conversations_for_user(body.user_id)
    if not purged:
        _enqueue_firebase_retry(db, body.user_id)

    return {"success": True, "user_email": email, "firebase_purged": purged}


def _enqueue_firebase_retry(db: Session, user_id: int) -> None:
    """Insert a pending Firebase purge retry row if the realtime DB call failed."""
    try:
        db.execute(
            __import__("sqlalchemy").text(
                """
                INSERT INTO firebase_purge_retries (user_id)
                VALUES (:uid)
                ON CONFLICT DO NOTHING
                """
            ),
            {"uid": user_id},
        )
        db.commit()
    except Exception:
        logger.error("Failed to enqueue Firebase retry for uid=%s", user_id, exc_info=True)
