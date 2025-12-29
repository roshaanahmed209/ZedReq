from typing import Optional, Dict, Any, List
from ..config.database import Database

class Post:
    """Post model"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, user_id: str, content: str) -> Dict[str, Any]:
        """Create a new post (user_id is UUID)"""
        return self.db.execute_returning(
            '''INSERT INTO posts (user_id, content) VALUES (%s, %s)
               RETURNING *''',
            (user_id, content.strip())
        )
    
    def find_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Find post by ID"""
        return self.db.fetch_one(
            'SELECT * FROM posts WHERE id = %s',
            (post_id,)
        )
    
    def find_all(self, user_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Find all posts with user info and like status (user_id is UUID)"""
        query = '''
            SELECT 
                p.id,
                p.user_id,
                p.content,
                p.created_at,
                u.username,
                u.full_name,
                u.avatar,
                (SELECT COUNT(*) FROM likes WHERE post_id = p.id) as like_count,
                CASE WHEN %s IS NOT NULL 
                    THEN (SELECT COUNT(*) FROM likes WHERE post_id = p.id AND user_id = %s::uuid)
                    ELSE 0 
                END as is_liked
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        '''
        return self.db.fetch_all(query, (user_id, user_id, limit, offset))
    
    def find_by_user_id(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Find posts by user UUID"""
        return self.db.fetch_all(
            'SELECT * FROM posts WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s',
            (user_id, limit, offset)
        )
    
    def update(self, post_id: int, content: str) -> Optional[Dict[str, Any]]:
        """Update post"""
        return self.db.execute_returning(
            '''UPDATE posts SET content = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE id = %s RETURNING *''',
            (content.strip(), post_id)
        )
    
    def delete(self, post_id: int) -> bool:
        """Delete post"""
        cursor = self.db.execute('DELETE FROM posts WHERE id = %s', (post_id,))
        return cursor.rowcount > 0
