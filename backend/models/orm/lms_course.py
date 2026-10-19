"""LMS Course ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Index
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course_section import LMSCourseSection
    from .lms_course_resource import LMSCourseResource
    from .lms_question import LMSQuestion
    from .lms_user_course import LMSUserCourse
    from .lms_user_course_performance import LMSUserCoursePerformance


class LMSCourse(Base):
    """SQLAlchemy ORM model for LMS courses"""
    __tablename__ = 'lms_courses'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Course Info
    title = Column(String(255), nullable=False)
    description = Column(Text)
    icon = Column(String(10))
    lessons = Column(Integer, default=0)
    duration = Column(String(50))
    category = Column(String(100), index=True)
    difficulty = Column(String(20), default='beginner', index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sections: Mapped[list["LMSCourseSection"]] = relationship(
        "LMSCourseSection",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="LMSCourseSection.order_index"
    )
    
    resources: Mapped[list["LMSCourseResource"]] = relationship(
        "LMSCourseResource",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="LMSCourseResource.order_index"
    )
    
    questions: Mapped[list["LMSQuestion"]] = relationship(
        "LMSQuestion",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="LMSQuestion.order_index"
    )
    
    user_courses: Mapped[list["LMSUserCourse"]] = relationship(
        "LMSUserCourse",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    user_performances: Mapped[list["LMSUserCoursePerformance"]] = relationship(
        "LMSUserCoursePerformance",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_lms_courses_category_active', 'category', 'is_active'),
    )
    
    def __repr__(self):
        return f"<LMSCourse(id={self.id}, title='{self.title}')>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'lessons': self.lessons,
            'duration': self.duration,
            'category': self.category,
            'difficulty': self.difficulty,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_relations:
            data['sections_count'] = len(self.sections) if self.sections else 0
            data['resources_count'] = len(self.resources) if self.resources else 0
            data['questions_count'] = len(self.questions) if self.questions else 0
        
        return data
