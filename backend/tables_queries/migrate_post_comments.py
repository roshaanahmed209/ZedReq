"""
Migration: post_comment table (comments + optional media_url)
============================================================
Idempotent: safe to run on new or existing databases.

Run from the backend directory:
    python -m tables_queries.migrate_post_comments

Or run the SQL file with psql:
    psql "$DATABASE_URL" -f tables_queries/migrate_post_comments.sql
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import init_database

STATEMENTS = [
    """
CREATE TABLE IF NOT EXISTS post_comment (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES post(post_id) ON DELETE CASCADE,
    uid INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    body TEXT NOT NULL DEFAULT '',
    media_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",
    "ALTER TABLE post_comment ADD COLUMN IF NOT EXISTS media_url TEXT;",
    "ALTER TABLE post_comment ALTER COLUMN body SET DEFAULT '';",
    "CREATE INDEX IF NOT EXISTS idx_post_comment_post ON post_comment (post_id);",
    "CREATE INDEX IF NOT EXISTS idx_post_comment_post_created ON post_comment (post_id, created_at DESC);",
]


def run_migration():
    print("[*] Connecting to database...")
    db = init_database()

    print("\n[*] Applying post_comment migration...")
    print("=" * 50)

    try:
        for i, sql in enumerate(STATEMENTS, 1):
            stmt = sql.strip()
            db.execute(stmt)
            preview = stmt.split("\n")[0][:70]
            print(f"  [OK] Step {i}/{len(STATEMENTS)}: {preview}...")

        print("\n" + "=" * 50)
        print("[OK] post_comment migration finished.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
