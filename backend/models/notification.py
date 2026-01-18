"""Notification Model - Uses integer user IDs referencing users(uid)"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

# SQL to create this table - run via migration if it doesn't exist
TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    related_user_id INTEGER REFERENCES users(uid) ON DELETE SET NULL,
    related_request_id INTEGER REFERENCES connection_requests(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notif_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
'''


class Notification(BaseModel):
    """Notification model using integer user IDs"""
    table_name = 'notifications'
    
    def create(
        self, 
        user_id: int, 
        notification_type: str, 
        title: str, 
        message: str = None,
        related_user_id: int = None,
        related_request_id: int = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new notification"""
        return self.db.execute_returning(
            '''INSERT INTO notifications (user_id, type, title, message, related_user_id, related_request_id)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING *''',
            (user_id, notification_type, title, message, related_user_id, related_request_id)
        )
    
    def find_by_id(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """Find notification by ID"""
        return self.db.fetch_one(
            'SELECT * FROM notifications WHERE id = %s',
            (notification_id,)
        )
    
    def get_user_notifications(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user with related user info"""
        unread_filter = "AND n.is_read = FALSE" if unread_only else ""
        
        return self.db.fetch_all(
            f'''SELECT n.*, 
                       u.uid as related_user_uid, u.username as related_username, 
                       u.name as related_name, d.profile_pic as related_profile_pic
               FROM notifications n
               LEFT JOIN users u ON n.related_user_id = u.uid
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE n.user_id = %s {unread_filter}
               ORDER BY n.created_at DESC
               LIMIT %s OFFSET %s''',
            (user_id, limit, offset)
        )
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        result = self.db.fetch_one(
            'SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE',
            (user_id,)
        )
        return result['count'] if result else 0
    
    def mark_as_read(self, notification_id: int) -> Optional[Dict[str, Any]]:
        """Mark a notification as read"""
        return self.db.execute_returning(
            'UPDATE notifications SET is_read = TRUE WHERE id = %s RETURNING *',
            (notification_id,)
        )
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        cursor = self.db.execute(
            'UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE',
            (user_id,)
        )
        return cursor.rowcount
    
    def delete(self, notification_id: int) -> bool:
        """Delete a notification"""
        cursor = self.db.execute(
            'DELETE FROM notifications WHERE id = %s',
            (notification_id,)
        )
        return cursor.rowcount > 0
    
    def delete_old_notifications(self, user_id: int, keep_days: int = 30) -> int:
        """Delete notifications older than specified days"""
        cursor = self.db.execute(
            '''DELETE FROM notifications 
               WHERE user_id = %s AND created_at < CURRENT_TIMESTAMP - INTERVAL '%s days' ''',
            (user_id, keep_days)
        )
        return cursor.rowcount
