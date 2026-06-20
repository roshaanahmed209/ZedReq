"""
Script to backfill post embeddings for posts missing embeddings.
Processes posts in batches to avoid API rate limits.

Doubles as the one-off backfill for existing posts and the nightly batch job
(see utils/scheduler.py:run_post_embedding_backfill).

Traffic-friendly by design: it runs on a background scheduler thread (off the
request path), throttles between items/batches, and uses a short-lived DB
session per batch so it never holds a pooled connection (or an idle transaction)
for the whole run — the connection is released during the throttle sleeps.
"""
import os
import sys
import time
from typing import List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.database_orm import get_db
from models.orm.post import Post
from utils.post_embeddings import generate_post_embedding, store_post_embedding
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Per-item / per-batch throttle so the job stays gentle on OpenAI and the DB pool.
ITEM_DELAY_SECONDS = float(os.environ.get('POST_EMBEDDING_BACKFILL_ITEM_DELAY', 0.1))
BATCH_DELAY_SECONDS = float(os.environ.get('POST_EMBEDDING_BACKFILL_BATCH_DELAY', 2.0))


def _missing_post_ids(limit: Optional[int]) -> List[int]:
    """Lightweight pass: collect ids of non-deleted posts without embeddings, then release the session."""
    db = next(get_db())
    try:
        query = (
            db.query(Post.post_id)
            .filter(Post.not_deleted(), Post.embedding.is_(None))
            .order_by(Post.post_id)
        )
        if limit:
            query = query.limit(limit)
        return [row[0] for row in query.all()]
    finally:
        db.close()


def _process_batch(batch_ids: List[int]) -> tuple:
    """Embed + store one batch in its own short-lived session. Returns (successful, failed)."""
    successful = 0
    failed = 0
    db = next(get_db())
    try:
        posts = db.query(Post).filter(Post.post_id.in_(batch_ids)).all()
        for post in posts:
            try:
                logger.debug(f"Generating embedding for post {post.post_id}")
                embedding = generate_post_embedding(post)
                if embedding and store_post_embedding(post.post_id, embedding, db):
                    successful += 1
                else:
                    failed += 1
                    logger.warning(f"Failed to embed/store post {post.post_id}")
            except Exception as e:
                failed += 1
                logger.error(f"Error processing post {post.post_id}: {e}", exc_info=True)
            # Throttle between items (connection still light; only this session is held)
            time.sleep(ITEM_DELAY_SECONDS)
    finally:
        db.close()  # Release the pooled connection before the inter-batch sleep
    return successful, failed


def backfill_post_embeddings(
    batch_size: int = None,
    limit: Optional[int] = None,
    dry_run: bool = False
) -> dict:
    """
    Backfill embeddings for posts missing embeddings.

    Args:
        batch_size: Number of posts to process per batch (default from settings)
        limit: Maximum number of posts to process (None = all)
        dry_run: If True, only count posts without generating embeddings

    Returns:
        Dictionary with statistics
    """
    batch_size = batch_size or settings.POST_EMBEDDING_BACKFILL_BATCH_SIZE

    post_ids = _missing_post_ids(limit)
    total_posts = len(post_ids)
    logger.info(f"Found {total_posts} posts missing embeddings")

    if total_posts == 0 or dry_run:
        if dry_run:
            logger.info(f"[DRY RUN] Would process {total_posts} posts in batches of {batch_size}")
        return {
            'total_posts': total_posts,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'dry_run': dry_run,
        }

    processed = 0
    successful = 0
    failed = 0
    total_batches = (total_posts + batch_size - 1) // batch_size

    for i in range(0, total_posts, batch_size):
        batch_ids = post_ids[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_ids)} posts)")

        ok, bad = _process_batch(batch_ids)
        successful += ok
        failed += bad
        processed += len(batch_ids)

        # Longer delay between batches (no DB connection held during this sleep)
        if i + batch_size < total_posts:
            logger.info(f"Batch {batch_num} complete. Waiting {BATCH_DELAY_SECONDS}s before next batch...")
            time.sleep(BATCH_DELAY_SECONDS)

    logger.info(
        f"Backfill complete: {processed} processed, {successful} successful, {failed} failed"
    )

    return {
        'total_posts': total_posts,
        'processed': processed,
        'successful': successful,
        'failed': failed,
        'dry_run': False,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Backfill post embeddings')
    parser.add_argument('--batch-size', type=int, default=None, help='Batch size (default from settings)')
    parser.add_argument('--limit', type=int, default=None, help='Maximum number of posts to process')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (only count, no processing)')

    args = parser.parse_args()

    print("=" * 60)
    print("Post Embedding Backfill Script")
    print("=" * 60)

    result = backfill_post_embeddings(
        batch_size=args.batch_size,
        limit=args.limit,
        dry_run=args.dry_run
    )

    print("\nResults:")
    print(f"  Total posts missing embeddings: {result['total_posts']}")
    if not result['dry_run']:
        print(f"  Processed: {result['processed']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
    print("=" * 60)
