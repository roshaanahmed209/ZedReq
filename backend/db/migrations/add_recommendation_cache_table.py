"""
Migration: Add recommendation cache table and profile version tracking
- Create user_job_recommendations_cache table
- Add profile_version column to description table
- Create indexes for performance
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
CREATE_RECOMMENDATION_CACHE_TABLE = '''
CREATE TABLE IF NOT EXISTS user_job_recommendations_cache (
    user_id INTEGER PRIMARY KEY REFERENCES users(uid) ON DELETE CASCADE,
    recommendations JSONB NOT NULL,
    cache_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
'''

CREATE_CACHE_INDEXES = '''
CREATE INDEX IF NOT EXISTS idx_recommendations_cache_user_id 
ON user_job_recommendations_cache(user_id);

CREATE INDEX IF NOT EXISTS idx_recommendations_cache_expires 
ON user_job_recommendations_cache(expires_at) 
WHERE expires_at IS NOT NULL;
'''

ADD_PROFILE_VERSION_COLUMN = '''
ALTER TABLE description 
ADD COLUMN IF NOT EXISTS profile_version INTEGER DEFAULT 1;
'''

CREATE_PROFILE_VERSION_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_description_profile_version 
ON description(profile_version) 
WHERE profile_version IS NOT NULL;
'''

def run_migration():
    """Run the migration to add recommendation cache table and profile version tracking"""
    db = Database(get_connection_params())
    
    print("=" * 60)
    print("Running Migration: Add recommendation cache table and profile version")
    print("=" * 60)
    
    try:
        # Create recommendation cache table
        print("  [1/4] Creating user_job_recommendations_cache table...")
        db.execute(CREATE_RECOMMENDATION_CACHE_TABLE)
        print("  [OK] Recommendation cache table created")
        
        # Create cache indexes
        print("  [2/4] Creating indexes for recommendation cache...")
        db.execute(CREATE_CACHE_INDEXES)
        print("  [OK] Cache indexes created")
        
        # Add profile_version column to description table
        print("  [3/4] Adding profile_version column to description table...")
        db.execute(ADD_PROFILE_VERSION_COLUMN)
        print("  [OK] Profile version column added")
        
        # Create profile version index
        print("  [4/4] Creating index for profile_version...")
        db.execute(CREATE_PROFILE_VERSION_INDEX)
        print("  [OK] Profile version index created")
        
        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Update profile services to increment profile_version on changes")
        print("2. Implement recommendation cache service")
        print("3. Update recommendation service to use cache")
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
