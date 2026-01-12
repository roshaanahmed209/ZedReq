"""Like Model"""
from typing import Optional, Dict, Any
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS likes (
    like_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES post(post_id) ON DELETE CASCADE,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, uid)
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id)',
    'CREATE INDEX IF NOT EXISTS idx_likes_user ON likes(uid)'
]


class Like(BaseModel):
    """Like model for post likes"""
    table_name = 'likes'
    
    def toggle(self, post_id: int, uid: int) -> bool:
        """
        Toggle like on a post
        Returns True if liked, False if unliked
        """
        # Check if already liked
        existing = self.db.fetch_one(
            'SELECT like_id FROM likes WHERE post_id = %s AND uid = %s',
            (post_id, uid)
        )
        
        if existing:
            # Unlike
            self.db.execute(
                'DELETE FROM likes WHERE post_id = %s AND uid = %s',
                (post_id, uid)
            )
            return False
        else:
            # Like
            self.db.execute_returning(
                'INSERT INTO likes (post_id, uid) VALUES (%s, %s) RETURNING like_id',
                (post_id, uid)
            )
            return True
    
    def get_count(self, post_id: int) -> int:
        """Get total likes for a post"""
        result = self.db.fetch_one(
            'SELECT COUNT(*) as count FROM likes WHERE post_id = %s',
            (post_id,)
        )
        return result['count'] if result else 0
    
    def has_liked(self, post_id: int, uid: int) -> bool:
        """Check if user has liked a post"""
        result = self.db.fetch_one(
            'SELECT 1 FROM likes WHERE post_id = %s AND uid = %s',
            (post_id, uid)
        )
        return result is not None
    
    def get_likers(self, post_id: int, limit: int = 50) -> list:
        """Get users who liked a post"""
        return self.db.fetch_all(
            '''SELECT u.uid, u.username, u.name 
               FROM likes l
               JOIN users u ON l.uid = u.uid
               WHERE l.post_id = %s
               ORDER BY l.created_at DESC
               LIMIT %s''',
            (post_id, limit)
        )
