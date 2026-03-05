"""Rate Limiting Dependencies for FastAPI Endpoints"""
from fastapi import HTTPException, status, Depends
from typing import Callable
import time
from collections import defaultdict
from threading import Lock
import logging

from dependencies.auth import get_current_user

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter for API endpoints"""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests allowed per minute per user
        """
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)  # user_id -> list of request timestamps
        self.lock = Lock()
        self.window_seconds = 60
    
    def is_allowed(self, user_id: int) -> bool:
        """
        Check if request is allowed for user
        
        Args:
            user_id: User ID making the request
            
        Returns:
            True if allowed, False if rate limit exceeded
        """
        with self.lock:
            now = time.time()
            user_requests = self.requests[user_id]
            
            # Remove requests outside the time window
            user_requests[:] = [t for t in user_requests if now - t < self.window_seconds]
            
            # Check if limit exceeded
            if len(user_requests) >= self.requests_per_minute:
                return False
            
            # Record this request
            user_requests.append(now)
            return True
    
    def get_remaining(self, user_id: int) -> int:
        """Get remaining requests for user in current window"""
        with self.lock:
            now = time.time()
            user_requests = self.requests[user_id]
            user_requests[:] = [t for t in user_requests if now - t < self.window_seconds]
            return max(0, self.requests_per_minute - len(user_requests))


# Global rate limiters for different endpoint types
_profile_limiter = RateLimiter(requests_per_minute=120)  # More lenient for profile reads
_write_limiter = RateLimiter(requests_per_minute=30)  # Stricter for write operations
_analytics_limiter = RateLimiter(requests_per_minute=60)  # Moderate for analytics


def rate_limit(limiter: RateLimiter, error_message: str = "Rate limit exceeded"):
    """
    Decorator/dependency for rate limiting
    
    Args:
        limiter: RateLimiter instance to use
        error_message: Error message to return when limit exceeded
    
    Returns:
        Dependency function
    """
    def dependency(current_user: dict):
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        if not limiter.is_allowed(user_id):
            remaining = limiter.get_remaining(user_id)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": error_message,
                    "retry_after": 60,
                    "remaining": remaining
                },
                headers={
                    "X-RateLimit-Limit": str(limiter.requests_per_minute),
                    "X-RateLimit-Remaining": str(remaining),
                    "Retry-After": "60"
                }
            )
        
        return current_user
    
    return dependency


# Pre-configured rate limit dependencies
def profile_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for profile read operations"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _profile_limiter.is_allowed(user_id):
        remaining = _profile_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many profile requests",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": str(_profile_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user


def write_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for write operations (create, update, delete)"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _write_limiter.is_allowed(user_id):
        remaining = _write_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many write requests",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": str(_write_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user


def analytics_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for analytics operations"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _analytics_limiter.is_allowed(user_id):
        remaining = _analytics_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many analytics requests",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": str(_analytics_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user
