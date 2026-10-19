"""
Migration: Add azel_jobs table for persistent background job tracking.

Previously jobs were stored in an in-memory dict which was wiped on every
Render restart/redeploy, causing 404 "Job not found" errors for polling
clients when the service restarted mid-job.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

CREATE_AZEL_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS azel_jobs (
    job_id      TEXT PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    status      TEXT NOT NULL DEFAULT 'queued',
    response    JSONB,
    error       TEXT,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
"""

CREATE_AZEL_JOBS_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_azel_jobs_user_id    ON azel_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_azel_jobs_status     ON azel_jobs(status);
CREATE INDEX IF NOT EXISTS idx_azel_jobs_created_at ON azel_jobs(created_at);
"""


def run_migration():
    db = Database(get_connection_params())
    print("=" * 60)
    print("Running Migration: add_azel_jobs_table")
    print("=" * 60)
    try:
        print("  [1/2] Creating azel_jobs table...")
        db.execute(CREATE_AZEL_JOBS_TABLE)
        print("  [OK]  azel_jobs table created")

        print("  [2/2] Creating indexes...")
        db.execute(CREATE_AZEL_JOBS_INDEXES)
        print("  [OK]  Indexes created")

        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
