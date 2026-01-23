"""Notification Service - Using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from models.orm import Notification, User


class NotificationService:
    """Notification management service using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
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
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_user_id=related_user_id,
            related_request_id=related_request_id
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return self._format_notification(notification)
    
    def get_notifications(
        self,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user's notifications"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = (
            query
            .order_by(desc(Notification.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [self._format_notification_with_user(n) for n in notifications]
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .count()
        )
    
    def mark_as_read(self, notification_id: int, user_id: int) -> None:
        """Mark a notification as read"""
        notification = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
            .first()
        )
        
        if not notification:
            raise LookupError("Notification not found")
        
        notification.is_read = True
        self.db.commit()
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read"""
        count = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .update({'is_read': True})
        )
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: int, user_id: int) -> None:
        """Delete a notification"""
        notification = (
            self.db.query(Notification)
            .filter(
                and_(
                    Notification.id == notification_id,
                    Notification.user_id == user_id
                )
            )
            .first()
        )
        
        if not notification:
            raise LookupError("Notification not found")
        
        self.db.delete(notification)
        self.db.commit()
    
    def _format_notification(self, notification: Notification) -> Dict[str, Any]:
        """Format notification for response"""
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "related_user_id": notification.related_user_id,
            "related_request_id": notification.related_request_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None
        }
    
    def _format_notification_with_user(self, notification: Notification) -> Dict[str, Any]:
        """Format notification with related user info"""
        result = {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "title": notification.title,
            "message": notification.message,
            "related_request_id": notification.related_request_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "related_user": None
        }
        
        # Include related user if present
        if notification.related_user:
            result["related_user"] = {
                "id": notification.related_user.uid,
                "username": notification.related_user.username,
                "name": notification.related_user.name,
                "profile_pic": None  # Would need to join with description table for profile_pic
            }
        
        return result
