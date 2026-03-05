"""Connection ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User


class Connection(Base):
    """SQLAlchemy ORM model for connections table"""
    __tablename__ = 'connections'
    
    connection_id = Column(Integer, primary_key=True, autoincrement=True)
    follower_uid = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    followed_uid = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    connected_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    follower: Mapped["User"] = relationship(
        "User",
        foreign_keys=[follower_uid],
        backref="following"
    )
    followed: Mapped["User"] = relationship(
        "User",
        foreign_keys=[followed_uid],
        backref="followers"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('follower_uid', 'followed_uid', name='uq_connection'),
        Index('idx_connections_follower', 'follower_uid'),
        Index('idx_connections_followed', 'followed_uid'),
    )
    
    def __repr__(self):
        return f"<Connection(id={self.connection_id}, follower={self.follower_uid}, followed={self.followed_uid})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'connection_id': self.connection_id,
            'id': self.connection_id,
            'follower_uid': self.follower_uid,
            'followed_uid': self.followed_uid,
            'connected_at': self.connected_at.isoformat() if self.connected_at else None,
        }
