"""Admin authentication router"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from dependencies.database import get_db
from dependencies.auth import get_current_admin
from services.auth_service import AuthService
from schemas.admin import AdminLogin, AdminLoginResponse, AdminResponse, AdminCreate
from models.orm.admin_activity_log import AdminActivityLog
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/auth", tags=["Admin Authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Get auth service instance"""
    return AuthService(db)


def log_admin_activity(
    admin_id: int,
    action_type: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Log admin activity"""
    try:
        activity_log = AdminActivityLog(
            admin_id=admin_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(activity_log)
        db.commit()
    except Exception as e:
        logger.error(f"Error logging admin activity: {e}")
        db.rollback()


@router.post("/login", response_model=AdminLoginResponse)
async def login(
    login_data: AdminLogin,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Admin login endpoint
    
    Returns JWT access token on successful authentication
    """
    try:
        # Get client IP and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = auth_service.login(
            username=login_data.username,
            password=login_data.password,
            ip_address=ip_address
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Log successful login
        admin_id = result["admin"]["id"]
        log_admin_activity(
            admin_id=admin_id,
            action_type="login",
            ip_address=ip_address,
            user_agent=user_agent,
            db=auth_service.db
        )
        
        return AdminLoginResponse(**result)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get current authenticated admin user information
    """
    return AdminResponse(**current_admin)


@router.post("/register")
async def register_admin(
    admin_data: AdminCreate,
    request: Request,
    current_admin: dict = Depends(get_current_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new admin user (requires super_admin role)
    """
    # Only super_admin can create new admins
    if current_admin.get("role") != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required to create admin users"
        )
    
    try:
        # Get client IP and user agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        admin_user = auth_service.register_admin(
            username=admin_data.username,
            email=admin_data.email,
            password=admin_data.password,
            role=admin_data.role
        )
        
        # Log admin creation
        log_admin_activity(
            admin_id=current_admin["id"],
            action_type="admin_create",
            target_type="admin_user",
            target_id=admin_user["id"],
            details={"username": admin_data.username, "role": admin_data.role},
            ip_address=ip_address,
            user_agent=user_agent,
            db=auth_service.db
        )
        
        return {
            "success": True,
            "message": "Admin user created successfully",
            "admin": AdminResponse(**admin_user)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
