"""LMS User Section Progress ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, Boolean, Numeric, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course_section import LMSCourseSection


class LMSUserSectionProgress(Base):
    """SQLAlchemy ORM model for user progress and evaluation metrics within course sections"""
    __tablename__ = 'lms_user_section_progress'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    section_id = Column(
        Integer,
        ForeignKey('lms_course_sections.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Progress Info
    completed_items = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    
    # Evaluation / Performance Metrics (populated by evaluate_answer cascade)
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    accuracy_percentage = Column(Numeric(5, 2), default=0.00)
    total_points_earned = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    section: Mapped["LMSCourseSection"] = relationship(
        "LMSCourseSection",
        back_populates="user_progress"
    )
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'section_id', name='uq_user_section'),
    )
    
    def __repr__(self):
        return f"<LMSUserSectionProgress(id={self.id}, user_id={self.user_id}, section_id={self.section_id}, accuracy={self.accuracy_percentage}%)>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'section_id': self.section_id,
            'completed_items': self.completed_items,
            'is_completed': self.is_completed,
            'questions_answered': self.questions_answered or 0,
            'correct_answers': self.correct_answers or 0,
            'accuracy_percentage': float(self.accuracy_percentage) if self.accuracy_percentage else 0.0,
            'total_points_earned': self.total_points_earned or 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations and self.section:
            data['section_title'] = self.section.title
            data['section_total_items'] = self.section.total_items
            if self.section.total_items and self.section.total_items > 0:
                data['progress_percentage'] = round((self.completed_items / self.section.total_items) * 100, 2)
        
        return data
