"""Feed Service - Production-grade feed with Redis caching and cursor pagination using ORM"""
import json
import math
import os
import re
import secrets
from typing import Optional, Dict, Any, List, Tuple, Literal
from datetime import datetime
from sqlalchemy import and_, or_, desc, func, cast, String
from sqlalchemy.orm import Session

from config.cache import get_redis_client, is_redis_available, get_cached, set_cached
from config.database import get_database
from models.orm import Post, Like, Connection, User, Description
from services.post_service import PostService
from services.user_interest_service import get_user_interest_vector
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
        
        phase, phase_cursor, disc_state = self._parse_feed_cursor(cursor)
        
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
                    user_id=user_id,
                    exclude_uids=circle_uids,
                    disc_state=disc_state,
                    limit=limit,
                )
        else:
            feed_segment = 'discovery'
            posts, has_more, next_cursor = self._paginate_discovery(
                user_id=user_id,
                exclude_uids=circle_uids,
                disc_state=disc_state,
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
    
    def _make_discovery_seed(self) -> str:
        return secrets.token_hex(8)

    def _discovery_shuffle_key(self, seed: str):
        """Stable pseudo-random order per feed session (seed in cursor)."""
        return func.md5(func.concat(cast(Post.post_id, String), seed))

    def _get_discovery_feed_posts(
        self,
        exclude_uids: List[int],
        seed: str,
        offset: int,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Posts from users outside the viewer's circle, shuffled by seed."""
        query = (
            self.db.query(Post)
            .join(User, Post.uid == User.uid)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(Post.not_deleted())
        )
        if exclude_uids:
            query = query.filter(~Post.uid.in_(exclude_uids))
        posts = (
            query
            .order_by(self._discovery_shuffle_key(seed))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return self._format_post_rows(posts)
    
    def _discovery_has_any(self, exclude_uids: List[int]) -> bool:
        q = self.db.query(Post.post_id).filter(Post.not_deleted())
        if exclude_uids:
            q = q.filter(~Post.uid.in_(exclude_uids))
        return q.first() is not None
    
    def _paginate_discovery(
        self,
        user_id: int,
        exclude_uids: List[int],
        disc_state: Optional[Tuple[str, Any, int]],
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        """
        Discovery pagination. Personalized (vector-ranked) when the user has an
        interest vector; otherwise falls back to the original random shuffle.
        """
        kind = disc_state[0] if disc_state else 'new'

        # Continuing a ranked session: serve the next page from the cached ranking.
        if kind == 'ranked':
            ranking_id = str(disc_state[1])
            offset = int(disc_state[2])
            ranked_ids = self._load_ranked_list(ranking_id)
            if ranked_ids is not None:
                return self._serve_ranked_page(ranked_ids, ranking_id, offset, limit)
            # Ranking expired from cache → rebuild a fresh personalized ranking.
            kind = 'new'
            disc_state = ('new', None, 0)

        # Starting (or restarting) discovery: try personalized first.
        if kind == 'new':
            personalized = self._build_personalized_discovery(user_id, exclude_uids, limit)
            if personalized is not None:
                return personalized

        # Cold-start / no embeddings / no candidates → original random discovery.
        return self._paginate_random_discovery(exclude_uids, disc_state, limit)

    def _paginate_random_discovery(
        self,
        exclude_uids: List[int],
        disc_state: Optional[Tuple[str, Any, int]],
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        """Original seed-shuffled discovery (cold-start fallback)."""
        if disc_state is None or disc_state[0] == 'new':
            seed = self._make_discovery_seed()
            offset = int(disc_state[2]) if disc_state else 0
        else:
            seed = str(disc_state[1])
            offset = int(disc_state[2])

        raw = self._get_discovery_feed_posts(
            exclude_uids=exclude_uids,
            seed=seed,
            offset=offset,
            limit=limit + 1,
        )
        if len(raw) > limit:
            page = raw[:limit]
            return page, True, self._build_disc_cursor(seed, offset + limit)
        if not raw:
            return [], False, None
        return raw, False, None

    # ------------------------------------------------------------------
    # Personalized (vector-ranked) discovery
    # ------------------------------------------------------------------

    DISC_RANK_PREFIX = "feed:disc_rank:"
    DISC_RANK_TTL = int(os.environ.get('FEED_DISC_RANK_TTL', 1800))  # ranked-session lifetime
    DISC_CANDIDATE_LIMIT = int(os.environ.get('FEED_DISC_CANDIDATE_LIMIT', 200))

    def _build_personalized_discovery(
        self,
        user_id: int,
        exclude_uids: List[int],
        limit: int,
    ) -> Optional[Tuple[List[Dict[str, Any]], bool, Optional[str]]]:
        """
        Build a fresh personalized ranking and return its first page.
        Returns None to signal the caller to fall back to random discovery
        (no interest vector, or no candidates).
        """
        try:
            user_vec = get_user_interest_vector(user_id, self.db)
        except Exception as e:
            logger.warning(f"Interest vector failed for user {user_id}: {e}")
            user_vec = None
        if not user_vec:
            return None

        candidates = self._vector_post_search(
            user_vec, exclude_uids, candidate_limit=self.DISC_CANDIDATE_LIMIT
        )
        if not candidates:
            return None

        ranked_ids = self._score_candidates(candidates)
        if not ranked_ids:
            return None

        ranking_id = secrets.token_hex(8)
        self._store_ranked_list(ranking_id, ranked_ids)
        return self._serve_ranked_page(ranked_ids, ranking_id, 0, limit)

    def _vector_post_search(
        self,
        user_vec: List[float],
        exclude_uids: List[int],
        candidate_limit: int = 200,
    ) -> List[Dict[str, Any]]:
        """pgvector cosine search over post embeddings, excluding the viewer's circle."""
        try:
            embedding_str = '[' + ','.join(map(str, user_vec)) + ']'
            query = """
            SELECT post_id, uid, created_at, likes, comments,
                   1 - (embedding::vector <=> %s::vector) AS similarity
            FROM post
            WHERE (is_deleted IS NOT TRUE)
                AND embedding IS NOT NULL
                AND (uid IS NULL OR uid <> ALL(%s))
            ORDER BY embedding::vector <=> %s::vector
            LIMIT %s
            """
            params = (embedding_str, list(exclude_uids or []), embedding_str, candidate_limit)
            db_raw = get_database()
            rows = db_raw.fetch_all(query, params)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Vector post search failed: {e}", exc_info=True)
            return []

    def _recency_score(self, created_at) -> float:
        """Recency decay (mirrors recommendation_service tiers): newer → higher."""
        if not created_at:
            return 0.2
        try:
            if isinstance(created_at, str):
                post_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                post_date = created_at
            now = datetime.now(post_date.tzinfo) if post_date.tzinfo else datetime.now()
            age_days = (now - post_date).days
        except (ValueError, AttributeError, TypeError):
            return 0.2
        if age_days <= 1:
            return 1.0
        if age_days <= 7:
            return 0.8
        if age_days <= 30:
            return 0.6
        if age_days <= 90:
            return 0.4
        return 0.2

    def _score_candidates(self, candidates: List[Dict[str, Any]]) -> List[int]:
        """
        Composite re-rank of vector-search candidates. Discovery excludes the
        viewer's circle, so the connection bonus does not apply here.
            score = 0.6*similarity + 0.2*recency + 0.2*popularity
        Returns post_ids ordered best-first.
        """
        if not candidates:
            return []

        pops = [
            math.log1p((c.get('likes') or 0) + (c.get('comments') or 0))
            for c in candidates
        ]
        max_pop = max(pops) if pops else 0.0

        scored: List[Tuple[float, int]] = []
        for c, pop in zip(candidates, pops):
            similarity = float(c.get('similarity') or 0.0)
            recency = self._recency_score(c.get('created_at'))
            popularity = (pop / max_pop) if max_pop > 0 else 0.0
            score = 0.6 * similarity + 0.2 * recency + 0.2 * popularity
            scored.append((score, c['post_id']))

        scored.sort(key=lambda x: (-x[0], -x[1]))
        return [pid for _, pid in scored]

    def _serve_ranked_page(
        self,
        ranked_ids: List[int],
        ranking_id: str,
        offset: int,
        limit: int,
    ) -> Tuple[List[Dict[str, Any]], bool, Optional[str]]:
        """Return one page (offset..offset+limit) of a cached ranked post-id list."""
        slice_ids = ranked_ids[offset:offset + limit]
        posts = self._fetch_posts_by_ids_ordered(slice_ids)
        has_more = (offset + limit) < len(ranked_ids)
        next_cursor = (
            self._build_disc_ranked_cursor(ranking_id, offset + limit) if has_more else None
        )
        return posts, has_more, next_cursor

    def _fetch_posts_by_ids_ordered(self, post_ids: List[int]) -> List[Dict[str, Any]]:
        """Fetch and format posts preserving the given id order; drops deleted/missing."""
        if not post_ids:
            return []
        posts = (
            self.db.query(Post)
            .join(User, Post.uid == User.uid)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(Post.post_id.in_(post_ids), Post.not_deleted())
            .all()
        )
        by_id = {p.post_id: p for p in posts}
        ordered = [by_id[pid] for pid in post_ids if pid in by_id]
        return self._format_post_rows(ordered)

    def _store_ranked_list(self, ranking_id: str, post_ids: List[int]) -> None:
        try:
            set_cached(f"{self.DISC_RANK_PREFIX}{ranking_id}", post_ids, ttl=self.DISC_RANK_TTL)
        except Exception as e:
            logger.debug(f"Failed to store ranked discovery list {ranking_id}: {e}")

    def _load_ranked_list(self, ranking_id: str) -> Optional[List[int]]:
        try:
            cached = get_cached(f"{self.DISC_RANK_PREFIX}{ranking_id}")
            if cached is None:
                return None
            return [int(x) for x in cached]
        except Exception as e:
            logger.debug(f"Failed to load ranked discovery list {ranking_id}: {e}")
            return None
    
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
    ) -> Tuple[
        Literal['conn', 'disc'],
        Optional[Tuple[Any, int]],
        Optional[Tuple[str, Any, int]],
    ]:
        """Returns phase, connection time cursor, and discovery (kind, seed, offset)."""
        if not cursor:
            return 'conn', None, None
        if cursor == self.DISC_START_CURSOR:
            return 'disc', None, ('new', None, 0)
        if cursor.startswith('conn:'):
            payload = cursor[5:]
            ts, sep, pid = payload.rpartition('|')
            if not sep:
                return 'conn', None, None
            try:
                return 'conn', (ts, int(pid)), None
            except ValueError:
                logger.warning(f"Invalid conn cursor: {cursor}")
                return 'conn', None, None
        disc_ranked_offset = re.match(r'^disc:r([0-9a-f]+):o(\d+)$', cursor)
        if disc_ranked_offset:
            ranking_id, offset_str = disc_ranked_offset.groups()
            try:
                return 'disc', None, ('ranked', ranking_id, int(offset_str))
            except ValueError:
                logger.warning(f"Invalid ranked disc offset in cursor: {cursor}")
                return 'disc', None, ('new', None, 0)
        disc_seed_offset = re.match(r'^disc:s([0-9a-f]+):o(\d+)$', cursor)
        if disc_seed_offset:
            seed, offset_str = disc_seed_offset.groups()
            try:
                return 'disc', None, ('seed', seed, int(offset_str))
            except ValueError:
                logger.warning(f"Invalid disc offset in cursor: {cursor}")
                return 'disc', None, ('new', None, 0)
        if cursor.startswith('disc:'):
            # Legacy time-based discovery cursors: start a fresh shuffled page
            logger.debug(f"Legacy discovery cursor, reshuffling: {cursor}")
            return 'disc', None, ('new', None, 0)
        legacy = self._parse_legacy_conn_cursor(cursor)
        return 'conn', legacy, None
    
    def _ts_for_cursor(self, created_at) -> str:
        if hasattr(created_at, 'isoformat'):
            return created_at.isoformat()
        return str(created_at)
    
    def _build_conn_cursor(self, created_at, post_id: int) -> str:
        return f"conn:{self._ts_for_cursor(created_at)}|{post_id}"
    
    def _build_disc_cursor(self, seed: str, offset: int) -> str:
        return f"disc:s{seed}:o{offset}"

    def _build_disc_ranked_cursor(self, ranking_id: str, offset: int) -> str:
        return f"disc:r{ranking_id}:o{offset}"
    
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
