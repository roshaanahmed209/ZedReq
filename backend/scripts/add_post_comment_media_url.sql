-- Run once on existing databases that already have post_comment (before media_url existed).
ALTER TABLE post_comment ADD COLUMN IF NOT EXISTS media_url TEXT;
ALTER TABLE post_comment ALTER COLUMN body SET DEFAULT '';
