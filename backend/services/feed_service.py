"""Feed Service - Production-grade feed with Redis caching and cursor pagination"""
import json
import redis
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from models.post import Post
from models.like import Like
from models.connection import Connection
from config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FeedService:
    """
    Feed service with Redis caching and cursor-based pagination.
    Designed for scalability with 1000+ users.
    """
    
    CACHE_PREFIX = "feed:user:"
    CACHE_TTL = Config.REDIS_CACHE_TTL  # 5 minutes default
    
    def __init__(self, db):
        self.db = db
        self.post_model = Post(db)
        self.like_model = Like(db)
        self.connection_model = Connection(db)
        self._redis = None
    
    @property
    def redis(self):
        """Lazy Redis connection with fallback for development"""
        # Skip Redis entirely if disabled in config
        if not Config.REDIS_ENABLED:
            return None
            
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    Config.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=1,
                    socket_timeout=1
                )
                # Test connection
                self._redis.ping()
                logger.info("Redis connected successfully")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(f"Redis not available, caching disabled: {e}")
                self._redis = None
        return self._redis
    
    def get_user_feed(
        self,
        user_id: int,
        cursor: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get personalized feed for user with cursor-based pagination.
        
        Args:
            user_id: Current user's ID
            cursor: Cursor string in format "timestamp_postid"
            limit: Number of posts to return (max 50)
            
        Returns:
            Dict with posts, pagination info, and metadata
        """
        # Validate limit
        limit = min(limit, 50)
        
        # Try cache first (only for first page without cursor)
        if cursor is None and self.redis:
            cached = self._get_cached_feed(user_id)
            if cached:
                logger.debug(f"Cache hit for user {user_id} feed")
                return cached
        
        # Parse cursor
        parsed_cursor = self._parse_cursor(cursor) if cursor else None
        
        # Get user's following list
        following = self.connection_model.get_following(user_id)
        following_uids = [f['followed_uid'] for f in following]
        
        # Fetch posts
        posts = self.post_model.get_feed_with_connections(
            user_id=user_id,
            following_uids=following_uids,
            cursor=parsed_cursor,
            limit=limit + 1  # Fetch one extra to check if there are more
        )
        
        # Check if there are more posts
        has_more = len(posts) > limit
        if has_more:
            posts = posts[:limit]  # Remove the extra post
        
        # Enrich posts with like status and format response
        enriched_posts = self._enrich_posts(posts, user_id)
        
        # Build next cursor
        next_cursor = None
        if has_more and posts:
            last_post = posts[-1]
            next_cursor = self._build_cursor(last_post['created_at'], last_post['post_id'])
        
        result = {
            'posts': enriched_posts,
            'pagination': {
                'next_cursor': next_cursor,
                'has_more': has_more,
                'limit': limit
            },
            'meta': {
                'following_count': len(following_uids),
                'cache_hit': False
            }
        }
        
        # Cache first page
        if cursor is None and self.redis:
            self._cache_feed(user_id, result)
        
        return result
    
    def _enrich_posts(self, posts: List[Dict], user_id: int) -> List[Dict[str, Any]]:
        """Enrich posts with like status and format for API response"""
        enriched = []
        
        for post in posts:
            # Check if user liked this post
            is_liked = self.like_model.has_liked(post['post_id'], user_id)
            
            enriched.append({
                'id': post['post_id'],
                'user_id': post['uid'],
                'content': post['post_desc'],
                'media_url': post.get('media_url'),
                'media_type': post.get('media_type'),
                'created_at': post['created_at'].isoformat() if hasattr(post['created_at'], 'isoformat') else str(post['created_at']),
                'username': post.get('username', ''),
                'full_name': post.get('name', ''),
                'profile_pic': post.get('profile_pic'),
                'like_count': post.get('likes', 0),
                'comment_count': post.get('comments', 0),
                'is_liked': is_liked
            })
        
        return enriched
    
    def _parse_cursor(self, cursor: str) -> Optional[Tuple[str, int]]:
        """Parse cursor string into (timestamp, post_id) tuple"""
        try:
            parts = cursor.rsplit('_', 1)
            if len(parts) != 2:
                return None
            timestamp_str, post_id_str = parts
            return (timestamp_str, int(post_id_str))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid cursor format: {cursor}")
            return None
    
    def _build_cursor(self, created_at, post_id: int) -> str:
        """Build cursor string from timestamp and post_id"""
        if hasattr(created_at, 'isoformat'):
            timestamp_str = created_at.isoformat()
        else:
            timestamp_str = str(created_at)
        return f"{timestamp_str}_{post_id}"
    
    def _get_cache_key(self, user_id: int) -> str:
        """Get Redis cache key for user's feed"""
        return f"{self.CACHE_PREFIX}{user_id}:page:1"
    
    def _get_cached_feed(self, user_id: int) -> Optional[Dict]:
        """Get cached feed from Redis"""
        try:
            if not self.redis:
                return None
            
            cache_key = self._get_cache_key(user_id)
            cached = self.redis.get(cache_key)
            
            if cached:
                result = json.loads(cached)
                result['meta']['cache_hit'] = True
                return result
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def _cache_feed(self, user_id: int, feed_data: Dict) -> bool:
        """Cache feed data in Redis"""
        try:
            if not self.redis:
                return False
            
            cache_key = self._get_cache_key(user_id)
            self.redis.setex(
                cache_key,
                self.CACHE_TTL,
                json.dumps(feed_data, default=str)
            )
            logger.debug(f"Cached feed for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def invalidate_user_feed(self, user_id: int) -> bool:
        """Invalidate cached feed for a user (call after creating a post)"""
        try:
            if not self.redis:
                return False
            
            cache_key = self._get_cache_key(user_id)
            self.redis.delete(cache_key)
            logger.debug(f"Invalidated feed cache for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def invalidate_followers_feed(self, user_id: int) -> bool:
        """Invalidate feed cache for all followers of a user"""
        try:
            if not self.redis:
                return False
            
            # Get all followers
            followers = self.connection_model.get_followers(user_id)
            
            # Invalidate each follower's cache
            for follower in followers:
                cache_key = self._get_cache_key(follower['follower_uid'])
                self.redis.delete(cache_key)
            
            logger.debug(f"Invalidated feed cache for {len(followers)} followers of user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Redis bulk delete error: {e}")
            return False


class PostServiceWithCache:
    """Extended post service with cache invalidation"""
    
    def __init__(self, db):
        self.db = db
        self.post_model = Post(db)
        self.like_model = Like(db)
        self.feed_service = FeedService(db)
    
    def create_post(
        self, 
        user_id: int, 
        content: str, 
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new post and invalidate relevant caches"""
        # Create the post
        post = self.post_model.create(user_id, content, media_url, media_type)
        
        if post:
            # Invalidate user's own feed cache
            self.feed_service.invalidate_user_feed(user_id)
            
            # Invalidate followers' feed caches
            self.feed_service.invalidate_followers_feed(user_id)
            
            logger.info(f"Post created: {post['post_id']} by user {user_id}")
            
            return {
                'id': post['post_id'],
                'content': post['post_desc'],
                'media_url': post.get('media_url'),
                'media_type': post.get('media_type'),
                'created_at': str(post['created_at'])
            }
        
        raise Exception("Failed to create post")
