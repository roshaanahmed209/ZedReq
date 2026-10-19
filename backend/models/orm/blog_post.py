"""Marketing blog posts — managed from backoffice, read on public site."""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slug = Column(String(220), nullable=False, unique=True, index=True)
    title = Column(String(300), nullable=False)
    excerpt = Column(Text, nullable=False, default="")
    body = Column(Text, nullable=False, default="")
    cover_image_url = Column(String(500), nullable=True)
    author_name = Column(String(120), nullable=False, default="ZedReq Team")
    tags = Column(JSONB, nullable=True)
    status = Column(String(20), nullable=False, default="draft", index=True)
    seo_title = Column(String(300), nullable=True)
    seo_description = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BlogPost(id={self.id}, slug={self.slug!r}, status={self.status!r})>"
