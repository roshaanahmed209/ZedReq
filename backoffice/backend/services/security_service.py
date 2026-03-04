"""Security service for account lockout, failed login tracking, and security events"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from models.orm.failed_login_attempt import FailedLoginAttempt
from models.orm.admin_activity_log import AdminActivityLog
import logging

logger = logging.getLogger(__name__)

# Security configuration
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
FAILED_ATTEMPT_WINDOW_MINUTES = 15


class SecurityService:
    """Service for security operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_account_lockout(self, username: str) -> tuple[bool, Optional[str]]:
        """
        Check if account is locked due to too many failed attempts
        
        Returns:
            Tuple of (is_locked, lockout_message)
        """
        lockout_time = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        
        # Count failed attempts in the last lockout period
        failed_attempts = self.db.query(FailedLoginAttempt).filter(
            and_(
                FailedLoginAttempt.username == username,
                FailedLoginAttempt.success == False,
                FailedLoginAttempt.attempted_at >= lockout_time
            )
        ).count()
        
        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            # Get the most recent failed attempt
            recent_attempt = self.db.query(FailedLoginAttempt).filter(
                and_(
                    FailedLoginAttempt.username == username,
                    FailedLoginAttempt.success == False
                )
            ).order_by(FailedLoginAttempt.attempted_at.desc()).first()
            
            if recent_attempt:
                time_remaining = LOCKOUT_DURATION_MINUTES - (
                    (datetime.utcnow() - recent_attempt.attempted_at).total_seconds() / 60
                )
                if time_remaining > 0:
                    return True, f"Account locked due to too many failed login attempts. Try again in {int(time_remaining)} minutes."
        
        return False, None
    
    def record_failed_login(
        self,
        username: str,
        ip_address: Optional[str] = None,
        success: bool = False
    ):
        """Record a login attempt"""
        try:
            attempt = FailedLoginAttempt(
                username=username,
                ip_address=ip_address,
                success=success
            )
            self.db.add(attempt)
            self.db.commit()
            
            if not success:
                # Check if we should log a security event
                failed_count = self.get_failed_attempts_count(username)
                if failed_count >= MAX_FAILED_ATTEMPTS:
                    self.log_security_event(
                        event_type='account_lockout',
                        username=username,
                        ip_address=ip_address,
                        details={'failed_attempts': failed_count}
                    )
        except Exception as e:
            logger.error(f"Error recording failed login: {e}")
            self.db.rollback()
    
    def get_failed_attempts_count(self, username: str, window_minutes: int = None) -> int:
        """Get count of failed login attempts in the last window"""
        window_minutes = window_minutes or FAILED_ATTEMPT_WINDOW_MINUTES
        window_start = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        return self.db.query(FailedLoginAttempt).filter(
            and_(
                FailedLoginAttempt.username == username,
                FailedLoginAttempt.success == False,
                FailedLoginAttempt.attempted_at >= window_start
            )
        ).count()
    
    def log_security_event(
        self,
        event_type: str,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict] = None,
        admin_id: Optional[int] = None
    ):
        """Log a security event"""
        try:
            log_entry = AdminActivityLog(
                admin_id=admin_id,
                action_type=f'security_{event_type}',
                target_type='security_event',
                details={
                    'event_type': event_type,
                    'username': username,
                    'ip_address': ip_address,
                    **(details or {})
                },
                ip_address=ip_address,
                user_agent=None
            )
            self.db.add(log_entry)
            self.db.commit()
            logger.warning(f"Security event logged: {event_type} for {username}")
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            self.db.rollback()
    
    def detect_suspicious_activity(
        self,
        username: str,
        ip_address: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Detect suspicious activity patterns
        
        Returns:
            Tuple of (is_suspicious, reason)
        """
        # Check for multiple IP addresses
        if ip_address:
            recent_attempts = self.db.query(FailedLoginAttempt).filter(
                and_(
                    FailedLoginAttempt.username == username,
                    FailedLoginAttempt.attempted_at >= datetime.utcnow() - timedelta(hours=1)
                )
            ).all()
            
            unique_ips = set(attempt.ip_address for attempt in recent_attempts if attempt.ip_address)
            if len(unique_ips) > 3:
                return True, "Multiple IP addresses detected in short time"
        
        # Check for rapid failed attempts
        failed_count = self.get_failed_attempts_count(username, window_minutes=5)
        if failed_count >= 3:
            return True, "Rapid failed login attempts detected"
        
        return False, None
    
    def cleanup_old_attempts(self, days: int = 30):
        """Clean up old failed login attempts"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted = self.db.query(FailedLoginAttempt).filter(
                FailedLoginAttempt.attempted_at < cutoff_date
            ).delete()
            self.db.commit()
            logger.info(f"Cleaned up {deleted} old failed login attempts")
            return deleted
        except Exception as e:
            logger.error(f"Error cleaning up old attempts: {e}")
            self.db.rollback()
            return 0
