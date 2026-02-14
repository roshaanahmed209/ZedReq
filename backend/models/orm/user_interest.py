"""User Interest ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class UserInterest(Base):
    """SQLAlchemy ORM model for user_interests table"""
    __tablename__ = 'user_interests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    interest_type = Column(String(50), nullable=False)  # company, group, influencer, school
    name = Column(String(200), nullable=False)
    url = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="interests"
    )
    
    def __repr__(self):
        return f"<UserInterest(id={self.id}, user_id={self.user_id}, type='{self.interest_type}', name='{self.name}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'interest_type': self.interest_type,
            'name': self.name,
            'url': self.url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
