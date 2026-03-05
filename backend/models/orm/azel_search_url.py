"""Azel Search URL ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class AzelSearchUrl(Base):
    """SQLAlchemy ORM model for Azel agent search URLs"""
    __tablename__ = 'azel_search_urls'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    course_id = Column(
        Integer,
        ForeignKey('lms_courses.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # URL Info
    url_id = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(String(500))
    snippet = Column(Text)
    search_query = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse",
        back_populates=None  # We don't need reverse relationship
    )
    
    # Table constraints and indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', 'url_id', name='uq_azel_search_urls'),
        Index('idx_azel_search_urls_user_course', 'user_id', 'course_id'),
        Index('idx_azel_search_urls_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<AzelSearchUrl(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, url_id='{self.url_id}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'url_id': self.url_id,
            'url': self.url,
            'title': self.title,
            'snippet': self.snippet,
            'search_query': self.search_query,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
