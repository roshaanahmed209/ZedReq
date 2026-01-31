"""LMS Dashboard ORM Model"""
from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base


class LMSDashboard(Base):
    """SQLAlchemy ORM model for aggregated user learning statistics"""
    __tablename__ = 'lms_dashboard'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        unique=True,
        index=True
    )
    
    # Statistics
    total_questions = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    wrong_answers = Column(Integer, default=0)
    overall_accuracy = Column(Numeric(5, 2), default=0.00)
    day_streak = Column(Integer, default=0)
    last_activity_date = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Table indexes
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_lms_dashboard_user'),
        Index('idx_lms_dashboard_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<LMSDashboard(id={self.id}, user_id={self.user_id}, accuracy={self.overall_accuracy}%)>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'overall_accuracy': float(self.overall_accuracy) if self.overall_accuracy else 0.0,
            'day_streak': self.day_streak,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
