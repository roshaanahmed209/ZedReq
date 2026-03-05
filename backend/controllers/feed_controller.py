"""Feed Controller - Handles feed HTTP requests"""
from flask import request
from services.feed_service import FeedService, PostServiceWithCache
from middleware.auth_middleware import get_current_user_id
from utils.response import success_response, error_response
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FeedController:
    """Feed request handlers"""
    
    def __init__(self, db):
        self.feed_service = FeedService(db)
        self.post_service = PostServiceWithCache(db)
    
    def get_feed(self):
        """
        Get personalized feed with cursor-based pagination.
        
        Query params:
            cursor: Pagination cursor (optional)
            limit: Number of posts (default: 20, max: 50)
        """
        user_id = get_current_user_id()
        
        # Parse query params
        cursor = request.args.get('cursor')
        try:
            limit = int(request.args.get('limit', 20))
        except ValueError:
            limit = 20
        
        # Get feed
        feed_data = self.feed_service.get_user_feed(
            user_id=user_id,
            cursor=cursor,
            limit=limit
        )
        
        return success_response(feed_data)
    
    def create_post(self):
        """
        Create a new post with optional media.
        
        Body:
            content: Post text content (required)
            media_url: Cloudinary media URL (optional)
            media_type: Type of media - 'image' or 'video' (optional)
        """
        user_id = get_current_user_id()
        data = getattr(request, 'validated', request.get_json() or {})
        
        content = data.get('content', '').strip()
        media_url = data.get('media_url')
        media_type = data.get('media_type')
        
        if not content and not media_url:
            return error_response("Post must have content or media", 400)
        
        # Validate media_type if media_url is provided
        if media_url and media_type not in [None, 'image', 'video']:
            return error_response("media_type must be 'image' or 'video'", 400)
        
        try:
            post = self.post_service.create_post(
                user_id=user_id,
                content=content,
                media_url=media_url,
                media_type=media_type
            )
            return success_response(post, "Post created successfully", 201)
        except Exception as e:
            logger.error(f"Create post error: {e}")
            return error_response("Failed to create post", 500)
