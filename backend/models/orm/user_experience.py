"""User Experience ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class UserExperience(Base):
    """SQLAlchemy ORM model for user_experience table"""
    __tablename__ = 'user_experience'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    title = Column(String(150), nullable=False)
    company = Column(String(150), nullable=False)
    location = Column(String(150))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)
    description = Column(Text)
    employment_type = Column(String(50))  # full-time, part-time, contract, internship, etc.
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="experiences"
    )
    
    def __repr__(self):
        return f"<UserExperience(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_current': self.is_current,
            'description': self.description,
            'employment_type': self.employment_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
