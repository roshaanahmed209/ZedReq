"""
Background Azel (LMS question generation) jobs for long-running pipelines.

Avoids HTTP proxy timeouts (e.g. Render ~100s) by returning 202 immediately and
letting the client poll for completion.
"""
from __future__ import annotations

import logging
import threading
import time
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}
_MAX_JOBS = 200
_JOB_TTL_SECONDS = 3600


def _prune_locked(now: float) -> None:
    if len(_jobs) <= _MAX_JOBS:
        return
    # Drop oldest by created_at
    sorted_ids = sorted(_jobs.keys(), key=lambda jid: _jobs[jid].get("created_at", 0))
    for jid in sorted_ids[: max(0, len(_jobs) - _MAX_JOBS + 50)]:
        if now - _jobs[jid].get("created_at", now) > _JOB_TTL_SECONDS:
            _jobs.pop(jid, None)


def create_job(user_id: int) -> str:
    job_id = str(uuid.uuid4())
    now = time.time()
    with _lock:
        _prune_locked(now)
        _jobs[job_id] = {
            "user_id": user_id,
            "status": "queued",
            "created_at": now,
            "result": None,
            "error": None,
            "response": None,
        }
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        row = _jobs.get(job_id)
        if row is None:
            return None
        return dict(row)


def job_belongs_to_user(job_id: str, user_id: int) -> bool:
    with _lock:
        row = _jobs.get(job_id)
        return row is not None and row.get("user_id") == user_id


def _set_job(job_id: str, **kwargs) -> None:
    with _lock:
        if job_id not in _jobs:
            return
        _jobs[job_id].update(kwargs)


def run_azel_job(
    job_id: str,
    user_id: int,
    course_id: int,
    section_id: Optional[int],
    level: str,
    course_title: str,
    rate_limit_payload: Dict[str, Any],
) -> None:
    """Runs in a daemon thread; updates job record when done."""
    try:
        _set_job(job_id, status="running")
        from agents.Azel_agent import get_azel_agent

        agent = get_azel_agent()
        result = agent.process_course_context(
            user_id=user_id,
            course_id=course_id,
            section_id=section_id,
            level=level,
            course_title=course_title,
        )
        success = bool(result.get("success"))
        if success:
            message = "Course context processed successfully"
        else:
            message = "Course context processing completed with errors"

        response_body = {
            "message": message,
            "result": result,
            "success": success,
            "rate_limit": rate_limit_payload,
        }
        _set_job(
            job_id,
            status="completed",
            response=response_body,
            result=result,
            error=result.get("error"),
        )
        logger.info(
            "[AZEL-JOB] job_id=%s user_id=%s course_id=%s completed success=%s questions_saved=%s",
            job_id,
            user_id,
            course_id,
            success,
            result.get("questions_saved"),
        )
    except Exception as e:
        logger.error("[AZEL-JOB] job_id=%s failed: %s", job_id, e, exc_info=True)
        _set_job(
            job_id,
            status="failed",
            error=str(e),
            response={
                "message": "An unexpected error occurred while processing the course.",
                "result": {"success": False, "error": str(e)},
                "success": False,
                "rate_limit": rate_limit_payload,
            },
        )


def spawn_azel_job_thread(
    job_id: str,
    user_id: int,
    course_id: int,
    section_id: Optional[int],
    level: str,
    course_title: str,
    rate_limit_payload: Dict[str, Any],
) -> None:
    t = threading.Thread(
        target=run_azel_job,
        args=(job_id, user_id, course_id, section_id, level, course_title, rate_limit_payload),
        daemon=True,
        name=f"azel-job-{job_id[:8]}",
    )
    t.start()
