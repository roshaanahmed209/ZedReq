"""Public blog post reads — published posts only."""
from __future__ import annotations

import math
from typing import List, Optional

from sqlalchemy.orm import Session

from models.orm.blog_post import BlogPost
from schemas.blog_post import BlogPostListItem, BlogPostListResponse, BlogPostPublic


def _normalize_tags(raw) -> List[str]:
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(t).strip() for t in raw if str(t).strip()]
    return []


def _to_list_item(row: BlogPost) -> BlogPostListItem:
    return BlogPostListItem(
        slug=row.slug,
        title=row.title,
        excerpt=row.excerpt or "",
        cover_image_url=row.cover_image_url,
        author_name=row.author_name or "ZedReq Team",
        tags=_normalize_tags(row.tags),
        published_at=row.published_at,
    )


def _to_public(row: BlogPost) -> BlogPostPublic:
    base = _to_list_item(row)
    return BlogPostPublic(
        **base.model_dump(),
        body=row.body or "",
        seo_title=row.seo_title,
        seo_description=row.seo_description,
    )


def list_published_posts(db: Session, page: int = 1, limit: int = 20) -> BlogPostListResponse:
    page = max(1, page)
    limit = max(1, min(limit, 50))
    offset = (page - 1) * limit

    q = db.query(BlogPost).filter(BlogPost.status == "published")
    total = q.count()
    rows = (
        q.order_by(BlogPost.published_at.desc().nullslast(), BlogPost.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    pages = math.ceil(total / limit) if total else 0
    return BlogPostListResponse(
        items=[_to_list_item(r) for r in rows],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


def get_published_post_by_slug(db: Session, slug: str) -> Optional[BlogPostPublic]:
    slug_norm = (slug or "").strip().lower()
    if not slug_norm:
        return None
    row = (
        db.query(BlogPost)
        .filter(BlogPost.slug == slug_norm, BlogPost.status == "published")
        .first()
    )
    if not row:
        return None
    return _to_public(row)
