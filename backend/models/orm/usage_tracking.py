"""Usage Tracking ORM Model - Monthly feature usage counters"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func

from config.database_orm import Base


class UsageTracking(Base):
    """
    Tracks per-user, per-feature, per-month usage counts.
    UNIQUE(user_id, feature, period_start) enables atomic upsert via
    INSERT ... ON CONFLICT DO UPDATE.
    """
    __tablename__ = 'usage_tracking'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False
    )
    feature = Column(String(50), nullable=False)  # ai_messages, course_enrollments, interview_sessions
    period_start = Column(Date, nullable=False)  # 1st of the month (UTC)
    usage_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'feature', 'period_start', name='uq_usage_user_feature_period'),
        Index('idx_usage_tracking_lookup', 'user_id', 'feature', 'period_start'),
    )

    def __repr__(self):
        return (
            f"<UsageTracking(id={self.id}, user_id={self.user_id}, "
            f"feature='{self.feature}', period='{self.period_start}', count={self.usage_count})>"
        )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'feature': self.feature,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
