"""LMS Weekly Performance ORM Model"""
from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base


class LMSWeeklyPerformance(Base):
    """SQLAlchemy ORM model for daily/weekly performance tracking"""
    __tablename__ = 'lms_weekly_performance'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Date
    date = Column(Date, nullable=False)
    
    # Performance Metrics
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    study_time_minutes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_user_date'),
        Index('idx_lms_weekly_perf_user_date', 'user_id', 'date'),
    )
    
    def __repr__(self):
        return f"<LMSWeeklyPerformance(id={self.id}, user_id={self.user_id}, date={self.date}, questions={self.questions_answered})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        accuracy = 0.0
        if self.questions_answered > 0:
            accuracy = round((self.correct_answers / self.questions_answered) * 100, 2)
        
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'study_time_minutes': self.study_time_minutes,
            'accuracy': accuracy,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
