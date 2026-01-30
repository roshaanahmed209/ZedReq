"""
Standalone Migration: Create Job Portal Tables
This script connects directly to the database without using the config system.
It reads environment variables directly using dotenv.
"""
import os
import sys

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Try psycopg3 first, fall back to psycopg2
try:
    import psycopg
    PSYCOPG_VERSION = 3
except ImportError:
    import psycopg2
    PSYCOPG_VERSION = 2

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
# DATABASE CONNECTION
# ============================================================================

def get_connection():
    """Get database connection from environment variables"""
    # Check for DATABASE_URL first
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if PSYCOPG_VERSION == 3:
            return psycopg.connect(database_url)
        else:
            return psycopg2.connect(database_url)
    
    # Otherwise use individual parameters
    params = {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': int(os.environ.get('POSTGRES_PORT', 5432)),
        'dbname': os.environ.get('POSTGRES_DB', 'ZedReq'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', ''),
    }
    
    if PSYCOPG_VERSION == 3:
        return psycopg.connect(**params)
    else:
        return psycopg2.connect(**params)


# ============================================================================
# MIGRATION FUNCTIONS
# ============================================================================

def run_migration():
    """Run the job tables migration"""
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
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
                cursor.execute(sql)
                print(f"  [OK] Created table: {table_name}")
            except Exception as e:
                print(f"  [ERROR] Error creating {table_name}: {e}")
        
        # Create indexes
        print("-" * 60)
        print("Creating indexes...")
        
        for index_sql in INDEXES:
            try:
                cursor.execute(index_sql)
                index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
                print(f"  [OK] Created index: {index_name}")
            except Exception as e:
                print(f"  [ERROR] Error creating index: {e}")
        
        print("=" * 60)
        print("Job Portal Migration Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"  [FATAL ERROR] Migration failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def rollback_migration():
    """Rollback the job tables migration (drop tables)"""
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("=" * 60)
        print("Rolling back Job Portal Migration...")
        print("=" * 60)
        
        # Drop in reverse order (due to foreign keys)
        tables = ["job_saved", "job_applications", "job_postings"]
        
        for table_name in tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
                print(f"  [OK] Dropped table: {table_name}")
            except Exception as e:
                print(f"  [ERROR] Error dropping {table_name}: {e}")
        
        print("=" * 60)
        print("Rollback Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"  [FATAL ERROR] Rollback failed: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Job Portal Migration (Standalone)')
    parser.add_argument('--rollback', action='store_true', help='Rollback migration (drop tables)')
    
    args = parser.parse_args()
    
    if args.rollback:
        confirm = input("⚠️  Are you sure you want to drop all job tables? (yes/no): ")
        if confirm.lower() == 'yes':
            rollback_migration()
        else:
            print("Cancelled.")
    else:
        run_migration()
