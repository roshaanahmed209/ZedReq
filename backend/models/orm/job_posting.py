"""Job Posting ORM Model"""
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, 
    ForeignKey, DateTime, Index, TypeDecorator
)
from sqlalchemy.orm import relationship, Mapped, deferred
from sqlalchemy.sql import func

from config.database_orm import Base


# Custom type for pgvector - just passes through as text for ORM purposes
class VectorType(TypeDecorator):
    """Pass-through type for pgvector - actual vector operations use raw SQL"""
    impl = Text
    cache_ok = True


if TYPE_CHECKING:
    from .job_application import JobApplication
    from .job_saved import JobSaved


class JobPosting(Base):
    """SQLAlchemy ORM model for job postings"""
    __tablename__ = 'job_postings'
    
    # Primary Key
    job_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key to users table
    poster_id = Column(
        Integer, 
        ForeignKey('users.uid', ondelete='CASCADE'), 
        nullable=False,
        index=True
    )
    
    # Core Job Info
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    company_name = Column(String(150))
    location = Column(String(150), index=True)
    city = Column(String(150), index=True)  # Parsed city from location
    country = Column(String(150), index=True)  # Parsed country from location
    job_link = Column(Text)  # Job link/reference within ZedRec domain
    
    # Type & Requirements
    job_type = Column(String(50), default='full-time', index=True)
    is_remote = Column(Boolean, default=False, index=True)
    experience_level = Column(String(50))
    skills_required = Column(Text)
    
    # Salary
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    
    # Status
    status = Column(String(20), default='active', index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Embedding (pgvector) - deferred to avoid loading in regular queries
    # This column is managed via raw SQL, not through SQLAlchemy ORM
    # Using VectorType as a pass-through - actual vector operations use raw SQL
    embedding = deferred(Column('embedding', VectorType, nullable=True))
    
    # Relationships
    applications: Mapped[list["JobApplication"]] = relationship(
        "JobApplication",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    saves: Mapped[list["JobSaved"]] = relationship(
        "JobSaved",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_job_postings_remote_active', 'is_remote', 'status'),
        Index('idx_job_postings_created_desc', created_at.desc()),
    )
    
    def __repr__(self):
        return f"<JobPosting(job_id={self.job_id}, title='{self.title}')>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'job_id': self.job_id,
            'poster_id': self.poster_id,
            'title': self.title,
            'description': self.description,
            'company_name': self.company_name,
            'location': self.location,
            'city': self.city,
            'country': self.country,
            'job_link': self.job_link,
            'job_type': self.job_type,
            'is_remote': self.is_remote,
            'experience_level': self.experience_level,
            'skills_required': self.skills_required,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            data['application_count'] = self.applications.count()
            data['save_count'] = self.saves.count()
        
        return data
