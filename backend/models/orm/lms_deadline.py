"""LMS Deadline ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class LMSDeadline(Base):
    """SQLAlchemy ORM model for course deadlines/assignments"""
    __tablename__ = 'lms_deadlines'
    
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
    
    # Deadline Info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    reminder_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_lms_deadlines_user_due', 'user_id', 'due_date'),
    )
    
    def __repr__(self):
        return f"<LMSDeadline(id={self.id}, user_id={self.user_id}, title='{self.title}', due={self.due_date})>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'reminder_sent': self.reminder_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_relations and self.course:
            data['course_title'] = self.course.title
            data['course_icon'] = self.course.icon
        
        return data
