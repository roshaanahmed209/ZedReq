"""Pydantic schemas for admin operations"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class AdminLogin(BaseModel):
    """Admin login request schema (password length not enforced here; DB stores strong passwords)"""
    username: str = Field(..., min_length=1, max_length=50, description="Username or email")
    password: str = Field(..., min_length=1, max_length=512, description="Password")


class AdminResponse(BaseModel):
    """Admin user response schema"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    last_login: Optional[str] = None
    created_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class AdminLoginResponse(BaseModel):
    """Admin login response schema"""
    admin: AdminResponse
    access_token: str
    token_type: str = "bearer"


class AdminCreate(BaseModel):
    """Admin creation request schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=512)
    role: str = Field(default="admin", pattern="^(admin|super_admin)$")


class UserListResponse(BaseModel):
    """User list response schema"""
    users: list[dict]
    total: int
    page: int
    limit: int
    pages: int


class UserDetailsResponse(BaseModel):
    """User details response schema - accepts the full user dict from admin_service"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    profile_url: Optional[str] = None
    subscription: Optional[dict] = None
    stats: Optional[dict] = None
    last_login: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChangePlanRequest(BaseModel):
    """Request schema for changing a user's plan"""
    plan: str = Field(..., pattern="^(free|pro|premium|enterprise)$", description="New plan: free, pro, premium, or enterprise")


class CancelSubscriptionRequest(BaseModel):
    """Request schema for cancelling a subscription"""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for cancellation")


class SuspendRequest(BaseModel):
    """Request schema for suspending a user"""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for suspension")


class ResetPasswordRequest(BaseModel):
    """Request schema for resetting a user's password"""
    new_password: str = Field(..., min_length=8, max_length=128, description="New password for the user")


class Disable2FARequest(BaseModel):
    """Request schema for disabling 2FA"""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for disabling 2FA")


class DeleteUserRequest(BaseModel):
    """Request schema for deleting (soft) a user"""
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for deletion")


class SendNotificationRequest(BaseModel):
    """Request schema for sending a notification to a user"""
    subject: str = Field(..., min_length=1, max_length=200, description="Notification subject")
    message: str = Field(..., min_length=1, max_length=2000, description="Notification message")


class AssignEnterprisePlanRequest(BaseModel):
    """Request schema for assigning enterprise plan to a user by email"""
    email: EmailStr = Field(..., description="Registered user email to assign enterprise plan")


class RevenueAnalyticsResponse(BaseModel):
    """Revenue analytics response schema"""
    revenue_by_period: list[dict]
    total_revenue: float
    total_transactions: int


class CostAnalyticsResponse(BaseModel):
    """Cost analytics response schema"""
    costs_by_category: list[dict]
    total_costs: float


class CashFlowResponse(BaseModel):
    """Cash flow response schema"""
    revenue: dict
    costs: dict
    net_cash_flow: float
    profit_margin: float


class SubscriptionMetricsResponse(BaseModel):
    """Subscription metrics response schema"""
    total_users: int
    active_subscriptions: int
    free_users: int
    plans_breakdown: dict
    mrr: float
    conversion_rate: float


class EnterpriseInquiryItem(BaseModel):
    """One enterprise sales lead from the main app"""

    id: int
    user_id: int
    contact_email: str
    user_email: Optional[str] = None
    username: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class EnterpriseInquiryListResponse(BaseModel):
    """Paginated enterprise inquiries"""

    items: list[EnterpriseInquiryItem]
    total: int
    page: int
    limit: int
    pages: int


class EnterpriseInquiryStatusUpdate(BaseModel):
    """Admin workflow status for a lead"""

    status: str = Field(..., pattern="^(new|contacted|closed)$")
