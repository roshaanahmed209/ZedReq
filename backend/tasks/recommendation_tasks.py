"""
Background tasks for recommendation generation
Can be used with FastAPI BackgroundTasks or APScheduler
"""
from typing import Optional
from sqlalchemy.orm import Session

from services.recommendation_service import RecommendationService
from services.recommendation_cache_service import RecommendationCacheService
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_and_cache_recommendations(
    user_id: int,
    db: Session,
    limit: int = 10
) -> bool:
    """
    Background task to generate and cache recommendations for a user.
    This is non-blocking and can be called after profile updates.
    
    Args:
        user_id: User ID
        db: Database session
        limit: Number of recommendations to generate
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Background task: Generating recommendations for user {user_id}")
        
        # Check if cache is already valid (avoid unnecessary work)
        cache_service = RecommendationCacheService(db)
        if cache_service.is_cache_valid(user_id):
            logger.debug(f"Cache already valid for user {user_id}, skipping generation")
            return True
        
        # Generate recommendations (this will automatically cache them)
        recommendation_service = RecommendationService(db)
        recommendations = recommendation_service.get_recommendations(user_id, limit=limit)
        
        if recommendations:
            logger.info(f"Background task: Generated and cached {len(recommendations)} recommendations for user {user_id}")
            return True
        else:
            logger.warning(f"Background task: No recommendations generated for user {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"Background task: Error generating recommendations for user {user_id}: {e}", exc_info=True)
        return False


def precompute_recommendations_for_active_users(
    db: Session,
    days_active: int = 7,
    limit: int = 10
) -> dict:
    """
    Precompute recommendations for users who have been active recently.
    This can be run as a scheduled job.
    
    Args:
        db: Database session
        days_active: Number of days to look back for active users
        limit: Number of recommendations per user
        
    Returns:
        Dictionary with statistics
    """
    try:
        from datetime import datetime, timedelta
        from models.orm.user import User
        
        cutoff_date = datetime.now() - timedelta(days=days_active)
        
        # Get active users (users who logged in recently)
        active_users = (
            db.query(User.uid)
            .filter(User.last_login >= cutoff_date)
            .all()
        )
        
        total_users = len(active_users)
        logger.info(f"Precomputing recommendations for {total_users} active users")
        
        successful = 0
        failed = 0
        
        for (user_id,) in active_users:
            try:
                success = generate_and_cache_recommendations(user_id, db, limit=limit)
                if success:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                logger.error(f"Error precomputing for user {user_id}: {e}")
        
        logger.info(f"Precomputation complete: {successful} successful, {failed} failed out of {total_users} users")
        
        return {
            'total_users': total_users,
            'successful': successful,
            'failed': failed
        }
        
    except Exception as e:
        logger.error(f"Error in precomputation task: {e}", exc_info=True)
        return {
            'total_users': 0,
            'successful': 0,
            'failed': 0,
            'error': str(e)
        }
