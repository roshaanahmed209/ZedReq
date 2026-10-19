"""User Subscription ORM Model - Links users to subscription plans"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base


class UserSubscription(Base):
    """
    One active subscription per user.
    Users without a row default to 'free' plan in SubscriptionService.
    """
    __tablename__ = 'user_subscriptions'

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        unique=True,
        nullable=False,
        index=True
    )
    plan_id = Column(
        Integer,
        ForeignKey('subscription_plans.plan_id', ondelete='RESTRICT'),
        nullable=False,
        index=True
    )
    status = Column(String(20), nullable=False, default='active', index=True)  # active, cancelled, expired
    assigned_by = Column(String(50), nullable=False, default='system')  # system, admin, self
    started_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    plan: Mapped["SubscriptionPlan"] = relationship("SubscriptionPlan", back_populates="user_subscriptions")

    def __repr__(self):
        return (
            f"<UserSubscription(subscription_id={self.subscription_id}, "
            f"user_id={self.user_id}, plan_id={self.plan_id}, status='{self.status}')>"
        )

    def to_dict(self):
        return {
            'subscription_id': self.subscription_id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'status': self.status,
            'assigned_by': self.assigned_by,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
