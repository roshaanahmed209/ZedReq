from typing import Optional, Dict, Any, List
from ..config.database import Database

class Post:
    """Post model"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, user_id: int, content: str) -> Dict[str, Any]:
        """Create a new post"""
        cursor = self.db.execute(
            'INSERT INTO posts (user_id, content) VALUES (?, ?)',
            (user_id, content.strip())
        )
        return self.find_by_id(cursor.lastrowid)
    
    def find_by_id(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Find post by ID"""
        return self.db.fetch_one(
            'SELECT * FROM posts WHERE id = ?',
            (post_id,)
        )
    
    def find_all(self, user_id: Optional[int] = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Find all posts with user info and like status"""
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
                (SELECT COUNT(*) FROM likes WHERE post_id = p.id AND user_id = ?) as is_liked
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        '''
        return self.db.fetch_all(query, (user_id or 0, limit, offset))
    
    def find_by_user_id(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Find posts by user ID"""
        return self.db.fetch_all(
            'SELECT * FROM posts WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?',
            (user_id, limit, offset)
        )
    
    def update(self, post_id: int, content: str) -> Optional[Dict[str, Any]]:
        """Update post"""
        self.db.execute(
            'UPDATE posts SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (content.strip(), post_id)
        )
        return self.find_by_id(post_id)
    
    def delete(self, post_id: int) -> bool:
        """Delete post"""
        cursor = self.db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        return cursor.rowcount > 0
