"""User Education ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class UserEducation(Base):
    """SQLAlchemy ORM model for user_education table"""
    __tablename__ = 'user_education'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    school = Column(String(200), nullable=False)
    degree = Column(String(150))
    field_of_study = Column(String(150))
    start_year = Column(Integer)
    end_year = Column(Integer)
    grade = Column(String(50))
    activities = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="educations"
    )
    
    def __repr__(self):
        return f"<UserEducation(id={self.id}, user_id={self.user_id}, school='{self.school}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'school': self.school,
            'degree': self.degree,
            'field_of_study': self.field_of_study,
            'start_year': self.start_year,
            'end_year': self.end_year,
            'grade': self.grade,
            'activities': self.activities,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
