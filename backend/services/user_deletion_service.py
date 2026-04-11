"""
Purge a user from operational tables after writing a full snapshot to deleted_user_archive.

Security pattern: EXPLICIT PRE-DELETE before ORM object removal.

SQLAlchemy tracks every relationship that has a `backref` pointing to User. When
`session.delete(user)` is called SQLAlchemy tries to nullify every backref FK before
issuing the DELETE. Any NOT NULL constraint on those columns causes an
IntegrityError. The fix is to issue explicit `DELETE … WHERE FK = user_id` statements
for every such table BEFORE calling `session.delete(user)`, bypassing ORM bookkeeping
entirely. Tables that have ON DELETE CASCADE in the DB but NO backref to User (LMS
tables, job_postings, job_applications, usage_tracking, etc.) are safely left to the
database CASCADE triggered by the final DELETE FROM users.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, or_, text
from sqlalchemy.orm import Session

from models.orm import (
    # Core social
    User,
    Connection,
    ConnectionRequest,
    Notification,
    # Profile content
    ProfileAnalytics,
    UsersContext,
    UserExperience,
    UserEducation,
    UserProject,
    UserInterest,
    UserRecommendation,
    # Content authored by user
    PostComment,
    LiveInterview,
    # Billing (snapshot already taken before delete)
    Payment,
    # Archive + other
    Description,
    DeletedUserArchive,
    UserSubscription,
)
from utils.errors import NotFoundError
from utils.logger import setup_logger

logger = setup_logger(__name__)

USER_SNAPSHOT_REDACT_KEYS = frozenset(
    {
        "password_hash",
        "two_factor_secret",
        "two_factor_backup_codes",
        "verification_token",
    }
)


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def _user_row_to_snapshot(user: User) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for col in User.__table__.columns:
        key = col.name
        if key in USER_SNAPSHOT_REDACT_KEYS:
            continue
        out[key] = _json_safe(getattr(user, key, None))
    return out


def _description_snapshot_for_id(db: Session, desc_id: int) -> Optional[Dict[str, Any]]:
    row = db.execute(
        text(
            """
            SELECT desc_id, short_desc, about, certificates, proj_id, skills, current_status,
                   role, company, location, city, country, industry, profile_pic, cover_pic, resume,
                   created_at, updated_at, profile_version,
                   embedding::text AS embedding
            FROM description
            WHERE desc_id = :did
            """
        ),
        {"did": desc_id},
    ).mappings().first()
    if not row:
        return None
    return {k: _json_safe(row[k]) for k in row.keys()}


def _payment_to_snapshot(p: Payment) -> Dict[str, Any]:
    base = p.to_dict()
    base["paddle_subscription_id"] = p.paddle_subscription_id
    base["paddle_price_id"] = p.paddle_price_id
    return base


class UserDeletionService:
    def __init__(self, db: Session):
        self.db = db

    def purge_user(
        self,
        user_id: int,
        *,
        deletion_source: str,
        admin_id: Optional[int] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """
        Archive full snapshot, remove all child rows, then delete user.
        Returns former user_email (for notifications).

        Delete order is significant: tables that reference other child tables
        (e.g. notifications → connection_requests) must be deleted before those
        they reference, to avoid FK violations during pre-delete.
        """
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError("User")

        desc_id = user.description_id

        # ── Snapshot phase ────────────────────────────────────────────────────
        user_snapshot = _user_row_to_snapshot(user)

        description_snapshot: Optional[Dict[str, Any]] = None
        if desc_id:
            description_snapshot = _description_snapshot_for_id(self.db, desc_id)

        subs = (
            self.db.query(UserSubscription)
            .filter(UserSubscription.user_id == user_id)
            .all()
        )
        subscriptions_snapshot: List[Dict[str, Any]] = [s.to_dict() for s in subs]

        pays = self.db.query(Payment).filter(Payment.uid == user_id).all()
        payments_snapshot: List[Dict[str, Any]] = [_payment_to_snapshot(p) for p in pays]

        try:
            # ── Archive write ──────────────────────────────────────────────────
            archive = DeletedUserArchive(
                original_uid=user.uid,
                user_email=user.user_email,
                deletion_source=deletion_source,
                admin_id=admin_id,
                reason=(reason[:2000] if reason else None),
                user_snapshot=user_snapshot,
                description_snapshot=description_snapshot,
                subscriptions_snapshot=subscriptions_snapshot or None,
                payments_snapshot=payments_snapshot or None,
                ip_address=ip_address,
                user_agent=(user_agent[:1024] if user_agent else None),
            )
            self.db.add(archive)

            # ── Explicit pre-deletes ───────────────────────────────────────────
            # Every table listed here has a NOT NULL FK to users.uid AND a
            # SQLAlchemy backref on User. Without these explicit deletes SQLAlchemy
            # issues UPDATE … SET <fk> = NULL before the user DELETE, which the DB
            # rejects with NotNullViolation.
            #
            # ORDER: delete leaf dependents before the rows they reference.
            #   notifications → connection_requests (nullable FK, but delete first anyway)
            #   profile_analytics owns no children

            # 1. Notifications — user_id (NOT NULL, backref="notifications")
            #                    related_user_id (nullable, but clean up while here)
            self.db.execute(
                delete(Notification).where(
                    or_(
                        Notification.user_id == user_id,
                        Notification.related_user_id == user_id,
                    )
                )
            )

            # 2. Connection requests — sender_id / receiver_id (both NOT NULL)
            self.db.execute(
                delete(ConnectionRequest).where(
                    or_(
                        ConnectionRequest.sender_id == user_id,
                        ConnectionRequest.receiver_id == user_id,
                    )
                )
            )

            # 3. Connections — follower_uid / followed_uid (both NOT NULL)
            self.db.execute(
                delete(Connection).where(
                    or_(
                        Connection.follower_uid == user_id,
                        Connection.followed_uid == user_id,
                    )
                )
            )

            # 4. Profile analytics — user_id (NOT NULL, backref="profile_views")
            #                        viewer_id (nullable, clean up while here)
            self.db.execute(
                delete(ProfileAnalytics).where(
                    or_(
                        ProfileAnalytics.user_id == user_id,
                        ProfileAnalytics.viewer_id == user_id,
                    )
                )
            )

            # 5. Users context — user_id (NOT NULL, backref="user_context")
            self.db.execute(
                delete(UsersContext).where(UsersContext.user_id == user_id)
            )

            # 6. Profile feature tables — user_id (all NOT NULL, all have backrefs)
            self.db.execute(
                delete(UserExperience).where(UserExperience.user_id == user_id)
            )
            self.db.execute(
                delete(UserEducation).where(UserEducation.user_id == user_id)
            )
            self.db.execute(
                delete(UserProject).where(UserProject.user_id == user_id)
            )
            self.db.execute(
                delete(UserInterest).where(UserInterest.user_id == user_id)
            )
            # UserRecommendation: user appears as recipient OR as recommender
            self.db.execute(
                delete(UserRecommendation).where(
                    or_(
                        UserRecommendation.user_id == user_id,
                        UserRecommendation.recommender_id == user_id,
                    )
                )
            )

            # 7. Post comments — uid (NOT NULL, backref="post_comments")
            self.db.execute(
                delete(PostComment).where(PostComment.uid == user_id)
            )

            # 8. Live interviews — user_id (NOT NULL, backref="live_interviews")
            self.db.execute(
                delete(LiveInterview).where(LiveInterview.user_id == user_id)
            )

            # 9. Payment — uid (NOT NULL, backref="payment")
            #    Snapshot was captured above; safe to delete now.
            self.db.execute(
                delete(Payment).where(Payment.uid == user_id)
            )

            # 10. Description — referenced via User.description_id (viewonly, no cascade)
            if desc_id:
                self.db.execute(
                    delete(Description).where(Description.desc_id == desc_id)
                )

            # ── Final user delete (triggers DB CASCADE for remaining tables) ───
            # Tables handled by DB ON DELETE CASCADE (no backref on User, so no
            # ORM interference): user_subscriptions, usage_tracking, job_postings,
            # job_applications, job_saved, lms_*, azel_search_urls, etc.
            email = user.user_email
            self.db.delete(user)
            self.db.commit()

            logger.info(
                "Purged user uid=%s from operational DB (source=%s)",
                user_id,
                deletion_source,
            )
            return email

        except Exception:
            self.db.rollback()
            logger.error("purge_user failed for uid=%s", user_id, exc_info=True)
            raise
