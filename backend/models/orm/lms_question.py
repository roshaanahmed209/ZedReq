"""LMS Question ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse
    from .lms_course_section import LMSCourseSection
    from .lms_user_answer import LMSUserAnswer


class LMSQuestion(Base):
    """SQLAlchemy ORM model for questions/assessments"""
    __tablename__ = 'lms_questions'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    course_id = Column(
        Integer,
        ForeignKey('lms_courses.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    section_id = Column(
        Integer,
        ForeignKey('lms_course_sections.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Question Info
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default='text')  # text, multiple_choice, etc.
    options = Column(JSONB)  # For multiple choice questions
    correct_answer = Column(Text)
    points = Column(Integer, default=1)
    order_index = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse",
        back_populates="questions"
    )
    
    section: Mapped["LMSCourseSection"] = relationship(
        "LMSCourseSection",
        back_populates="questions"
    )
    
    user_answers: Mapped[list["LMSUserAnswer"]] = relationship(
        "LMSUserAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_lms_questions_course', 'course_id'),
    )
    
    def __repr__(self):
        return f"<LMSQuestion(id={self.id}, course_id={self.course_id}, type='{self.question_type}')>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'course_id': self.course_id,
            'section_id': self.section_id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'points': self.points,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_relations:
            data['answers_count'] = self.user_answers.count() if hasattr(self.user_answers, 'count') else len(self.user_answers)
        
        return data
