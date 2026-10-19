from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BlogPostListItem(BaseModel):
    slug: str
    title: str
    excerpt: str
    cover_image_url: Optional[str] = None
    author_name: str
    tags: List[str] = Field(default_factory=list)
    published_at: Optional[datetime] = None


class BlogPostPublic(BlogPostListItem):
    body: str
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None


class BlogPostListResponse(BaseModel):
    items: List[BlogPostListItem]
    total: int
    page: int
    limit: int
    pages: int
