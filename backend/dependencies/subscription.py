"""
Subscription Quota Dependencies - Server-side enforcement for feature limits.

Security:
- These are FastAPI Dependencies injected into protected endpoints.
- All checks run on the server; frontend UI is cosmetic only.
- Plan is always fetched from the DB, never from JWT claims.
- Atomic check-and-increment prevents race conditions.
- Returns quota info in response headers (X-Quota-*) for frontend display.
"""
import logging
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from config.database_orm import get_db
from dependencies.auth import get_current_user
from services.subscription_service import (
    SubscriptionService,
    FEATURE_AI_MESSAGES,
    FEATURE_COURSE_ENROLLMENTS,
    FEATURE_INTERVIEW_SESSIONS,
)

logger = logging.getLogger(__name__)


def _get_subscription_service(db: Session = Depends(get_db)) -> SubscriptionService:
    """Create a SubscriptionService instance with the current DB session."""
    return SubscriptionService(db)


async def require_ai_quota(
    request: Request,
    current_user: dict = Depends(get_current_user),
    svc: SubscriptionService = Depends(_get_subscription_service),
) -> dict:
    """
    Dependency that checks and increments AI message quota atomically.
    Raises 403 if monthly limit is exceeded.
    Stores quota info on request.state for response headers.
    """
    user_id = current_user["id"]
    result = svc.check_and_increment(user_id, FEATURE_AI_MESSAGES)

    if not result["allowed"]:
        logger.warning(
            f"AI message quota exceeded for user {user_id}: "
            f"{result['used']}/{result['limit']} ({result['plan']} plan)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Your message limit has been reached. Upgrade your plan to increase your limit.",
                "limit": result["limit"],
                "used": result["used"],
                "plan": result["plan"],
                "feature": FEATURE_AI_MESSAGES,
            },
        )

    # Store quota info for response headers
    request.state.quota_info = result
    return current_user


async def require_lms_quota(
    request: Request,
    current_user: dict = Depends(get_current_user),
    svc: SubscriptionService = Depends(_get_subscription_service),
) -> dict:
    """
    Dependency that checks and increments LMS course enrollment quota atomically.
    Raises 403 if monthly enrollment limit is exceeded.
    """
    user_id = current_user["id"]
    result = svc.check_and_increment(user_id, FEATURE_COURSE_ENROLLMENTS)

    if not result["allowed"]:
        logger.warning(
            f"Course enrollment quota exceeded for user {user_id}: "
            f"{result['used']}/{result['limit']} ({result['plan']} plan)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Your enrollment limit has been reached. Upgrade your plan to increase your limit.",
                "limit": result["limit"],
                "used": result["used"],
                "plan": result["plan"],
                "feature": FEATURE_COURSE_ENROLLMENTS,
            },
        )

    request.state.quota_info = result
    return current_user


async def require_interview_quota(
    request: Request,
    current_user: dict = Depends(get_current_user),
    svc: SubscriptionService = Depends(_get_subscription_service),
) -> dict:
    """
    Dependency that checks and increments interview session quota atomically.
    Raises 403 if monthly interview limit is exceeded.
    Also stores max_call_duration on request.state for the endpoint to use.
    """
    user_id = current_user["id"]
    result = svc.check_and_increment(user_id, FEATURE_INTERVIEW_SESSIONS)

    if not result["allowed"]:
        logger.warning(
            f"Interview session quota exceeded for user {user_id}: "
            f"{result['used']}/{result['limit']} ({result['plan']} plan)"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Monthly interview session quota exceeded",
                "limit": result["limit"],
                "used": result["used"],
                "plan": result["plan"],
                "feature": FEATURE_INTERVIEW_SESSIONS,
            },
        )

    # Also fetch max interview duration for the endpoint
    max_duration = svc.get_max_interview_duration(user_id)
    request.state.quota_info = result
    request.state.max_interview_duration = max_duration
    return current_user


async def get_quota_info(
    current_user: dict = Depends(get_current_user),
    svc: SubscriptionService = Depends(_get_subscription_service),
) -> dict:
    """
    Dependency that returns full usage summary without incrementing.
    Used by the /subscription/usage endpoint.
    """
    user_id = current_user["id"]
    return svc.get_usage_summary(user_id)
