"""
Migration: Add pgvector support for job recommendations
- Install pgvector extension
- Add embedding column to job_postings table
- Create user_job_preferences table
- Create vector indexes for performance
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
INSTALL_PGVECTOR_EXTENSION = '''
CREATE EXTENSION IF NOT EXISTS vector;
'''

ADD_EMBEDDING_COLUMN = '''
ALTER TABLE job_postings 
ADD COLUMN IF NOT EXISTS embedding vector(3072);
'''

CREATE_USER_JOB_PREFERENCES_TABLE = '''
CREATE TABLE IF NOT EXISTS user_job_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(uid) ON DELETE CASCADE,
    preferred_location TEXT,
    preferred_job_type VARCHAR(50),
    preferred_remote BOOLEAN,
    salary_expectation_min INTEGER,
    salary_expectation_max INTEGER,
    experience_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

CREATE_VECTOR_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_job_embeddings 
ON job_postings 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
'''

CREATE_PREFERENCES_INDEXES = '''
CREATE INDEX IF NOT EXISTS idx_user_job_preferences_user_id 
ON user_job_preferences(user_id);

CREATE INDEX IF NOT EXISTS idx_user_job_preferences_location 
ON user_job_preferences(preferred_location) 
WHERE preferred_location IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_user_job_preferences_job_type 
ON user_job_preferences(preferred_job_type) 
WHERE preferred_job_type IS NOT NULL;
'''

def run_migration():
    """Run the migration to add pgvector support for job recommendations"""
    db = Database(get_connection_params())
    
    print("=" * 60)
    print("Running Migration: Add pgvector support for job recommendations")
    print("=" * 60)
    
    try:
        # Check if pgvector extension is available
        print("  [1/5] Checking for pgvector extension...")
        try:
            db.execute(INSTALL_PGVECTOR_EXTENSION)
            print("  [OK] pgvector extension installed/available")
            pgvector_available = True
        except Exception as e:
            print(f"  [WARNING] pgvector extension not available: {e}")
            print("  [INFO] Skipping embedding column. Install pgvector to enable embeddings.")
            print("  [INFO] To install pgvector:")
            print("         - On Windows: Download from https://github.com/pgvector/pgvector/releases")
            print("         - On Linux: sudo apt-get install postgresql-XX-pgvector")
            print("         - On macOS: brew install pgvector")
            print("         - Or use Docker image: pgvector/pgvector:pg16")
            print("  [INFO] Continuing with other parts of migration...")
            pgvector_available = False
        
        # Add embedding column to job_postings (only if pgvector is available)
        if pgvector_available:
            print("  [2/5] Adding embedding column to job_postings...")
            try:
                db.execute(ADD_EMBEDDING_COLUMN)
                print("  [OK] Embedding column added")
            except Exception as e:
                print(f"  [WARNING] Failed to add embedding column: {e}")
                pgvector_available = False
        else:
            print("  [2/5] Skipping embedding column (pgvector not available)")
        
        # Create user_job_preferences table (always create, doesn't require pgvector)
        print("  [3/5] Creating user_job_preferences table...")
        db.execute(CREATE_USER_JOB_PREFERENCES_TABLE)
        print("  [OK] user_job_preferences table created")
        
        # Create vector index (only if pgvector is available)
        if pgvector_available:
            print("  [4/5] Creating vector index for embeddings...")
            try:
                db.execute(CREATE_VECTOR_INDEX)
                print("  [OK] Vector index created")
            except Exception as e:
                print(f"  [WARNING] Vector index creation failed (may need existing data): {e}")
                print("  [INFO] You can create the index later when there are embeddings")
        else:
            print("  [4/5] Skipping vector index (pgvector not available)")
        
        # Create preference indexes (always create, doesn't require pgvector)
        print("  [5/5] Creating indexes for user_job_preferences...")
        db.execute(CREATE_PREFERENCES_INDEXES)
        print("  [OK] Preference indexes created")
        
        print("=" * 60)
        if pgvector_available:
            print("Migration completed successfully!")
        else:
            print("Migration completed (with warnings - pgvector not available)")
            print("Install pgvector and re-run to enable embedding columns.")
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
