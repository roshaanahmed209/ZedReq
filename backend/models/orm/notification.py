"""Notification ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User
    from .connection_request import ConnectionRequest


class Notification(Base):
    """SQLAlchemy ORM model for notifications table"""
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    related_user_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='SET NULL'),
        nullable=True
    )
    related_request_id = Column(
        Integer,
        ForeignKey('connection_requests.id', ondelete='SET NULL'),
        nullable=True
    )
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        backref="notifications"
    )
    related_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[related_user_id],
        backref="related_notifications"
    )
    related_request: Mapped["ConnectionRequest"] = relationship(
        "ConnectionRequest",
        foreign_keys=[related_request_id]
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_notif_user', 'user_id'),
        Index('idx_notif_unread', 'user_id', 'is_read'),
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}', is_read={self.is_read})>"
    
    def to_dict(self, include_related_info=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'related_user_id': self.related_user_id,
            'related_request_id': self.related_request_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_related_info:
            if self.related_user:
                data['related_username'] = self.related_user.username
                data['related_name'] = self.related_user.name
        
        return data
