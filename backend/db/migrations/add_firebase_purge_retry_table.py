"""
Migration: Create firebase_purge_retries table.
Tracks failed Firebase Realtime Database cleanup attempts after user deletion,
so a background scheduler can retry them until they succeed.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS firebase_purge_retries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_attempt_at TIMESTAMPTZ,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    succeeded_at TIMESTAMPTZ
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_firebase_purge_retries_pending
ON firebase_purge_retries(user_id)
WHERE succeeded_at IS NULL;
"""


def run_migration():
    db = Database(get_connection_params())
    print("=" * 60)
    print("Migration: firebase_purge_retries")
    print("=" * 60)
    try:
        print("  [1/2] Creating table...")
        db.execute(CREATE_TABLE)
        print("  [OK] Table created")
        print("  [2/2] Creating indexes...")
        db.execute(CREATE_INDEXES)
        print("  [OK] Indexes created")
        print("Migration completed successfully.")
    except Exception as e:
        print(f"  [ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
