"""Activity logs router"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from dependencies.database import get_db
from dependencies.auth import require_admin_role
from services.admin_service import AdminService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/activity", tags=["Activity Logs"])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    """Get admin service instance"""
    return AdminService(db)


@router.get("/logs")
async def get_activity_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    admin_id: Optional[int] = Query(None),
    action_type: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get paginated activity logs"""
    try:
        result = service.get_activity_logs(
            page, limit, admin_id, action_type, start_date, end_date
        )
        return result
    except Exception as e:
        logger.error(f"Error getting activity logs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity logs"
        )


@router.get("/logs/{log_id}")
async def get_activity_log(
    log_id: int,
    current_admin: dict = Depends(require_admin_role),
    service: AdminService = Depends(get_admin_service)
):
    """Get specific activity log by ID"""
    try:
        from models.orm.admin_activity_log import AdminActivityLog
        
        log = service.db.query(AdminActivityLog).filter(
            AdminActivityLog.id == log_id
        ).first()
        
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity log not found"
            )
        
        return log.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting activity log: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity log"
        )
