"""LMS Recommendation ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class LMSRecommendation(Base):
    """SQLAlchemy ORM model for AI course recommendations"""
    __tablename__ = 'lms_recommendations'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    course_id = Column(
        Integer,
        ForeignKey('lms_courses.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Recommendation Info
    reason = Column(Text)
    priority = Column(Integer, default=0)
    is_dismissed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_lms_recommendations_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<LMSRecommendation(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, priority={self.priority})>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'reason': self.reason,
            'priority': self.priority,
            'is_dismissed': self.is_dismissed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_relations and self.course:
            data['course_title'] = self.course.title
            data['course_icon'] = self.course.icon
            data['course_description'] = self.course.description
        
        return data
