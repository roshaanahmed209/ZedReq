"""
Migration Script: Add Settings related columns
Adds:
- two_factor_enabled to users table
- resume to description table
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# MIGRATION SQL
# ============================================================================

# Add two_factor_enabled column to users table
ADD_2FA_COLUMN = '''
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS two_factor_enabled BOOLEAN DEFAULT FALSE;
'''

# Add resume column to description table
ADD_RESUME_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS resume TEXT;
'''


def get_db():
    """Get database connection"""
    from config.database import get_connection_params, Database
    params = get_connection_params()
    return Database(params)


def run_migration(db=None):
    """Run the migration to add settings columns"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("=" * 60)
    print("Running Settings Column Migration")
    print("Adding two_factor_enabled to users and resume to description...")
    print("=" * 60)
    
    try:
        # Add columns
        print("\n[1/2] Adding two_factor_enabled column to users table...")
        db.execute(ADD_2FA_COLUMN)
        print("  [OK] two_factor_enabled column added successfully")
        
        print("\n[2/2] Adding resume column to description table...")
        db.execute(ADD_RESUME_COLUMN)
        print("  [OK] resume column added successfully")
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        if close_db:
            db.close()


def rollback_migration(db=None):
    """Rollback the migration (drop columns)"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("=" * 60)
    print("Rolling back Settings Column Migration...")
    print("=" * 60)
    
    try:
        # Drop columns
        print("\n[1/2] Dropping two_factor_enabled from users table...")
        db.execute("ALTER TABLE users DROP COLUMN IF EXISTS two_factor_enabled;")
        print("  [OK] two_factor_enabled dropped")
        
        print("\n[2/2] Dropping resume from description table...")
        db.execute("ALTER TABLE description DROP COLUMN IF EXISTS resume;")
        print("  [OK] resume dropped")
        
        print("\n" + "=" * 60)
        print("Rollback completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Rollback failed: {e}")
        raise
    finally:
        if close_db:
            db.close()


def get_migration_sql():
    """Get all migration SQL as a single string"""
    sql_parts = [
        "-- Settings Column Migration",
        "-- Run this SQL to add settings related columns\n",
        ADD_2FA_COLUMN,
        ADD_RESUME_COLUMN,
    ]
    
    return "\n".join(sql_parts)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Settings column migration')
    parser.add_argument('--rollback', action='store_true', help='Rollback migration')
    parser.add_argument('--print-sql', action='store_true', help='Print SQL instead of executing')
    
    args = parser.parse_args()
    
    if args.print_sql:
        print(get_migration_sql())
    elif args.rollback:
        rollback_migration()
    else:
        run_migration()
