"""Bearable Cost ORM Model"""
from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime
from sqlalchemy.sql import func

from config.database_orm import Base


class BearableCost(Base):
    """SQLAlchemy ORM model for bearable_costs table"""
    __tablename__ = 'bearable_costs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cost_name = Column(String(100), nullable=False, unique=True)
    amount = Column(Numeric(10, 4), nullable=False)
    is_fixed = Column(Boolean, nullable=False, default=False)
    unit_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<BearableCost(id={self.id}, name='{self.cost_name}', amount={self.amount}, fixed={self.is_fixed})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'cost_name': self.cost_name,
            'amount': float(self.amount) if self.amount else 0.0,
            'is_fixed': self.is_fixed,
            'unit_type': self.unit_type,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
            'updated_at': self.updated_at.isoformat() + 'Z' if self.updated_at else None,
        }
