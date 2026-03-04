"""Revenue Transaction ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class RevenueTransaction(Base):
    """SQLAlchemy ORM model for revenue_transactions table"""
    __tablename__ = 'revenue_transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    plan_type = Column(String(50))
    provider = Column(String(50), index=True)
    provider_transaction_id = Column(String(255), index=True)
    status = Column(String(20), default='pending', index=True)
    description = Column(Text)
    metadata = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<RevenueTransaction(id={self.id}, type='{self.transaction_type}', amount={self.amount})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount) if self.amount else 0.0,
            'currency': self.currency,
            'plan_type': self.plan_type,
            'provider': self.provider,
            'provider_transaction_id': self.provider_transaction_id,
            'status': self.status,
            'description': self.description,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
