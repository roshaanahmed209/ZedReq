"""Public read-only blog posts for the marketing site."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from config.database_orm import get_db
from schemas.blog_post import BlogPostListResponse, BlogPostPublic
from services.blog_post_service import get_published_post_by_slug, list_published_posts

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/blog-posts", response_model=BlogPostListResponse)
def read_blog_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """List published blog posts (no authentication)."""
    return list_published_posts(db, page=page, limit=limit)


@router.get("/blog-posts/{slug}", response_model=BlogPostPublic)
def read_blog_post(slug: str, db: Session = Depends(get_db)):
    """Get one published blog post by slug (no authentication)."""
    post = get_published_post_by_slug(db, slug)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found")
    return post
