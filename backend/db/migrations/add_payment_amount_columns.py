"""
Migration: Add payment amount, currency, payment_date, and transaction_id columns to payment table

Adds columns to track actual payment amounts and transaction details.
This enables revenue tracking directly in the payment table.

Usage:
    python backend/db/migrations/add_payment_amount_columns.py

Rollback:
    python backend/db/migrations/add_payment_amount_columns.py --rollback
"""
import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

# Migration SQL
ADD_PAYMENT_AMOUNT_COLUMNS = '''
ALTER TABLE payment
ADD COLUMN IF NOT EXISTS amount NUMERIC(10, 2),
ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'USD',
ADD COLUMN IF NOT EXISTS payment_date TIMESTAMP,
ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS last_payment_date TIMESTAMP;
'''

ADD_TRANSACTION_ID_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_payment_transaction_id ON payment(transaction_id);
'''

ADD_PAYMENT_DATE_INDEX = '''
CREATE INDEX IF NOT EXISTS idx_payment_payment_date ON payment(payment_date);
'''

# Rollback SQL
DROP_PAYMENT_AMOUNT_COLUMNS = '''
ALTER TABLE payment
DROP COLUMN IF EXISTS amount,
DROP COLUMN IF EXISTS currency,
DROP COLUMN IF EXISTS payment_date,
DROP COLUMN IF EXISTS transaction_id,
DROP COLUMN IF EXISTS last_payment_date;
'''


def check_columns_exist(db):
    """Check if payment amount columns already exist on payment table"""
    try:
        result = db.fetch_one("""
            SELECT COUNT(*) as count
            FROM information_schema.columns
            WHERE table_name = 'payment'
            AND column_name IN ('amount', 'currency', 'payment_date', 'transaction_id', 'last_payment_date')
        """)
        return result and result[0] >= 5
    except Exception:
        return False


def run_migration(db):
    """Add payment amount columns to payment table"""
    if check_columns_exist(db):
        print("  [SKIP] Payment amount columns already exist on payment table")
        return True

    try:
        print("  Adding payment amount columns to payment table...")
        db.execute(ADD_PAYMENT_AMOUNT_COLUMNS)
        print("  Creating index idx_payment_transaction_id...")
        db.execute(ADD_TRANSACTION_ID_INDEX)
        print("  Creating index idx_payment_payment_date...")
        db.execute(ADD_PAYMENT_DATE_INDEX)
        print("  [OK] Payment amount columns added successfully")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to add payment amount columns: {e}")
        return False


def run_rollback(db):
    """Remove payment amount columns from payment table"""
    if not check_columns_exist(db):
        print("  [SKIP] Payment amount columns do not exist on payment table")
        return True

    try:
        print("  Dropping payment amount columns from payment table...")
        # Drop indexes first
        try:
            db.execute("DROP INDEX IF EXISTS idx_payment_transaction_id;")
            db.execute("DROP INDEX IF EXISTS idx_payment_payment_date;")
        except Exception:
            pass  # Indexes might not exist
        db.execute(DROP_PAYMENT_AMOUNT_COLUMNS)
        print("  [OK] Payment amount columns removed successfully")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to remove payment amount columns: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Add payment amount columns to payment table')
    parser.add_argument('--rollback', action='store_true', help='Rollback the migration')
    args = parser.parse_args()

    params = get_connection_params()
    db = Database(params)

    try:
        if args.rollback:
            print("Rolling back: remove payment amount columns from payment...")
            run_rollback(db)
        else:
            print("Migrating: add payment amount columns to payment...")
            run_migration(db)
    finally:
        db.close()
