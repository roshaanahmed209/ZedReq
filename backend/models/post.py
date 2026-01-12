"""Post Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS post (
    post_id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    media_ref_id INTEGER,
    post_desc TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_post_uid ON post(uid)',
    'CREATE INDEX IF NOT EXISTS idx_post_created ON post(created_at DESC)'
]


class Post(BaseModel):
    """Post model"""
    table_name = 'post'
    
    def create(self, uid: int, post_desc: str, media_ref_id: int = None) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO post (uid, post_desc, media_ref_id)
               VALUES (%s, %s, %s) RETURNING *''',
            (uid, post_desc, media_ref_id)
        )
    
    def get_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Get post by ID"""
        return self.db.fetch_one(
            '''SELECT p.*, u.name, u.username FROM post p
               JOIN users u ON p.uid = u.uid
               WHERE p.post_id = %s AND p.is_deleted = FALSE''',
            (post_id,)
        )
    
    def get_feed(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT p.*, u.name, u.username FROM post p
               JOIN users u ON p.uid = u.uid
               WHERE p.is_deleted = FALSE
               ORDER BY p.created_at DESC LIMIT %s OFFSET %s''',
            (limit, offset)
        )
    
    def get_by_user(self, uid: int) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT * FROM post 
               WHERE uid = %s AND is_deleted = FALSE 
               ORDER BY created_at DESC''', 
            (uid,)
        )
    
    def update(self, post_id: int, uid: int, post_desc: str) -> Optional[Dict[str, Any]]:
        """Update post (only by owner)"""
        return self.db.execute_returning(
            '''UPDATE post SET post_desc = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE post_id = %s AND uid = %s RETURNING *''',
            (post_desc, post_id, uid)
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
