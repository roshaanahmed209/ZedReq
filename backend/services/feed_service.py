"""Feed Service - Production-grade feed with Redis caching and cursor pagination using ORM"""
import json
import os
from typing import Optional, Dict, Any, List, Tuple, Literal
from datetime import datetime
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from config.cache import get_redis_client, is_redis_available
from models.orm import Post, Like, Connection, User, Description
from services.post_service import PostService
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FeedService:
    """
    Feed service with Redis caching and cursor-based pagination using ORM.
    Designed for scalability with 1000+ users.
    """
    
    DISC_START_CURSOR = "disc:start"
    CACHE_PREFIX = "feed:user:"
    CACHE_TTL = int(os.environ.get('REDIS_CACHE_TTL', 300))  # 5 minutes default
    
    def __init__(self, db: Session):
        self.db = db
        self.post_service = PostService(db)

    @property
    def redis(self):
        """Shared Redis client from config.cache (None when unavailable)."""
        return get_redis_client()

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
            cursor: Opaque pagination token from the previous response (connection and discovery phases).
            limit: Number of posts to return (max 50)
            
        Returns:
            Dict with posts, pagination, and meta including ``feed_segment`` (connections | discovery).
        """
        # Validate limit
        limit = min(limit, 50)
        
        # Try cache first (only for first page without cursor; discovery-only first pages are not cached)
        if cursor is None and is_redis_available():
            cached = self._get_cached_feed(user_id)
            if cached:
                logger.debug(f"Cache hit for user {user_id} feed")
                return cached
        
        phase, phase_cursor = self._parse_feed_cursor(cursor)
        
        following_uids = self._get_following_uids(user_id)
        circle_uids = list(set(following_uids + [user_id]))
        
        posts: List[Dict[str, Any]] = []
        feed_segment: Literal['connections', 'discovery'] = 'connections'
        has_more = False
        next_cursor: Optional[str] = None
        
        if phase == 'conn':
            posts = self._get_connection_feed_posts(
                circle_uids=circle_uids,
                cursor=phase_cursor,
                limit=limit + 1,
            )
            if len(posts) > limit:
                has_more = True
                posts = posts[:limit]
                next_cursor = self._build_conn_cursor(posts[-1]['created_at'], posts[-1]['post_id'])
            elif posts:
                # Last page of connection-scoped posts; discovery starts on the next request
                feed_segment = 'connections'
                disc_pending = self._discovery_has_any(exclude_uids=circle_uids)
                has_more = disc_pending
                next_cursor = self.DISC_START_CURSOR if disc_pending else None
            else:
                # No (more) connection posts: discovery on this request (infinite scroll continues seamlessly)
                feed_segment = 'discovery'
                posts, has_more, next_cursor = self._paginate_discovery(
                    exclude_uids=circle_uids,
                    cursor_tuple=None,
                    limit=limit,
                )
        else:
            feed_segment = 'discovery'
            posts, has_more, next_cursor = self._paginate_discovery(
                exclude_uids=circle_uids,
                cursor_tuple=phase_cursor,
                limit=limit,
            )
        
        enriched_posts = self._enrich_posts(posts, user_id)
        
        result = {
            'posts': enriched_posts,
            'pagination': {
                'next_cursor': next_cursor,
                'has_more': has_more,
                'limit': limit
            },
            'meta': {
                'following_count': len(following_uids),
                'cache_hit': False,
                'feed_segment': feed_segment,
            }
        }
        
        if (
            cursor is None
            and is_redis_available()
            and feed_segment == 'connections'
            and (not enriched_posts or all(p['user_id'] in circle_uids for p in enriched_posts))
        ):
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
    
    def _apply_feed_time_cursor(self, query, cursor: Optional[Tuple[Any, int]]):
        if not cursor:
            return query
        cursor_time, cursor_id = cursor
        try:
            if isinstance(cursor_time, str):
                cursor_dt = datetime.fromisoformat(cursor_time.replace('Z', '+00:00'))
            else:
                cursor_dt = cursor_time
            return query.filter(
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
            return query
    
    def _format_post_rows(self, posts: List[Post]) -> List[Dict[str, Any]]:
        result = []
        for post in posts:
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
    
    def _get_connection_feed_posts(
        self,
        circle_uids: List[int],
        cursor: Optional[Tuple[Any, int]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Posts from self + followed users only."""
        if not circle_uids:
            return []
        query = (
            self.db.query(Post)
            .join(User, Post.uid == User.uid)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(
                and_(
                    Post.uid.in_(circle_uids),
                    Post.not_deleted()
                )
            )
        )
        query = self._apply_feed_time_cursor(query, cursor)
        posts = (
            query
            .order_by(desc(Post.created_at), desc(Post.post_id))
            .limit(limit)
            .all()
        )
        return self._format_post_rows(posts)
    
    def _get_discovery_feed_posts(
        self,
        exclude_uids: List[int],
        cursor: Optional[Tuple[Any, int]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Posts from users outside the viewer's circle (not following / not self)."""
        query = (
            self.db.query(Post)
            .join(User, Post.uid == User.uid)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(Post.not_deleted())
        )
        if exclude_uids:
            query = query.filter(~Post.uid.in_(exclude_uids))
        query = self._apply_feed_time_cursor(query, cursor)
        posts = (
            query
            .order_by(desc(Post.created_at), desc(Post.post_id))
            .limit(limit)
            .all()
        )
        return self._format_post_rows(posts)
    
    def _discovery_has_any(self, exclude_uids: List[int]) -> bool:
        q = self.db.query(Post.post_id).filter(Post.not_deleted())
        if exclude_uids:
            q = q.filter(~Post.uid.in_(exclude_uids))
        return q.first() is not None
    
    def _discovery_has_more_after(
        self,
        exclude_uids: List[int],
        last_created_at,
        last_post_id: int,
    ) -> bool:
        nxt = self._get_discovery_feed_posts(
            exclude_uids=exclude_uids,
            cursor=(last_created_at, last_post_id),
            limit=1,
        )
        return len(nxt) > 0
    
    def _paginate_discovery(
        self,
        exclude_uids: List[int],
        cursor_tuple: Optional[Tuple[Any, int]],
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        raw = self._get_discovery_feed_posts(
            exclude_uids=exclude_uids,
            cursor=cursor_tuple,
            limit=limit + 1,
        )
        if len(raw) > limit:
            page = raw[:limit]
            return page, True, self._build_disc_cursor(page[-1]['created_at'], page[-1]['post_id'])
        if not raw:
            return [], False, None
        has_more = self._discovery_has_more_after(
            exclude_uids,
            raw[-1]['created_at'],
            raw[-1]['post_id'],
        )
        next_c = (
            self._build_disc_cursor(raw[-1]['created_at'], raw[-1]['post_id'])
            if has_more
            else None
        )
        return raw, has_more, next_c
    
    def _enrich_posts(self, posts: List[Dict], user_id: int) -> List[Dict[str, Any]]:
        """Enrich posts with like status and format for API response (optimized with batch query)"""
        if not posts:
            return []
        
        # Batch query: Get all like statuses in a single query
        post_ids = [post['post_id'] for post in posts]
        liked_post_ids = self._get_liked_post_ids_batch(post_ids, user_id)
        comment_counts = self.post_service.get_comment_counts_by_post_ids(post_ids)
        
        enriched = []
        for post in posts:
            # Check if user liked this post (from batch query result)
            is_liked = post['post_id'] in liked_post_ids
            
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
                'comment_count': comment_counts.get(post['post_id'], 0),
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
    
    def _get_liked_post_ids_batch(self, post_ids: List[int], user_id: int) -> set:
        """
        Batch query to get all post IDs that the user has liked
        
        Args:
            post_ids: List of post IDs to check
            user_id: User ID
        
        Returns:
            Set of post IDs that the user has liked
        """
        if not post_ids:
            return set()
        
        liked_posts = (
            self.db.query(Like.post_id)
            .filter(
                and_(
                    Like.post_id.in_(post_ids),
                    Like.uid == user_id
                )
            )
            .all()
        )
        
        return {post_id for (post_id,) in liked_posts}
    
    def _parse_legacy_conn_cursor(self, cursor: str) -> Optional[Tuple[str, int]]:
        """Legacy cursor: {iso}_{post_id} (conn phase)."""
        try:
            parts = cursor.rsplit('_', 1)
            if len(parts) != 2:
                return None
            timestamp_str, post_id_str = parts
            return (timestamp_str, int(post_id_str))
        except (ValueError, AttributeError):
            logger.warning(f"Invalid cursor format: {cursor}")
            return None
    
    def _parse_feed_cursor(
        self, cursor: Optional[str]
    ) -> Tuple[Literal['conn', 'disc'], Optional[Tuple[Any, int]]]:
        if not cursor:
            return 'conn', None
        if cursor == self.DISC_START_CURSOR:
            return 'disc', None
        if cursor.startswith('conn:'):
            payload = cursor[5:]
            ts, sep, pid = payload.rpartition('|')
            if not sep:
                return 'conn', None
            try:
                return 'conn', (ts, int(pid))
            except ValueError:
                logger.warning(f"Invalid conn cursor: {cursor}")
                return 'conn', None
        if cursor.startswith('disc:'):
            payload = cursor[5:]
            if payload == 'start':
                return 'disc', None
            ts, sep, pid = payload.rpartition('|')
            if not sep:
                logger.warning(f"Invalid disc cursor: {cursor}")
                return 'disc', None
            try:
                return 'disc', (ts, int(pid))
            except ValueError:
                logger.warning(f"Invalid disc cursor: {cursor}")
                return 'disc', None
        legacy = self._parse_legacy_conn_cursor(cursor)
        return 'conn', legacy
    
    def _ts_for_cursor(self, created_at) -> str:
        if hasattr(created_at, 'isoformat'):
            return created_at.isoformat()
        return str(created_at)
    
    def _build_conn_cursor(self, created_at, post_id: int) -> str:
        return f"conn:{self._ts_for_cursor(created_at)}|{post_id}"
    
    def _build_disc_cursor(self, created_at, post_id: int) -> str:
        return f"disc:{self._ts_for_cursor(created_at)}|{post_id}"
    
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
