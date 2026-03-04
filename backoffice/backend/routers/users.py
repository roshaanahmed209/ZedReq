"""User management router"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from dependencies.database import get_db
from dependencies.auth import require_admin_role
from services.admin_service import AdminService
from schemas.admin import UserListResponse, UserDetailsResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/users", tags=["User Management"])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Get admin service instance"""
    return AdminService(db)


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}", response_model=UserDetailsResponse)
async def get_user_details(
    user_id: int,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get comprehensive user details"""
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


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: int,
    new_role: str,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Update user role"""
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        success = service.update_user_role(
            user_id=user_id,
            new_role=new_role,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"success": True, "message": "User role updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )


@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: int,
    reason: str,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Suspend a user account"""
    try:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        success = service.suspend_user(
            user_id=user_id,
            reason=reason,
            admin_id=current_admin["id"],
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {"success": True, "message": "User suspended"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error suspending user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to suspend user"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    request: Request,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Delete a user account"""
    try:
        # Log deletion attempt
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        service._log_admin_activity(
            admin_id=current_admin["id"],
            action_type='user_delete',
            target_type='user',
            target_id=user_id,
            details={},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # TODO: Implement actual deletion when integrated with main database
        return {"success": True, "message": "User deletion logged (integration pending)"}
    except Exception as e:
        logger.error(f"Error deleting user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
