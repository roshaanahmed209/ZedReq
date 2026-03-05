"""Post Model"""
from typing import Optional, Dict, Any, List, Tuple
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS post (
    post_id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    media_url TEXT,
    media_type VARCHAR(20),
    post_desc TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_post_uid ON post(uid)',
    'CREATE INDEX IF NOT EXISTS idx_post_created ON post(created_at DESC)',
    'CREATE INDEX IF NOT EXISTS idx_post_uid_created_deleted ON post(uid, created_at DESC, is_deleted)',
    'CREATE INDEX IF NOT EXISTS idx_post_feed ON post(created_at DESC, post_id DESC) WHERE is_deleted = FALSE'
]


class Post(BaseModel):
    """Post model"""
    table_name = 'post'
    
    def create(self, uid: int, post_desc: str, media_url: str = None, media_type: str = None) -> Optional[Dict[str, Any]]:
        """Create a new post with optional media"""
        return self.db.execute_returning(
            '''INSERT INTO post (uid, post_desc, media_url, media_type)
               VALUES (%s, %s, %s, %s) RETURNING *''',
            (uid, post_desc, media_url, media_type)
        )
    
    def get_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get post by ID with user info"""
        return self.db.fetch_one(
            '''SELECT p.*, u.name, u.username, d.profile_pic
               FROM post p
               JOIN users u ON p.uid = u.uid
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE p.post_id = %s AND p.is_deleted = FALSE''',
            (post_id,)
        )
    
    def get_feed(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all posts for feed (deprecated - use get_feed_with_connections)"""
        return self.db.fetch_all(
            '''SELECT p.*, u.name, u.username, d.profile_pic
               FROM post p
               JOIN users u ON p.uid = u.uid
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE p.is_deleted = FALSE
               ORDER BY p.created_at DESC LIMIT %s OFFSET %s''',
            (limit, offset)
        )
    
    def get_feed_with_connections(
        self, 
        user_id: int, 
        following_uids: List[int], 
        cursor: Optional[Tuple[str, int]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get personalized feed with cursor-based pagination.
        Shows posts from followed users and the current user.
        
        Args:
            user_id: Current user's ID
            following_uids: List of user IDs that current user follows
            cursor: Tuple of (created_at, post_id) for pagination
            limit: Number of posts to fetch
            
        Returns:
            List of posts with user info
        """
        # Include current user in the feed
        all_uids = list(set(following_uids + [user_id]))
        
        if cursor:
            cursor_time, cursor_id = cursor
            return self.db.fetch_all(
                '''SELECT p.*, u.name, u.username, d.profile_pic
                   FROM post p
                   JOIN users u ON p.uid = u.uid
                   LEFT JOIN description d ON u.description_id = d.desc_id
                   WHERE p.uid = ANY(%s)
                     AND p.is_deleted = FALSE
                     AND (p.created_at, p.post_id) < (%s, %s)
                   ORDER BY p.created_at DESC, p.post_id DESC
                   LIMIT %s''',
                (all_uids, cursor_time, cursor_id, limit)
            )
        else:
            return self.db.fetch_all(
                '''SELECT p.*, u.name, u.username, d.profile_pic
                   FROM post p
                   JOIN users u ON p.uid = u.uid
                   LEFT JOIN description d ON u.description_id = d.desc_id
                   WHERE p.uid = ANY(%s)
                     AND p.is_deleted = FALSE
                   ORDER BY p.created_at DESC, p.post_id DESC
                   LIMIT %s''',
                (all_uids, limit)
            )
    
    def get_by_user(self, uid: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get posts by a specific user"""
        return self.db.fetch_all(
            '''SELECT p.*, u.name, u.username, d.profile_pic
               FROM post p
               JOIN users u ON p.uid = u.uid
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE p.uid = %s AND p.is_deleted = FALSE 
               ORDER BY p.created_at DESC
               LIMIT %s OFFSET %s''', 
            (uid, limit, offset)
        )
    
    def update(self, post_id: int, uid: int, post_desc: str) -> Optional[Dict[str, Any]]:
        """Update post (only by owner)"""
        return self.db.execute_returning(
            '''UPDATE post SET post_desc = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE post_id = %s AND uid = %s RETURNING *''',
            (post_desc, post_id, uid)
        )
    
    def update_media(self, post_id: int, uid: int, media_url: str, media_type: str) -> Optional[Dict[str, Any]]:
        """Update post media (only by owner)"""
        return self.db.execute_returning(
            '''UPDATE post SET media_url = %s, media_type = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE post_id = %s AND uid = %s RETURNING *''',
            (media_url, media_type, post_id, uid)
        )
    
    def soft_delete(self, post_id: int, uid: int) -> Optional[Dict[str, Any]]:
        """Soft delete post (only by owner)"""
        return self.db.execute_returning(
            '''UPDATE post SET is_deleted = TRUE, updated_at = CURRENT_TIMESTAMP 
               WHERE post_id = %s AND uid = %s RETURNING post_id''',
            (post_id, uid)
        )
    
    def increment_likes(self, post_id: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''UPDATE post SET likes = likes + 1 
               WHERE post_id = %s AND is_deleted = FALSE RETURNING *''',
            (post_id,)
        )
    
    def decrement_likes(self, post_id: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''UPDATE post SET likes = GREATEST(0, likes - 1)
               WHERE post_id = %s AND is_deleted = FALSE RETURNING *''',
            (post_id,)
        )
    
    def increment_comments(self, post_id: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''UPDATE post SET comments = comments + 1 
               WHERE post_id = %s AND is_deleted = FALSE RETURNING *''',
            (post_id,)
        )
    
    def get_post_count_by_user(self, uid: int) -> int:
        """Get total post count for a user"""
        result = self.db.fetch_one(
            'SELECT COUNT(*) as count FROM post WHERE uid = %s AND is_deleted = FALSE',
            (uid,)
        )
        return result['count'] if result else 0