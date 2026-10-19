"""LMS User Course ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class LMSUserCourse(Base):
    """SQLAlchemy ORM model for user course enrollment and progress"""
    __tablename__ = 'lms_user_courses'
    
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
    
    # Progress Info
    progress = Column(Integer, default=0)  # 0-100 percentage
    status = Column(String(20), default='not_started', index=True)  # not_started, in_progress, completed
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    last_accessed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse",
        back_populates="user_courses"
    )
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_user_course'),
        Index('idx_lms_user_courses_user', 'user_id'),
        Index('idx_lms_user_courses_course', 'course_id'),
        Index('idx_lms_user_courses_status', 'status'),
        Index('idx_lms_user_courses_lookup', 'user_id', 'course_id', 'status'),
    )
    
    def __repr__(self):
        return f"<LMSUserCourse(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, progress={self.progress}%)>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'progress': self.progress,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'last_accessed_at': self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations and self.course:
            data['course_title'] = self.course.title
            data['course_icon'] = self.course.icon
            data['course_description'] = self.course.description
            data['course_lessons'] = self.course.lessons
            data['course_duration'] = self.course.duration
            data['course_category'] = self.course.category
            data['course_difficulty'] = self.course.difficulty
        
        return data
