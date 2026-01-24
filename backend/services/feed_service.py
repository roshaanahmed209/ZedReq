"""Feed Service - Production-grade feed with Redis caching and cursor pagination using ORM"""
import json
import redis
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

from models.orm import Post, Like, Connection, User, Description
from services.post_service import PostService
from utils.logger import setup_logger
import os

logger = setup_logger(__name__)


class FeedService:
    """
    Feed service with Redis caching and cursor-based pagination using ORM.
    Designed for scalability with 1000+ users.
    """
    
    CACHE_PREFIX = "feed:user:"
    CACHE_TTL = int(os.environ.get('REDIS_CACHE_TTL', 300))  # 5 minutes default
    
    def __init__(self, db: Session):
        self.db = db
        self.post_service = PostService(db)
        self._redis = None
    
    @property
    def redis(self):
        """Lazy Redis connection with fallback for development"""
        # Skip Redis entirely if disabled in config
        redis_enabled = os.environ.get('REDIS_ENABLED', 'false').lower() == 'true'
        if not redis_enabled:
            return None
        
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            
        if self._redis is None:
            try:
                self._redis = redis.from_url(
                    redis_url,
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
        
        # Get user's following list using ORM
        following_uids = self._get_following_uids(user_id)
        
        # Fetch posts using ORM
        posts = self._get_feed_posts(
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
    
    def _get_following_uids(self, user_id: int) -> List[int]:
        """Get list of user IDs that the user follows"""
        connections = (
            self.db.query(Connection)
            .filter(Connection.follower_uid == user_id)
            .all()
        )
        return [conn.followed_uid for conn in connections]
    
    def _get_feed_posts(
        self,
        user_id: int,
        following_uids: List[int],
        cursor: Optional[Tuple[str, int]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get posts for feed using ORM"""
        # Include current user in the feed
        all_uids = list(set(following_uids + [user_id]))
        
        query = (
            self.db.query(Post)
            .join(User, Post.uid == User.uid)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(
                and_(
                    Post.uid.in_(all_uids),
                    Post.is_deleted == False
                )
            )
        )
        
        # Apply cursor if provided
        if cursor:
            cursor_time, cursor_id = cursor
            # Parse timestamp string to datetime if needed
            try:
                if isinstance(cursor_time, str):
                    cursor_dt = datetime.fromisoformat(cursor_time.replace('Z', '+00:00'))
                else:
                    cursor_dt = cursor_time
                
                query = query.filter(
                    or_(
                        Post.created_at < cursor_dt,
                        and_(
                            Post.created_at == cursor_dt,
                            Post.post_id < cursor_id
                        )
                    )
                )
            except (ValueError, AttributeError):
                logger.warning(f"Invalid cursor timestamp: {cursor_time}")
        
        posts = (
            query
            .order_by(desc(Post.created_at), desc(Post.post_id))
            .limit(limit)
            .all()
        )
        
        # Format posts
        result = []
        for post in posts:
            # Get profile pic
            profile_pic = None
            if post.user and post.user.description_id:
                user_desc = (
                    self.db.query(Description)
                    .filter(Description.desc_id == post.user.description_id)
                    .first()
                )
                if user_desc:
                    profile_pic = user_desc.profile_pic
            
            result.append({
                'post_id': post.post_id,
                'uid': post.uid,
                'post_desc': post.post_desc,
                'media_url': post.media_url,
                'media_type': post.media_type,
                'likes': post.likes,
                'comments': post.comments,
                'created_at': post.created_at,
                'username': post.user.username if post.user else None,
                'name': post.user.name if post.user else None,
                'profile_pic': profile_pic
            })
        
        return result
    
    def _enrich_posts(self, posts: List[Dict], user_id: int) -> List[Dict[str, Any]]:
        """Enrich posts with like status and format for API response"""
        enriched = []
        
        for post in posts:
            # Check if user liked this post using ORM
            is_liked = self._has_liked(post['post_id'], user_id)
            
            created_at = post['created_at']
            if hasattr(created_at, 'isoformat'):
                created_str = created_at.isoformat()
            else:
                created_str = str(created_at)
            
            enriched.append({
                'id': post['post_id'],
                'user_id': post['uid'],
                'content': post['post_desc'],
                'media_url': post.get('media_url'),
                'media_type': post.get('media_type'),
                'created_at': created_str,
                'username': post.get('username', ''),
                'full_name': post.get('name', ''),
                'profile_pic': post.get('profile_pic'),
                'like_count': post.get('likes', 0),
                'comment_count': post.get('comments', 0),
                'is_liked': is_liked
            })
        
        return enriched
    
    def _has_liked(self, post_id: int, user_id: int) -> bool:
        """Check if user has liked a post using ORM"""
        like = (
            self.db.query(Like)
            .filter(
                and_(
                    Like.post_id == post_id,
                    Like.uid == user_id
                )
            )
            .first()
        )
        return like is not None
    
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
            
            # Get all followers using ORM
            followers = (
                self.db.query(Connection)
                .filter(Connection.followed_uid == user_id)
                .all()
            )
            
            # Invalidate each follower's cache
            for follower in followers:
                cache_key = self._get_cache_key(follower.follower_uid)
                self.redis.delete(cache_key)
            
            logger.debug(f"Invalidated feed cache for {len(followers)} followers of user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Redis bulk delete error: {e}")
            return False
