"""
Migration: Add ip_address and user_agent columns to deleted_user_archive.
These capture the network context of every purge for audit purposes.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

ALTER_SQL = """
ALTER TABLE deleted_user_archive
    ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45),
    ADD COLUMN IF NOT EXISTS user_agent TEXT;
"""


def run_migration():
    db = Database(get_connection_params())
    print("=" * 60)
    print("Migration: alter_deleted_user_archive_add_ip_ua")
    print("=" * 60)
    try:
        db.execute(ALTER_SQL)
        print("  [OK] Columns added")
        print("Migration completed successfully.")
    except Exception as e:
        print(f"  [ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
