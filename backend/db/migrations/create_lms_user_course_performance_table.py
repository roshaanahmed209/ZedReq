"""
Migration: Create lms_user_course_performance table
This table stores user performance metrics per course
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database_orm import engine, get_db
from sqlalchemy import text

# SQL to create the table
CREATE_TABLE_SQL = '''
CREATE TABLE IF NOT EXISTS lms_user_course_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    accuracy_percentage DECIMAL(5,2) DEFAULT 0.00,
    total_points_earned INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)
);
'''

# Indexes
CREATE_INDEXES_SQL = [
    'CREATE INDEX IF NOT EXISTS idx_lms_course_perf_user ON lms_user_course_performance(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_course_perf_course ON lms_user_course_performance(course_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_course_perf_user_course ON lms_user_course_performance(user_id, course_id)',
]


def run_migration():
    """Create the lms_user_course_performance table"""
    print("=" * 60)
    print("Creating lms_user_course_performance table...")
    print("=" * 60)
    
    db = next(get_db())
    
    try:
        # Create table
        print("\n[1/2] Creating table...")
        db.execute(text(CREATE_TABLE_SQL))
        db.commit()
        print("  [OK] Table created successfully")
        
        # Create indexes
        print("\n[2/2] Creating indexes...")
        for index_sql in CREATE_INDEXES_SQL:
            try:
                db.execute(text(index_sql))
                index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
                print(f"  [OK] Created index: {index_name}")
            except Exception as e:
                print(f"  [WARN] Index creation: {e}")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
