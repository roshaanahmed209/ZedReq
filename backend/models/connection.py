from typing import Optional, Dict, Any, List
from psycopg2 import errors as pg_errors
from ..config.database import Database

class Connection:
    """Connection model"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, user1_id: str, user2_id: str, status: str = 'pending') -> Optional[Dict[str, Any]]:
        """Create a connection (user IDs are UUIDs)"""
        # Ensure user1_id < user2_id for consistency (compare as strings for UUIDs)
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        
        try:
            return self.db.execute_returning(
                '''INSERT INTO connections (user1_id, user2_id, status) VALUES (%s, %s, %s)
                   RETURNING *''',
                (id1, id2, status)
            )
        except Exception as e:
            if isinstance(e.__cause__, pg_errors.UniqueViolation) or 'unique' in str(e).lower():
                return None  # Connection already exists
            raise
    
    def find_by_id(self, connection_id: int) -> Optional[Dict[str, Any]]:
        """Find connection by ID"""
        return self.db.fetch_one(
            'SELECT * FROM connections WHERE id = %s',
            (connection_id,)
        )
    
    def find_connection(self, user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
        """Find connection between two users (user IDs are UUIDs)"""
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        return self.db.fetch_one(
            'SELECT * FROM connections WHERE user1_id = %s AND user2_id = %s',
            (id1, id2)
        )
    
    def update_status(self, user1_id: str, user2_id: str, status: str) -> bool:
        """Update connection status (user IDs are UUIDs)"""
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        cursor = self.db.execute(
            '''UPDATE connections SET status = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE user1_id = %s AND user2_id = %s''',
            (status, id1, id2)
        )
        return cursor.rowcount > 0
    
    def delete(self, user1_id: str, user2_id: str) -> bool:
        """Delete connection (user IDs are UUIDs)"""
        id1, id2 = (user1_id, user2_id) if user1_id < user2_id else (user2_id, user1_id)
        cursor = self.db.execute(
            'DELETE FROM connections WHERE user1_id = %s AND user2_id = %s',
            (id1, id2)
        )
        return cursor.rowcount > 0
    
    def get_connections(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all connections for a user"""
        query = '''
            SELECT c.*, 
                   CASE WHEN c.user1_id = %s THEN u2.id ELSE u1.id END as other_user_id,
                   CASE WHEN c.user1_id = %s THEN u2.username ELSE u1.username END as other_username,
                   CASE WHEN c.user1_id = %s THEN u2.full_name ELSE u1.full_name END as other_full_name
            FROM connections c
            JOIN users u1 ON c.user1_id = u1.id
            JOIN users u2 ON c.user2_id = u2.id
            WHERE (c.user1_id = %s OR c.user2_id = %s)
        '''
        params = [user_id, user_id, user_id, user_id, user_id]
        
        if status:
            query += ' AND c.status = %s'
            params.append(status)
        
        query += ' ORDER BY c.created_at DESC'
        
        return self.db.fetch_all(query, tuple(params))
    
    def get_count(self, user_id: str, status: str = 'accepted') -> int:
        """Get connection count"""
        result = self.db.fetch_one(
            'SELECT COUNT(*) as count FROM connections WHERE (user1_id = %s OR user2_id = %s) AND status = %s',
            (user_id, user_id, status)
        )
        return result['count'] if result else 0
