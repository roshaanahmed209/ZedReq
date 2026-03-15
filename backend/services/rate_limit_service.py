"""Rate-Limit Service

Provides atomic server-side rate limiting for expensive LMS AI actions.

Usage
-----
    from services.rate_limit_service import RateLimitService, RateLimitExceeded

    svc = RateLimitService(db)
    try:
        remaining = svc.check_and_increment(
            user_id=42,
            action="generate_questions",
            max_calls=3,
            course_id=7,   # omit for global actions
        )
        # remaining == how many calls the user still has after this one
    except RateLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc))
"""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from models.orm.lms_rate_limit import LMSRateLimit

logger = logging.getLogger(__name__)

# ── well-known action names (use these constants everywhere) ─────────────────
ACTION_GENERATE_RECOMMENDATIONS = "generate_recommendations"
ACTION_GENERATE_QUESTIONS = "generate_questions"


class RateLimitExceeded(Exception):
    """Raised when a user has exhausted their allowed calls for an action."""

    def __init__(self, action: str, max_calls: int, course_id: Optional[int] = None):
        scope = f" for course {course_id}" if course_id is not None else ""
        super().__init__(
            f"Rate limit reached for '{action}'{scope}. "
            f"Maximum {max_calls} attempt(s) allowed."
        )
        self.action = action
        self.max_calls = max_calls
        self.course_id = course_id


class RateLimitService:
    """Handles atomic read-increment-check against the lms_rate_limits table."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_and_increment(
        self,
        user_id: int,
        action: str,
        max_calls: int,
        course_id: Optional[int] = None,
    ) -> int:
        """Atomically check the current count, raise if limit is reached, else
        increment and return the number of remaining calls after this one.

        Parameters
        ----------
        user_id   : authenticated user
        action    : one of the ACTION_* constants defined in this module
        max_calls : maximum number of calls permitted (inclusive)
        course_id : scope to a specific course; None means global

        Returns
        -------
        int  – remaining calls (0 means this was the last allowed call)

        Raises
        ------
        RateLimitExceeded  – if the user has already reached max_calls
        """
        record = self._get_or_create(user_id, action, course_id)

        if record.count >= max_calls:
            logger.warning(
                "[RateLimit] BLOCKED user_id=%s action=%r course_id=%s "
                "count=%s max=%s",
                user_id, action, course_id, record.count, max_calls,
            )
            raise RateLimitExceeded(action, max_calls, course_id)

        record.count += 1
        self.db.flush()  # write within the calling transaction; caller commits

        remaining = max_calls - record.count
        logger.info(
            "[RateLimit] ALLOWED user_id=%s action=%r course_id=%s "
            "count=%s/%s remaining=%s",
            user_id, action, course_id, record.count, max_calls, remaining,
        )
        return remaining

    def get_count(
        self,
        user_id: int,
        action: str,
        course_id: Optional[int] = None,
    ) -> int:
        """Return the current call count without modifying it."""
        record = self._get_record(user_id, action, course_id)
        return record.count if record else 0

    def get_remaining(
        self,
        user_id: int,
        action: str,
        max_calls: int,
        course_id: Optional[int] = None,
    ) -> int:
        """Return how many calls the user still has left (never negative)."""
        return max(0, max_calls - self.get_count(user_id, action, course_id))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_record(
        self,
        user_id: int,
        action: str,
        course_id: Optional[int],
    ) -> Optional[LMSRateLimit]:
        query = self.db.query(LMSRateLimit).filter(
            LMSRateLimit.user_id == user_id,
            LMSRateLimit.action == action,
        )
        if course_id is None:
            query = query.filter(LMSRateLimit.course_id.is_(None))
        else:
            query = query.filter(LMSRateLimit.course_id == course_id)
        return query.first()

    def _get_or_create(
        self,
        user_id: int,
        action: str,
        course_id: Optional[int],
    ) -> LMSRateLimit:
        """Fetch the row or INSERT a new one with count=0.

        Uses a SELECT … FOR UPDATE to prevent concurrent increments from
        creating duplicate rows under high concurrency.
        """
        query = self.db.query(LMSRateLimit).filter(
            LMSRateLimit.user_id == user_id,
            LMSRateLimit.action == action,
        )
        if course_id is None:
            query = query.filter(LMSRateLimit.course_id.is_(None))
        else:
            query = query.filter(LMSRateLimit.course_id == course_id)

        record = query.with_for_update().first()

        if record is None:
            record = LMSRateLimit(
                user_id=user_id,
                action=action,
                course_id=course_id,
                count=0,
            )
            self.db.add(record)
            self.db.flush()  # assign PK so subsequent code can reference it

        return record
