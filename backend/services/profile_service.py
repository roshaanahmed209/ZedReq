"""Profile Service - User profile operations using SQLAlchemy ORM"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models.orm import User, Description, Connection, ConnectionRequest, UsersContext
from utils.errors import NotFoundError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ProfileService:
    """Profile business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get complete user profile with description info"""
        try:
            user = (
                self.db.query(User)
                .filter(User.uid == user_id)
                .first()
            )
            
            if not user:
                return None
            
            # Get base user info
            # Convert stored profile path to full URL using current environment
            from utils.profile_url import get_full_profile_url
            full_profile_url = get_full_profile_url(user.profile_url) if user.profile_url else None
            
            result = {
                'id': user.uid,
                'uid': user.uid,
                'username': user.username or '',
                'name': user.name or '',
                'email': user.user_email or '',
                'user_email': user.user_email or '',
                'profile_url': full_profile_url,  # Full URL generated dynamically
                'profile_path': user.profile_url,  # Also include path for reference
                'two_factor_enabled': user.two_factor_enabled or False,  # Include 2FA status
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'profile_pic': None,
                'cover_pic': None,
                'short_desc': None,
                'about': None,
                'skills': None,
                'certificates': None,
                'current_status': None,
                'role': None,
                'company': None,
                'location': None,
                'industry': None
            }
            
            # Get description if available
            if user.description_id:
                description = (
                    self.db.query(Description)
                    .filter(Description.desc_id == user.description_id)
                    .first()
                )
                if description:
                    result.update({
                        'profile_pic': description.profile_pic,
                        'cover_pic': description.cover_pic,
                        'short_desc': description.short_desc,
                        'about': description.about,
                        'skills': description.skills,
                        'certificates': description.certificates,
                        'current_status': description.current_status,
                        'role': description.role,
                        'company': description.company,
                        'location': description.location,
                        'industry': description.industry
                    })
            
            # Extract interests from runtime_context (latest entry containing "interests")
            result['interests'] = None  # Default to None
            try:
                users_context = (
                    self.db.query(UsersContext)
                    .filter(UsersContext.user_id == user_id)
                    .first()
                )
                if users_context and users_context.runtime_context:
                    # Look for the most recent entry containing interests
                    if isinstance(users_context.runtime_context, list):
                        for item in reversed(users_context.runtime_context):  # Start from most recent
                            if isinstance(item, dict) and 'content' in item:
                                content = item['content']
                                # Check if this content looks like interests (contains common patterns)
                                # Interests are typically comma-separated and relatively short
                                if isinstance(content, str) and ',' in content and len(content) < 1000:
                                    # Likely interests string (comma-separated, reasonable length)
                                    result['interests'] = content.strip()
                                    break
            except Exception as e:
                logger.warning(f"Error extracting interests from runtime_context: {e}")
            
            return result
        except Exception as e:
            logger.error(f"Get user profile error: {e}", exc_info=True)
            raise
    
    def get_connection_status(self, current_user_id: int, target_user_id: int) -> str:
        """
        Get connection status between two users
        Returns: 'connected', 'pending', or 'none'
        """
        try:
            # Check if already connected
            connection = (
                self.db.query(Connection)
                .filter(
                    or_(
                        and_(
                            Connection.follower_uid == current_user_id,
                            Connection.followed_uid == target_user_id
                        ),
                        and_(
                            Connection.follower_uid == target_user_id,
                            Connection.followed_uid == current_user_id
                        )
                    )
                )
                .first()
            )
            
            if connection:
                return 'connected'
            
            # Check for pending connection request
            pending_request = (
                self.db.query(ConnectionRequest)
                .filter(
                    and_(
                        ConnectionRequest.status == 'pending',
                        or_(
                            and_(
                                ConnectionRequest.sender_id == current_user_id,
                                ConnectionRequest.receiver_id == target_user_id
                            ),
                            and_(
                                ConnectionRequest.sender_id == target_user_id,
                                ConnectionRequest.receiver_id == current_user_id
                            )
                        )
                    )
                )
                .first()
            )
            
            if pending_request:
                return 'pending'
            
            return 'none'
        except Exception as e:
            logger.error(f"Get connection status error: {e}", exc_info=True)
            return 'none'
    
    def get_profile_with_connection_status(
        self, 
        target_user_id: int, 
        current_user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get user profile with connection status
        Returns profile data with connection_status field
        """
        profile = self.get_user_profile(target_user_id)
        
        if not profile:
            return None
        
        # Add connection status if viewing another user's profile
        if current_user_id and current_user_id != target_user_id:
            profile['connection_status'] = self.get_connection_status(
                current_user_id, 
                target_user_id
            )
            
            # Track profile view
            try:
                from services.profile_analytics_service import ProfileAnalyticsService
                analytics_service = ProfileAnalyticsService(self.db)
                analytics_service.track_profile_view(
                    user_id=target_user_id,
                    viewer_id=current_user_id,
                    source='direct'
                )
            except Exception as e:
                logger.warning(f"Failed to track profile view: {e}")
        else:
            profile['connection_status'] = None
        
        return profile
    
    def get_connection_counts(self, user_id: int) -> Dict[str, int]:
        """Get followers and following counts for a user"""
        try:
            followers_count = (
                self.db.query(Connection)
                .filter(Connection.followed_uid == user_id)
                .count()
            )
            
            following_count = (
                self.db.query(Connection)
                .filter(Connection.follower_uid == user_id)
                .count()
            )
            
            return {
                'followers': followers_count,
                'following': following_count,
                'connections': followers_count  # For now, connections = followers
            }
        except Exception as e:
            logger.error(f"Get connection counts error: {e}", exc_info=True)
            return {'followers': 0, 'following': 0, 'connections': 0}
    
    def update_profile(self, user_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile information"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Update user basic info
            if 'name' in update_data:
                user.name = update_data['name']
            if 'username' in update_data:
                user.username = update_data['username']
            
            # Get or create description
            description = None
            if user.description_id:
                description = (
                    self.db.query(Description)
                    .filter(Description.desc_id == user.description_id)
                    .first()
                )
            
            if not description:
                # Create new description
                description = Description()
                self.db.add(description)
                self.db.flush()  # Get the desc_id
                user.description_id = description.desc_id
            
            # Update description fields
            if 'short_desc' in update_data:
                description.short_desc = update_data['short_desc']
            if 'about' in update_data:
                description.about = update_data['about']
            if 'skills' in update_data:
                description.skills = update_data['skills']
            if 'certificates' in update_data:
                description.certificates = update_data['certificates']
            if 'current_status' in update_data:
                description.current_status = update_data['current_status']
            if 'role' in update_data:
                description.role = update_data['role']
            if 'company' in update_data:
                description.company = update_data['company']
            if 'profile_pic' in update_data:
                description.profile_pic = update_data['profile_pic']
            if 'cover_pic' in update_data:
                description.cover_pic = update_data['cover_pic']
            # Track if embedding-relevant fields changed (these affect recommendations)
            recommendation_fields = {'skills', 'current_status', 'role', 'company', 'location', 'city', 'country', 'about', 'short_desc', 'resume'}
            recommendation_changed = any(key in recommendation_fields for key in update_data.keys())
            embedding_changed = recommendation_changed  # Same fields affect embeddings
            
            if 'location' in update_data:
                description.location = update_data['location']
                # Parse and store city/country
                from services.recommendation_service import RecommendationService
                rec_service = RecommendationService(self.db)
                parsed_location = rec_service._parse_location(update_data['location'])
                description.city = parsed_location.get('city')
                description.country = parsed_location.get('country')
            
            if 'industry' in update_data:
                description.industry = update_data['industry']
            
            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(description)
            
            # Update user embedding and invalidate cache if relevant fields changed
            if embedding_changed:
                try:
                    from utils.job_embeddings import update_user_embedding_if_needed
                    update_user_embedding_if_needed(user_id, self.db)
                    
                    # Invalidate recommendation cache and increment profile version
                    from services.recommendation_cache_service import RecommendationCacheService
                    cache_service = RecommendationCacheService(self.db)
                    cache_service.increment_profile_version(user_id)
                except Exception as e:
                    logger.warning(f"Failed to update embedding/cache for user {user_id}: {e}")
                    # Don't fail profile update if embedding/cache update fails
            
            logger.info(f"Profile updated for user {user_id}")
            
            # Return updated profile
            return self.get_user_profile(user_id)
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update profile error: {e}", exc_info=True)
            raise
