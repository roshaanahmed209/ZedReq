"""Post ORM Model"""
from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Index, TypeDecorator, or_
from sqlalchemy.orm import relationship, Mapped, deferred
from sqlalchemy.sql import func

from config.database_orm import Base


# Custom type for pgvector - just passes through as text for ORM purposes
class VectorType(TypeDecorator):
    """Pass-through type for pgvector - actual vector operations use raw SQL"""
    impl = Text
    cache_ok = True


if TYPE_CHECKING:
    from .user import User


class Post(Base):
    """SQLAlchemy ORM model for post table"""
    __tablename__ = 'post'
    
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(
        Integer,
        ForeignKey('users.uid', ondelete='CASCADE'),
        nullable=True,
        index=True
    )
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    media_url = Column(Text)
    media_type = Column(String(20))
    post_desc = Column(Text)
    post_link = Column(Text)  # Post link/reference within ZedRec domain
    is_deleted = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Embedding (pgvector) - deferred to avoid loading in regular queries.
    # Managed via raw SQL, not through SQLAlchemy ORM. VectorType is a text
    # pass-through; actual vector operations use raw SQL (see utils/post_embeddings.py).
    embedding = deferred(Column('embedding', VectorType, nullable=True))

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[uid],
        backref="posts"
    )
    
    # Table indexes
    __table_args__ = (
        Index('idx_post_uid', 'uid'),
        Index('idx_post_created', created_at.desc()),
        Index('idx_post_uid_created_deleted', 'uid', created_at.desc(), 'is_deleted'),
    )
    
    @classmethod
    def not_deleted(cls):
        """SQL filter: row is visible (not soft-deleted). NULL is treated as not deleted."""
        return or_(cls.is_deleted.is_(False), cls.is_deleted.is_(None))
    
    def __repr__(self):
        return f"<Post(post_id={self.post_id}, uid={self.uid}, is_deleted={self.is_deleted})>"
    
    def to_dict(self, include_user_info=False):
        """Convert to dictionary"""
        data = {
            'post_id': self.post_id,
            'id': self.post_id,
            'uid': self.uid,
            'likes': self.likes,
            'comments': self.comments,
            'media_url': self.media_url,
            'media_type': self.media_type,
            'post_desc': self.post_desc,
            'post_link': self.post_link,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_user_info and self.user:
            data['username'] = self.user.username
            data['name'] = self.user.name
        
        return data
