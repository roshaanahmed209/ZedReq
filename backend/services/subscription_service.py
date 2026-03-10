"""
Subscription Service - Server-side enforcement of plan-based feature limits.

Security Design:
- All quota checks run server-side (FastAPI dependency), never trust client.
- Atomic INSERT ... ON CONFLICT DO UPDATE prevents TOCTOU race conditions.
- Plan is always fetched from DB, never from JWT claims.
- UTC month boundaries (period_start = 1st of current month).
- Enterprise plan can only be assigned by super_admin.
"""
import logging
from datetime import date, datetime, timezone
from typing import Dict, Any, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.orm import Session

from models.orm.subscription_plan import SubscriptionPlan
from models.orm.user_subscription import UserSubscription
from models.orm.usage_tracking import UsageTracking

logger = logging.getLogger(__name__)

# Feature name constants - used in usage_tracking.feature column
FEATURE_AI_MESSAGES = "ai_messages"
FEATURE_COURSE_ENROLLMENTS = "course_enrollments"
FEATURE_INTERVIEW_SESSIONS = "interview_sessions"

# Default plan definitions
PLAN_DEFINITIONS = {
    "free": {
        "ai_messages_per_month": 30,
        "course_enrollments_per_month": 2,
        "interview_sessions_per_month": 1,
        "interview_max_duration_seconds": 60,
    },
    "pro": {
        "ai_messages_per_month": 100,
        "course_enrollments_per_month": 3,
        "interview_sessions_per_month": 3,
        "interview_max_duration_seconds": 60,
    },
    "premium": {
        "ai_messages_per_month": 500,
        "course_enrollments_per_month": 5,
        "interview_sessions_per_month": 5,
        "interview_max_duration_seconds": 60,
    },
    "enterprise": {
        "ai_messages_per_month": -1,  # unlimited
        "course_enrollments_per_month": -1,
        "interview_sessions_per_month": -1,
        "interview_max_duration_seconds": 600,  # 10 minutes
    },
}


