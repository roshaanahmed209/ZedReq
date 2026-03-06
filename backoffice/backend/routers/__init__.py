"""Routers package"""
from .auth import router as auth_router
from .users import router as users_router
from .analytics import router as analytics_router
from .financial import router as financial_router
from .activity import router as activity_router
from .monitoring import router as monitoring_router
from .collector import router as collector_router

__all__ = [
    "auth_router",
    "users_router",
    "analytics_router",
    "financial_router",
    "activity_router",
    "monitoring_router",
    "collector_router",
]
