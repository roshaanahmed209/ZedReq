"""Recommendation Cache Service - Manages cached job recommendations"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from config.database import get_database
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RecommendationCacheService:
    """Service for managing cached job recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_enabled = settings.RECOMMENDATION_CACHE_ENABLED
    
    def get_cached_recommendations(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached recommendations if they exist and are valid.
        
        Args:
            user_id: User ID
            
        Returns:
            Cached recommendations list if valid, None otherwise
        """
        if not self.cache_enabled:
            return None
        
        try:
            # Get user's current profile version
            profile_version = self._get_profile_version(user_id)
            if profile_version is None:
                return None
            
            # Get cached recommendations
            db_raw = get_database()
            query = """
            SELECT recommendations, cache_version, expires_at
            FROM user_job_recommendations_cache
            WHERE user_id = %s
            """
            
            result = db_raw.fetch_one(query, (user_id,))
            
            if not result:
                logger.debug(f"No cached recommendations found for user {user_id}")
                return None
            
            # Check if cache is valid (version matches and not expired)
            cache_version = result.get('cache_version', 0)
            expires_at = result.get('expires_at')
            
            # Check version match
            if cache_version != profile_version:
                logger.debug(f"Cache version mismatch for user {user_id}: cache={cache_version}, profile={profile_version}")
                return None
            
            # Check expiration
            if expires_at:
                expires_dt = expires_at if isinstance(expires_at, datetime) else datetime.fromisoformat(str(expires_at))
                if datetime.now() > expires_dt:
                    logger.debug(f"Cache expired for user {user_id}")
                    return None
            
            # Cache is valid
            recommendations = result.get('recommendations')
            if isinstance(recommendations, str):
                import json
                recommendations = json.loads(recommendations)
            
            logger.debug(f"Returning cached recommendations for user {user_id} (version {cache_version})")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting cached recommendations for user {user_id}: {e}", exc_info=True)
            return None
    
    def store_recommendations(
        self, 
        user_id: int, 
        recommendations: List[Dict[str, Any]],
        ttl_hours: Optional[int] = None
    ) -> bool:
        """
        Store recommendations in cache.
        
        Args:
            user_id: User ID
            recommendations: List of recommendation dictionaries
            ttl_hours: Optional TTL in hours (uses default from settings if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.cache_enabled:
            return False
        
        try:
            # Get current profile version
            profile_version = self._get_profile_version(user_id)
            if profile_version is None:
                logger.warning(f"Cannot store cache for user {user_id}: profile version not found")
                return False
            
            # Calculate expiration time
            expires_at = None
            if ttl_hours or settings.RECOMMENDATION_CACHE_TTL_HOURS:
                ttl = ttl_hours or settings.RECOMMENDATION_CACHE_TTL_HOURS
                expires_at = datetime.now() + timedelta(hours=ttl)
            
            # Convert recommendations to JSON
            import json
            recommendations_json = json.dumps(recommendations)
            
            # Store in cache (upsert)
            db_raw = get_database()
            query = """
            INSERT INTO user_job_recommendations_cache 
                (user_id, recommendations, cache_version, updated_at, expires_at)
            VALUES (%s, %s::jsonb, %s, CURRENT_TIMESTAMP, %s)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                recommendations = EXCLUDED.recommendations,
                cache_version = EXCLUDED.cache_version,
                updated_at = CURRENT_TIMESTAMP,
                expires_at = EXCLUDED.expires_at
            """
            
            db_raw.execute(query, (user_id, recommendations_json, profile_version, expires_at))
            
            logger.info(f"Stored {len(recommendations)} recommendations in cache for user {user_id} (version {profile_version})")
            return True
            
        except Exception as e:
            logger.error(f"Error storing cached recommendations for user {user_id}: {e}", exc_info=True)
            return False
    
    def invalidate_cache(self, user_id: int) -> bool:
        """
        Invalidate (delete) cached recommendations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db_raw = get_database()
            query = "DELETE FROM user_job_recommendations_cache WHERE user_id = %s"
            db_raw.execute(query, (user_id,))
            
            logger.info(f"Invalidated recommendation cache for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating cache for user {user_id}: {e}", exc_info=True)
            return False
    
    def is_cache_valid(self, user_id: int) -> bool:
        """
        Check if cache exists and is valid for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if cache is valid, False otherwise
        """
        cached = self.get_cached_recommendations(user_id)
        return cached is not None
    
    def _get_profile_version(self, user_id: int) -> Optional[int]:
        """
        Get current profile version for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Profile version or None if not found
        """
        try:
            from models.orm.user import User
            from models.orm.description import Description
            
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user or not user.description_id:
                return None
            
            description = self.db.query(Description).filter(Description.desc_id == user.description_id).first()
            if not description:
                return None
            
            return description.profile_version or 1
            
        except Exception as e:
            logger.error(f"Error getting profile version for user {user_id}: {e}", exc_info=True)
            return None
    
    def increment_profile_version(self, user_id: int) -> bool:
        """
        Increment profile version for a user (triggers cache invalidation).
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from models.orm.user import User
            from models.orm.description import Description
            
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user or not user.description_id:
                logger.warning(f"Cannot increment profile version for user {user_id}: description not found")
                return False
            
            description = self.db.query(Description).filter(Description.desc_id == user.description_id).first()
            if not description:
                return False
            
            # Increment version
            description.profile_version = (description.profile_version or 1) + 1
            self.db.commit()
            
            # Invalidate cache
            self.invalidate_cache(user_id)
            
            logger.info(f"Incremented profile version for user {user_id} to {description.profile_version}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error incrementing profile version for user {user_id}: {e}", exc_info=True)
            return False
