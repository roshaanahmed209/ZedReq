"""Reserved Seat ORM Model"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Column, Integer, String, DateTime, Index, ForeignKey
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class ReservedSeat(Base):
    """SQLAlchemy ORM model for reserved seats"""
    __tablename__ = 'reserved_seats'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User Information
    email = Column(String(255), nullable=False, unique=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Promo Code
    promo_code = Column(String(20), nullable=False, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id]
    )
    
    def __repr__(self):
        return f"<ReservedSeat(id={self.id}, email='{self.email}', promo_code='{self.promo_code}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'user_id': self.user_id,
            'promo_code': self.promo_code,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
