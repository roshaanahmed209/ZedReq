"""Like ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .user import User
    from .post import Post


class Like(Base):
    """SQLAlchemy ORM model for likes table"""
    __tablename__ = 'likes'
    
    like_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(
        Integer,
        ForeignKey('post.post_id', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    uid = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    post: Mapped["Post"] = relationship(
        "Post",
        foreign_keys=[post_id],
        backref="likes_list"
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[uid],
        backref="likes"
    )
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('post_id', 'uid', name='uq_like_post_user'),
        Index('idx_likes_post', 'post_id'),
        Index('idx_likes_user', 'uid'),
    )
    
    def __repr__(self):
        return f"<Like(like_id={self.like_id}, post_id={self.post_id}, uid={self.uid})>"
    
    def to_dict(self, include_user_info=False):
        """Convert to dictionary"""
        data = {
            'like_id': self.like_id,
            'id': self.like_id,
            'post_id': self.post_id,
            'uid': self.uid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        
        if include_user_info and self.user:
            data['username'] = self.user.username
            data['name'] = self.user.name
        
        return data
