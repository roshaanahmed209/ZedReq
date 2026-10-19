"""Background tasks for profile views — Zed context / LLM off the HTTP critical path."""
import logging

from config.database_orm import SessionLocal
from services.profile_analytics_service import ProfileAnalyticsService

logger = logging.getLogger(__name__)


def run_profile_view_context_update(viewer_id: int, profile_user_id: int) -> None:
    """
    Intended for FastAPI BackgroundTasks (runs after the response is sent).
    Uses a dedicated DB session; failures are logged only.
    """
    if not viewer_id or not profile_user_id or viewer_id == profile_user_id:
        return
    db = SessionLocal()
    try:
        try:
            ProfileAnalyticsService(db).track_profile_view(
                user_id=profile_user_id,
                viewer_id=viewer_id,
                source="direct",
            )
        except Exception as e:
            logger.warning(
                "Background profile view analytics failed viewer=%s profile=%s: %s",
                viewer_id,
                profile_user_id,
                e,
            )
        from services.context_updater import ContextUpdater

        updater = ContextUpdater(db)
        updater.update_context_from_action(
            user_id=viewer_id,
            action="view",
            entity_type="profile",
            entity_id=profile_user_id,
        )
    except Exception as e:
        logger.error(
            "Background profile context update failed viewer=%s profile=%s: %s",
            viewer_id,
            profile_user_id,
            e,
            exc_info=True,
        )
    finally:
        db.close()
