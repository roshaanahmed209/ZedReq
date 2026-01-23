"""Description (Profile) ORM Model"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base


class Description(Base):
    """SQLAlchemy ORM model for description (user profile) table"""
    __tablename__ = 'description'
    
    desc_id = Column(Integer, primary_key=True, autoincrement=True)
    short_desc = Column(Text)
    about = Column(Text)
    certificates = Column(Text)
    proj_id = Column(Integer)
    skills = Column(Text)
    current_status = Column(String(100))
    profile_pic = Column(Text)
    cover_pic = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    # Users can reference this via description_id foreign key
    # users: Mapped[list["User"]] = relationship("User", back_populates="description")
    
    def __repr__(self):
        return f"<Description(desc_id={self.desc_id}, current_status='{self.current_status}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'desc_id': self.desc_id,
            'id': self.desc_id,
            'short_desc': self.short_desc,
            'about': self.about,
            'certificates': self.certificates,
            'proj_id': self.proj_id,
            'skills': self.skills,
            'current_status': self.current_status,
            'profile_pic': self.profile_pic,
            'cover_pic': self.cover_pic,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
