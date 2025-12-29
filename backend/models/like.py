from typing import Optional, Dict, Any, List
import psycopg
from ..config.database import Database

class Like:
    """Like model"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, post_id: int, user_id: str) -> bool:
        """Create a like"""
        try:
            self.db.execute(
                'INSERT INTO likes (post_id, user_id) VALUES (%s, %s)',
                (post_id, user_id)
            )
            return True
        except psycopg.errors.UniqueViolation:
            return False  # Already liked
        except Exception as e:
            if 'unique' in str(e).lower():
                return False  # Already liked
            raise
    
    def delete(self, post_id: int, user_id: str) -> bool:
        """Delete a like"""
        cursor = self.db.execute(
            'DELETE FROM likes WHERE post_id = %s AND user_id = %s',
            (post_id, user_id)
        )
        return cursor.rowcount > 0
    
    def toggle(self, post_id: int, user_id: str) -> bool:
        """Toggle like status"""
        existing = self.db.fetch_one(
            'SELECT id FROM likes WHERE post_id = %s AND user_id = %s',
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
            'SELECT COUNT(*) as count FROM likes WHERE post_id = %s',
            (post_id,)
        )
        return result['count'] if result else 0
    
    def exists(self, post_id: int, user_id: str) -> bool:
        """Check if like exists"""
        result = self.db.fetch_one(
            'SELECT id FROM likes WHERE post_id = %s AND user_id = %s',
            (post_id, user_id)
        )
        return result is not None
