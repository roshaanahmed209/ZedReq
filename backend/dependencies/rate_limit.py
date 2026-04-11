"""Rate Limiting Dependencies for FastAPI Endpoints"""
from fastapi import HTTPException, status, Depends
from typing import Callable
import time
from collections import defaultdict
from threading import Lock
import logging

from dependencies.auth import get_current_user

logger = logging.getLogger(__name__)


def _redis_sliding_window(key: str, limit: int, window: int) -> tuple[bool, int]:
    """
    Attempt a Redis INCR-based sliding window check.

    Returns (allowed: bool, remaining: int) or raises no exception — on any
    Redis failure returns (None, None) to signal the caller should fall back
    to the in-memory implementation.
    """
    try:
        from config.cache import _init_redis
        client, available = _init_redis()
        if not available or client is None:
            return None, None
        pipe = client.pipeline()
        pipe.incr(key)
        pipe.expire(key, window, nx=True)
        count, _ = pipe.execute()
        count = int(count)
        allowed = count <= limit
        remaining = max(0, limit - count)
        return allowed, remaining
    except Exception as exc:
        logger.debug("Redis rate-limit error (falling back to memory): %s", exc)
        return None, None


class RateLimiter:
    """
    Per-user rate limiter.

    Uses Redis (INCR + EXPIRE sliding window) when available; gracefully
    falls back to an in-process TTL list so deploys without Redis still
    work.  In multi-worker production deployments Redis is required for
    cross-process enforcement.
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        # In-memory fallback store
        self._requests: dict[int, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _memory_is_allowed(self, user_id: int) -> bool:
        with self._lock:
            now = time.time()
            bucket = self._requests[user_id]
            bucket[:] = [t for t in bucket if now - t < self.window_seconds]
            if len(bucket) >= self.requests_per_minute:
                return False
            bucket.append(now)
            return True

    def _memory_remaining(self, user_id: int) -> int:
        with self._lock:
            now = time.time()
            bucket = self._requests[user_id]
            bucket[:] = [t for t in bucket if now - t < self.window_seconds]
            return max(0, self.requests_per_minute - len(bucket))

    def is_allowed(self, user_id: int) -> bool:
        key = f"rl:user:{user_id}:{self.requests_per_minute}"
        allowed, _ = _redis_sliding_window(key, self.requests_per_minute, self.window_seconds)
        if allowed is None:
            return self._memory_is_allowed(user_id)
        return allowed

    def get_remaining(self, user_id: int) -> int:
        key = f"rl:user:{user_id}:{self.requests_per_minute}"
        _, remaining = _redis_sliding_window(key, self.requests_per_minute, self.window_seconds)
        if remaining is None:
            return self._memory_remaining(user_id)
        return remaining


# Global rate limiters for different endpoint types
_profile_limiter = RateLimiter(requests_per_minute=120)  # More lenient for profile reads
_write_limiter = RateLimiter(requests_per_minute=30)  # Stricter for write operations
_analytics_limiter = RateLimiter(requests_per_minute=60)  # Moderate for analytics
# Comments: extra per-user cap (spam / abuse) on top of write_rate_limit
_comment_action_limiter = RateLimiter(requests_per_minute=20)


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


def comment_write_rate_limit(current_user: dict = Depends(write_rate_limit)):
    """
    Stricter per-user limit for comment create/delete (abuse prevention).
    Stacks after write_rate_limit so both apply.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    if not _comment_action_limiter.is_allowed(user_id):
        remaining = _comment_action_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many comments. Please wait a minute and try again.",
                "retry_after": 60,
                "remaining": remaining,
            },
            headers={
                "X-RateLimit-Limit": str(_comment_action_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60",
            },
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
