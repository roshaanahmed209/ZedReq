from typing import Optional, Dict, Any, List
from ..config.database import Database

class Like:
    """Like model"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, post_id: int, user_id: int) -> bool:
        """Create a like"""
        try:
            self.db.execute(
                'INSERT INTO likes (post_id, user_id) VALUES (?, ?)',
                (post_id, user_id)
            )
            return True
        except Exception as e:
            if 'UNIQUE' in str(e):
                return False  # Already liked
            raise
    
    def delete(self, post_id: int, user_id: int) -> bool:
        """Delete a like"""
        cursor = self.db.execute(
            'DELETE FROM likes WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        )
        return cursor.rowcount > 0
    
    def toggle(self, post_id: int, user_id: int) -> bool:
        """Toggle like status"""
        existing = self.db.fetch_one(
            'SELECT id FROM likes WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        )
        
        if existing:
            self.delete(post_id, user_id)
            return False  # Unliked
        else:
            self.create(post_id, user_id)
            return True  # Liked
    
    def get_count(self, post_id: int) -> int:
        """Get like count for a post"""
        result = self.db.fetch_one(
            'SELECT COUNT(*) as count FROM likes WHERE post_id = ?',
            (post_id,)
        )
        return result['count'] if result else 0
    
    def exists(self, post_id: int, user_id: int) -> bool:
        """Check if like exists"""
        result = self.db.fetch_one(
            'SELECT id FROM likes WHERE post_id = ? AND user_id = ?',
            (post_id, user_id)
        )
        return result is not None
