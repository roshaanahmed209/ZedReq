"""Authentication dependencies for FastAPI"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from config.database_orm import get_db
from services.auth_service import AuthService
from utils.auth import decode_access_token
from models.orm.admin_user import AdminUser

security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current authenticated admin user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
    
    Returns:
        Dict with admin user info
    
    Raises:
        HTTPException: If token is invalid or admin not found
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin_id: int = int(payload.get("sub"))
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService(db)
    admin_user = auth_service.get_admin_by_id(admin_id)
    
    if admin_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is deactivated"
        )
    
    return {
        "id": admin_user.id,
        "username": admin_user.username,
        "email": admin_user.email,
        "role": admin_user.role,
        "is_active": admin_user.is_active
    }


def require_admin_role(current_admin: dict = Depends(get_current_admin)) -> dict:
    """
    Require admin or super_admin role
    
    Args:
        current_admin: Current admin user from get_current_admin
    
    Returns:
        Admin user dict
    
    Raises:
        HTTPException: If user doesn't have admin role
    """
    if current_admin.get("role") not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_admin


def require_super_admin(current_admin: dict = Depends(get_current_admin)) -> dict:
    """
    Require super_admin role
    
    Args:
        current_admin: Current admin user from get_current_admin
    
    Returns:
        Admin user dict
    
    Raises:
        HTTPException: If user doesn't have super_admin role
    """
    if current_admin.get("role") != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_admin
