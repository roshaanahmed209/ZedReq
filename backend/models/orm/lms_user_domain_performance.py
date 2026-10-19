"""LMS User Domain Performance ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, Numeric, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_domain import LMSDomain


class LMSUserDomainPerformance(Base):
    """SQLAlchemy ORM model for user performance by learning domain"""
    __tablename__ = 'lms_user_domain_performance'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    domain_id = Column(
        Integer,
        ForeignKey('lms_domains.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Performance Metrics
    questions_answered = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    accuracy_percentage = Column(Numeric(5, 2), default=0.00)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    domain: Mapped["LMSDomain"] = relationship(
        "LMSDomain",
        back_populates="user_performances"
    )
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'domain_id', name='uq_user_domain'),
        Index('idx_lms_domain_perf_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<LMSUserDomainPerformance(id={self.id}, user_id={self.user_id}, domain_id={self.domain_id}, accuracy={self.accuracy_percentage}%)>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'domain_id': self.domain_id,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy_percentage': float(self.accuracy_percentage) if self.accuracy_percentage else 0.0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations and self.domain:
            data['domain_name'] = self.domain.name
            data['domain_icon'] = self.domain.icon
            data['domain_description'] = self.domain.description
        
        return data
