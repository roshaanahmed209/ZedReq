"""
JWT Token Denylist — revoke individual tokens by their jti claim.

Uses Redis (via config/cache._init_redis) with a TTLCache in-memory fallback
so behaviour is correct whether or not Redis is available.

Keys: "jti:{jti_value}"  — value is irrelevant, existence = revoked.
TTL is set to the token's remaining lifetime so the key is self-cleaning.
"""
import logging
import time
from typing import Optional

from cachetools import TTLCache

logger = logging.getLogger(__name__)

# In-memory fallback store: keeps up to 4096 revoked jtis for up to 24 h.
# This is only used when Redis is unavailable — in a multi-worker deployment
# Redis is required for cross-process revocation to work.
_memory_denylist: TTLCache = TTLCache(maxsize=4096, ttl=86400)


def _redis_key(jti: str) -> str:
    return f"jti:{jti}"


def revoke(jti: str, ttl_seconds: int) -> None:
    """
    Mark a token as revoked.

    Args:
        jti: The unique token identifier from the JWT payload.
        ttl_seconds: How many seconds until the token would have expired anyway.
                     The denylist entry is kept for this long, then auto-deleted.
    """
    if ttl_seconds <= 0:
        return  # Token already expired — nothing to revoke

    try:
        from config.cache import _init_redis
        client, available = _init_redis()
        if available and client is not None:
            client.setex(_redis_key(jti), ttl_seconds, "1")
            return
    except Exception as exc:
        logger.warning("Redis denylist write failed, falling back to memory: %s", exc)

    # Memory fallback
    _memory_denylist[_redis_key(jti)] = True


def is_revoked(jti: Optional[str]) -> bool:
    """
    Return True if the token identified by *jti* has been revoked.

    A missing or None jti is treated as NOT revoked so that tokens issued
    before jti was added continue to work (backwards compatibility window).
    """
    if not jti:
        return False

    try:
        from config.cache import _init_redis
        client, available = _init_redis()
        if available and client is not None:
            return client.exists(_redis_key(jti)) > 0
    except Exception as exc:
        logger.warning("Redis denylist read failed, falling back to memory: %s", exc)

    return _redis_key(jti) in _memory_denylist
