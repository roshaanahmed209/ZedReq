"""LMS Rate-Limit ORM Model

Tracks how many times a user has invoked an expensive / AI-powered LMS action
(e.g. refresh recommendations, generate course questions).

Design decisions
----------------
* One row per (user_id, action, course_id) tuple — course_id is NULL for
  global actions such as "generate_recommendations".
* `count` is incremented server-side inside a single UPDATE … RETURNING so the
  read-modify-write is atomic within a transaction.
* `first_used_at` and `last_used_at` give an audit trail without needing a
  separate events table.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class LMSRateLimit(Base):
    """Persistent, server-side rate-limit counter for LMS AI actions."""

    __tablename__ = "lms_rate_limits"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.uid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Short identifier for the action being rate-limited.
    # Defined values:
    #   "generate_recommendations" – refresh AI recommendations
    #   "generate_questions"       – trigger Azel agent per course
    action = Column(String(64), nullable=False)

    # NULL for global actions; set to course_id for per-course actions.
    course_id = Column(
        Integer,
        ForeignKey("lms_courses.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    count = Column(Integer, nullable=False, default=0)

    first_used_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        # Enforce uniqueness so there is always exactly one row per scope.
        UniqueConstraint(
            "user_id", "action", "course_id",
            name="uq_lms_rate_limit_user_action_course",
        ),
        Index("idx_lms_rate_limits_user_action", "user_id", "action"),
    )

    def __repr__(self):
        return (
            f"<LMSRateLimit(user={self.user_id}, action={self.action!r}, "
            f"course={self.course_id}, count={self.count})>"
        )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "course_id": self.course_id,
            "count": self.count,
            "first_used_at": self.first_used_at.isoformat() if self.first_used_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
        }
