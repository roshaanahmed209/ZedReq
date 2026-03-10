"""User management router"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from dependencies.database import get_db
from dependencies.auth import require_admin_role, require_super_admin
from services.admin_service import AdminService
from schemas.admin import (
    UserListResponse,
    UserDetailsResponse,
    ChangePlanRequest,
    CancelSubscriptionRequest,
    SuspendRequest,
    ResetPasswordRequest,
    Disable2FARequest,
    DeleteUserRequest,
    SendNotificationRequest,
    AssignEnterprisePlanRequest,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/users", tags=["User Management"])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Get admin service instance"""
    return AdminService(db)


def _extract_request_meta(request: Request):
    """Extract IP address and user agent from request"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


# ============================================================================
# Read-Only Endpoints (admin or super_admin)
# ============================================================================

@router.get("", response_model=UserListResponse)
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    subscription_status: Optional[str] = Query(None),
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get paginated list of all users with filters"""
    try:
        result = service.get_all_users(page, limit, search, role, subscription_status)
        return UserListResponse(**result)
    except Exception as e:
        logger.error(f"Error getting users: {e}", exc_info=True)
        error_detail = str(e)
        if "connection" in error_detail.lower() or "database" in error_detail.lower():
            error_detail = f"Database connection failed: {error_detail}. Please verify MAIN_APP_DB_* settings in backoffice/.env"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/{user_id}", response_model=UserDetailsResponse)
async def get_user_details(
    user_id: int,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get comprehensive user details"""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        details = service.get_user_details(user_id)
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserDetailsResponse(**details)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user details"
        )


@router.get("/{user_id}/export")
async def export_user_data(
    user_id: int,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Export all user data (GDPR compliance). Read-only — zero writes to main DB."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        export = service.export_user_data(
            user_id=user_id,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return export
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting user data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export user data"
        )


# ============================================================================
# Write Endpoints — admin role (plan changes, subscriptions)
# ============================================================================

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Update user role"""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        success = service.update_user_role(
            user_id=user_id,
            new_role=new_role,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"success": True, "message": "User role updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@router.put("/{user_id}/plan")
async def change_user_plan(
    user_id: int,
    body: ChangePlanRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Change a user's subscription plan. UPSERT user_subscriptions + sync payment."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.change_user_plan(
            user_id=user_id,
            new_plan=body.plan,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error changing user plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change user plan"
        )


@router.post("/{user_id}/cancel-subscription")
async def cancel_subscription(
    user_id: int,
    body: CancelSubscriptionRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Cancel a user's active subscription. 1 UPDATE on payment table."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.cancel_subscription(
            user_id=user_id,
            reason=body.reason,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    body: SuspendRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Suspend a user account. Log-only in backoffice DB."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        success = service.suspend_user(
            user_id=user_id,
            reason=body.reason,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return {"success": True, "message": "User suspended"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suspending user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suspend user"
        )


@router.post("/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: int,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Unsuspend a user account. Log-only in backoffice DB."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.unsuspend_user(
            user_id=user_id,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error unsuspending user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsuspend user"
        )


@router.post("/{user_id}/force-logout")
async def force_logout_user(
    user_id: int,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Force logout a user. Log-only in backoffice DB."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.force_logout_user(
            user_id=user_id,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error forcing user logout: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to force logout user"
        )


@router.post("/{user_id}/notify")
async def send_user_notification(
    user_id: int,
    body: SendNotificationRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Send admin notification to a user. Log-only in backoffice DB."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.send_user_notification(
            user_id=user_id,
            subject=body.subject,
            message=body.message,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )


# ============================================================================
# Destructive Endpoints — require super_admin role
# ============================================================================

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    body: ResetPasswordRequest,
    request: Request,
    current_admin: dict = Depends(require_super_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Reset a user's password. Requires super_admin. 1 UPDATE on users table."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.reset_user_password(
            user_id=user_id,
            new_password=body.new_password,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error resetting user password: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user password"
        )


@router.post("/{user_id}/disable-2fa")
async def disable_user_2fa(
    user_id: int,
    body: Disable2FARequest,
    request: Request,
    current_admin: dict = Depends(require_super_admin),
    service: AdminService = Depends(get_admin_service)
):
    """Disable 2FA for a user. Requires super_admin. 1 UPDATE on users table."""
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.disable_user_2fa(
            user_id=user_id,
            reason=body.reason,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error disabling 2FA: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable 2FA"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    body: DeleteUserRequest = None,
    current_admin: dict = Depends(require_super_admin),
    service: AdminService = Depends(get_admin_service)
):
    """
    Soft-delete a user account. Requires super_admin.
    Cancels subscription + logs deletion intent. No cascading DELETE.
    """
    if user_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    try:
        ip_address, user_agent = _extract_request_meta(request)
        reason = body.reason if body else "Admin deletion"
        result = service.delete_user_soft(
            user_id=user_id,
            reason=reason,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


# ============================================================================
# Enterprise Plan Assignment (super_admin only)
# ============================================================================

@router.post("/assign-enterprise", dependencies=[Depends(require_super_admin)])
async def assign_enterprise_plan(
    body: AssignEnterprisePlanRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """
    Assign enterprise plan to a user by email.
    Requires super_admin role. Full audit trail.
    """
    try:
        ip_address, user_agent = _extract_request_meta(request)
        result = service.assign_enterprise_plan(
            user_email=body.email,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning enterprise plan: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign enterprise plan"
        )
