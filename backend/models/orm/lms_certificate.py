"""LMS Certificate ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .lms_course import LMSCourse


class LMSCertificate(Base):
    """SQLAlchemy ORM model for course completion certificates"""
    __tablename__ = 'lms_certificates'
    
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
    
    # Certificate Info
    certificate_number = Column(String(100), unique=True)
    title = Column(String(255), nullable=False)
    issued_at = Column(DateTime, server_default=func.now())
    expiry_date = Column(DateTime)
    pdf_url = Column(String(500))
    
    # Relationships
    course: Mapped["LMSCourse"] = relationship(
        "LMSCourse"
    )
    
    # Table constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_user_course_cert'),
        Index('idx_lms_certificates_user', 'user_id'),
    )
    
    def __repr__(self):
        return f"<LMSCertificate(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, number='{self.certificate_number}')>"
    
    def to_dict(self, include_relations=False):
        """Convert model to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'certificate_number': self.certificate_number,
            'title': self.title,
            'issued_at': self.issued_at.isoformat() if self.issued_at else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'pdf_url': self.pdf_url,
        }
        
        if include_relations and self.course:
            data['course_title'] = self.course.title
            data['course_icon'] = self.course.icon
        
        return data
