"""Subscription Plan ORM Model - Defines plan tiers and their limits"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from config.database_orm import Base


class SubscriptionPlan(Base):
    """
    Static plan definitions table.
    Seeded on startup with free/pro/enterprise rows.
    -1 means unlimited for any limit column.
    """
    __tablename__ = 'subscription_plans'

    plan_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_name = Column(String(50), unique=True, nullable=False, index=True)

    # Feature limits (-1 = unlimited)
    ai_messages_per_month = Column(Integer, nullable=False, default=0)
    course_enrollments_per_month = Column(Integer, nullable=False, default=0)
    interview_sessions_per_month = Column(Integer, nullable=False, default=0)
    interview_max_duration_seconds = Column(Integer, nullable=False, default=60)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="plan")

    def __repr__(self):
        return f"<SubscriptionPlan(plan_id={self.plan_id}, name='{self.plan_name}')>"

    def to_dict(self):
        return {
            'plan_id': self.plan_id,
            'plan_name': self.plan_name,
            'ai_messages_per_month': self.ai_messages_per_month,
            'course_enrollments_per_month': self.course_enrollments_per_month,
            'interview_sessions_per_month': self.interview_sessions_per_month,
            'interview_max_duration_seconds': self.interview_max_duration_seconds,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
