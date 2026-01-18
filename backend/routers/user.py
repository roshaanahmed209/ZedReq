"""User Router - User profile endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from dependencies.auth import get_current_user
from config.database import get_database
from models.user import User

router = APIRouter()


@router.get("")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user)
):
    """Get current user's profile - matches /api/user from Flask"""
    db = get_database()
    user_model = User(db)
    
    # Get full profile with description
    profile = user_model.get_user_profile(current_user["id"])
    
    if profile:
        return {
            "uid": profile["id"],
            "username": profile["username"],
            "name": profile["name"],
            "email": profile["email"],
            "profile_pic": profile.get("profile_pic"),
            "short_desc": profile.get("short_desc"),
            "about": profile.get("about"),
            "skills": profile.get("skills"),
            "current_status": profile.get("current_status"),
            "created_at": profile.get("created_at")
        }
    
    # Fallback to basic info from token
    return {
        "uid": current_user["id"],
        "username": current_user["username"],
        "name": current_user["name"],
        "email": current_user["email"],
        "profile_pic": current_user.get("profile_pic"),
        "short_desc": current_user.get("short_desc"),
        "about": current_user.get("about"),
        "created_at": current_user.get("created_at")
    }


@router.get("/search")
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: dict = Depends(get_current_user)
):
    """Search users by username or name"""
    db = get_database()
    user_model = User(db)
    
    users = user_model.search_users(q, limit=20)
    
    return [
        {
            "uid": u["id"],
            "username": u["username"],
            "name": u["name"],
            "email": u.get("email"),
            "profile_pic": u.get("profile_pic"),
            "created_at": u.get("created_at")
        }
        for u in users
    ]
