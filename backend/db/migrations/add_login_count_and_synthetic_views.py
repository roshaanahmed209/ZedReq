"""
Migration: Add login_count and synthetic_profile_views to users table.

Powers the "first login shows 0 profile views, subsequent logins show
accumulating random numbers" behavior:
- login_count: number of successful logins (used to detect the first login)
- synthetic_profile_views: persisted, accumulating baseline added to real
  profile-view counts in the analytics summary
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

ADD_LOGIN_COUNT = '''
ALTER TABLE users
ADD COLUMN IF NOT EXISTS login_count INTEGER NOT NULL DEFAULT 0;
'''

ADD_SYNTHETIC_PROFILE_VIEWS = '''
ALTER TABLE users
ADD COLUMN IF NOT EXISTS synthetic_profile_views INTEGER NOT NULL DEFAULT 0;
'''


def run_migration():
    """Run the migration to add login_count and synthetic_profile_views columns"""
    db = Database(get_connection_params())

    print("=" * 60)
    print("Running Migration: Add login_count + synthetic_profile_views")
    print("=" * 60)

    try:
        print("  [1/2] Adding login_count column to users table...")
        db.execute(ADD_LOGIN_COUNT)
        print("  [OK] login_count column added")

        print("  [2/2] Adding synthetic_profile_views column to users table...")
        db.execute(ADD_SYNTHETIC_PROFILE_VIEWS)
        print("  [OK] synthetic_profile_views column added")

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
