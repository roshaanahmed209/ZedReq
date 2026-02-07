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
        # Install pgvector extension
        print("  [1/5] Installing pgvector extension...")
        db.execute(INSTALL_PGVECTOR_EXTENSION)
        print("  [OK] pgvector extension installed")
        
        # Add embedding column to job_postings
        print("  [2/5] Adding embedding column to job_postings...")
        db.execute(ADD_EMBEDDING_COLUMN)
        print("  [OK] Embedding column added")
        
        # Create user_job_preferences table
        print("  [3/5] Creating user_job_preferences table...")
        db.execute(CREATE_USER_JOB_PREFERENCES_TABLE)
        print("  [OK] user_job_preferences table created")
        
        # Create vector index
        print("  [4/5] Creating vector index for embeddings...")
        try:
            db.execute(CREATE_VECTOR_INDEX)
            print("  [OK] Vector index created")
        except Exception as e:
            print(f"  [WARNING] Vector index creation failed (may need existing data): {e}")
            print("  [INFO] You can create the index later when there are embeddings")
        
        # Create preference indexes
        print("  [5/5] Creating indexes for user_job_preferences...")
        db.execute(CREATE_PREFERENCES_INDEXES)
        print("  [OK] Preference indexes created")
        
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
