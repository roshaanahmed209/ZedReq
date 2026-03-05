"""
Migration: Create Job Portal Tables
- job_postings: Store job listings
- job_applications: Track applications
- job_saved: Bookmarked jobs
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import get_database

# ============================================================================
# TABLE CREATION SQL
# ============================================================================

JOB_POSTINGS_TABLE = '''
CREATE TABLE IF NOT EXISTS job_postings (
    job_id SERIAL PRIMARY KEY,
    poster_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    
    -- Core Job Info
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    company_name VARCHAR(150),
    location VARCHAR(150),
    
    -- Type & Requirements
    job_type VARCHAR(50) DEFAULT 'full-time',
    is_remote BOOLEAN DEFAULT FALSE,
    experience_level VARCHAR(50),
    skills_required TEXT,
    
    -- Salary
    salary_min INTEGER,
    salary_max INTEGER,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

JOB_APPLICATIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS job_applications (
    application_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    applicant_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    
    status VARCHAR(30) DEFAULT 'pending',
    cover_letter TEXT,
    match_score INTEGER,
    
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(job_id, applicant_id)
);
'''

JOB_SAVED_TABLE = '''
CREATE TABLE IF NOT EXISTS job_saved (
    saved_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(job_id, user_id)
);
'''

# ============================================================================
# INDEXES
# ============================================================================

INDEXES = [
    # Job Postings Indexes
    'CREATE INDEX IF NOT EXISTS idx_job_postings_poster ON job_postings(poster_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_status ON job_postings(status)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_created ON job_postings(created_at DESC)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_location ON job_postings(location)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_remote ON job_postings(is_remote) WHERE is_remote = TRUE',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_type ON job_postings(job_type)',
    
    # Job Applications Indexes
    'CREATE INDEX IF NOT EXISTS idx_job_applications_job ON job_applications(job_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_applications_applicant ON job_applications(applicant_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_applications_status ON job_applications(status)',
    
    # Job Saved Indexes
    'CREATE INDEX IF NOT EXISTS idx_job_saved_user ON job_saved(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_saved_job ON job_saved(job_id)',
]

# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def run_migration():
    """Run the job tables migration"""
    db = get_database()
    
    print("=" * 60)
    print("Running Job Portal Migration...")
    print("=" * 60)
    
    tables = [
        ("job_postings", JOB_POSTINGS_TABLE),
        ("job_applications", JOB_APPLICATIONS_TABLE),
        ("job_saved", JOB_SAVED_TABLE),
    ]
    
    # Create tables
    for table_name, sql in tables:
        try:
            db.execute(sql)
            print(f"  [OK] Created table: {table_name}")
        except Exception as e:
            print(f"  [ERROR] Error creating {table_name}: {e}")
    
    # Create indexes
    print("-" * 60)
    print("Creating indexes...")
    
    for index_sql in INDEXES:
        try:
            db.execute(index_sql)
            index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
            print(f"  [OK] Created index: {index_name}")
        except Exception as e:
            print(f"  [ERROR] Error creating index: {e}")
    
    print("=" * 60)
    print("Job Portal Migration Complete!")
    print("=" * 60)


def rollback_migration():
    """Rollback the job tables migration (drop tables)"""
    db = get_database()
    
    print("=" * 60)
    print("Rolling back Job Portal Migration...")
    print("=" * 60)
    
    # Drop in reverse order (due to foreign keys)
    tables = ["job_saved", "job_applications", "job_postings"]
    
    for table_name in tables:
        try:
            db.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            print(f"  [OK] Dropped table: {table_name}")
        except Exception as e:
            print(f"  [ERROR] Error dropping {table_name}: {e}")
    
    print("=" * 60)
    print("Rollback Complete!")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Job Portal Migration')
    parser.add_argument('--rollback', action='store_true', help='Rollback migration (drop tables)')
    
    args = parser.parse_args()
    
    if args.rollback:
        rollback_migration()
    else:
        run_migration()
