"""
Migration Script: Add runtime_context Column to Users_context Table
Adds:
- runtime_context column to existing users_context table
- runtime_context column stores button click context in list format (JSONB)
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# MIGRATION SQL
# ============================================================================

# Add runtime_context column to existing users_context table
ADD_RUNTIME_CONTEXT_COLUMN = '''
ALTER TABLE users_context 
ADD COLUMN IF NOT EXISTS runtime_context JSONB;
'''


def get_db():
    """Get database connection"""
    from config.database import get_connection_params, Database
    params = get_connection_params()
    return Database(params)


def run_migration(db=None):
    """Run the migration to add runtime_context column to users_context table"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("=" * 60)
    print("Running Users_context Column Migration")
    print("Adding runtime_context column...")
    print("=" * 60)
    
    try:
        # Add runtime_context column
        print("\n[1/1] Adding runtime_context column to users_context table...")
        db.execute(ADD_RUNTIME_CONTEXT_COLUMN)
        print("  [OK] runtime_context column added successfully")
        
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
    """Rollback the migration (drop runtime_context column)"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("=" * 60)
    print("Rolling back Users_context Column Migration...")
    print("Dropping runtime_context column...")
    print("=" * 60)
    
    try:
        # Drop column
        print("\n[1/1] Dropping runtime_context column from users_context table...")
        db.execute("ALTER TABLE users_context DROP COLUMN IF EXISTS runtime_context;")
        print("  [OK] runtime_context column dropped")
        
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
        "-- Users_context Column Migration",
        "-- Run this SQL to add runtime_context column to users_context table\n",
        "-- Add runtime_context column",
        ADD_RUNTIME_CONTEXT_COLUMN,
    ]
    
    return "\n".join(sql_parts)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Users_context column migration - Add runtime_context column')
    parser.add_argument('--rollback', action='store_true', help='Rollback migration (drop table)')
    parser.add_argument('--print-sql', action='store_true', help='Print SQL instead of executing')
    
    args = parser.parse_args()
    
    if args.print_sql:
        print(get_migration_sql())
    elif args.rollback:
        rollback_migration()
    else:
        run_migration()
