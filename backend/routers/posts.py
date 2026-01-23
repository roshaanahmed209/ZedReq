"""Posts Router - Post CRUD operations using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional

from dependencies.auth import get_current_user
from config.database_orm import get_db
from services.post_service import PostService

router = APIRouter()


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    """Dependency to get post service with ORM session"""
    return PostService(db)


class CreatePostRequest(BaseModel):
    """Create post request body"""
    content: str = Field(..., min_length=1, max_length=5000, alias="post_desc")
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    
    class Config:
        populate_by_name = True


class UpdatePostRequest(BaseModel):
    """Update post request body"""
    content: str = Field(..., min_length=1, max_length=5000, alias="post_desc")
    
    class Config:
        populate_by_name = True


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: CreatePostRequest,
    current_user: dict = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """Create a new post"""
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
    current_user: dict = Depends(get_current_user),
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
            detail=str(e)
        )


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user),
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
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: int,
    current_user: dict = Depends(get_current_user),
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


@router.get("/{post_id}/likes")
async def get_post_likes(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    post_service: PostService = Depends(get_post_service)
):
    """Get users who liked a post"""
    # Check if post exists
    post = post_service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    likers = post_service.get_likers(post_id, limit=50)
    
    return {
        "count": len(likers),
        "users": [
            {
                "uid": u["uid"],
                "username": u["username"],
                "name": u["name"]
            }
            for u in likers
        ]
    }
