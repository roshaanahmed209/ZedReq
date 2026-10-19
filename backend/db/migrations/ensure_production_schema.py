"""
Idempotent production schema reconciliation.

Runs fast ADD COLUMN IF NOT EXISTS / CREATE TABLE IF NOT EXISTS statements so
ORM models and narrow SQL endpoints stay aligned after deploys. Safe to repeat.
"""
from __future__ import annotations

from config.database import Database, get_connection_params

# Keep statements small and fast — startup has a 20s thread timeout per init task.
SCHEMA_STATEMENTS = [
    # users — ORM User expects these; missing columns → 500 on profile/feed/messaging
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20) NOT NULL DEFAULT 'email'",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS synthetic_profile_views INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_url TEXT",
    # description — profile / feed joins
    "ALTER TABLE description ADD COLUMN IF NOT EXISTS role VARCHAR(150)",
    "ALTER TABLE description ADD COLUMN IF NOT EXISTS company VARCHAR(150)",
    "ALTER TABLE description ADD COLUMN IF NOT EXISTS location VARCHAR(150)",
    "ALTER TABLE description ADD COLUMN IF NOT EXISTS industry VARCHAR(100)",
    "ALTER TABLE description ADD COLUMN IF NOT EXISTS profile_version INTEGER DEFAULT 1",
    "ALTER TABLE description ADD COLUMN IF NOT EXISTS city VARCHAR(150)",
    "ALTER TABLE description ADD COLUMN IF NOT EXISTS country VARCHAR(150)",
    # payment — subscription GET/PUT
    "ALTER TABLE payment ADD COLUMN IF NOT EXISTS subscription_id INTEGER",
    "ALTER TABLE payment ADD COLUMN IF NOT EXISTS paddle_subscription_id VARCHAR(255)",
    "ALTER TABLE payment ADD COLUMN IF NOT EXISTS paddle_price_id VARCHAR(255)",
    "CREATE INDEX IF NOT EXISTS idx_payment_paddle_subscription_id ON payment(paddle_subscription_id)",
    # subscription tables — quota + plan selection
    """CREATE TABLE IF NOT EXISTS subscription_plans (
        plan_id SERIAL PRIMARY KEY,
        plan_name VARCHAR(50) UNIQUE NOT NULL,
        ai_messages_per_month INTEGER NOT NULL DEFAULT 0,
        course_enrollments_per_month INTEGER NOT NULL DEFAULT 0,
        interview_sessions_per_month INTEGER NOT NULL DEFAULT 0,
        interview_max_duration_seconds INTEGER NOT NULL DEFAULT 60,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    )""",
    """CREATE TABLE IF NOT EXISTS user_subscriptions (
        subscription_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE REFERENCES users(uid) ON DELETE CASCADE,
        plan_id INTEGER NOT NULL REFERENCES subscription_plans(plan_id) ON DELETE RESTRICT,
        status VARCHAR(20) NOT NULL DEFAULT 'active',
        assigned_by VARCHAR(50) NOT NULL DEFAULT 'system',
        started_at TIMESTAMPTZ DEFAULT NOW(),
        expires_at TIMESTAMPTZ NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    )""",
    "CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan_id ON user_subscriptions(plan_id)",
    "CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status)",
    """CREATE TABLE IF NOT EXISTS usage_tracking (
        tracking_id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
        feature VARCHAR(50) NOT NULL,
        period_start DATE NOT NULL,
        usage_count INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE (user_id, feature, period_start)
    )""",
    "CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_feature ON usage_tracking(user_id, feature, period_start)",
]

PLAN_SEED_ROWS = [
    ("free", 30, 2, 1, 60),
    ("pro", 100, 3, 3, 60),
    ("premium", 500, 5, 5, 60),
    ("enterprise", -1, -1, -1, 600),
]


def run_migration() -> None:
    db = Database(get_connection_params())
    try:
        for sql in SCHEMA_STATEMENTS:
            try:
                db.execute(sql)
            except Exception as step_err:
                print(f"  [WARN] ensure_production_schema step skipped: {step_err}")

        for plan_name, ai, courses, interviews, duration in PLAN_SEED_ROWS:
            db.execute(
                """
                INSERT INTO subscription_plans (
                    plan_name, ai_messages_per_month, course_enrollments_per_month,
                    interview_sessions_per_month, interview_max_duration_seconds, is_active
                )
                VALUES (%s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (plan_name) DO NOTHING
                """,
                (plan_name, ai, courses, interviews, duration),
            )
    finally:
        db.close()


if __name__ == "__main__":
    print("Running ensure_production_schema...")
    run_migration()
    print("Done.")
