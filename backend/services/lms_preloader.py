"""LMS Dashboard Background Preloader
========================================
Pre-warms the LMS dashboard cache immediately after a user logs in, so the
first visit to the dashboard returns instantly from cache instead of hitting
the database.

Design principles
-----------------
* **Isolated thread pool** (max 3 workers): preload threads never starve the
  main request handlers competing for the same Uvicorn thread pool.
* **Per-user deduplication**: if the same user logs in twice quickly, only one
  preload is ever in-flight at a time.
* **Global DB semaphore** (2 concurrent preloads): even with 3 executor workers,
  at most 2 heavy DB reads run simultaneously, leaving headroom for OLTP traffic.
* **Login-response first**: a short back-off (0.4 s) ensures the login response
  is sent back to the client before the preloader starts touching the database.
* **Dedicated session**: every preload opens its *own* SQLAlchemy session
  (`BackgroundSessionLocal`, autoflush=False) and closes it when done —
  completely isolated from the request-scoped session.
* **Per-statement DB timeout**: a 15-second PostgreSQL statement_timeout is set
  on the background session so a slow query never holds a connection forever.
* **Warm-cache short-circuit**: if the cache is already populated (e.g. user
  refreshed the page), the worker exits immediately without touching the DB.
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Set

from sqlalchemy import text

from config.cache import get_cached

logger = logging.getLogger(__name__)


# ── Dedicated background thread pool ─────────────────────────────────────────
# Max 3 workers keeps background I/O pressure low.
_preload_executor = ThreadPoolExecutor(
    max_workers=3,
    thread_name_prefix="lms-preload",
)

# ── Per-user in-flight deduplication ─────────────────────────────────────────
# Prevents stacking duplicate preloads for the same user when they log in
# multiple times in quick succession.
_in_flight: Set[int] = set()
_in_flight_lock = threading.Lock()

# ── Global DB concurrency cap ─────────────────────────────────────────────────
# Even if 3 threads are available, only 2 run heavy DB reads at once.
# This leaves connection-pool slots free for normal request traffic.
_db_semaphore = threading.Semaphore(2)


# ─────────────────────────────────────────────────────────────────────────────
# Internal worker
# ─────────────────────────────────────────────────────────────────────────────

def _do_preload(user_id: int) -> None:
    """
    Worker function executed inside the thread pool.

    Opens a dedicated read-optimised DB session, calls
    ``LMSService.get_dashboard_all``, and lets the service's own caching
    layer store the result.  The session is always closed in the finally
    block, even on error.
    """
    cache_key = f"lms:dashboard_all:{user_id}"

    # ── 1. Short back-off: let the login response reach the client first ──────
    time.sleep(0.4)

    # ── 2. Warm-cache short-circuit ───────────────────────────────────────────
    if get_cached(cache_key) is not None:
        logger.debug("[LMS preload] Cache already warm for user %d — skipping.", user_id)
        _release_in_flight(user_id)
        return

    # ── 3. Acquire global DB semaphore (blocks if 2 preloads already running) ─
    acquired = _db_semaphore.acquire(blocking=True, timeout=30)
    if not acquired:
        logger.warning(
            "[LMS preload] Timed-out waiting for DB semaphore (user %d).", user_id
        )
        _release_in_flight(user_id)
        return

    db = None
    try:
        # ── 4. Open a background-optimised session ───────────────────────────
        # Import here to avoid circular imports at module load time.
        from config.database_orm import BackgroundSessionLocal

        db = BackgroundSessionLocal()

        # Set a per-session statement timeout (PostgreSQL) so a slow query
        # cannot hold the connection indefinitely.
        # The SET is session-scoped; the session is closed afterwards anyway.
        try:
            db.execute(text("SET statement_timeout = '15000'"))  # 15 seconds
        except Exception:
            # Non-fatal: some DB drivers / older PG versions may not support this
            pass

        # ── 5. Run the actual dashboard aggregation ───────────────────────────
        from services.lms_service import LMSService

        svc = LMSService(db)
        svc.get_dashboard_all(user_id)

        logger.info("[LMS preload] Dashboard pre-warmed for user %d.", user_id)

    except Exception as exc:
        # Never let an exception crash the background thread.
        logger.error(
            "[LMS preload] Pre-warm failed for user %d: %s", user_id, exc, exc_info=True
        )
    finally:
        if db is not None:
            try:
                db.close()
            except Exception:
                pass
        _db_semaphore.release()
        _release_in_flight(user_id)


def _release_in_flight(user_id: int) -> None:
    """Remove *user_id* from the in-flight set (helper to avoid duplication)."""
    with _in_flight_lock:
        _in_flight.discard(user_id)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def schedule_lms_preload(user_id: int) -> None:
    """
    Schedule an asynchronous LMS dashboard pre-warm for *user_id*.

    This function is **non-blocking** and safe to call from an async route
    handler or a FastAPI ``BackgroundTask``.  The actual heavy DB work runs
    inside the dedicated ``_preload_executor`` thread pool and is fully
    isolated from the main request-handling threads.

    Duplicate calls for the same user while a preload is already in-flight
    are silently ignored.

    Args:
        user_id: Primary key of the user whose dashboard should be pre-warmed.
    """
    with _in_flight_lock:
        if user_id in _in_flight:
            logger.debug(
                "[LMS preload] Already in-flight for user %d — ignoring duplicate.", user_id
            )
            return
        _in_flight.add(user_id)

    try:
        _preload_executor.submit(_do_preload, user_id)
        logger.debug("[LMS preload] Submitted pre-warm task for user %d.", user_id)
    except Exception as exc:
        logger.error(
            "[LMS preload] Could not submit task for user %d: %s", user_id, exc
        )
        _release_in_flight(user_id)
