"""
Purge a user from operational tables after writing a full snapshot to deleted_user_archive.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, or_, text
from sqlalchemy.orm import Session

from models.orm import (
    User,
    Connection,
    ConnectionRequest,
    Description,
    Notification,
    ProfileAnalytics,
    Payment,
    UserSubscription,
    DeletedUserArchive,
    UsersContext,
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
        Archive full snapshot, remove related operational rows, delete user (CASCADE).
        Returns former user_email (for notifications).
        """
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError("User")

        desc_id = user.description_id
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

            # user_id is NOT NULL — must remove rows for this user as recipient, not only
            # rows where they appear as related_user_id (SQLAlchemy otherwise NULLs user_id).
            self.db.execute(
                delete(Notification).where(
                    or_(
                        Notification.user_id == user_id,
                        Notification.related_user_id == user_id,
                    )
                )
            )
            self.db.execute(
                delete(ProfileAnalytics).where(ProfileAnalytics.viewer_id == user_id)
            )
            # Delete users_context explicitly — column is NOT NULL so SQLAlchemy's
            # automatic SET NULL before CASCADE would fail without this.
            self.db.execute(
                delete(UsersContext).where(UsersContext.user_id == user_id)
            )
            # connection_requests / connections: User backrefs make SQLAlchemy UPDATE
            # child FKs to NULL before delete, which violates NOT NULL on these columns.
            self.db.execute(
                delete(ConnectionRequest).where(
                    or_(
                        ConnectionRequest.sender_id == user_id,
                        ConnectionRequest.receiver_id == user_id,
                    )
                )
            )
            self.db.execute(
                delete(Connection).where(
                    or_(
                        Connection.follower_uid == user_id,
                        Connection.followed_uid == user_id,
                    )
                )
            )

            if desc_id:
                self.db.execute(delete(Description).where(Description.desc_id == desc_id))

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
