"""
Migration: Add job_link column to job_postings table
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
ADD_JOB_LINK_COLUMN = '''
ALTER TABLE job_postings 
ADD COLUMN IF NOT EXISTS job_link TEXT;
'''

def run_migration():
    """Run the migration to add job_link column"""
    db = Database(get_connection_params())
    
    print("=" * 60)
    print("Running Migration: Add job_link to job_postings")
    print("=" * 60)
    
    try:
        db.execute(ADD_JOB_LINK_COLUMN)
        print("  [OK] Added job_link column to job_postings table")
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
