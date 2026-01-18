"""Notification Service - Notification management"""
from typing import List, Dict, Any, Optional

from models.notification import Notification
from models.user import User


class NotificationService:
    """Notification management service"""
    
    def __init__(self, db):
        self.db = db
        self.notification_model = Notification(db)
        self.user_model = User(db)
    
    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str = None,
        related_user_id: int = None,
        related_request_id: int = None
    ) -> Dict[str, Any]:
        """Create a new notification"""
        notification = self.notification_model.create(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_user_id=related_user_id,
            related_request_id=related_request_id
        )
        
        if not notification:
            raise Exception("Failed to create notification")
        
        return self._format_notification(notification)
    
    def get_notifications(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's notifications"""
        notifications = self.notification_model.get_user_notifications(
            user_id=user_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only
        )
        
        return [self._format_notification_with_user(n) for n in notifications]
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return self.notification_model.get_unread_count(user_id)
    
    def mark_as_read(self, notification_id: int, user_id: int) -> None:
        """Mark a notification as read"""
        notification = self.notification_model.find_by_id(notification_id)
        
        if not notification:
            raise LookupError("Notification not found")
        
        if notification['user_id'] != user_id:
            raise PermissionError("You cannot modify this notification")
        
        self.notification_model.mark_as_read(notification_id)
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read"""
        return self.notification_model.mark_all_as_read(user_id)
    
    def delete_notification(self, notification_id: int, user_id: int) -> None:
        """Delete a notification"""
        notification = self.notification_model.find_by_id(notification_id)
        
        if not notification:
            raise LookupError("Notification not found")
        
        if notification['user_id'] != user_id:
            raise PermissionError("You cannot delete this notification")
        
        self.notification_model.delete(notification_id)
    
    def _format_notification(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Format notification for response"""
        return {
            "id": notification['id'],
            "user_id": notification['user_id'],
            "type": notification['type'],
            "title": notification['title'],
            "message": notification.get('message'),
            "related_user_id": notification.get('related_user_id'),
            "related_request_id": notification.get('related_request_id'),
            "is_read": notification['is_read'],
            "created_at": notification['created_at']
        }
    
    def _format_notification_with_user(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Format notification with related user info"""
        result = {
            "id": notification['id'],
            "user_id": notification['user_id'],
            "type": notification['type'],
            "title": notification['title'],
            "message": notification.get('message'),
            "related_request_id": notification.get('related_request_id'),
            "is_read": notification['is_read'],
            "created_at": notification['created_at'],
            "related_user": None
        }
        
        # Include related user if present
        if notification.get('related_user_uid'):
            result["related_user"] = {
                "id": notification['related_user_uid'],
                "username": notification.get('related_username'),
                "name": notification.get('related_name'),
                "profile_pic": notification.get('related_profile_pic')
            }
        
        return result
