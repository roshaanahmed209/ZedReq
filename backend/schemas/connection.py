"""Connection Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .user import UserSummary


class ConnectionRequestCreate(BaseModel):
    """Create connection request"""
    message: Optional[str] = None


class ConnectionRequestResponse(BaseModel):
    """Connection request response"""
    id: int
    sender_id: int
    receiver_id: int
    status: str
    message: Optional[str] = None
    sender: Optional[UserSummary] = None
    receiver: Optional[UserSummary] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ConnectionResponse(BaseModel):
    """Accepted connection response"""
    id: int
    user_id: int
    connected_user_id: int
    connected_user: Optional[UserSummary] = None
    connected_at: datetime
    
    class Config:
        from_attributes = True
