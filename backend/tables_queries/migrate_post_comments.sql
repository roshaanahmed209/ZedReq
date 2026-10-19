-- Post comments (text + optional image URL) — idempotent migration for PostgreSQL.
--
-- Run with psql, e.g.:
--   psql "$DATABASE_URL" -f tables_queries/migrate_post_comments.sql
-- From backend directory:
--   psql "$DATABASE_URL" -f backend/tables_queries/migrate_post_comments.sql
--
-- Or use: python -m tables_queries.migrate_post_comments
-- (from the backend directory, with .env / DB settings loaded)

-- New databases: full table
CREATE TABLE IF NOT EXISTS post_comment (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES post(post_id) ON DELETE CASCADE,
    uid INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    body TEXT NOT NULL DEFAULT '',
    media_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Existing installs that already had post_comment without media_url / default body
ALTER TABLE post_comment ADD COLUMN IF NOT EXISTS media_url TEXT;
ALTER TABLE post_comment ALTER COLUMN body SET DEFAULT '';

CREATE INDEX IF NOT EXISTS idx_post_comment_post ON post_comment (post_id);
CREATE INDEX IF NOT EXISTS idx_post_comment_post_created ON post_comment (post_id, created_at DESC);
