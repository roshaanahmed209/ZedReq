"""Connection Request Model - Uses integer user IDs referencing users(uid)"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

# SQL to create this table - run via migration if it doesn't exist
TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS connection_requests (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sender_id, receiver_id)
);
CREATE INDEX IF NOT EXISTS idx_conn_req_sender ON connection_requests(sender_id);
CREATE INDEX IF NOT EXISTS idx_conn_req_receiver ON connection_requests(receiver_id);
CREATE INDEX IF NOT EXISTS idx_conn_req_status ON connection_requests(status);
'''


class ConnectionRequest(BaseModel):
    """Connection request model using integer user IDs"""
    table_name = 'connection_requests'
    
    def create(self, sender_id: int, receiver_id: int, message: str = None) -> Optional[Dict[str, Any]]:
        """Create a new connection request"""
        return self.db.execute_returning(
            '''INSERT INTO connection_requests (sender_id, receiver_id, message)
               VALUES (%s, %s, %s)
               ON CONFLICT (sender_id, receiver_id) DO NOTHING
               RETURNING *''',
            (sender_id, receiver_id, message)
        )
    
    def find_by_id(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Find request by ID"""
        return self.db.fetch_one(
            'SELECT * FROM connection_requests WHERE id = %s',
            (request_id,)
        )
    
    def find_by_users(self, sender_id: int, receiver_id: int) -> Optional[Dict[str, Any]]:
        """Find request between two users"""
        return self.db.fetch_one(
            '''SELECT * FROM connection_requests 
               WHERE sender_id = %s AND receiver_id = %s''',
            (sender_id, receiver_id)
        )
    
    def find_pending_between_users(self, user1_id: int, user2_id: int) -> Optional[Dict[str, Any]]:
        """Find any pending request between two users (either direction)"""
        return self.db.fetch_one(
            '''SELECT * FROM connection_requests 
               WHERE status = 'pending' AND (
                   (sender_id = %s AND receiver_id = %s) OR
                   (sender_id = %s AND receiver_id = %s)
               )''',
            (user1_id, user2_id, user2_id, user1_id)
        )
    
    def get_pending_received(self, user_id: int) -> List[Dict[str, Any]]:
        """Get pending requests received by user with sender info"""
        return self.db.fetch_all(
            '''SELECT cr.*, 
                      u.uid as sender_user_id, u.username as sender_username, 
                      u.name as sender_name, d.profile_pic as sender_profile_pic
               FROM connection_requests cr
               JOIN users u ON cr.sender_id = u.uid
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE cr.receiver_id = %s AND cr.status = 'pending'
               ORDER BY cr.created_at DESC''',
            (user_id,)
        )
    
    def get_pending_sent(self, user_id: int) -> List[Dict[str, Any]]:
        """Get pending requests sent by user with receiver info"""
        return self.db.fetch_all(
            '''SELECT cr.*, 
                      u.uid as receiver_user_id, u.username as receiver_username, 
                      u.name as receiver_name, d.profile_pic as receiver_profile_pic
               FROM connection_requests cr
               JOIN users u ON cr.receiver_id = u.uid
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE cr.sender_id = %s AND cr.status = 'pending'
               ORDER BY cr.created_at DESC''',
            (user_id,)
        )
    
    def update_status(self, request_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Update request status (pending, accepted, rejected)"""
        return self.db.execute_returning(
            '''UPDATE connection_requests 
               SET status = %s, updated_at = CURRENT_TIMESTAMP
               WHERE id = %s
               RETURNING *''',
            (status, request_id)
        )
    
    def delete(self, request_id: int) -> bool:
        """Delete a connection request"""
        cursor = self.db.execute(
            'DELETE FROM connection_requests WHERE id = %s',
            (request_id,)
        )
        return cursor.rowcount > 0
