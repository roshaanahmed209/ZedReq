"""LMS Domain ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_user_domain_performance import LMSUserDomainPerformance


class LMSDomain(Base):
    """SQLAlchemy ORM model for learning domains/categories"""
    __tablename__ = 'lms_domains'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Domain Info
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    icon = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user_performances: Mapped[list["LMSUserDomainPerformance"]] = relationship(
        "LMSUserDomainPerformance",
        back_populates="domain",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self):
        return f"<LMSDomain(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
