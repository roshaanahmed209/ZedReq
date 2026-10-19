-- Prefer the full migration (table + indexes + alters):
--   ../tables_queries/migrate_post_comments.sql
--   or: python -m tables_queries.migrate_post_comments

-- Minimal upgrade if post_comment already exists without media_url:
ALTER TABLE post_comment ADD COLUMN IF NOT EXISTS media_url TEXT;
ALTER TABLE post_comment ALTER COLUMN body SET DEFAULT '';
