"""
Migration: Add subscription_id FK column to payment table

Links the payment table to user_subscriptions so that when a plan changes,
both tables stay in sync via a single-transaction write path.

Usage:
    python backend/db/migrations/add_payment_subscription_id.py

Rollback:
    python backend/db/migrations/add_payment_subscription_id.py --rollback
"""
import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
ADD_SUBSCRIPTION_ID_COLUMN = '''
ALTER TABLE payment
ADD COLUMN IF NOT EXISTS subscription_id INTEGER REFERENCES user_subscriptions(subscription_id) ON DELETE SET NULL;
'''

ADD_SUBSCRIPTION_ID_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_payment_subscription_id ON payment(subscription_id);
'''

# Rollback SQL
DROP_SUBSCRIPTION_ID_COLUMN = '''
ALTER TABLE payment
DROP COLUMN IF EXISTS subscription_id;
'''


def check_column_exists(db):
    """Check if subscription_id column already exists on payment table"""
    try:
        result = db.fetch_one("""
            SELECT COUNT(*) as count
            FROM information_schema.columns
            WHERE table_name = 'payment'
            AND column_name = 'subscription_id'
        """)
        return result and result[0] >= 1
    except Exception:
        return False


def run_migration(db):
    """Add subscription_id column to payment table"""
    if check_column_exists(db):
        print("  [SKIP] subscription_id column already exists on payment table")
        return True

    try:
        print("  Adding subscription_id column to payment table...")
        db.execute(ADD_SUBSCRIPTION_ID_COLUMN)
        print("  Creating index idx_payment_subscription_id...")
        db.execute(ADD_SUBSCRIPTION_ID_INDEX)
        print("  [OK] subscription_id column added successfully")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to add subscription_id column: {e}")
        return False


def run_rollback(db):
    """Remove subscription_id column from payment table"""
    if not check_column_exists(db):
        print("  [SKIP] subscription_id column does not exist on payment table")
        return True

    try:
        print("  Dropping subscription_id column from payment table...")
        db.execute(DROP_SUBSCRIPTION_ID_COLUMN)
        print("  [OK] subscription_id column removed successfully")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to remove subscription_id column: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add subscription_id FK to payment table')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()

    params = get_connection_params()
    db = Database(params)

    try:
        if args.rollback:
            print("Rolling back: remove subscription_id from payment...")
            run_rollback(db)
        else:
            print("Migrating: add subscription_id to payment...")
            run_migration(db)
    finally:
        db.close()
