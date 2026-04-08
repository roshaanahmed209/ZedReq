"""User Router - User profile endpoints using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import inspect

logger = logging.getLogger(__name__)

from dependencies.auth import get_current_user
from dependencies.rate_limit import write_rate_limit, RateLimiter
from dependencies.subscription import get_quota_info
from config.database_orm import get_db
from services.user_service import UserService
from services.profile_service import ProfileService
from tasks.profile_context_tasks import run_profile_view_context_update
from services.lms_service import LMSService
from services.settings_service import SettingsService
from services.messaging_service import MessagingService
from services.subscription_billing_service import SubscriptionBillingService
from services.two_factor_service import TwoFactorService
from services.search_service import SearchService
from schemas.settings import (
    ProfileUpdate,
    PasswordChange,
    EmailUpdate,
    SubscriptionUpdate,
    SubscriptionInfo,
    SubscriptionCancelRequest,
    SubscriptionChangePlanRequest,
    EnterpriseInquiryRequest,
    DeleteAccountRequest,
    ProfileDescriptionUpdate,
)
from schemas.two_factor import (
    TwoFactorSetupResponse,
    TwoFactorVerifySetup,
    TwoFactorBackupCodesResponse,
    TwoFactorStatusResponse
)
from utils.errors import NotFoundError, ValidationError
from models.orm.enterprise_inquiry import EnterpriseInquiry

# Rate limiter for sensitive operations (password, email, account deletion)
_sensitive_limiter = RateLimiter(requests_per_minute=5)  # Very strict for sensitive operations

_enterprise_inquiry_limiter = RateLimiter(requests_per_minute=10)


def enterprise_inquiry_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit enterprise inquiry submissions per user."""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    if not _enterprise_inquiry_limiter.is_allowed(user_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many inquiries. Please try again later.",
        )
    return current_user


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


def get_subscription_billing_service(db: Session = Depends(get_db)) -> SubscriptionBillingService:
    return SubscriptionBillingService(db)


def get_two_factor_service(db: Session = Depends(get_db)) -> TwoFactorService:
    """Dependency to get 2FA service with ORM session"""
    return TwoFactorService(db)


def get_search_service(db: Session = Depends(get_db)) -> SearchService:
    """Dependency to get search service with ORM session"""
    return SearchService(db)


