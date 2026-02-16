"""User Router - User profile endpoints using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

from dependencies.auth import get_current_user
from dependencies.rate_limit import write_rate_limit, RateLimiter
from config.database_orm import get_db
from services.user_service import UserService
from services.profile_service import ProfileService
from services.lms_service import LMSService
from services.settings_service import SettingsService
from schemas.settings import (
    ProfileUpdate,
    PasswordChange,
    EmailUpdate,
    TwoFactorUpdate,
    SubscriptionUpdate,
    SubscriptionInfo
)
from utils.errors import NotFoundError, ValidationError

# Rate limiter for sensitive operations (password, email, account deletion)
_sensitive_limiter = RateLimiter(requests_per_minute=5)  # Very strict for sensitive operations

def sensitive_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for sensitive operations (password change, email change, account deletion)"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _sensitive_limiter.is_allowed(user_id):
        remaining = _sensitive_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many sensitive operations. Please wait before trying again.",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": "5",
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user

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


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    """Dependency to get settings service with ORM session"""
    return SettingsService(db)


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


# Settings Endpoints

@router.put("/profile")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: dict = Depends(write_rate_limit),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user profile settings"""
    try:
        updated_profile = settings_service.update_profile(
            user_id=current_user["id"],
            profile_pic=profile_data.profile_pic,
            cover_pic=profile_data.cover_pic,
            resume=profile_data.resume,
            interests=profile_data.interests,
            location=profile_data.location
        )
        return updated_profile
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Update profile error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(sensitive_rate_limit),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Change user password"""
    try:
        settings_service.change_password(
            user_id=current_user["id"],
            current_password=password_data.current_password,
            new_password=password_data.new_password
        )
        return {"message": "Password changed successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Change password error: {e}", exc_info=True)
        # Don't leak specific error details for security
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password. Please try again later."
        )


@router.put("/email")
async def update_email(
    email_data: EmailUpdate,
    current_user: dict = Depends(sensitive_rate_limit),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user email"""
    try:
        result = settings_service.update_email(
            user_id=current_user["id"],
            new_email=email_data.email
        )
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Update email error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email"
        )


@router.put("/2fa")
async def toggle_two_factor(
    two_factor_data: TwoFactorUpdate,
    current_user: dict = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Toggle two-factor authentication"""
    try:
        enabled = settings_service.toggle_two_factor(
            user_id=current_user["id"],
            enabled=two_factor_data.enabled
        )
        return {"enabled": enabled, "message": f"Two-factor authentication {'enabled' if enabled else 'disabled'}"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Toggle 2FA error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update 2FA settings"
        )


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription(
    current_user: dict = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get user subscription information"""
    try:
        subscription = settings_service.get_subscription_info(current_user["id"])
        return subscription
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Get subscription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription information"
        )


@router.put("/subscription", response_model=SubscriptionInfo)
async def update_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: dict = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user subscription plan"""
    try:
        subscription = settings_service.update_subscription(
            user_id=current_user["id"],
            plan=subscription_data.plan
        )
        return subscription
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Update subscription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )


@router.delete("/account")
async def delete_account(
    current_user: dict = Depends(sensitive_rate_limit),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Delete user account"""
    try:
        settings_service.delete_account(current_user["id"])
        return {"message": "Account deleted successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Delete account error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
