"""
Migration: Paddle Billing — payment.paddle_* columns + paddle_webhook_events idempotency table.

Usage:
    python backend/db/migrations/add_paddle_billing_columns.py
"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

MIGRATION_STEPS = [
    "ALTER TABLE payment ADD COLUMN IF NOT EXISTS paddle_subscription_id VARCHAR(255)",
    "ALTER TABLE payment ADD COLUMN IF NOT EXISTS paddle_price_id VARCHAR(255)",
    "CREATE INDEX IF NOT EXISTS idx_payment_paddle_subscription_id ON payment(paddle_subscription_id)",
    """CREATE TABLE IF NOT EXISTS paddle_webhook_events (
    event_id VARCHAR(128) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)""",
    "CREATE INDEX IF NOT EXISTS idx_paddle_webhook_events_created ON paddle_webhook_events(created_at)",
]

ROLLBACK_STEPS = [
    "DROP TABLE IF EXISTS paddle_webhook_events",
    "ALTER TABLE payment DROP COLUMN IF EXISTS paddle_price_id",
    "ALTER TABLE payment DROP COLUMN IF EXISTS paddle_subscription_id",
]


def run_migration(db: Database) -> bool:
    try:
        for stmt in MIGRATION_STEPS:
            db.execute(stmt + ";")
        print("  [OK] Paddle billing columns / webhook events table")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def run_rollback(db: Database) -> bool:
    try:
        for stmt in ROLLBACK_STEPS:
            db.execute(stmt + ";")
        print("  [OK] Rollback paddle billing migration")
        return True
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    db = Database(get_connection_params())
    try:
        if args.rollback:
            run_rollback(db)
        else:
            run_migration(db)
    finally:
        db.close()
