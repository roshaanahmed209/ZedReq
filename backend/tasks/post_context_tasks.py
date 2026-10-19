"""Background tasks for post likes — Zed context / LLM off the HTTP critical path."""
import logging

from config.database_orm import SessionLocal

logger = logging.getLogger(__name__)


def run_post_like_context_update(user_id: int, post_id: int) -> None:
    """
    Runs after the like response is sent. Summarizes the liked post for Zed preferences.
    """
    if not user_id or not post_id:
        return
    db = SessionLocal()
    try:
        from services.context_updater import ContextUpdater

        ContextUpdater(db).update_context_from_action(
            user_id=user_id,
            action="like",
            entity_type="post",
            entity_id=post_id,
        )
    except Exception as e:
        logger.error(
            "Background post-like context update failed user=%s post=%s: %s",
            user_id,
            post_id,
            e,
            exc_info=True,
        )
    finally:
        db.close()
