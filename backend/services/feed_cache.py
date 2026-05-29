"""Feed cache invalidation helpers (Redis-backed via FeedService)."""
from sqlalchemy.orm import Session

from services.feed_service import FeedService
from utils.logger import setup_logger

logger = setup_logger(__name__)


def invalidate_feed_for_author(db: Session, author_id: int) -> None:
    """Clear first-page feed cache for author and all followers."""
    if not author_id:
        return
    try:
        feed = FeedService(db)
        feed.invalidate_user_feed(author_id)
        feed.invalidate_followers_feed(author_id)
    except Exception as e:
        logger.warning("Feed cache invalidation failed for author %s: %s", author_id, e)


def invalidate_feed_for_users(db: Session, *user_ids: int) -> None:
    """Clear first-page feed cache for each user (e.g. after connect/disconnect)."""
    seen = set()
    for uid in user_ids:
        if not uid or uid in seen:
            continue
        seen.add(uid)
        try:
            FeedService(db).invalidate_user_feed(uid)
        except Exception as e:
            logger.warning("Feed cache invalidation failed for user %s: %s", uid, e)
