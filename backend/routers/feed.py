"""Feed Router - Feed and post listing endpoints using ORM"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.auth import get_current_user
from config.database_orm import get_db
from services.feed_service import FeedService

router = APIRouter()


def get_feed_service(db: Session = Depends(get_db)) -> FeedService:
    """Dependency to get feed service with ORM session"""
    return FeedService(db)


@router.get("")
async def get_feed(
    limit: int = Query(default=20, ge=1, le=50, description="Number of posts"),
    cursor: Optional[str] = Query(default=None, description="Pagination cursor"),
    current_user: dict = Depends(get_current_user),
    feed_service: FeedService = Depends(get_feed_service)
):
    """
    Get personalized feed for current user.
    Shows posts from followed users and own posts.
    """
    try:
        user_id = current_user["id"]
        
        # Get feed using FeedService
        feed_data = feed_service.get_user_feed(
            user_id=user_id,
            cursor=cursor,
            limit=limit
        )
        
        return feed_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch feed: {str(e)}"
        )
