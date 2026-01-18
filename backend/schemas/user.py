"""User Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    name: str
    email: Optional[str] = None


class UserProfile(UserBase):
    """User profile with additional info"""
    id: int
    profile_pic: Optional[str] = None
    short_desc: Optional[str] = None
    about: Optional[str] = None
    skills: Optional[str] = None
    current_status: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    name: Optional[str] = Field(None, max_length=100)
    short_desc: Optional[str] = None
    about: Optional[str] = None
    skills: Optional[str] = None
    current_status: Optional[str] = None
    profile_pic: Optional[str] = None


class UserSummary(BaseModel):
    """Minimal user info for lists"""
    id: int
    username: str
    name: str
    profile_pic: Optional[str] = None
    
    class Config:
        from_attributes = True
