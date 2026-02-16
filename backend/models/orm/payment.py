"""Payment ORM Model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CHAR
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base


class Payment(Base):
    """SQLAlchemy ORM model for payment table"""
    __tablename__ = 'payment'
    
    pay_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Payment provider info (Stripe/PayPal tokens - NEVER store raw card numbers)
    payment_provider = Column(String(50), nullable=False, default='stripe')
    provider_customer_id = Column(String(255))
    provider_payment_method_id = Column(String(255))
    
    # Card display info only (last 4 digits for display)
    card_last_four = Column(CHAR(4))
    card_brand = Column(String(20))
    card_exp_month = Column(Integer)
    card_exp_year = Column(Integer)
    
    # Billing info
    billing_name = Column(String(100))
    billing_email = Column(String(150))
    
    # Subscription status
    subscription_status = Column(String(50), default='inactive')
    subscription_plan = Column(String(50))
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    
    # Trial info
    trial_taken = Column(Boolean, default=False)
    trial_end = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[uid],
        backref="payment"
    )
    
    def __repr__(self):
        return f"<Payment(pay_id={self.pay_id}, uid={self.uid}, plan='{self.subscription_plan}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'pay_id': self.pay_id,
            'uid': self.uid,
            'payment_provider': self.payment_provider,
            'provider_customer_id': self.provider_customer_id,
            'provider_payment_method_id': self.provider_payment_method_id,
            'card_last_four': self.card_last_four,
            'card_brand': self.card_brand,
            'card_exp_month': self.card_exp_month,
            'card_exp_year': self.card_exp_year,
            'billing_name': self.billing_name,
            'billing_email': self.billing_email,
            'subscription_status': self.subscription_status,
            'subscription_plan': self.subscription_plan,
            'subscription_start': self.subscription_start.isoformat() if self.subscription_start else None,
            'subscription_end': self.subscription_end.isoformat() if self.subscription_end else None,
            'trial_taken': self.trial_taken,
            'trial_end': self.trial_end.isoformat() if self.trial_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
