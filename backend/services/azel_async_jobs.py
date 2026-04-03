"""
Background Azel (LMS question generation) jobs for long-running pipelines.

Avoids HTTP proxy timeouts (e.g. Render ~100s) by returning 202 immediately and
letting the client poll for completion.

Jobs are persisted to the ``azel_jobs`` PostgreSQL table so they survive
service restarts and redeployments (previously in-memory only, which caused
404 "Job not found" errors when Render restarted mid-job).
"""
from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers — thin wrappers around the azel_jobs DB table
# ---------------------------------------------------------------------------

def _db():
    """Return a fresh Database connection (caller must .close() it)."""
    from config.database import get_connection_params, Database
    return Database(get_connection_params())


def create_job(user_id: int) -> str:
    job_id = str(uuid.uuid4())
    db = _db()
    try:
        db.execute(
            """
            INSERT INTO azel_jobs (job_id, user_id, status, created_at, updated_at)
            VALUES (%s, %s, 'queued', NOW(), NOW())
            """,
            (job_id, user_id),
        )
    finally:
        db.close()
    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    db = _db()
    try:
        row = db.fetch_one(
            "SELECT job_id, user_id, status, response, error, created_at FROM azel_jobs WHERE job_id = %s",
            (job_id,),
        )
        return dict(row) if row else None
    finally:
        db.close()


def job_belongs_to_user(job_id: str, user_id: int) -> bool:
    db = _db()
    try:
        row = db.fetch_one(
            "SELECT 1 FROM azel_jobs WHERE job_id = %s AND user_id = %s",
            (job_id, user_id),
        )
        return row is not None
    finally:
        db.close()


def _set_job(job_id: str, **kwargs) -> None:
    if not kwargs:
        return
    db = _db()
    try:
        # Build SET clause dynamically for the fields that are provided
        allowed = {"status", "response", "error"}
        sets = []
        values = []
        for key, val in kwargs.items():
            if key not in allowed:
                continue
            sets.append(f"{key} = %s")
            # response must be stored as JSON
            if key == "response" and val is not None and not isinstance(val, str):
                val = json.dumps(val)
            values.append(val)
        if not sets:
            return
        sets.append("updated_at = NOW()")
        values.append(job_id)
        db.execute(
            f"UPDATE azel_jobs SET {', '.join(sets)} WHERE job_id = %s",
            tuple(values),
        )
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Background job runner
# ---------------------------------------------------------------------------

def run_azel_job(
    job_id: str,
    user_id: int,
    course_id: int,
    section_id: Optional[int],
    level: str,
    course_title: str,
    rate_limit_payload: Dict[str, Any],
) -> None:
    """Runs in a daemon thread; persists job state to DB when done."""
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
        message = "Course context processed successfully" if success else "Course context processing completed with errors"

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
