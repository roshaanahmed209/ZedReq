"""Financial Tracking router"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from dependencies.database import get_db
from dependencies.auth import require_admin_role
from services.financial_tracking_service import FinancialTrackingService
from models.orm.bearable_cost import BearableCost
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/financial-tracking", tags=["Financial Tracking"])


def get_financial_tracking_service(db: Session = Depends(get_db)) -> FinancialTrackingService:
    """Get financial tracking service instance"""
    return FinancialTrackingService(db)


class SyncRequest(BaseModel):
    """Sync request schema"""
    user_id: Optional[int] = None


class BearableCostCreate(BaseModel):
    """Bearable cost creation schema"""
    cost_name: str
    amount: float
    is_fixed: bool = False
    unit_type: Optional[str] = None


class BearableCostUpdate(BaseModel):
    """Bearable cost update schema"""
    cost_name: Optional[str] = None
    amount: Optional[float] = None
    is_fixed: Optional[bool] = None
    unit_type: Optional[str] = None


@router.get("/profit")
async def get_net_profit(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_admin: dict = Depends(require_admin_role),
    service: FinancialTrackingService = Depends(get_financial_tracking_service)
):
    """Calculate net profit"""
    try:
        result = service.calculate_net_profit(start_date, end_date)
        return result
    except Exception as e:
        logger.error(f"Error calculating net profit: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate net profit"
        )


@router.get("/users/{user_id}/summary")
async def get_user_financial_summary(
    user_id: int,
    current_admin: dict = Depends(require_admin_role),
    service: FinancialTrackingService = Depends(get_financial_tracking_service)
):
    """Get user financial summary"""
    try:
        result = service.get_user_financial_summary(user_id)
        return result
    except Exception as e:
        logger.error(f"Error getting user financial summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user financial summary"
        )


@router.post("/sync")
async def sync_payment_summaries(
    request: SyncRequest = Body(...),
    current_admin: dict = Depends(require_admin_role),
    service: FinancialTrackingService = Depends(get_financial_tracking_service)
):
    """Sync payment summaries from main app"""
    try:
        result = service.sync_user_payment_summary(request.user_id)
        return result
    except Exception as e:
        logger.error(f"Error syncing payment summaries: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync payment summaries"
        )


@router.post("/sync/all")
async def sync_all_payment_summaries(
    current_admin: dict = Depends(require_admin_role),
    service: FinancialTrackingService = Depends(get_financial_tracking_service)
):
    """Sync all payment summaries from main app"""
    try:
        result = service.refresh_all_summaries()
        return result
    except Exception as e:
        logger.error(f"Error syncing all payment summaries: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync all payment summaries"
        )


@router.get("/costs")
async def get_bearable_costs(
    current_admin: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """List all bearable costs"""
    try:
        costs = db.query(BearableCost).order_by(BearableCost.id).all()
        return {
            'costs': [cost.to_dict() for cost in costs]
        }
    except Exception as e:
        logger.error(f"Error getting bearable costs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bearable costs"
        )


@router.post("/costs")
async def create_bearable_cost(
    cost_data: BearableCostCreate,
    current_admin: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Create a new bearable cost (admin only)"""
    try:
        # Check if cost_name already exists
        existing = db.query(BearableCost).filter(
            BearableCost.cost_name == cost_data.cost_name
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cost with name '{cost_data.cost_name}' already exists"
            )
        
        cost = BearableCost(
            cost_name=cost_data.cost_name,
            amount=cost_data.amount,
            is_fixed=cost_data.is_fixed,
            unit_type=cost_data.unit_type
        )
        
        db.add(cost)
        db.commit()
        db.refresh(cost)
        
        return {
            'success': True,
            'message': 'Bearable cost created',
            'cost': cost.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating bearable cost: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bearable cost"
        )


@router.put("/costs/{cost_id}")
async def update_bearable_cost(
    cost_id: int,
    cost_data: BearableCostUpdate,
    current_admin: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Update a bearable cost (admin only)"""
    try:
        cost = db.query(BearableCost).filter(BearableCost.id == cost_id).first()
        
        if not cost:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bearable cost not found"
            )
        
        # Check if cost_name is being changed and if new name already exists
        if cost_data.cost_name and cost_data.cost_name != cost.cost_name:
            existing = db.query(BearableCost).filter(
                BearableCost.cost_name == cost_data.cost_name,
                BearableCost.id != cost_id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cost with name '{cost_data.cost_name}' already exists"
                )
        
        # Update fields
        if cost_data.cost_name is not None:
            cost.cost_name = cost_data.cost_name
        if cost_data.amount is not None:
            cost.amount = cost_data.amount
        if cost_data.is_fixed is not None:
            cost.is_fixed = cost_data.is_fixed
        if cost_data.unit_type is not None:
            cost.unit_type = cost_data.unit_type
        
        db.commit()
        db.refresh(cost)
        
        return {
            'success': True,
            'message': 'Bearable cost updated',
            'cost': cost.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating bearable cost: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update bearable cost"
        )


@router.delete("/costs/{cost_id}")
async def delete_bearable_cost(
    cost_id: int,
    current_admin: dict = Depends(require_admin_role),
    db: Session = Depends(get_db)
):
    """Delete a bearable cost (admin only)"""
    try:
        cost = db.query(BearableCost).filter(BearableCost.id == cost_id).first()
        
        if not cost:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bearable cost not found"
            )
        
        db.delete(cost)
        db.commit()
        
        return {
            'success': True,
            'message': 'Bearable cost deleted'
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting bearable cost: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete bearable cost"
        )
