"""LMS Activity ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class LMSActivity(Base):
    """SQLAlchemy ORM model for learning activity log"""
    __tablename__ = 'lms_activities'
    
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
        ForeignKey('lms_courses.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Activity Info
    activity_type = Column(String(50), nullable=False)  # enrollment, section_complete, answer_submit, etc.
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(10))
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_lms_activities_user', 'user_id'),
        Index('idx_lms_activities_created', 'created_at'),
        Index('idx_lms_activities_user_created', 'user_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<LMSActivity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}', title='{self.title}')>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'activity_type': self.activity_type,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_relations and self.course:
            data['course_title'] = self.course.title
            data['course_icon'] = self.course.icon
        
        return data
