"""Connection Request ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class ConnectionRequest(Base):
    """SQLAlchemy ORM model for connection_requests table"""
    __tablename__ = 'connection_requests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    receiver_id = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    status = Column(String(20), default='pending', index=True)
    message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sender: Mapped["User"] = relationship(
        "User",
        foreign_keys=[sender_id],
        backref="sent_connection_requests"
    )
    receiver: Mapped["User"] = relationship(
        "User",
        foreign_keys=[receiver_id],
        backref="received_connection_requests"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('sender_id', 'receiver_id', name='uq_connection_request'),
        Index('idx_conn_req_sender', 'sender_id'),
        Index('idx_conn_req_receiver', 'receiver_id'),
        Index('idx_conn_req_status', 'status'),
    )
    
    def __repr__(self):
        return f"<ConnectionRequest(id={self.id}, sender={self.sender_id}, receiver={self.receiver_id}, status='{self.status}')>"
    
    def to_dict(self, include_user_info=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'status': self.status,
            'message': self.message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info:
            if self.sender:
                data['sender_username'] = self.sender.username
                data['sender_name'] = self.sender.name
            if self.receiver:
                data['receiver_username'] = self.receiver.username
                data['receiver_name'] = self.receiver.name
        
        return data
