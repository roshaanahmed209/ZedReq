"""Network Schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class NetworkUserResponse(BaseModel):
    """User in network discovery/connections list"""
    id: int
    username: str
    name: str
    profile_pic: Optional[str] = None
    short_desc: Optional[str] = None
    current_status: Optional[str] = None
    skills: Optional[str] = None
    
    class Config:
        from_attributes = True


class SuggestedUserResponse(NetworkUserResponse):
    """User suggestion with mutual connections count"""
    mutual_connections: int = 0
    mutual_connection_names: Optional[List[str]] = None


class ConnectionStats(BaseModel):
    """User's connection statistics"""
    total_connections: int
    pending_requests_received: int
    pending_requests_sent: int
