"""Live Interview ORM Model"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, 
    DateTime, Index, JSON
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User
    from .job_posting import JobPosting


class LiveInterview(Base):
    """SQLAlchemy ORM model for live interview sessions"""
    __tablename__ = 'live_interviews'
    
    # Primary Key
    interview_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    job_id = Column(
        Integer,
        ForeignKey('job_postings.job_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Tavus Integration
    tavus_conversation_id = Column(String(255), index=True)
    tavus_response = Column(JSONB)
    
    # Interview Data
    questions = Column(JSONB)  # Generated interview questions with criteria
    user_responses = Column(JSONB)  # User's responses from interview
    
    # Scoring
    overall_score = Column(Integer)  # 0-100
    score_breakdown = Column(JSONB)  # Detailed scores by criteria
    feedback = Column(Text)  # Detailed feedback from Tav_check_agent
    
    # Tracking
    attempt_number = Column(Integer, nullable=False, default=1)
    status = Column(String(20), default='pending', index=True)
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", backref="live_interviews")
    job: Mapped["JobPosting"] = relationship("JobPosting", backref="live_interviews")
    
    # Table indexes
    __table_args__ = (
        Index('idx_live_interviews_user_job', 'user_id', 'job_id'),
    )
    
    def __repr__(self):
        return f"<LiveInterview(interview_id={self.interview_id}, user_id={self.user_id}, job_id={self.job_id}, status='{self.status}')>"
    
    def to_dict(self, include_relations=False) -> Dict[str, Any]:
        """Convert model to dictionary"""
        data = {
            'interview_id': self.interview_id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'tavus_conversation_id': self.tavus_conversation_id,
            'tavus_response': self.tavus_response,
            'questions': self.questions,
            'user_responses': self.user_responses,
            'overall_score': self.overall_score,
            'score_breakdown': self.score_breakdown,
            'feedback': self.feedback,
            'attempt_number': self.attempt_number,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            if self.job:
                data['job'] = {
                    'job_id': self.job.job_id,
                    'title': self.job.title,
                    'company_name': self.job.company_name,
                }
            if self.user:
                data['user'] = {
                    'user_id': self.user.uid,
                    'name': self.user.name,
                }
        
        return data
