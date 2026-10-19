"""
Rate Limiting Utilities
Centralized rate limiting with semaphore management for API calls
"""
import os
import threading
import time
import logging
from typing import Optional, Dict
from contextlib import contextmanager
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """Thread-safe rate limiter using semaphores and time-based tracking"""
    
    def __init__(
        self,
        max_concurrent: int,
        name: str = "default",
        requests_per_minute: Optional[int] = None
    ):
        """
        Initialize rate limiter
        
        Args:
            max_concurrent: Maximum concurrent requests allowed
            name: Name identifier for this limiter
            requests_per_minute: Optional RPM limit (enforces time-based rate limiting)
        """
        self.name = name
        self.max_concurrent = max_concurrent
        self.semaphore = threading.Semaphore(max_concurrent)
        self.requests_per_minute = requests_per_minute
        
        # Time-based rate limiting
        self.request_times = []
        self.lock = threading.Lock()
        
        logger.info(f"RateLimiter '{name}' initialized: max_concurrent={max_concurrent}, rpm={requests_per_minute}")
    
    @contextmanager
    def acquire(self):
        """
        Context manager to acquire rate limit permit
        
        Usage:
            with rate_limiter.acquire():
                # Make API call
                pass
        """
        # Check RPM limit first (before acquiring semaphore to avoid blocking)
        if self.requests_per_minute:
            self._wait_for_rpm_limit()
        
        # Wait for semaphore (concurrent limit)
        # Acquire after RPM check to avoid semaphore leak if RPM check fails
        self.semaphore.acquire()
        
        try:
            yield
        finally:
            self.semaphore.release()
    
    def _wait_for_rpm_limit(self):
        """Wait if necessary to respect requests per minute limit"""
        # Calculate wait time while holding lock (quick operation)
        wait_time = 0
        with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.request_times = [t for t in self.request_times if now - t < 60]
            
            if len(self.request_times) >= self.requests_per_minute:
                # Calculate wait time until oldest request expires
                oldest_time = min(self.request_times)
                wait_time = 60 - (now - oldest_time) + 0.1  # Add small buffer
            else:
                # Record this request immediately if under limit
                self.request_times.append(time.time())
        
        # Sleep outside the lock to avoid serializing all requests
        if wait_time > 0:
            logger.debug(f"RateLimiter '{self.name}': Waiting {wait_time:.2f}s for RPM limit")
            time.sleep(wait_time)
            
            # Re-acquire lock to record request after waiting
            with self.lock:
                now = time.time()
                # Clean up again after waiting
                self.request_times = [t for t in self.request_times if now - t < 60]
                # Record this request
                self.request_times.append(time.time())


class RateLimiterManager:
    """Singleton manager for rate limiters"""
    
    _instance = None
    _lock = threading.Lock()
    _limiters: Dict[str, RateLimiter] = {}
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def get_limiter(
        self,
        name: str,
        max_concurrent: Optional[int] = None,
        requests_per_minute: Optional[int] = None
    ) -> RateLimiter:
        """
        Get or create a rate limiter
        
        Args:
            name: Unique name for the limiter
            max_concurrent: Max concurrent requests (from env if not provided)
            requests_per_minute: RPM limit (from env if not provided)
        
        Returns:
            RateLimiter instance
            
        Note:
            If a limiter with the given name already exists, the provided parameters
            are ignored and the existing limiter is returned. To update a limiter,
            it must be removed first or a new name must be used.
        """
        with self._lock:
            if name not in self._limiters:
                # Get defaults from environment
                if max_concurrent is None:
                    env_key = f"{name.upper()}_MAX_CONCURRENT"
                    max_concurrent = int(os.environ.get(env_key, 5))
                
                if requests_per_minute is None:
                    env_key = f"{name.upper()}_RATE_LIMIT_RPM"
                    requests_per_minute = int(os.environ.get(env_key, 0)) or None
                
                self._limiters[name] = RateLimiter(
                    max_concurrent=max_concurrent,
                    name=name,
                    requests_per_minute=requests_per_minute
                )
            else:
                # Log warning if parameters are provided but limiter already exists
                if max_concurrent is not None or requests_per_minute is not None:
                    logger.warning(
                        f"RateLimiter '{name}' already exists. "
                        f"Provided parameters (max_concurrent={max_concurrent}, "
                        f"requests_per_minute={requests_per_minute}) are ignored. "
                        f"Using existing limiter configuration."
                    )
        
        return self._limiters[name]


# Convenience functions
def get_rate_limiter(name: str, **kwargs) -> RateLimiter:
    """Get a rate limiter by name"""
    manager = RateLimiterManager.get_instance()
    return manager.get_limiter(name, **kwargs)


# Pre-configured limiters (will be initialized on first use)
def get_openai_limiter() -> RateLimiter:
    """Get OpenAI API rate limiter"""
    max_concurrent = int(os.environ.get('OPENAI_MAX_CONCURRENT_REQUESTS', 5))
    rpm = int(os.environ.get('OPENAI_RATE_LIMIT_RPM', 0)) or None
    return get_rate_limiter('openai', max_concurrent=max_concurrent, requests_per_minute=rpm)


def get_duckduckgo_search_limiter() -> RateLimiter:
    """Get web search (DuckDuckGo) rate limiter"""
    max_concurrent = int(os.environ.get('DUCKDUCKGO_SEARCH_MAX_CONCURRENT', 3))
    return get_rate_limiter('duckduckgo_search', max_concurrent=max_concurrent)


def get_google_search_limiter() -> RateLimiter:
    """
    Deprecated: Use get_duckduckgo_search_limiter() instead.
    This function is kept for backward compatibility but uses DuckDuckGo env vars.
    """
    logger.warning(
        "get_google_search_limiter() is deprecated. "
        "Use get_duckduckgo_search_limiter() instead. "
        "Falling back to DuckDuckGo configuration."
    )
    return get_duckduckgo_search_limiter()


def get_qdrant_limiter() -> RateLimiter:
    """Get Qdrant API rate limiter"""
    max_concurrent = int(os.environ.get('QDRANT_MAX_CONCURRENT_OPS', 10))
    return get_rate_limiter('qdrant', max_concurrent=max_concurrent)
