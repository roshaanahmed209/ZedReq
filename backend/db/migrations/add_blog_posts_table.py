"""
Migration: Create blog_posts table and seed one sample published post.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database import get_connection_params, Database

CREATE_BLOG_POSTS_TABLE = '''
CREATE TABLE IF NOT EXISTS blog_posts (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(220) NOT NULL UNIQUE,
    title VARCHAR(300) NOT NULL,
    excerpt TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    cover_image_url VARCHAR(500),
    author_name VARCHAR(120) NOT NULL DEFAULT 'ZedReq Team',
    tags JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    seo_title VARCHAR(300),
    seo_description TEXT,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
'''

CREATE_BLOG_POSTS_INDEXES = '''
CREATE INDEX IF NOT EXISTS idx_blog_posts_status ON blog_posts(status);
CREATE INDEX IF NOT EXISTS idx_blog_posts_published_at ON blog_posts(published_at DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_blog_posts_slug ON blog_posts(slug);
'''

SAMPLE_SLUG = "how-to-prepare-for-ai-mock-interviews"

SAMPLE_BODY = """## Why mock interviews matter

The gap between knowing your experience and articulating it under pressure is where most candidates lose offers. Mock interviews give you a low-stakes environment to practice structure, pacing, and follow-up answers before the real conversation.

## What makes AI mock interviews different

ZedReq mock interviews adapt to your target role and résumé. You get immediate feedback on clarity, relevance, and confidence — not just a generic question list. That means each session targets the gaps that actually show up in hiring loops.

## How to prepare in 30 minutes

1. **Review the job description** — highlight three responsibilities you can speak to with concrete examples.
2. **Pick one STAR story** — Situation, Task, Action, Result. Keep it under two minutes when spoken aloud.
3. **Run one mock on ZedReq** — treat it like a real call: quiet room, camera optional, no notes on screen.
4. **Read the feedback** — note one phrasing change and one content gap to fix before your next attempt.

## Common mistakes to avoid

- Answering the question you wish they had asked instead of the one they asked.
- Listing responsibilities without outcomes or metrics.
- Skipping the "why this company" thread — tie your motivation to their product or mission.

## Next steps

Publish your best answers into your ZedReq profile, share mock session highlights with mentors, and schedule another mock within 48 hours while the feedback is fresh. Consistency beats cramming."""

SEED_SAMPLE_POST = '''
INSERT INTO blog_posts (
    slug, title, excerpt, body, author_name, tags, status,
    seo_title, seo_description, published_at
)
SELECT
    %s, %s, %s, %s,
    'ZedReq Team',
    '["interviews", "career", "ai"]'::jsonb,
    'published',
    %s, %s,
    CURRENT_TIMESTAMP
WHERE NOT EXISTS (
    SELECT 1 FROM blog_posts WHERE slug = %s
);
'''


def run_migration():
    db = Database(get_connection_params())

    print("=" * 60)
    print("Running Migration: Create blog_posts table")
    print("=" * 60)

    try:
        print("  [1/3] Creating blog_posts table...")
        db.execute(CREATE_BLOG_POSTS_TABLE)
        print("  [OK] blog_posts table created")

        print("  [2/3] Creating indexes...")
        db.execute(CREATE_BLOG_POSTS_INDEXES)
        print("  [OK] Indexes created")

        print("  [3/3] Seeding sample published post...")
        sample_title = "How to Prepare for AI Mock Interviews"
        sample_excerpt = (
            "A practical 30-minute prep routine for ZedReq mock interviews: "
            "structure your stories, avoid common mistakes, and turn feedback into your next offer."
        )
        sample_seo_title = "How to Prepare for AI Mock Interviews | ZedReq Blog"
        sample_seo_desc = (
            "Learn a focused prep routine for AI mock interviews on ZedReq — "
            "STAR stories, feedback loops, and mistakes to avoid before your next hiring loop."
        )
        db.execute(
            SEED_SAMPLE_POST,
            (
                SAMPLE_SLUG,
                sample_title,
                sample_excerpt,
                SAMPLE_BODY,
                sample_seo_title,
                sample_seo_desc,
                SAMPLE_SLUG,
            ),
        )
        print("  [OK] Sample post seeded (if not already present)")

        print("=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"  [ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
