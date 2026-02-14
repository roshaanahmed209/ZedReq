"""Posts Router - Post CRUD operations using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import Optional
import logging

from dependencies.auth import get_current_user
from dependencies.rate_limit import profile_rate_limit, write_rate_limit
from config.database_orm import get_db
from services.post_service import PostService
from utils.errors import NotFoundError, AuthorizationError
from utils.api_security import sanitize_text_for_storage, validate_url_safe
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    """Dependency to get post service with ORM session"""
    return PostService(db)


class CreatePostRequest(BaseModel):
    """Create post request body"""
    content: str = Field(..., min_length=1, max_length=5000, alias="post_desc")
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    
    @validator('content')
    def sanitize_content(cls, v):
        """Sanitize post content to prevent XSS"""
        return sanitize_text_for_storage(str(v), max_length=5000)
    
    @validator('media_url')
    def validate_media_url(cls, v):
        """Validate media URL if provided"""
        if v is None or v == "":
            return v
        try:
            return validate_url_safe(v)
        except ValueError as e:
            raise ValueError(f"Invalid media URL: {str(e)}")
    
    @validator('media_type')
    def validate_media_type(cls, v):
        """Validate media type if provided"""
        if v is None:
            return v
        allowed_types = ['image', 'video', 'audio', 'document']
        if v.lower() not in allowed_types:
            raise ValueError(f"media_type must be one of: {', '.join(allowed_types)}")
        return v.lower()
    
    class Config:
        populate_by_name = True


class UpdatePostRequest(BaseModel):
    """Update post request body"""
    content: str = Field(..., min_length=1, max_length=5000, alias="post_desc")
    
    @validator('content')
    def sanitize_content(cls, v):
        """Sanitize post content to prevent XSS"""
        return sanitize_text_for_storage(str(v), max_length=5000)
    
    class Config:
        populate_by_name = True


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: CreatePostRequest,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    post_service: PostService = Depends(get_post_service)
):
    """Create a new post"""
    try:
        post = post_service.create_post(
            user_id=current_user["id"],
            content=post_data.content,
            media_url=post_data.media_url,
            media_type=post_data.media_type
        )
        
        return {
            "id": post["id"],
            "user_id": post["user_id"],
            "content": post["content"],
            "media_url": post.get("media_url"),
            "media_type": post.get("media_type"),
            "likes": post.get("likes", 0),
            "comments": post.get("comments", 0),
            "created_at": post.get("created_at"),
            "message": "Post created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )


@router.get("/user/{user_id}")
async def get_user_posts(
    user_id: int,
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    post_service: PostService = Depends(get_post_service)
):
    """Get all posts by a specific user with pagination"""
    try:
        posts, total = post_service.get_posts_by_user_paginated(
            target_user_id=user_id,
            current_user_id=current_user["id"],
            limit=limit,
            offset=offset
        )
        
        return {
            "posts": posts,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting user posts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user posts"
        )


@router.get("/user/{user_id}/featured")
async def get_user_featured_posts(
    user_id: int,
    limit: int = Query(10, ge=1, le=20),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    post_service: PostService = Depends(get_post_service)
):
    """Get featured posts (posts with media) by a specific user with pagination"""
    try:
        posts, total = post_service.get_featured_posts_by_user_paginated(
            target_user_id=user_id,
            current_user_id=current_user["id"],
            limit=limit,
            offset=offset
        )
        
        return {
            "posts": posts,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting featured posts: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch featured posts"
        )


@router.get("/{post_id}")
async def get_post(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """Get a specific post by ID"""
    post = post_service.get_post(post_id, current_user["id"])
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return {
        "id": post["id"],
        "user_id": post["user_id"],
        "content": post["content"],
        "media_url": post.get("media_url"),
        "media_type": post.get("media_type"),
        "created_at": post.get("created_at"),
        "username": post.get("username", ""),
        "full_name": post.get("name", ""),
        "profile_pic": post.get("profile_pic"),
        "like_count": post.get("likes", 0),
        "comment_count": post.get("comments", 0),
        "is_liked": post.get("is_liked", False)
    }


@router.put("/{post_id}")
async def update_post(
    post_id: int,
    post_data: UpdatePostRequest,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    post_service: PostService = Depends(get_post_service)
):
    """Update a post (only by owner)"""
    try:
        post = post_service.update_post(
            post_id=post_id,
            user_id=current_user["id"],
            content=post_data.content
        )
        
        return {
            "id": post["id"],
            "content": post["content"],
            "updated_at": post.get("updated_at"),
            "message": "Post updated successfully"
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this post"
        )
    except Exception as e:
        logger.error(f"Error updating post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post"
        )


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    post_service: PostService = Depends(get_post_service)
):
    """Delete a post (soft delete, only by owner)"""
    try:
        post_service.delete_post(post_id, current_user["id"])
        return {"message": "Post deleted successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    except AuthorizationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post"
        )
    except Exception as e:
        logger.error(f"Error deleting post: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete post"
        )


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: int,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    post_service: PostService = Depends(get_post_service)
):
    """Toggle like on a post"""
    try:
        result = post_service.toggle_like(post_id, current_user["id"])
        return {
            "is_liked": result["is_liked"],
            "like_count": result["like_count"],
            "message": "Post liked" if result["is_liked"] else "Post unliked"
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    except Exception as e:
        logger.error(f"Error toggling like: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle like"
        )


@router.get("/{post_id}/likes")
async def get_post_likes(
    post_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    post_service: PostService = Depends(get_post_service)
):
    """Get users who liked a post with pagination"""
    try:
        # Check if post exists
        post = post_service.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        likers = post_service.get_likers(post_id, limit=limit, offset=offset)
        
        return {
            "count": len(likers),
            "users": [
                {
                    "uid": u["uid"],
                    "username": u["username"],
                    "name": u["name"]
                }
                for u in likers
            ],
            "limit": limit,
            "offset": offset
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting post likes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch post likes"
        )
