"""LMS User Course Performance ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, Numeric, ForeignKey, Date, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class LMSUserCoursePerformance(Base):
    """SQLAlchemy ORM model for user performance by course"""
    __tablename__ = 'lms_user_course_performance'
    
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
    
    # Performance Metrics
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    accuracy_percentage = Column(Numeric(5, 2), default=0.00)
    total_points_earned = Column(Integer, default=0)
    last_activity_date = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse",
        back_populates="user_performances"
    )
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_user_course_perf'),
        Index('idx_lms_course_perf_user', 'user_id'),
        Index('idx_lms_course_perf_course', 'course_id'),
        Index('idx_lms_course_perf_user_course', 'user_id', 'course_id'),
    )
    
    def __repr__(self):
        return f"<LMSUserCoursePerformance(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, accuracy={self.accuracy_percentage}%)>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'accuracy_percentage': float(self.accuracy_percentage) if self.accuracy_percentage else 0.0,
            'total_points_earned': self.total_points_earned,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations and self.course:
            data['course_title'] = self.course.title
            data['course_icon'] = self.course.icon
            data['course_category'] = self.course.category
        
        return data
