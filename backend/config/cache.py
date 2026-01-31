"""Redis Cache Configuration with Fallback Support"""
from redis import Redis
from redis.exceptions import ConnectionError, RedisError
import json
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Redis client with connection error handling
_redis_client = None
_redis_available = False


def _init_redis():
    """Initialize Redis client with fallback handling"""
    global _redis_client, _redis_available
    
    if _redis_client is not None:
        return _redis_client, _redis_available
    
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
        logger.warning(f"Redis not available, using fallback (no caching): {e}")
    
    return _redis_client, _redis_available


def get_cached_dashboard(user_id: int):
    """Get cached dashboard with fallback to None if Redis unavailable"""
    redis_client, available = _init_redis()
    
    if not available or redis_client is None:
        return None
    
    try:
        key = f"lms:dashboard:{user_id}"
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except (ConnectionError, RedisError, Exception) as e:
        logger.warning(f"Redis cache read failed, using fallback: {e}")
        return None
    
    return None


def cache_dashboard(user_id: int, data: dict, ttl: int = 300):
    """Cache dashboard with fallback (silently fails if Redis unavailable)"""
    redis_client, available = _init_redis()
    
    if not available or redis_client is None:
        return  # Silently skip caching if Redis unavailable
    
    try:
        key = f"lms:dashboard:{user_id}"
        redis_client.setex(key, ttl, json.dumps(data))
    except (ConnectionError, RedisError, Exception) as e:
        logger.warning(f"Redis cache write failed: {e}")
        # Don't raise - gracefully degrade


def invalidate_dashboard_cache(user_id: int):
    """Invalidate dashboard cache with fallback"""
    redis_client, available = _init_redis()
    
    if not available or redis_client is None:
        return  # Silently skip if Redis unavailable
    
    try:
        key = f"lms:dashboard:{user_id}"
        redis_client.delete(key)
    except (ConnectionError, RedisError, Exception) as e:
        logger.warning(f"Redis cache invalidation failed: {e}")
        # Don't raise - gracefully degrade


def is_redis_available() -> bool:
    """Check if Redis is available"""
    _, available = _init_redis()
    return available
