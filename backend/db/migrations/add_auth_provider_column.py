"""
Migration: Add auth_provider column to users table

Tracks whether a user signed up via email/password or a third-party provider
(currently 'email' or 'google'). Defaults to 'email' for all existing rows.

Usage:
    python backend/db/migrations/add_auth_provider_column.py

Rollback:
    python backend/db/migrations/add_auth_provider_column.py --rollback
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

ADD_COLUMN = """
ALTER TABLE users
ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) NOT NULL DEFAULT 'email';
"""

DROP_COLUMN = """
ALTER TABLE users
DROP COLUMN IF EXISTS auth_provider;
"""

CHECK_SQL = """
SELECT COUNT(*) AS count
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'auth_provider'
"""


def column_exists(db):
    try:
        result = db.fetch_one(CHECK_SQL)
        if result:
            count = result.get('count', 0) if isinstance(result, dict) else result[0]
            return int(count) >= 1
        return False
    except Exception as e:
        print(f"  [WARN] Could not check existing column: {e}")
        return False


def run_migration(rollback=False):
    db = Database(get_connection_params())

    print("=" * 60)
    if rollback:
        print("Running Rollback: Remove auth_provider column from users")
    else:
        print("Running Migration: Add auth_provider column to users")
    print("=" * 60)

    try:
        if rollback:
            print("  [1/2] Checking if auth_provider column exists...")
            if not column_exists(db):
                print("  [INFO] Column does not exist. Nothing to rollback.")
                print("=" * 60)
                print("Rollback completed (no changes needed)")
                print("=" * 60)
                return
            print("  [2/2] Dropping auth_provider column...")
            db.execute(DROP_COLUMN)
            print("  [OK] auth_provider column removed successfully")
        else:
            print("  [1/2] Checking if auth_provider column already exists...")
            if column_exists(db):
                print("  [INFO] Column already exists. Skipping migration.")
                print("=" * 60)
                print("Migration completed (no changes needed)")
                print("=" * 60)
                return
            print("  [2/2] Adding auth_provider column to users table...")
            db.execute(ADD_COLUMN)
            print("  [OK] auth_provider column added successfully")

        print("=" * 60)
        print("Completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add or remove auth_provider column from users table')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()
    run_migration(rollback=args.rollback)
