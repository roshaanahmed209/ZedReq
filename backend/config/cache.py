"""Redis Cache Configuration with In-Memory TTL Fallback Support"""
from redis import Redis
from redis.exceptions import ConnectionError, RedisError
from cachetools import TTLCache
import threading
import json
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client with connection error handling
_redis_client = None
_redis_available = False
_redis_initialized = False  # Track if we've attempted initialization

# In-memory TTL cache fallback (used when Redis is unavailable)
# maxsize=512 entries, ttl=120 seconds (2 minutes)
_memory_cache = TTLCache(maxsize=512, ttl=120)
_memory_cache_lock = threading.Lock()


def _init_redis():
    """Initialize Redis client with fallback handling"""
    global _redis_client, _redis_available, _redis_initialized
    
    # If already initialized and available, return immediately
    if _redis_available and _redis_client is not None:
        return _redis_client, _redis_available
    
    # If already initialized but unavailable, return without retrying
    if _redis_initialized and not _redis_available:
        return _redis_client, _redis_available
    
    # Mark as initialized to prevent repeated connection attempts
    _redis_initialized = True
    
    try:
        _redis_client = Redis(
            host=os.environ.get('REDIS_HOST', 'localhost'),
            port=int(os.environ.get('REDIS_PORT', 6379)),
            db=int(os.environ.get('REDIS_DB', 0)),
            decode_responses=False,
            socket_connect_timeout=2,  # 2 second timeout
            socket_timeout=2,
            retry_on_timeout=False
        )
        # Test connection
        _redis_client.ping()
        _redis_available = True
        logger.info("Redis connection established successfully")
    except (ConnectionError, RedisError, Exception) as e:
        _redis_available = False
        _redis_client = None
        # Only log once at INFO level (not WARNING) since fallback is working
        logger.info(f"Redis not available, using in-memory TTL cache fallback: {e}")
    
    return _redis_client, _redis_available


def get_cached_dashboard(user_id: int):
    """Get cached dashboard — tries Redis first, falls back to in-memory TTLCache"""
    redis_client, available = _init_redis()
    
    if available and redis_client is not None:
        try:
            key = f"lms:dashboard:{user_id}"
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning(f"Redis cache read failed, trying memory cache: {e}")
    
    # Fallback: in-memory cache
    with _memory_cache_lock:
        return _memory_cache.get(f"lms:dashboard:{user_id}")


def cache_dashboard(user_id: int, data: dict, ttl: int = 300):
    """Cache dashboard — tries Redis first, falls back to in-memory TTLCache"""
    redis_client, available = _init_redis()
    key = f"lms:dashboard:{user_id}"
    
    if available and redis_client is not None:
        try:
            redis_client.setex(key, ttl, json.dumps(data))
            return
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning(f"Redis cache write failed, using memory cache: {e}")
    
    # Fallback: in-memory cache
    with _memory_cache_lock:
        _memory_cache[key] = data


def invalidate_dashboard_cache(user_id: int):
    """Invalidate dashboard cache in both Redis and in-memory"""
    redis_client, available = _init_redis()
    key = f"lms:dashboard:{user_id}"
    
    if available and redis_client is not None:
        try:
            redis_client.delete(key)
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning(f"Redis cache invalidation failed: {e}")
    
    # Always also clear from memory cache
    with _memory_cache_lock:
        _memory_cache.pop(key, None)


# ========================================================================
# Generic in-memory cache helpers (for non-dashboard data)
# ========================================================================

def get_cached(key: str):
    """Get any value from in-memory cache (or Redis if available)"""
    redis_client, available = _init_redis()
    
    if available and redis_client is not None:
        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except (ConnectionError, RedisError, Exception):
            pass
    
    with _memory_cache_lock:
        return _memory_cache.get(key)


def set_cached(key: str, data, ttl: int = 120):
    """Set any value in in-memory cache (and Redis if available)"""
    redis_client, available = _init_redis()
    
    if available and redis_client is not None:
        try:
            redis_client.setex(key, ttl, json.dumps(data))
            return
        except (ConnectionError, RedisError, Exception):
            pass
    
    with _memory_cache_lock:
        _memory_cache[key] = data


def invalidate_cached(key: str):
    """Invalidate any cached key from both Redis and in-memory"""
    redis_client, available = _init_redis()
    
    if available and redis_client is not None:
        try:
            redis_client.delete(key)
        except (ConnectionError, RedisError, Exception):
            pass
    
    with _memory_cache_lock:
        _memory_cache.pop(key, None)


def is_redis_available() -> bool:
    """Check if Redis is available"""
    _, available = _init_redis()
    return available
