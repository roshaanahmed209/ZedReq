"""Authentication service for admin users"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from models.orm.admin_user import AdminUser
from models.orm.failed_login_attempt import FailedLoginAttempt
from utils.auth import (
    hash_password,
    verify_password,
    validate_password_strength,
    validate_email,
    validate_username,
    create_access_token
)
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Account lockout configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30


class AuthService:
    """Service for admin authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_admin(
        self,
        username: str,
        email: str,
        password: str,
        role: str = 'admin'
    ) -> Optional[Dict[str, Any]]:
        """
        Register a new admin user
        
        Args:
            username: Admin username
            email: Admin email
            password: Plain text password
            role: Admin role (admin or super_admin)
        
        Returns:
            Admin user dict or None if registration fails
        """
        try:
            # Validate inputs
            is_valid, error = validate_username(username)
            if not is_valid:
                raise ValueError(error)
            
            if not validate_email(email):
                raise ValueError("Invalid email format")
            
            is_valid, error = validate_password_strength(password)
            if not is_valid:
                raise ValueError(error)
            
            if role not in ['admin', 'super_admin']:
                raise ValueError("Invalid role. Must be 'admin' or 'super_admin'")
            
            # Check if username or email already exists
            existing_user = self.db.query(AdminUser).filter(
                (AdminUser.username == username) | (AdminUser.email == email)
            ).first()
            
            if existing_user:
                raise ValueError("Username or email already exists")
            
            # Create admin user
            admin_user = AdminUser(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role=role,
                is_active=True
            )
            
            self.db.add(admin_user)
            self.db.commit()
            self.db.refresh(admin_user)
            
            logger.info(f"Admin user registered: {username}")
            
            return admin_user.to_dict()
            
        except ValueError as e:
            self.db.rollback()
            logger.error(f"Registration error: {e}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected registration error: {e}", exc_info=True)
            raise
    
    def login(
        self,
        username: str,
        password: str,
        ip_address: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate admin user and return JWT token
        
        Args:
            username: Admin username or email
            password: Plain text password
            ip_address: Client IP address for logging
        
        Returns:
            Dict with admin info and access token, or None if login fails
        """
        try:
            # Check for account lockout
            if self._is_account_locked(username):
                raise ValueError("Account is temporarily locked due to too many failed login attempts")
            
            # Find admin user by username or email
            admin_user = self.db.query(AdminUser).filter(
                (AdminUser.username == username) | (AdminUser.email == username)
            ).first()
            
            if not admin_user:
                self._record_failed_login(username, ip_address, success=False)
                raise ValueError("Invalid username or password")
            
            if not admin_user.is_active:
                self._record_failed_login(username, ip_address, success=False)
                raise ValueError("Account is deactivated")
            
            # Verify password
            if not verify_password(password, admin_user.password_hash):
                self._record_failed_login(username, ip_address, success=False)
                raise ValueError("Invalid username or password")
            
            # Login successful
            admin_user.last_login = datetime.utcnow()
            self.db.commit()
            
            self._record_failed_login(username, ip_address, success=True)
            
            # Create access token
            access_token = create_access_token(
                data={"sub": str(admin_user.id), "username": admin_user.username, "role": admin_user.role}
            )
            
            logger.info(f"Admin login successful: {username}")
            
            return {
                "admin": admin_user.to_dict(),
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except ValueError as e:
            logger.warning(f"Login failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected login error: {e}", exc_info=True)
            raise
    
    def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to too many failed attempts"""
        lockout_time = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        
        # Count failed attempts in the last lockout period
        failed_attempts = self.db.query(FailedLoginAttempt).filter(
            and_(
                FailedLoginAttempt.username == username,
                FailedLoginAttempt.success == False,
                FailedLoginAttempt.attempted_at >= lockout_time
            )
        ).count()
        
        return failed_attempts >= MAX_FAILED_ATTEMPTS
    
    def _record_failed_login(
        self,
        username: str,
        ip_address: Optional[str],
        success: bool
    ):
        """Record login attempt"""
        try:
            attempt = FailedLoginAttempt(
                username=username,
                ip_address=ip_address,
                success=success
            )
            self.db.add(attempt)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error recording login attempt: {e}")
            self.db.rollback()
    
    def get_admin_by_id(self, admin_id: int) -> Optional[AdminUser]:
        """Get admin user by ID"""
        return self.db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    
    def get_admin_by_username(self, username: str) -> Optional[AdminUser]:
        """Get admin user by username"""
        return self.db.query(AdminUser).filter(AdminUser.username == username).first()
