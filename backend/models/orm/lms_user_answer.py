"""LMS User Answer ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, Boolean, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_question import LMSQuestion


class LMSUserAnswer(Base):
    """SQLAlchemy ORM model for user answers to questions"""
    __tablename__ = 'lms_user_answers'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    question_id = Column(
        Integer,
        ForeignKey('lms_questions.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Answer Info
    answer_text = Column(Text)
    is_correct = Column(Boolean)
    points_earned = Column(Integer, default=0)
    
    # Evaluation Info
    feedback = Column(Text)
    submitted_at = Column(DateTime, server_default=func.now())
    evaluated_at = Column(DateTime)
    
    # Relationships
    question: Mapped["LMSQuestion"] = relationship(
        "LMSQuestion",
        back_populates="user_answers"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_lms_user_answers_user', 'user_id'),
        Index('idx_lms_user_answers_question', 'question_id'),
        Index('idx_lms_user_answers_user_correct', 'user_id', 'is_correct'),
    )
    
    def __repr__(self):
        return f"<LMSUserAnswer(id={self.id}, user_id={self.user_id}, question_id={self.question_id}, correct={self.is_correct})>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'answer_text': self.answer_text,
            'is_correct': self.is_correct,
            'points_earned': self.points_earned,
            'feedback': self.feedback,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'evaluated_at': self.evaluated_at.isoformat() if self.evaluated_at else None,
        }
        
        if include_relations and self.question:
            data['question_text'] = self.question.question_text
            data['question_type'] = self.question.question_type
            data['points'] = self.question.points
        
        return data
