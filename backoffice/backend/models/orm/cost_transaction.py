"""Cost Transaction ORM Model"""
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class CostTransaction(Base):
    """SQLAlchemy ORM model for cost_transactions table"""
    __tablename__ = 'cost_transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cost_category = Column(String(50), nullable=False, index=True)
    service_name = Column(String(100), index=True)
    amount = Column(Numeric(10, 4), nullable=False)
    currency = Column(String(3), default='USD')
    unit_type = Column(String(20))
    quantity = Column(Numeric(10, 2))
    user_id = Column(Integer, nullable=True, index=True)
<<<<<<< HEAD
    metadata = Column(JSONB)
=======
    extra_metadata = Column('metadata', JSONB)
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<CostTransaction(id={self.id}, category='{self.cost_category}', amount={self.amount})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'cost_category': self.cost_category,
            'service_name': self.service_name,
            'amount': float(self.amount) if self.amount else 0.0,
            'currency': self.currency,
            'unit_type': self.unit_type,
            'quantity': float(self.quantity) if self.quantity else None,
            'user_id': self.user_id,
<<<<<<< HEAD
            'metadata': self.metadata,
=======
            'metadata': self.extra_metadata,
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
