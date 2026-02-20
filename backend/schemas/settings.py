"""Settings Schemas"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from utils.api_security import sanitize_text_for_storage, validate_url_safe


class ProfileUpdate(BaseModel):
    """Profile update request"""
    profile_pic: Optional[str] = None
    cover_pic: Optional[str] = None
    resume: Optional[str] = None  # Cloudinary URL or file data
    interests: Optional[str] = None  # Comma-separated interests
    location: Optional[str] = Field(None, max_length=150)
    
    @validator('profile_pic')
    def validate_profile_pic_url(cls, v):
        """Validate and sanitize profile picture URL"""
        if v is None or v == "":
            return v
        try:
            return validate_url_safe(v, allowed_schemes=['http', 'https'])
        except ValueError as e:
            raise ValueError(f"Invalid profile picture URL: {str(e)}")
    
    @validator('cover_pic')
    def validate_cover_pic_url(cls, v):
        """Validate and sanitize cover picture URL"""
        if v is None or v == "":
            return v
        try:
            return validate_url_safe(v, allowed_schemes=['http', 'https'])
        except ValueError as e:
            raise ValueError(f"Invalid cover picture URL: {str(e)}")
    
    @validator('resume')
    def validate_resume_url(cls, v):
        """Validate resume URL"""
        if v is None or v == "":
            return v
        try:
            return validate_url_safe(v, allowed_schemes=['http', 'https'])
        except ValueError as e:
            raise ValueError(f"Invalid resume URL: {str(e)}")
    
    @validator('interests')
    def sanitize_interests(cls, v):
        """Sanitize interests input"""
        if v is None or v == "":
            return v
        return sanitize_text_for_storage(str(v), max_length=1000)
    
    @validator('location')
    def sanitize_location(cls, v):
        """Sanitize location input"""
        if v is None or v == "":
            return v
        return sanitize_text_for_storage(str(v), max_length=150)


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=25)


class EmailUpdate(BaseModel):
    """Email update request"""
    email: EmailStr


class TwoFactorUpdate(BaseModel):
    """Two-factor authentication update request"""
    enabled: bool


class SubscriptionUpdate(BaseModel):
    """Subscription update request"""
    plan: str = Field(..., pattern="^(free|pro|premium)$")


class SubscriptionInfo(BaseModel):
    """Subscription information response"""
    plan: str = "free"
    status: str = "inactive"
    subscription_start: Optional[str] = None
    subscription_end: Optional[str] = None
    
    class Config:
        # Allow None values to be converted to defaults
        orm_mode = False