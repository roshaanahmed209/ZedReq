"""
Migration: Create deleted_user_archive table
Stores full JSON snapshots when a user account is purged from operational tables.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

CREATE_DELETED_USER_ARCHIVE = """
CREATE TABLE IF NOT EXISTS deleted_user_archive (
    id BIGSERIAL PRIMARY KEY,
    original_uid INTEGER NOT NULL,
    user_email VARCHAR(150),
    deleted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletion_source VARCHAR(20) NOT NULL,
    admin_id INTEGER,
    reason TEXT,
    user_snapshot JSONB NOT NULL,
    description_snapshot JSONB,
    subscriptions_snapshot JSONB,
    payments_snapshot JSONB
);
"""

CREATE_DELETED_USER_ARCHIVE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_deleted_user_archive_original_uid
ON deleted_user_archive(original_uid);

CREATE INDEX IF NOT EXISTS idx_deleted_user_archive_user_email
ON deleted_user_archive(user_email);

CREATE INDEX IF NOT EXISTS idx_deleted_user_archive_deleted_at
ON deleted_user_archive(deleted_at DESC);
"""


def run_migration():
    db = Database(get_connection_params())
    print("=" * 60)
    print("Migration: deleted_user_archive")
    print("=" * 60)
    try:
        print("  [1/2] Creating table...")
        db.execute(CREATE_DELETED_USER_ARCHIVE)
        print("  [OK] Table created")
        print("  [2/2] Creating indexes...")
        db.execute(CREATE_DELETED_USER_ARCHIVE_INDEXES)
        print("  [OK] Indexes created")
        print("Migration completed successfully.")
    except Exception as e:
        print(f"  [ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
