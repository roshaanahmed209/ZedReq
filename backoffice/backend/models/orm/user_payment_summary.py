"""User Payment Summary ORM Model"""
from sqlalchemy import Column, Integer, Numeric, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func

from config.database_orm import Base


class UserPaymentSummary(Base):
    """SQLAlchemy ORM model for user_payment_summary table"""
    __tablename__ = 'user_payment_summary'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    plan_id = Column(Integer, nullable=True)
    total_amount_paid = Column(Numeric(12, 2), nullable=False, default=0)
    total_refunded = Column(Numeric(12, 2), nullable=False, default=0)
    last_paid_amount = Column(Numeric(12, 2), nullable=True)
    last_payment_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_user_payment_summary_user_id', 'user_id'),
    )
    
    def __repr__(self):
        return f"<UserPaymentSummary(id={self.id}, user_id={self.user_id}, total_paid={self.total_amount_paid})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'total_amount_paid': float(self.total_amount_paid) if self.total_amount_paid else 0.0,
            'total_refunded': float(self.total_refunded) if self.total_refunded else 0.0,
            'last_paid_amount': float(self.last_paid_amount) if self.last_paid_amount else None,
            'last_payment_date': self.last_payment_date.isoformat() + 'Z' if self.last_payment_date else None,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }
