"""Post comment ORM model"""
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Text
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from config.database_orm import Base

if TYPE_CHECKING:
    from .post import Post
    from .user import User


class PostComment(Base):
    """SQLAlchemy ORM model for post_comment table"""

    __tablename__ = "post_comment"

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(
        Integer,
        ForeignKey("post.post_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uid = Column(
        Integer,
        ForeignKey("users.uid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    body = Column(Text, nullable=False, default="")
    media_url = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    post: Mapped["Post"] = relationship(
        "Post",
        foreign_keys=[post_id],
        backref="comment_rows",
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[uid],
        backref="post_comments",
    )

    __table_args__ = (
        Index("idx_post_comment_post", "post_id"),
        Index("idx_post_comment_post_created", "post_id", created_at.desc()),
    )

    def __repr__(self):
        return f"<PostComment(comment_id={self.comment_id}, post_id={self.post_id}, uid={self.uid})>"
