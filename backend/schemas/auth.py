"""Authentication Schemas"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserRegister(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """User login request"""
    username: str  # Can be username or email
    password: str


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional["UserResponse"] = None
    # 2FA fields
    requires_2fa: bool = False
    temp_token: Optional[str] = None
    message: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User information response"""
    id: int
    username: str
    email: str
    name: str
    profile_pic: Optional[str] = None
    short_desc: Optional[str] = None
    about: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Update forward reference
TokenResponse.model_rebuild()
