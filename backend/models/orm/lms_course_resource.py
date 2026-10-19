"""LMS Course Resource ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class LMSCourseResource(Base):
    """SQLAlchemy ORM model for course resources (videos, documents, links)"""
    __tablename__ = 'lms_course_resources'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    course_id = Column(
        Integer,
        ForeignKey('lms_courses.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Resource Info
    title = Column(String(255), nullable=False)
    resource_type = Column(String(50), nullable=False)  # video, document, link, etc.
    url = Column(String(500))
    description = Column(Text)
    order_index = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse",
        back_populates="resources"
    )
    
    def __repr__(self):
        return f"<LMSCourseResource(id={self.id}, title='{self.title}', type='{self.resource_type}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'resource_type': self.resource_type,
            'url': self.url,
            'description': self.description,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
