"""Notification Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .user import UserSummary


class NotificationResponse(BaseModel):
    """Notification response"""
    id: int
    user_id: int
    type: str
    title: str
    message: Optional[str] = None
    related_user: Optional[UserSummary] = None
    related_request_id: Optional[int] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    """Unread notification count"""
    count: int


class NotificationCreate(BaseModel):
    """Create notification (internal use)"""
    user_id: int
    type: str
    title: str
    message: Optional[str] = None
    related_user_id: Optional[int] = None
    related_request_id: Optional[int] = None
