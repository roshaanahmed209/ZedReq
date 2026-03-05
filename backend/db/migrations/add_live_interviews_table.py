"""
Migration: Create live_interviews table for AI mock interview system
- Stores interview sessions with Tavus AI
- Tracks user performance and scores
- Manages attempt numbers per user-job pair
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
CREATE_LIVE_INTERVIEWS_TABLE = '''
CREATE TABLE IF NOT EXISTS live_interviews (
    interview_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    tavus_conversation_id VARCHAR(255),
    tavus_response JSONB,
    questions JSONB,
    user_responses JSONB,
    overall_score INTEGER,
    score_breakdown JSONB,
    feedback TEXT,
    riz_feedback JSONB,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

ADD_RIZ_FEEDBACK_COLUMN = '''
ALTER TABLE live_interviews 
ADD COLUMN IF NOT EXISTS riz_feedback JSONB;
'''

CREATE_LIVE_INTERVIEWS_INDEXES = '''
CREATE INDEX IF NOT EXISTS idx_live_interviews_user_id 
ON live_interviews(user_id);

CREATE INDEX IF NOT EXISTS idx_live_interviews_job_id 
ON live_interviews(job_id);

CREATE INDEX IF NOT EXISTS idx_live_interviews_user_job 
ON live_interviews(user_id, job_id);

CREATE INDEX IF NOT EXISTS idx_live_interviews_status 
ON live_interviews(status) 
WHERE status IN ('pending', 'in_progress');

CREATE INDEX IF NOT EXISTS idx_live_interviews_tavus_conversation_id 
ON live_interviews(tavus_conversation_id) 
WHERE tavus_conversation_id IS NOT NULL;
'''

def run_migration():
    """Run the migration to create live_interviews table"""
    db = Database(get_connection_params())
    
    print("=" * 60)
    print("Running Migration: Create live_interviews table")
    print("=" * 60)
    
    try:
        # Create table
        print("  [1/3] Creating live_interviews table...")
        db.execute(CREATE_LIVE_INTERVIEWS_TABLE)
        print("  [OK] live_interviews table created")
        
        # Add riz_feedback column (for existing tables that don't have it)
        print("  [2/3] Adding riz_feedback column (if missing)...")
        db.execute(ADD_RIZ_FEEDBACK_COLUMN)
        print("  [OK] riz_feedback column ensured")
        
        # Create indexes
        print("  [3/3] Creating indexes...")
        db.execute(CREATE_LIVE_INTERVIEWS_INDEXES)
        print("  [OK] Indexes created")
        
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
