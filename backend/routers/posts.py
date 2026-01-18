"""Posts Router - Post CRUD operations"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from dependencies.auth import get_current_user
from config.database import get_database
from models.post import Post
from models.like import Like

router = APIRouter()


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
    current_user: dict = Depends(get_current_user)
):
    """Create a new post"""
    db = get_database()
    post_model = Post(db)
    
    post = post_model.create(
        uid=current_user["id"],
        post_desc=post_data.content,
        media_url=post_data.media_url,
        media_type=post_data.media_type
    )
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )
    
    return {
        "id": post["post_id"],
        "user_id": post["uid"],
        "content": post["post_desc"],
        "media_url": post.get("media_url"),
        "media_type": post.get("media_type"),
        "likes": post.get("likes", 0),
        "comments": post.get("comments", 0),
        "created_at": str(post["created_at"]),
        "message": "Post created successfully"
    }


@router.get("/{post_id}")
async def get_post(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific post by ID"""
    db = get_database()
    post_model = Post(db)
    like_model = Like(db)
    
    post = post_model.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    is_liked = like_model.has_liked(post_id, current_user["id"])
    
    created_at = post['created_at']
    if hasattr(created_at, 'isoformat'):
        created_str = created_at.isoformat()
    else:
        created_str = str(created_at)
    
    return {
        "id": post["post_id"],
        "user_id": post["uid"],
        "content": post["post_desc"],
        "media_url": post.get("media_url"),
        "media_type": post.get("media_type"),
        "created_at": created_str,
        "username": post.get("username", ""),
        "full_name": post.get("name", ""),
        "profile_pic": post.get("profile_pic"),
        "like_count": post.get("likes", 0),
        "comment_count": post.get("comments", 0),
        "is_liked": is_liked
    }


@router.put("/{post_id}")
async def update_post(
    post_id: int,
    post_data: UpdatePostRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a post (only by owner)"""
    db = get_database()
    post_model = Post(db)
    
    post = post_model.update(
        post_id=post_id,
        uid=current_user["id"],
        post_desc=post_data.content
    )
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to update it"
        )
    
    return {
        "id": post["post_id"],
        "content": post["post_desc"],
        "updated_at": str(post.get("updated_at")),
        "message": "Post updated successfully"
    }


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a post (soft delete, only by owner)"""
    db = get_database()
    post_model = Post(db)
    
    result = post_model.soft_delete(post_id, current_user["id"])
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    
    return {"message": "Post deleted successfully"}


@router.post("/{post_id}/like")
async def toggle_like(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Toggle like on a post"""
    db = get_database()
    post_model = Post(db)
    like_model = Like(db)
    
    # Check if post exists
    post = post_model.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Toggle like
    is_liked = like_model.toggle(post_id, current_user["id"])
    
    # Update like count on post
    if is_liked:
        post_model.increment_likes(post_id)
    else:
        post_model.decrement_likes(post_id)
    
    # Get updated like count
    like_count = like_model.get_count(post_id)
    
    return {
        "is_liked": is_liked,
        "like_count": like_count,
        "message": "Post liked" if is_liked else "Post unliked"
    }


@router.get("/{post_id}/likes")
async def get_post_likes(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get users who liked a post"""
    db = get_database()
    post_model = Post(db)
    like_model = Like(db)
    
    # Check if post exists
    post = post_model.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    likers = like_model.get_likers(post_id, limit=50)
    
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
