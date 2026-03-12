"""
Migration: Add evaluation/performance columns to lms_user_section_progress table
Run this script to add questions_answered, correct_answers, accuracy_percentage,
and total_points_earned columns for section-scoped evaluation tracking.

Usage:
    python backend/db/migrations/add_section_performance_columns.py

Rollback:
    python backend/db/migrations/add_section_performance_columns.py --rollback
"""
import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
ADD_SECTION_PERF_COLUMNS = '''
ALTER TABLE lms_user_section_progress
ADD COLUMN IF NOT EXISTS questions_answered INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS correct_answers INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS accuracy_percentage NUMERIC(5,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS total_points_earned INTEGER DEFAULT 0;
'''

# Rollback SQL
DROP_SECTION_PERF_COLUMNS = '''
ALTER TABLE lms_user_section_progress
DROP COLUMN IF EXISTS questions_answered,
DROP COLUMN IF EXISTS correct_answers,
DROP COLUMN IF EXISTS accuracy_percentage,
DROP COLUMN IF EXISTS total_points_earned;
'''


def run_migration():
    """Add section performance columns"""
    print("Running migration: add_section_performance_columns")
    try:
        db = Database(get_connection_params())
        db.execute(ADD_SECTION_PERF_COLUMNS)
        db.close()
        print("Migration completed successfully!")
        print("Added columns: questions_answered, correct_answers, accuracy_percentage, total_points_earned")
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)


def run_rollback():
    """Remove section performance columns"""
    print("Rolling back migration: add_section_performance_columns")
    try:
        db = Database(get_connection_params())
        db.execute(DROP_SECTION_PERF_COLUMNS)
        db.close()
        print("Rollback completed successfully!")
    except Exception as e:
        print(f"Rollback failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add section performance columns migration')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()

    if args.rollback:
        run_rollback()
    else:
        run_migration()
