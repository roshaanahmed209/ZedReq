from typing import Optional, Dict, Any, List
from ..config.database import Database

class Connection:
    """Connection model"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, user1_id: int, user2_id: int, status: str = 'pending') -> Optional[Dict[str, Any]]:
        """Create a connection"""
        # Ensure user1_id < user2_id for consistency
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        
        try:
            cursor = self.db.execute(
                'INSERT INTO connections (user1_id, user2_id, status) VALUES (?, ?, ?)',
                (id1, id2, status)
            )
            return self.find_by_id(cursor.lastrowid)
        except Exception as e:
            if 'UNIQUE' in str(e):
                return None  # Connection already exists
            raise
    
    def find_by_id(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """Find connection by ID"""
        return self.db.fetch_one(
            'SELECT * FROM connections WHERE id = ?',
            (connection_id,)
        )
    
    def find_connection(self, user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
        """Find connection between two users"""
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        return self.db.fetch_one(
            'SELECT * FROM connections WHERE user1_id = ? AND user2_id = ?',
            (id1, id2)
        )
    
    def update_status(self, user1_id: int, user2_id: int, status: str) -> bool:
        """Update connection status"""
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        cursor = self.db.execute(
            '''UPDATE connections SET status = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE user1_id = ? AND user2_id = ?''',
            (status, id1, id2)
        )
        return cursor.rowcount > 0
    
    def delete(self, user1_id: int, user2_id: int) -> bool:
        """Delete connection"""
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        cursor = self.db.execute(
            'DELETE FROM connections WHERE user1_id = ? AND user2_id = ?',
            (id1, id2)
        )
        return cursor.rowcount > 0
    
    def get_connections(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all connections for a user"""
        query = '''
            SELECT c.*, 
                   CASE WHEN c.user1_id = ? THEN u2.id ELSE u1.id END as other_user_id,
                   CASE WHEN c.user1_id = ? THEN u2.username ELSE u1.username END as other_username,
                   CASE WHEN c.user1_id = ? THEN u2.full_name ELSE u1.full_name END as other_full_name
            FROM connections c
            JOIN users u1 ON c.user1_id = u1.id
            JOIN users u2 ON c.user2_id = u2.id
            WHERE (c.user1_id = ? OR c.user2_id = ?)
        '''
        params = [user_id, user_id, user_id, user_id, user_id]
        
        if status:
            query += ' AND c.status = ?'
            params.append(status)
        
        query += ' ORDER BY c.created_at DESC'
        
        return self.db.fetch_all(query, tuple(params))
    
    def get_count(self, user_id: int, status: str = 'accepted') -> int:
        """Get connection count"""
        result = self.db.fetch_one(
            'SELECT COUNT(*) as count FROM connections WHERE (user1_id = ? OR user2_id = ?) AND status = ?',
            (user_id, user_id, status)
        )
        return result['count'] if result else 0
