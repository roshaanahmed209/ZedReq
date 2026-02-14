"""User Project ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class UserProject(Base):
    """SQLAlchemy ORM model for user_projects table"""
    __tablename__ = 'user_projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    title = Column(String(200), nullable=False)
    description = Column(Text)
    url = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    associated_with = Column(String(200))  # company or school name
    technologies = Column(JSON)  # Array of technology names
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="projects"
    )
    
    def __repr__(self):
        return f"<UserProject(id={self.id}, user_id={self.user_id}, title='{self.title}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'associated_with': self.associated_with,
            'technologies': self.technologies if self.technologies else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
