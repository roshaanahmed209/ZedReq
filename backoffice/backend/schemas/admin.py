"""Pydantic schemas for admin operations"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class AdminLogin(BaseModel):
    """Admin login request schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username or email")
    password: str = Field(..., min_length=12, max_length=128, description="Password")


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
    password: str = Field(..., min_length=12, max_length=128)
    role: str = Field(default="admin", pattern="^(admin|super_admin)$")


class UserListResponse(BaseModel):
    """User list response schema"""
    users: list[dict]
    total: int
    page: int
    limit: int
    pages: int


class UserDetailsResponse(BaseModel):
    """User details response schema"""
    user: dict
    payment: Optional[dict] = None
    stats: dict


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
