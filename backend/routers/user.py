"""User Router - User profile endpoints using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

from dependencies.auth import get_current_user
from dependencies.rate_limit import write_rate_limit, RateLimiter
from config.database_orm import get_db
from services.user_service import UserService
from services.profile_service import ProfileService
from services.context_updater import ContextUpdater
from services.lms_service import LMSService
from services.settings_service import SettingsService
from services.two_factor_service import TwoFactorService
from schemas.settings import (
    ProfileUpdate,
    PasswordChange,
    EmailUpdate,
    SubscriptionUpdate,
    SubscriptionInfo
)
from schemas.two_factor import (
    TwoFactorSetupResponse,
    TwoFactorVerifySetup,
    TwoFactorBackupCodesResponse,
    TwoFactorStatusResponse
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


def get_two_factor_service(db: Session = Depends(get_db)) -> TwoFactorService:
    """Dependency to get 2FA service with ORM session"""
    return TwoFactorService(db)


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
            "two_factor_enabled": profile.get("two_factor_enabled", False),
            "interests": profile.get("interests"),  # Include interests from runtime_context
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
    profile_service: ProfileService = Depends(get_profile_service),
    db: Session = Depends(get_db)
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
    
    # Update context for Zed Agent (only when viewing someone else's profile)
    if current_user.get("id") != user_id:
        try:
            context_updater = ContextUpdater(db)
            context_updater.update_context_from_action(
                user_id=current_user["id"],
                action="view",
                entity_type="profile",
                entity_id=user_id
            )
        except Exception as e:
            # Don't fail the profile request if context update fails
            logger.warning(f"Failed to update context for profile view: {e}")
    
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


@router.put("/profile/description")
async def update_profile_description(
    description_data: Dict[str, Any],
    current_user: dict = Depends(write_rate_limit),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update user profile description fields (short_desc, about, skills, etc.)"""
    try:
        updated_profile = profile_service.update_profile(
            user_id=current_user["id"],
            update_data=description_data
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
        logger.error(f"Update profile description error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile description"
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


def _get_2fa_status_logic(
    current_user: dict,
    two_factor_service: TwoFactorService
) -> Dict[str, Any]:
    """Shared logic for getting 2FA status"""
    from models.orm import User
    user = (
        two_factor_service.db.query(User)
        .filter(User.uid == current_user["id"])
        .first()
    )
    if not user:
        raise NotFoundError('User')
    
    return {
        "enabled": user.two_factor_enabled or False,
        "verified": user.two_factor_verified or False,
        "has_backup_codes": bool(user.two_factor_backup_codes)
    }


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def get_2fa_status(
    current_user: dict = Depends(get_current_user),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service)
):
    """Get 2FA status for current user"""
    try:
        return _get_2fa_status_logic(current_user, two_factor_service)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Get 2FA status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get 2FA status"
        )


@router.get("/2fa", response_model=TwoFactorStatusResponse)
async def get_2fa_status_short(
    current_user: dict = Depends(get_current_user),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service)
):
    """Get 2FA status for current user (alias for /2fa/status)"""
    try:
        return _get_2fa_status_logic(current_user, two_factor_service)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Get 2FA status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get 2FA status"
        )


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    current_user: dict = Depends(sensitive_rate_limit),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service)
):
    """Generate 2FA secret and QR code for setup"""
    try:
        result = two_factor_service.generate_secret(current_user["id"])
        return result
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"2FA setup error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup 2FA"
        )


@router.post("/2fa/verify-setup")
async def verify_2fa_setup(
    verify_data: TwoFactorVerifySetup,
    current_user: dict = Depends(sensitive_rate_limit),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service)
):
    """Verify 2FA setup code and complete setup"""
    try:
        is_valid = two_factor_service.verify_setup_code(
            current_user["id"],
            verify_data.code
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid 2FA code. Please try again."
            )
        
        # Get backup codes
        backup_codes = two_factor_service.get_backup_codes(current_user["id"])
        
        return {
            "message": "2FA enabled successfully",
            "backup_codes": backup_codes
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"2FA verify setup error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify 2FA setup"
        )


@router.get("/2fa/backup-codes", response_model=TwoFactorBackupCodesResponse)
async def get_backup_codes(
    current_user: dict = Depends(get_current_user),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service)
):
    """Get backup codes for current user"""
    try:
        codes = two_factor_service.get_backup_codes(current_user["id"])
        return {
            "backup_codes": codes,
            "message": "Store these codes in a safe place. Each code can only be used once."
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Get backup codes error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get backup codes"
        )


@router.post("/2fa/regenerate-backup-codes", response_model=TwoFactorBackupCodesResponse)
async def regenerate_backup_codes(
    current_user: dict = Depends(sensitive_rate_limit),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service)
):
    """Regenerate backup codes for current user"""
    try:
        codes = two_factor_service.regenerate_backup_codes(current_user["id"])
        return {
            "backup_codes": codes,
            "message": "New backup codes generated. Store these in a safe place. Old codes are no longer valid."
        }
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Regenerate backup codes error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes"
        )


@router.delete("/2fa")
async def disable_2fa(
    current_user: dict = Depends(sensitive_rate_limit),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service)
):
    """Disable 2FA for current user"""
    try:
        two_factor_service.disable_2fa(current_user["id"])
        return {"message": "2FA disabled successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        logger.error(f"Disable 2FA error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable 2FA"
        )


@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription(
    current_user: dict = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get user subscription information"""
    try:
        subscription = settings_service.get_subscription_info(current_user["id"])
        # Ensure all required fields are present and valid strings
        subscription['plan'] = str(subscription.get('plan', 'free')).strip() or 'free'
        subscription['status'] = str(subscription.get('status', 'inactive')).strip() or 'inactive'
        # Ensure optional fields are None if not present
        subscription['subscription_start'] = subscription.get('subscription_start') or None
        subscription['subscription_end'] = subscription.get('subscription_end') or None
        
        # Validate and return
        return SubscriptionInfo(**subscription)
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
