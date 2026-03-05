"""
User Preferences Service
Manages user job preferences for recommendations
"""
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from config.database import get_database


class UserPreferencesService:
    """Service for managing user job preferences"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        Get user job preferences.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with user preferences (empty dict if not found)
        """
        db_raw = get_database()
        
        query = """
        SELECT 
            user_id,
            preferred_location,
            preferred_job_type,
            preferred_remote,
            salary_expectation_min,
            salary_expectation_max,
            experience_level,
            created_at,
            updated_at
        FROM user_job_preferences
        WHERE user_id = %s
        """
        
        result = db_raw.fetch_one(query, (user_id,))
        
        if result:
            return {
                'user_id': result['user_id'],
                'preferred_location': result.get('preferred_location'),
                'preferred_job_type': result.get('preferred_job_type'),
                'preferred_remote': result.get('preferred_remote'),
                'salary_expectation_min': result.get('salary_expectation_min'),
                'salary_expectation_max': result.get('salary_expectation_max'),
                'experience_level': result.get('experience_level'),
                'created_at': result.get('created_at'),
                'updated_at': result.get('updated_at')
            }
        
        return {}
    
    def create_or_update_preferences(
        self, 
        user_id: int, 
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Create or update user job preferences.
        
        Args:
            user_id: User ID
            preferences: Dictionary with preference fields:
                - preferred_location (str, optional)
                - preferred_job_type (str, optional)
                - preferred_remote (bool, optional)
                - salary_expectation_min (int, optional)
                - salary_expectation_max (int, optional)
                - experience_level (str, optional)
        
        Returns:
            True if successful, False otherwise
        """
        db_raw = get_database()
        
        # Build update query
        query = """
        INSERT INTO user_job_preferences (
            user_id,
            preferred_location,
            preferred_job_type,
            preferred_remote,
            salary_expectation_min,
            salary_expectation_max,
            experience_level,
            updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
        )
        ON CONFLICT (user_id) 
        DO UPDATE SET
            preferred_location = EXCLUDED.preferred_location,
            preferred_job_type = EXCLUDED.preferred_job_type,
            preferred_remote = EXCLUDED.preferred_remote,
            salary_expectation_min = EXCLUDED.salary_expectation_min,
            salary_expectation_max = EXCLUDED.salary_expectation_max,
            experience_level = EXCLUDED.experience_level,
            updated_at = CURRENT_TIMESTAMP
        """
        
        try:
            db_raw.execute(
                query,
                (
                    user_id,
                    preferences.get('preferred_location'),
                    preferences.get('preferred_job_type'),
                    preferences.get('preferred_remote'),
                    preferences.get('salary_expectation_min'),
                    preferences.get('salary_expectation_max'),
                    preferences.get('experience_level')
                )
            )
            
            # Invalidate recommendation cache since preferences affect recommendations
            try:
                from services.recommendation_cache_service import RecommendationCacheService
                cache_service = RecommendationCacheService(self.db)
                cache_service.increment_profile_version(user_id)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")
                # Don't fail preference update if cache invalidation fails
            
            return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create/update preferences for user {user_id}: {e}")
            return False
