"""Profile Analytics ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class ProfileAnalytics(Base):
    """SQLAlchemy ORM model for profile_analytics table"""
    __tablename__ = 'profile_analytics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    viewer_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    view_type = Column(String(50), nullable=False)  # profile_view, search_appearance
    source = Column(String(50))  # search, feed, direct, etc.
    viewed_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="profile_views"
    )
    viewer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[viewer_id],
        backref="viewed_profiles"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_profile_analytics_user_viewed', 'user_id', 'viewed_at'),
        Index('idx_profile_analytics_viewer', 'viewer_id'),
    )
    
    def __repr__(self):
        return f"<ProfileAnalytics(id={self.id}, user_id={self.user_id}, view_type='{self.view_type}')>"
    
    def to_dict(self, include_viewer_info=False):
        """Convert to dictionary"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'viewer_id': self.viewer_id,
            'view_type': self.view_type,
            'source': self.source,
            'viewed_at': self.viewed_at.isoformat() if self.viewed_at else None,
        }
        
        if include_viewer_info and self.viewer:
            result['viewer'] = {
                'id': self.viewer.uid,
                'username': self.viewer.username,
                'name': self.viewer.name
            }
        
        return result
