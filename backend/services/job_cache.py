"""Redis-backed cache for first-page job list endpoints."""
import json
import os
from typing import Any, Dict, List, Optional

from config.cache import get_redis_client, is_redis_available
from utils.logger import setup_logger

logger = setup_logger(__name__)

CACHE_PREFIX = "jobs:list:"
CACHE_TTL = int(os.environ.get("REDIS_CACHE_TTL", 300))
LIST_TYPES = ("all", "remote", "saved", "posted")


def _cache_key(list_type: str, user_id: int) -> str:
    return f"{CACHE_PREFIX}{list_type}:{user_id}"


def get_cached_job_list(list_type: str, user_id: int) -> Optional[List[Dict[str, Any]]]:
    if list_type not in LIST_TYPES or not user_id or not is_redis_available():
        return None
    try:
        client = get_redis_client()
        if not client:
            return None
        raw = client.get(_cache_key(list_type, user_id))
        if not raw:
            return None
        return json.loads(raw)
    except Exception as e:
        logger.warning("Job list cache get failed (%s:%s): %s", list_type, user_id, e)
        return None


def cache_job_list(list_type: str, user_id: int, jobs: List[Dict[str, Any]]) -> None:
    if list_type not in LIST_TYPES or not user_id or not is_redis_available():
        return
    try:
        client = get_redis_client()
        if not client:
            return
        client.setex(
            _cache_key(list_type, user_id),
            CACHE_TTL,
            json.dumps(jobs, default=str),
        )
    except Exception as e:
        logger.warning("Job list cache set failed (%s:%s): %s", list_type, user_id, e)


def invalidate_job_lists_for_user(user_id: int) -> None:
    """Clear all first-page job list caches for a user."""
    if not user_id or not is_redis_available():
        return
    try:
        client = get_redis_client()
        if not client:
            return
        keys = [_cache_key(t, user_id) for t in LIST_TYPES]
        if keys:
            client.delete(*keys)
        logger.debug("Invalidated job list cache for user %s", user_id)
    except Exception as e:
        logger.warning("Job list cache invalidation failed for user %s: %s", user_id, e)


def invalidate_job_lists_global() -> None:
    """Clear all-users job list caches (e.g. new public job posted)."""
    if not is_redis_available():
        return
    try:
        client = get_redis_client()
        if not client:
            return
        cursor = 0
        while True:
            cursor, keys = client.scan(cursor=cursor, match=f"{CACHE_PREFIX}*", count=100)
            if keys:
                client.delete(*keys)
            if cursor == 0:
                break
    except Exception as e:
        logger.warning("Global job list cache invalidation failed: %s", e)
