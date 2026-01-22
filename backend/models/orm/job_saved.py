"""Job Saved (Bookmark) ORM Model"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Column, Integer,
    ForeignKey, DateTime, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .job_posting import JobPosting


class JobSaved(Base):
    """SQLAlchemy ORM model for saved/bookmarked jobs"""
    __tablename__ = 'job_saved'
    
    # Primary Key
    saved_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    job_id = Column(
        Integer,
        ForeignKey('job_postings.job_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Timestamp
    saved_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job: Mapped["JobPosting"] = relationship(
        "JobPosting",
        back_populates="saves"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('job_id', 'user_id', name='uq_job_user_saved'),
    )
    
    def __repr__(self):
        return f"<JobSaved(id={self.saved_id}, job_id={self.job_id}, user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'saved_id': self.saved_id,
            'job_id': self.job_id,
            'user_id': self.user_id,
            'saved_at': self.saved_at.isoformat() if self.saved_at else None,
        }