@router.get("")
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Get current user's profile - matches /api/user from Flask"""
    # Get full profile with description using ProfileService
    profile = profile_service.get_user_profile(current_user["id"])
    
    if profile:
        uid = profile.get("id") or profile.get("uid")
        return {
            "id": uid,
            "uid": uid,
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


@router.get("/search")
async def search_all(
    q: str = Query(..., min_length=1, description="Search query"),
    search_type: Optional[str] = Query(None, alias="type", description="Filter by type: users, jobs, posts, or all"),
    limit: int = Query(10, ge=1, le=50, description="Results per type"),
    current_user: dict = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """
    LinkedIn-style comprehensive search across users, jobs, and posts
    
    Returns results from all types by default, or filter by type parameter.
    """
    # Determine search types
    if search_type and search_type.lower() in ['users', 'jobs', 'posts']:
        search_types = [search_type.lower()]
    else:
        search_types = ['users', 'jobs', 'posts']
    
    # Perform search
    results = search_service.search_all(
        query=q,
        current_user_id=current_user["id"],
        limit_per_type=limit,
        search_types=search_types
    )
    
    # Format response
    response = {
        "query": results["query"],
        "total_results": results["total_results"],
        "users": [],
        "jobs": [],
        "posts": []
    }
    
    # Format users
    for u in results.get("users", []):
        response["users"].append({
            "uid": u.get("id") or u.get("uid"),
            "username": u.get("username"),
            "name": u.get("name") or u.get("full_name"),
            "email": u.get("email") or u.get("user_email"),
            "created_at": u.get("created_at")
        })
    
    # Format jobs
    for j in results.get("jobs", []):
        response["jobs"].append({
            "job_id": j.get("job_id"),
            "title": j.get("title"),
            "company_name": j.get("company_name"),
            "location": j.get("location"),
            "job_type": j.get("job_type"),
            "is_remote": j.get("is_remote"),
            "description": j.get("description"),
            "skills_required": j.get("skills_required"),
            "created_at": j.get("created_at")
        })
    
    # Format posts
    for p in results.get("posts", []):
        response["posts"].append({
            "id": p.get("id") or p.get("post_id"),
            "post_id": p.get("post_id"),
            "user_id": p.get("user_id") or p.get("uid"),
            "content": p.get("content") or p.get("post_desc"),
            "username": p.get("username"),
            "full_name": p.get("full_name") or p.get("name"),
            "profile_pic": p.get("profile_pic"),
            "like_count": p.get("like_count") or p.get("likes", 0),
            "comment_count": p.get("comment_count") or p.get("comments", 0),
            "is_liked": p.get("is_liked", False),
            "created_at": p.get("created_at")
        })
    
    return response


def _normalize_subscription_response(subscription: Dict[str, Any]) -> SubscriptionInfo:
    """Coerce DB/datetime values into SubscriptionInfo fields."""

    def _dt_str(v):
        if v is None:
            return None
        if hasattr(v, "isoformat"):
            return v.isoformat()
        s = str(v).strip()
        return s if s else None

    return SubscriptionInfo(
        plan=str(subscription.get("plan") or "free").strip() or "free",
        status=str(subscription.get("status") or "inactive").strip() or "inactive",
        subscription_start=_dt_str(subscription.get("subscription_start")),
        subscription_end=_dt_str(subscription.get("subscription_end")),
        requires_plan_selection=bool(subscription.get("requires_plan_selection", True)),
        paddle_subscription_id=subscription.get("paddle_subscription_id"),
    )


# Literal paths must be registered before /{user_id} or "subscription" is parsed as user_id (422).
@router.get("/subscription", response_model=SubscriptionInfo)
async def get_subscription(
    current_user: dict = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Get user subscription information"""
    try:
        subscription = settings_service.get_subscription_info_with_flags(current_user["id"])
        return _normalize_subscription_response(subscription)
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


@router.get("/subscription/usage")
async def get_subscription_usage(
    usage_summary: dict = Depends(get_quota_info)
):
    """
    Get current subscription plan and remaining quotas for all features.

    Returns:
        Plan info (name, status, limits) and per-feature usage
        (used/limit/remaining for ai_messages, course_enrollments, interview_sessions).

    Security: Authenticated via get_current_user (inside get_quota_info dependency).
    Plan is always fetched fresh from DB, not from JWT or cache.
    """
    return usage_summary


@router.put("/subscription", response_model=SubscriptionInfo)
async def update_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: dict = Depends(get_current_user),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """Update user subscription plan (free only; paid tiers use Paddle checkout or change-plan)."""
    try:
        subscription = settings_service.update_subscription(
            user_id=current_user["id"],
            plan=subscription_data.plan,
            billing_email=subscription_data.billing_email,
        )
        return _normalize_subscription_response(subscription)
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


@router.post("/subscription/cancel")
async def cancel_paddle_subscription(
    body: SubscriptionCancelRequest,
    current_user: dict = Depends(write_rate_limit),
    billing: SubscriptionBillingService = Depends(get_subscription_billing_service),
):
    """Request cancellation of the user's Paddle subscription (renewals stop per effective_from)."""
    try:
        return billing.cancel_paddle_subscription(
            current_user["id"],
            effective_from=body.effective_from,
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.error(f"Cancel subscription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription",
        )


@router.post("/subscription/change-plan")
async def change_paddle_subscription_plan(
    body: SubscriptionChangePlanRequest,
    current_user: dict = Depends(write_rate_limit),
    billing: SubscriptionBillingService = Depends(get_subscription_billing_service),
):
    """Change an existing Paddle subscription between pro and premium."""
    try:
        return billing.change_paddle_plan(
            current_user["id"],
            target_plan=body.plan,
            proration_billing_mode=body.proration_billing_mode,
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.error(f"Change plan error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change subscription plan",
        )


@router.get("/{user_id}")
async def get_user_profile_by_id(
    user_id: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
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
    
    # Zed context + LLM summarization run after response (BackgroundTasks)
    viewer_id = current_user.get("id")
    if viewer_id and viewer_id != user_id:
        background_tasks.add_task(run_profile_view_context_update, viewer_id, user_id)
    
    response = {
        "uid": profile.get("id") or profile.get("uid"),
        "username": profile.get("username"),
        "name": profile.get("name"),
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
        "created_at": profile.get("created_at"),
    }
    # Only include email when viewing own profile (PII protection)
    if current_user.get("id") == user_id:
        response["email"] = profile.get("email") or profile.get("user_email")
    return response


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


# Settings Endpoints

@router.put("/profile")
async def update_profile(
    request: Request,
    current_user: dict = Depends(write_rate_limit),
    settings_service: SettingsService = Depends(get_settings_service)
):
    """
    Update user profile settings.
    Supports both JSON (application/json) and multipart/form-data (file uploads).
    """
    try:
        content_type = request.headers.get("content-type", "")
        
        # Handle multipart/form-data (file uploads)
        if "multipart/form-data" in content_type:
            form = await request.form()
            
            resume_url = None
            profile_pic_url = None
            cover_pic_url = None
            
            # Upload resume file if provided
            resume_file = form.get("resume")
            if resume_file and hasattr(resume_file, 'filename') and resume_file.filename:
                # Files from request.form() are already UploadFile objects, use directly
                # But we need to ensure it's properly handled
                if isinstance(resume_file, UploadFile):
                    resume_upload = resume_file
                else:
                    # Create a wrapper for non-UploadFile objects (shouldn't happen, but just in case)
                    class FormFileWrapper:
                        def __init__(self, form_file):
                            self.filename = form_file.filename
                            self._file = form_file
                            self.content_type = getattr(form_file, 'content_type', 'application/octet-stream')
                            self._content = None
                        
                        async def read(self):
                            if self._content is None:
                                if hasattr(self._file, 'read'):
                                    read_result = self._file.read()
                                    # If it's a coroutine, await it
                                    if inspect.iscoroutine(read_result):
                                        self._content = await read_result
                                    else:
                                        self._content = read_result
                                    
                                    # Ensure content is bytes
                                    if isinstance(self._content, str):
                                        self._content = self._content.encode()
                                    elif not isinstance(self._content, bytes):
                                        self._content = b''
                                else:
                                    self._content = b''
                            return self._content
                        
                        async def seek(self, position):
                            if hasattr(self._file, 'seek'):
                                seek_result = self._file.seek(position)
                                if inspect.iscoroutine(seek_result):
                                    await seek_result
                            self._content = None  # Reset cache
                        
                        @property
                        def file(self):
                            return self._file
                    
                    resume_upload = FormFileWrapper(resume_file)
                
                resume_url = await settings_service.upload_resume_file(
                    resume_file=resume_upload,
                    user_id=current_user["id"]
                )
            
            # Upload profile picture if provided (keep existing Cloudinary upload from frontend for now)
            profile_pic_file = form.get("profile_pic")
            if profile_pic_file and hasattr(profile_pic_file, 'filename') and profile_pic_file.filename:
                # Files from request.form() are already UploadFile objects, use directly
                if isinstance(profile_pic_file, UploadFile):
                    profile_pic_upload = profile_pic_file
                else:
                    # Fallback: create UploadFile from form file
                    profile_pic_upload = UploadFile(
                        filename=profile_pic_file.filename,
                        file=profile_pic_file.file if hasattr(profile_pic_file, 'file') else None
                    )
                profile_pic_url = await settings_service.upload_image_file(
                    image_file=profile_pic_upload,
                    file_type='profile_pic'
                )
            
            # Upload cover picture if provided (keep existing Cloudinary upload from frontend for now)
            cover_pic_file = form.get("cover_pic")
            if cover_pic_file and hasattr(cover_pic_file, 'filename') and cover_pic_file.filename:
                # Files from request.form() are already UploadFile objects, use directly
                if isinstance(cover_pic_file, UploadFile):
                    cover_pic_upload = cover_pic_file
                else:
                    # Fallback: create UploadFile from form file
                    cover_pic_upload = UploadFile(
                        filename=cover_pic_file.filename,
                        file=cover_pic_file.file if hasattr(cover_pic_file, 'file') else None
                    )
                cover_pic_url = await settings_service.upload_image_file(
                    image_file=cover_pic_upload,
                    file_type='cover_pic'
                )
            
            # Get other form fields (can be strings or files)
            name = form.get("name")
            interests = form.get("interests")
            location = form.get("location")
            
            # Handle profile_pic and cover_pic - they might be URLs (strings) from frontend Cloudinary upload
            profile_pic_value = form.get("profile_pic")
            cover_pic_value = form.get("cover_pic")
            
            # If they're strings (URLs), use them directly; if they're files, use uploaded URL
            final_profile_pic = profile_pic_url or (profile_pic_value if isinstance(profile_pic_value, str) else None)
            final_cover_pic = cover_pic_url or (cover_pic_value if isinstance(cover_pic_value, str) else None)
            
            updated_profile = settings_service.update_profile(
                user_id=current_user["id"],
                name=name,
                profile_pic=final_profile_pic,
                cover_pic=final_cover_pic,
                resume=resume_url,
                interests=interests,
                location=location
            )
            return updated_profile
        
        # Handle JSON (application/json) - backward compatibility
        else:
            profile_data = await request.json()
            updated_profile = settings_service.update_profile(
                user_id=current_user["id"],
                name=profile_data.get('name'),
                profile_pic=profile_data.get('profile_pic'),
                cover_pic=profile_data.get('cover_pic'),
                resume=profile_data.get('resume'),
                interests=profile_data.get('interests'),
                location=profile_data.get('location')
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
    description_data: ProfileDescriptionUpdate,
    current_user: dict = Depends(write_rate_limit),
    profile_service: ProfileService = Depends(get_profile_service)
):
    """Update user profile description fields (short_desc, about, skills, etc.)"""
    try:
        updated_profile = profile_service.update_profile(
            user_id=current_user["id"],
            update_data=description_data.model_dump(exclude_none=True)
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


class _PasswordConfirmBody(BaseModel):
    """Request body requiring current password confirmation."""
    current_password: str = Field(..., min_length=1)


@router.post("/2fa/backup-codes", response_model=TwoFactorBackupCodesResponse)
async def get_backup_codes(
    body: _PasswordConfirmBody,
    current_user: dict = Depends(sensitive_rate_limit),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service),
    db: Session = Depends(get_db),
):
    """
    Retrieve 2FA backup codes.

    Requires current password to prevent an attacker with a stolen access
    token from immediately harvesting backup codes and bypassing 2FA.
    """
    try:
        from models.orm import User as OrmUser
        from services.auth_service import verify_password
        user_row = db.query(OrmUser).filter(OrmUser.uid == current_user["id"]).first()
        if not user_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not verify_password(body.current_password, user_row.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        codes = two_factor_service.get_backup_codes(current_user["id"])
        return {
            "backup_codes": codes,
            "message": "Store these codes in a safe place. Each code can only be used once."
        }
    except HTTPException:
        raise
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
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
    body: _PasswordConfirmBody,
    current_user: dict = Depends(sensitive_rate_limit),
    two_factor_service: TwoFactorService = Depends(get_two_factor_service),
    db: Session = Depends(get_db),
):
    """
    Disable 2FA for current user.

    Requires current password to prevent an attacker with a stolen access
    token from permanently eliminating the second factor.
    """
    try:
        from models.orm import User as OrmUser
        from services.auth_service import verify_password
        user_row = db.query(OrmUser).filter(OrmUser.uid == current_user["id"]).first()
        if not user_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if not verify_password(body.current_password, user_row.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        two_factor_service.disable_2fa(current_user["id"])
        return {"message": "2FA disabled successfully"}
    except HTTPException:
        raise
    except NotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        logger.error(f"Disable 2FA error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable 2FA"
        )


@router.post("/enterprise-inquiry")
async def submit_enterprise_inquiry(
    body: EnterpriseInquiryRequest,
    current_user: dict = Depends(enterprise_inquiry_rate_limit),
    db: Session = Depends(get_db),
):
    """Persist enterprise interest (authenticated). User id from JWT only; visible in backoffice."""
    uid = current_user.get("id")
    email = str(body.email).strip()
    try:
        row = EnterpriseInquiry(
            user_id=int(uid),
            contact_email=email[:255],
            user_email=(current_user.get("email") or "")[:255] or None,
            username=(current_user.get("username") or "")[:100] or None,
            status="new",
        )
        db.add(row)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("enterprise_inquiry persist failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save your request. Please try again.",
        )
    logger.info(
        "enterprise_inquiry user_id=%s email=%s username=%s",
        uid,
        email,
        current_user.get("username"),
    )
    return {"success": True, "message": "Thank you. Our team will contact you soon."}


@router.delete("/account")
async def delete_account(
    request: Request,
    body: DeleteAccountRequest,
    current_user: dict = Depends(sensitive_rate_limit),
    settings_service: SettingsService = Depends(get_settings_service),
    db: Session = Depends(get_db),
):
    """Delete user account. Requires current password to confirm intent."""
    try:
        uid = current_user["id"]
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        settings_service.delete_account(
            uid,
            password=body.password,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        messaging = MessagingService()
        purged = await messaging.purge_conversations_for_user(uid)
        if not purged:
            _enqueue_firebase_retry(db, uid)
        return {"message": "Account deleted successfully", "firebase_purged": purged}
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
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


def _enqueue_firebase_retry(db: Session, user_id: int) -> None:
    """Insert a pending Firebase purge retry row when the realtime DB call fails."""
    from sqlalchemy import text
    try:
        db.execute(
            text(
                """
                INSERT INTO firebase_purge_retries (user_id)
                VALUES (:uid)
                ON CONFLICT DO NOTHING
                """
            ),
            {"uid": user_id},
        )
        db.commit()
    except Exception:
        logger.error("Failed to enqueue Firebase retry for uid=%s", user_id, exc_info=True)
