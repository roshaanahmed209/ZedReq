"""Analytics router"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from dependencies.database import get_db
from dependencies.auth import require_admin_role
from services.admin_service import AdminService
from schemas.admin import (
    RevenueAnalyticsResponse,
    CostAnalyticsResponse,
    CashFlowResponse,
    SubscriptionMetricsResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/analytics", tags=["Analytics"])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Get admin service instance"""
    return AdminService(db)


@router.get("/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get revenue analytics"""
    try:
        result = service.get_revenue_analytics(start_date, end_date, group_by)
        return RevenueAnalyticsResponse(**result)
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue analytics"
        )


@router.get("/costs", response_model=CostAnalyticsResponse)
async def get_cost_analytics(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get cost analytics"""
    try:
        result = service.get_cost_analytics(start_date, end_date)
        return CostAnalyticsResponse(**result)
    except Exception as e:
        logger.error(f"Error getting cost analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cost analytics"
        )


@router.get("/cash-flow", response_model=CashFlowResponse)
async def get_cash_flow(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get cash flow analysis"""
    try:
        result = service.get_cash_flow(start_date, end_date)
        return CashFlowResponse(**result)
    except Exception as e:
        logger.error(f"Error getting cash flow: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cash flow analysis"
        )


@router.get("/subscriptions", response_model=SubscriptionMetricsResponse)
async def get_subscription_metrics(
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get subscription metrics"""
    try:
        result = service.get_subscription_metrics()
        return SubscriptionMetricsResponse(**result)
    except Exception as e:
        logger.error(f"Error getting subscription metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription metrics"
        )


@router.get("/dashboard")
async def get_dashboard_summary(
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get dashboard summary with all key metrics"""
    try:
        result = service.get_dashboard_summary()
        return result
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary"
        )
