"""User Router - User profile endpoints using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from dependencies.auth import get_current_user
from config.database_orm import get_db
from services.user_service import UserService
from services.profile_service import ProfileService
from services.lms_service import LMSService

router = APIRouter()


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Dependency to get user service with ORM session"""
    return UserService(db)


def get_profile_service(db: Session = Depends(get_db)) -> ProfileService:
    """Dependency to get profile service with ORM session"""
    return ProfileService(db)


def get_lms_service(db: Session = Depends(get_db)) -> LMSService:
    """Dependency to get LMS service with ORM session"""
    from services.lms_service import LMSService
    return LMSService(db)


@router.get("")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get current user's profile - matches /api/user from Flask"""
    # Get full profile with description using ProfileService
    profile = profile_service.get_user_profile(current_user["id"])
    
    if profile:
        return {
            "uid": profile.get("id") or profile.get("uid"),
            "username": profile.get("username"),
            "name": profile.get("name"),
            "email": profile.get("email") or profile.get("user_email"),
            "profile_pic": profile.get("profile_pic"),
            "cover_pic": profile.get("cover_pic"),
            "short_desc": profile.get("short_desc"),
            "about": profile.get("about"),
            "skills": profile.get("skills"),
            "certificates": profile.get("certificates"),
            "current_status": profile.get("current_status"),
            "role": profile.get("role"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "industry": profile.get("industry"),
            "created_at": profile.get("created_at")
        }
    
    # Fallback to basic info from token
    return {
        "uid": current_user["id"],
        "username": current_user["username"],
        "name": current_user["name"],
        "email": current_user["email"],
        "profile_pic": current_user.get("profile_pic"),
        "cover_pic": current_user.get("cover_pic"),
        "short_desc": current_user.get("short_desc"),
        "about": current_user.get("about"),
        "created_at": current_user.get("created_at")
    }


@router.get("/{user_id}")
async def get_user_profile_by_id(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get user profile by ID with description data and connection status"""
    profile = profile_service.get_profile_with_connection_status(
        target_user_id=user_id,
        current_user_id=current_user.get("id")
    )
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return {
        "uid": profile.get("id") or profile.get("uid"),
        "username": profile.get("username"),
        "name": profile.get("name"),
        "email": profile.get("email") or profile.get("user_email"),
        "profile_url": profile.get("profile_url"),
        "profile_pic": profile.get("profile_pic"),
        "cover_pic": profile.get("cover_pic"),
        "short_desc": profile.get("short_desc"),
        "about": profile.get("about"),
        "skills": profile.get("skills"),
        "certificates": profile.get("certificates"),
        "current_status": profile.get("current_status"),
            "role": profile.get("role"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "industry": profile.get("industry"),
        "connection_status": profile.get("connection_status"),
        "created_at": profile.get("created_at")
        }


@router.get("/{user_id}/connections/count")
async def get_user_connection_counts(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get followers and following counts for a user"""
    counts = profile_service.get_connection_counts(user_id)
    return counts


@router.get("/{user_id}/certificates")
async def get_user_certificates(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    lms_service: LMSService = Depends(get_lms_service)
):
    """Get certificates for a specific user"""
    certificates = lms_service.get_user_certificates(user_id)
    return {
        "certificates": certificates,
        "total": len(certificates)
    }


@router.get("/search")
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    current_user: dict = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Search users by username or name"""
    users = user_service.search_users(q, exclude_user_id=current_user["id"], limit=20)
    
    return [
        {
            "uid": u.get("id") or u.get("uid"),
            "username": u.get("username"),
            "name": u.get("name") or u.get("full_name"),
            "email": u.get("email") or u.get("user_email"),
            "created_at": u.get("created_at")
        }
        for u in users
    ]
