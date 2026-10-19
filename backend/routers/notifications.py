"""Notifications Router - Notification management using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from schemas.notification import NotificationResponse, UnreadCountResponse
from services.notification_service import NotificationService
from dependencies.auth import get_current_user
from config.database_orm import get_db

router = APIRouter()


def get_notification_service(db: Session = Depends(get_db)) -> NotificationService:
    """Dependency to get notification service with ORM session"""
    return NotificationService(db)


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False),
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get user's notifications"""
    notifications = notification_service.get_notifications(
        user_id=current_user["id"],
        limit=limit,
        offset=offset,
        unread_only=unread_only
    )
    return notifications


@router.get("/unread/count", response_model=UnreadCountResponse)
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Get count of unread notifications"""
    count = notification_service.get_unread_count(
        user_id=current_user["id"]
    )
    return {"count": count}


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Mark a notification as read"""
    try:
        notification_service.mark_as_read(
            notification_id=notification_id,
            user_id=current_user["id"]
        )
        return {"message": "Notification marked as read"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/read-all")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    notification_service: NotificationService = Depends(get_notification_service)
):
    """Mark all notifications as read"""
    count = notification_service.mark_all_as_read(
        user_id=current_user["id"]
    )
    return {"message": f"Marked {count} notifications as read"}
