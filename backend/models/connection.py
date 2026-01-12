"""Connections (Followers/Following) Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS connections (
    connection_id SERIAL PRIMARY KEY,
    follower_uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    followed_uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (follower_uid, followed_uid)
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_connections_follower ON connections(follower_uid)',
    'CREATE INDEX IF NOT EXISTS idx_connections_followed ON connections(followed_uid)'
]


class Connection(BaseModel):
    """Connection (follow) model"""
    table_name = 'connections'
    
    def follow(self, follower_uid: int, followed_uid: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO connections (follower_uid, followed_uid)
               VALUES (%s, %s)
               ON CONFLICT (follower_uid, followed_uid) DO NOTHING
               RETURNING *''',
            (follower_uid, followed_uid)
        )
    
    def unfollow(self, follower_uid: int, followed_uid: int) -> bool:
        cursor = self.db.execute(
            'DELETE FROM connections WHERE follower_uid = %s AND followed_uid = %s',
            (follower_uid, followed_uid)
        )
        return cursor.rowcount > 0
    
    def get_followers(self, uid: int) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT c.*, u.name, u.user_email FROM connections c
               JOIN users u ON c.follower_uid = u.uid
               WHERE c.followed_uid = %s''',
            (uid,)
        )
    
    def get_following(self, uid: int) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT c.*, u.name, u.user_email FROM connections c
               JOIN users u ON c.followed_uid = u.uid
               WHERE c.follower_uid = %s''',
            (uid,)
        )
    
    def is_following(self, follower_uid: int, followed_uid: int) -> bool:
        result = self.db.fetch_one(
            'SELECT 1 FROM connections WHERE follower_uid = %s AND followed_uid = %s',
            (follower_uid, followed_uid)
        )
        return result is not None

