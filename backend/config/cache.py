"""Redis cache layer with in-memory TTL fallback.

Connection priority: REDIS_URL (Render) → REDIS_HOST/PORT/DB.
Set REDIS_ENABLED=false to disable explicitly. When REDIS_URL or REDIS_HOST
is set, Redis is used unless disabled. REDIS_REQUIRED=true fails startup if
Redis cannot be reached.
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
from typing import Any, Optional, Tuple

from cachetools import TTLCache
from redis import Redis
from redis.exceptions import ConnectionError, RedisError

logger = logging.getLogger(__name__)

_redis_client: Optional[Redis] = None
_redis_available: bool = False
_redis_initialized: bool = False
_redis_init_error: Optional[str] = None

_memory_cache: TTLCache = TTLCache(maxsize=512, ttl=120)
_memory_cache_lock = threading.Lock()


def _is_redis_explicitly_disabled() -> bool:
    return os.environ.get("REDIS_ENABLED", "").lower() == "false"


def _is_redis_configured() -> bool:
    if _is_redis_explicitly_disabled():
        return False
    if os.environ.get("REDIS_ENABLED", "").lower() == "true":
        return True
    if (os.environ.get("REDIS_URL") or "").strip():
        return True
    host = (os.environ.get("REDIS_HOST") or "").strip()
    return bool(host)


def _build_redis_client() -> Redis:
    redis_url = (os.environ.get("REDIS_URL") or "").strip()
    if redis_url:
        return Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=False,
        )
    return Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        db=int(os.environ.get("REDIS_DB", 0)),
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        retry_on_timeout=False,
    )


def _init_redis() -> Tuple[Optional[Redis], bool]:
    """Initialize shared Redis client (idempotent)."""
    global _redis_client, _redis_available, _redis_initialized, _redis_init_error

    if _redis_available and _redis_client is not None:
        return _redis_client, _redis_available

    if _redis_initialized and not _redis_available:
        return _redis_client, _redis_available

    _redis_initialized = True

    if not _is_redis_configured():
        _redis_available = False
        _redis_client = None
        _redis_init_error = "Redis not configured (set REDIS_URL or REDIS_HOST)"
        logger.info(_redis_init_error)
        return _redis_client, _redis_available

    try:
        client = _build_redis_client()
        client.ping()
        _redis_client = client
        _redis_available = True
        _redis_init_error = None
        logger.info("Redis connection established successfully")
    except (ConnectionError, RedisError, OSError, Exception) as e:
        _redis_available = False
        _redis_client = None
        _redis_init_error = str(e)
        logger.info("Redis not available, using in-memory TTL cache fallback: %s", e)

        if os.environ.get("REDIS_REQUIRED", "").lower() == "true":
            raise RuntimeError(f"REDIS_REQUIRED=true but Redis connection failed: {e}") from e

    return _redis_client, _redis_available


def get_redis_client() -> Optional[Redis]:
    """Return the shared Redis client, or None if unavailable."""
    client, _ = _init_redis()
    return client


def is_redis_available() -> bool:
    """Whether the shared Redis client connected successfully."""
    _, available = _init_redis()
    return available


def ping_redis() -> dict[str, Any]:
    """Health probe: availability and round-trip latency in milliseconds."""
    client, available = _init_redis()
    if not available or client is None:
        return {
            "available": False,
            "latency_ms": None,
            "error": _redis_init_error or "Redis unavailable",
        }
    try:
        start = time.perf_counter()
        client.ping()
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {"available": True, "latency_ms": latency_ms, "error": None}
    except (ConnectionError, RedisError, OSError) as e:
        return {"available": False, "latency_ms": None, "error": str(e)}


def get_cached_dashboard(user_id: int):
    """Get cached dashboard — tries Redis first, falls back to in-memory TTLCache."""
    redis_client, available = _init_redis()

    if available and redis_client is not None:
        try:
            key = f"lms:dashboard:{user_id}"
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning("Redis cache read failed, trying memory cache: %s", e)

    with _memory_cache_lock:
        return _memory_cache.get(f"lms:dashboard:{user_id}")


def cache_dashboard(user_id: int, data: dict, ttl: int = 300):
    """Cache dashboard — tries Redis first, falls back to in-memory TTLCache."""
    redis_client, available = _init_redis()
    key = f"lms:dashboard:{user_id}"

    if available and redis_client is not None:
        try:
            redis_client.setex(key, ttl, json.dumps(data))
            return
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning("Redis cache write failed, using memory cache: %s", e)

    with _memory_cache_lock:
        _memory_cache[key] = data


def invalidate_dashboard_cache(user_id: int):
    """Invalidate dashboard cache in both Redis and in-memory."""
    redis_client, available = _init_redis()
    keys = (f"lms:dashboard:{user_id}", f"lms:dashboard_all:{user_id}")

    if available and redis_client is not None:
        try:
            redis_client.delete(*keys)
        except (ConnectionError, RedisError, Exception) as e:
            logger.warning("Redis cache invalidation failed: %s", e)

    with _memory_cache_lock:
        for key in keys:
            _memory_cache.pop(key, None)


def get_cached(key: str):
    """Get any value from Redis or in-memory cache."""
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
    """Set any value in Redis or in-memory cache."""
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
    """Invalidate any cached key from Redis and in-memory."""
    redis_client, available = _init_redis()

    if available and redis_client is not None:
        try:
            redis_client.delete(key)
        except (ConnectionError, RedisError, Exception):
            pass

    with _memory_cache_lock:
        _memory_cache.pop(key, None)
