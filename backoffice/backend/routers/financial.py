"""Financial management router"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel
from dependencies.database import get_db
from dependencies.auth import require_admin_role
from services.financial_service import FinancialService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/financial", tags=["Financial Management"])


def get_financial_service(db: Session = Depends(get_db)) -> FinancialService:
    """Get financial service instance"""
    return FinancialService(db)


class RevenueTransactionCreate(BaseModel):
    """Revenue transaction creation schema"""
    transaction_type: str
    amount: float
    currency: str = "USD"
    user_id: Optional[int] = None
    plan_type: Optional[str] = None
    provider: Optional[str] = None
    provider_transaction_id: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: str = "pending"


class CostTransactionCreate(BaseModel):
    """Cost transaction creation schema"""
    cost_category: str
    amount: float
    service_name: Optional[str] = None
    currency: str = "USD"
    unit_type: Optional[str] = None
    quantity: Optional[float] = None
    user_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    transaction_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_admin: dict = Depends(require_admin_role),
    service: FinancialService = Depends(get_financial_service)
):
    """Get paginated list of revenue transactions"""
    try:
        result = service.get_transactions(
            page, limit, transaction_type, status, start_date, end_date
        )
        return result
    except Exception as e:
        logger.error(f"Error getting transactions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )


@router.post("/revenue")
async def create_revenue_transaction(
    transaction_data: RevenueTransactionCreate,
    current_admin: dict = Depends(require_admin_role),
    service: FinancialService = Depends(get_financial_service)
):
    """Create a revenue transaction"""
    try:
        transaction = service.create_revenue_transaction(
            transaction_type=transaction_data.transaction_type,
            amount=transaction_data.amount,
            currency=transaction_data.currency,
            user_id=transaction_data.user_id,
            plan_type=transaction_data.plan_type,
            provider=transaction_data.provider,
            provider_transaction_id=transaction_data.provider_transaction_id,
            description=transaction_data.description,
            metadata=transaction_data.metadata,
            status=transaction_data.status
        )
        return {
            "success": True,
            "message": "Revenue transaction created",
            "transaction": transaction.to_dict()
        }
    except Exception as e:
        logger.error(f"Error creating revenue transaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create revenue transaction"
        )


@router.post("/cost")
async def create_cost_transaction(
    transaction_data: CostTransactionCreate,
    current_admin: dict = Depends(require_admin_role),
    service: FinancialService = Depends(get_financial_service)
):
    """Create a cost transaction"""
    try:
        transaction = service.create_cost_transaction(
            cost_category=transaction_data.cost_category,
            amount=transaction_data.amount,
            service_name=transaction_data.service_name,
            currency=transaction_data.currency,
            unit_type=transaction_data.unit_type,
            quantity=transaction_data.quantity,
            user_id=transaction_data.user_id,
            metadata=transaction_data.metadata
        )
        return {
            "success": True,
            "message": "Cost transaction created",
            "transaction": transaction.to_dict()
        }
    except Exception as e:
        logger.error(f"Error creating cost transaction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create cost transaction"
        )


@router.get("/summaries")
async def get_financial_summaries(
    period_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_admin: dict = Depends(require_admin_role),
    service: FinancialService = Depends(get_financial_service)
):
    """Get financial summaries"""
    try:
        summaries = service.get_financial_summaries(
            period_type, start_date, end_date, limit
        )
        return {"summaries": summaries}
    except Exception as e:
        logger.error(f"Error getting financial summaries: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve financial summaries"
        )


@router.post("/summaries/generate")
async def generate_financial_summary(
    period_type: str = Body(..., regex="^(daily|weekly|monthly|yearly)$"),
    period_start: date = Body(...),
    period_end: date = Body(...),
    current_admin: dict = Depends(require_admin_role),
    service: FinancialService = Depends(get_financial_service)
):
    """Generate financial summary for a period"""
    try:
        summary = service.generate_financial_summary(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end
        )
        return {
            "success": True,
            "message": "Financial summary generated",
            "summary": summary.to_dict()
        }
    except Exception as e:
        logger.error(f"Error generating financial summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate financial summary"
        )


@router.get("/costs")
async def get_cost_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    cost_category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_admin: dict = Depends(require_admin_role),
    service: FinancialService = Depends(get_financial_service)
):
    """Get paginated list of cost transactions"""
    try:
        result = service.get_cost_transactions(
            page, limit, cost_category, start_date, end_date
        )
        return result
    except Exception as e:
        logger.error(f"Error getting cost transactions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cost transactions"
        )
