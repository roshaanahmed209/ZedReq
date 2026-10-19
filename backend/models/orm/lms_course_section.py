"""LMS Course Section ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse
    from .lms_question import LMSQuestion
    from .lms_user_section_progress import LMSUserSectionProgress


class LMSCourseSection(Base):
    """SQLAlchemy ORM model for course sections/modules"""
    __tablename__ = 'lms_course_sections'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    course_id = Column(
        Integer,
        ForeignKey('lms_courses.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Section Info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse",
        back_populates="sections"
    )
    
    questions: Mapped[list["LMSQuestion"]] = relationship(
        "LMSQuestion",
        back_populates="section",
        cascade="all, delete-orphan",
        order_by="LMSQuestion.order_index"
    )
    
    user_progress: Mapped[list["LMSUserSectionProgress"]] = relationship(
        "LMSUserSectionProgress",
        back_populates="section",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    def __repr__(self):
        return f"<LMSCourseSection(id={self.id}, title='{self.title}', course_id={self.course_id})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'order_index': self.order_index,
            'total_items': self.total_items,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