class SubscriptionService:
    """Business logic for subscription management and quota enforcement."""

    def __init__(self, db: Session):
        self.db = db

    # =========================================================================
    # PLAN SEEDING
    # =========================================================================

    @staticmethod
    def seed_plans(db: Session) -> None:
        """
        Upsert free/pro/premium/enterprise plan rows on startup.
        Safe to call multiple times (idempotent).
        """
        for plan_name, limits in PLAN_DEFINITIONS.items():
            existing = db.query(SubscriptionPlan).filter_by(plan_name=plan_name).first()
            if existing:
                # Update limits if changed
                for key, value in limits.items():
                    setattr(existing, key, value)
                existing.is_active = True
                logger.info(f"Updated subscription plan: {plan_name}")
            else:
                plan = SubscriptionPlan(
                    plan_name=plan_name,
                    is_active=True,
                    **limits,
                )
                db.add(plan)
                logger.info(f"Created subscription plan: {plan_name}")
        db.commit()
        logger.info("Subscription plans seeded successfully")

    # =========================================================================
    # PLAN LOOKUP
    # =========================================================================

    def get_user_plan(self, user_id: int) -> Dict[str, Any]:
        """
        Get the current plan for a user.
        Returns the free plan if user has no subscription row (default fallback).
        Always fetches from DB - never trusts JWT or cache.
        """
        subscription = (
            self.db.query(UserSubscription)
            .filter(
                UserSubscription.user_id == user_id,
                UserSubscription.status == 'active'
            )
            .first()
        )

        if subscription and subscription.plan:
            plan = subscription.plan
            return {
                "plan_id": plan.plan_id,
                "plan_name": plan.plan_name,
                "ai_messages_per_month": plan.ai_messages_per_month,
                "course_enrollments_per_month": plan.course_enrollments_per_month,
                "interview_sessions_per_month": plan.interview_sessions_per_month,
                "interview_max_duration_seconds": plan.interview_max_duration_seconds,
                "subscription_id": subscription.subscription_id,
                "status": subscription.status,
                "assigned_by": subscription.assigned_by,
                "started_at": subscription.started_at.isoformat() if subscription.started_at else None,
                "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
            }

        # Default to free plan
        free_plan = self.db.query(SubscriptionPlan).filter_by(plan_name="free").first()
        if free_plan:
            return {
                "plan_id": free_plan.plan_id,
                "plan_name": "free",
                "ai_messages_per_month": free_plan.ai_messages_per_month,
                "course_enrollments_per_month": free_plan.course_enrollments_per_month,
                "interview_sessions_per_month": free_plan.interview_sessions_per_month,
                "interview_max_duration_seconds": free_plan.interview_max_duration_seconds,
                "subscription_id": None,
                "status": "active",
                "assigned_by": "system",
                "started_at": None,
                "expires_at": None,
            }

        # Absolute fallback (should never happen if seeding ran)
        return {
            "plan_id": None,
            "plan_name": "free",
            "ai_messages_per_month": 30,
            "course_enrollments_per_month": 2,
            "interview_sessions_per_month": 1,
            "interview_max_duration_seconds": 60,
            "subscription_id": None,
            "status": "active",
            "assigned_by": "system",
            "started_at": None,
            "expires_at": None,
        }

    # =========================================================================
    # USAGE TRACKING - ATOMIC CHECK AND INCREMENT
    # =========================================================================

    def _get_current_period_start(self) -> date:
        """Get the 1st day of the current UTC month."""
        today = datetime.now(timezone.utc).date()
        return today.replace(day=1)

    def get_usage(self, user_id: int, feature: str) -> int:
        """Get current month's usage count for a feature."""
        period_start = self._get_current_period_start()
        tracking = (
            self.db.query(UsageTracking)
            .filter(
                UsageTracking.user_id == user_id,
                UsageTracking.feature == feature,
                UsageTracking.period_start == period_start,
            )
            .first()
        )
        return tracking.usage_count if tracking else 0

    def check_quota(self, user_id: int, feature: str) -> Dict[str, Any]:
        """
        Check if user has remaining quota for a feature.
        Returns quota info without incrementing.
        """
        plan = self.get_user_plan(user_id)
        limit_key = f"{feature}_per_month"
        limit = plan.get(limit_key, 0)

        # -1 means unlimited
        if limit == -1:
            return {
                "allowed": True,
                "limit": -1,
                "used": self.get_usage(user_id, feature),
                "remaining": -1,  # unlimited
                "plan": plan["plan_name"],
            }

        used = self.get_usage(user_id, feature)
        remaining = max(0, limit - used)

        return {
            "allowed": used < limit,
            "limit": limit,
            "used": used,
            "remaining": remaining,
            "plan": plan["plan_name"],
        }

    def check_and_increment(self, user_id: int, feature: str) -> Dict[str, Any]:
        """
        Atomically check quota and increment usage count.

        Uses PostgreSQL's INSERT ... ON CONFLICT DO UPDATE with a WHERE clause
        to prevent race conditions. This is a single atomic SQL statement:
        - If usage_count < limit: increments and returns new count
        - If usage_count >= limit: no update, returns None (quota exceeded)

        Security: No TOCTOU vulnerability because check+increment is atomic.
        """
        plan = self.get_user_plan(user_id)
        limit_key = f"{feature}_per_month"
        limit = plan.get(limit_key, 0)
        period_start = self._get_current_period_start()

        # -1 means unlimited - always allow, but still track
        if limit == -1:
            result = self.db.execute(
                text("""
                    INSERT INTO usage_tracking (user_id, feature, period_start, usage_count, created_at, updated_at)
                    VALUES (:user_id, :feature, :period_start, 1, NOW(), NOW())
                    ON CONFLICT (user_id, feature, period_start)
                    DO UPDATE SET usage_count = usage_tracking.usage_count + 1, updated_at = NOW()
                    RETURNING usage_count
                """),
                {
                    "user_id": user_id,
                    "feature": feature,
                    "period_start": period_start,
                },
            )
            row = result.fetchone()
            self.db.commit()
            used = row[0] if row else 1
            return {
                "allowed": True,
                "limit": -1,
                "used": used,
                "remaining": -1,
                "plan": plan["plan_name"],
            }

        # Atomic check-and-increment: only increments if under limit
        result = self.db.execute(
            text("""
                INSERT INTO usage_tracking (user_id, feature, period_start, usage_count, created_at, updated_at)
                VALUES (:user_id, :feature, :period_start, 1, NOW(), NOW())
                ON CONFLICT (user_id, feature, period_start)
                DO UPDATE SET
                    usage_count = usage_tracking.usage_count + 1,
                    updated_at = NOW()
                WHERE usage_tracking.usage_count < :limit
                RETURNING usage_count
            """),
            {
                "user_id": user_id,
                "feature": feature,
                "period_start": period_start,
                "limit": limit,
            },
        )
        row = result.fetchone()
        self.db.commit()

        if row is None:
            # Quota exceeded - the WHERE clause prevented the update
            used = self.get_usage(user_id, feature)
            return {
                "allowed": False,
                "limit": limit,
                "used": used,
                "remaining": 0,
                "plan": plan["plan_name"],
            }

        used = row[0]
        remaining = max(0, limit - used)
        return {
            "allowed": True,
            "limit": limit,
            "used": used,
            "remaining": remaining,
            "plan": plan["plan_name"],
        }

    # =========================================================================
    # USAGE SUMMARY (for frontend display)
    # =========================================================================

    def get_usage_summary(self, user_id: int) -> Dict[str, Any]:
        """
        Get complete usage summary for a user across all features.
        Used by GET /subscription/usage endpoint.
        """
        plan = self.get_user_plan(user_id)

        features = [FEATURE_AI_MESSAGES, FEATURE_COURSE_ENROLLMENTS, FEATURE_INTERVIEW_SESSIONS]
        usage = {}

        for feature in features:
            limit_key = f"{feature}_per_month"
            limit = plan.get(limit_key, 0)
            used = self.get_usage(user_id, feature)

            if limit == -1:
                remaining = -1  # unlimited
            else:
                remaining = max(0, limit - used)

            usage[feature] = {
                "used": used,
                "limit": limit,
                "remaining": remaining,
            }

        return {
            "plan": {
                "plan_name": plan["plan_name"],
                "plan_id": plan.get("plan_id"),
                "status": plan.get("status", "active"),
                "assigned_by": plan.get("assigned_by", "system"),
                "started_at": plan.get("started_at"),
                "expires_at": plan.get("expires_at"),
                "interview_max_duration_seconds": plan.get("interview_max_duration_seconds", 60),
            },
            "usage": usage,
        }

    # =========================================================================
    # ENTERPRISE PLAN ASSIGNMENT (backoffice only)
    # =========================================================================

    def assign_enterprise_plan(self, user_id: int, assigned_by: str = "admin") -> Dict[str, Any]:
        """
        Assign enterprise plan to a user. Only called from backoffice with super_admin.
        """
        enterprise_plan = (
            self.db.query(SubscriptionPlan)
            .filter_by(plan_name="enterprise", is_active=True)
            .first()
        )
        if not enterprise_plan:
            raise ValueError("Enterprise plan not found in database")

        # Upsert user_subscriptions row
        existing = (
            self.db.query(UserSubscription)
            .filter_by(user_id=user_id)
            .first()
        )

        if existing:
            existing.plan_id = enterprise_plan.plan_id
            existing.status = "active"
            existing.assigned_by = assigned_by
            existing.started_at = datetime.now(timezone.utc)
            existing.expires_at = None  # Enterprise doesn't expire
        else:
            new_sub = UserSubscription(
                user_id=user_id,
                plan_id=enterprise_plan.plan_id,
                status="active",
                assigned_by=assigned_by,
            )
            self.db.add(new_sub)

        self.db.commit()
        logger.info(f"Enterprise plan assigned to user {user_id} by {assigned_by}")

        return {
            "success": True,
            "message": f"Enterprise plan assigned to user {user_id}",
            "plan_name": "enterprise",
        }

    def get_max_interview_duration(self, user_id: int) -> int:
        """Get the max interview duration in seconds for a user's plan."""
        plan = self.get_user_plan(user_id)
        return plan.get("interview_max_duration_seconds", 60)
