"""Job Application ORM Model"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Column, Integer, String, Text,
    ForeignKey, DateTime, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .job_posting import JobPosting


class JobApplication(Base):
    """SQLAlchemy ORM model for job applications"""
    __tablename__ = 'job_applications'
    
    # Primary Key
    application_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    job_id = Column(
        Integer,
        ForeignKey('job_postings.job_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    applicant_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Application details
    status = Column(String(30), default='pending', index=True)
    cover_letter = Column(Text)
    match_score = Column(Integer)  # AI match percentage (0-100)
    
    # Timestamp
    applied_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job: Mapped["JobPosting"] = relationship(
        "JobPosting",
        back_populates="applications"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('job_id', 'applicant_id', name='uq_job_applicant'),
        Index('idx_applications_job_status', 'job_id', 'status'),
    )
    
    def __repr__(self):
        return f"<JobApplication(id={self.application_id}, job_id={self.job_id}, applicant_id={self.applicant_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'application_id': self.application_id,
            'job_id': self.job_id,
            'applicant_id': self.applicant_id,
            'status': self.status,
            'cover_letter': self.cover_letter,
            'match_score': self.match_score,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
        }
