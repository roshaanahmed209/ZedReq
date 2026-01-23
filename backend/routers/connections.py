"""Connections Router - Connection requests management using ORM"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas.connection import (
    ConnectionRequestCreate,
    ConnectionRequestResponse,
    ConnectionResponse
)
from services.connection_service import ConnectionService
from dependencies.auth import get_current_user
from config.database_orm import get_db

router = APIRouter()


def get_connection_service(db: Session = Depends(get_db)) -> ConnectionService:
    """Dependency to get connection service with ORM session"""
    return ConnectionService(db)


@router.post("/request/{user_id}", response_model=ConnectionRequestResponse, status_code=status.HTTP_201_CREATED)
async def send_connection_request(
    user_id: int,
    request_data: ConnectionRequestCreate = None,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """Send a connection request to another user"""
    sender_id = current_user["id"]
    
    if sender_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send connection request to yourself"
        )
    
    try:
        message = request_data.message if request_data else None
        result = connection_service.send_request(
            sender_id=sender_id,
            receiver_id=user_id,
            message=message
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send request")


@router.put("/accept/{request_id}", response_model=ConnectionResponse)
async def accept_connection_request(
    request_id: int,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """Accept a pending connection request"""
    try:
        result = connection_service.accept_request(
            request_id=request_id,
            receiver_id=current_user["id"]
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/reject/{request_id}")
async def reject_connection_request(
    request_id: int,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """Reject a pending connection request"""
    try:
        connection_service.reject_request(
            request_id=request_id,
            receiver_id=current_user["id"]
        )
        return {"message": "Connection request rejected"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{connection_id}")
async def remove_connection(
    connection_id: int,
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """Remove an existing connection"""
    try:
        connection_service.remove_connection(
            connection_id=connection_id,
            user_id=current_user["id"]
        )
        return {"message": "Connection removed"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/pending", response_model=List[ConnectionRequestResponse])
async def get_pending_requests(
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """Get pending connection requests received by current user"""
    requests = connection_service.get_pending_requests(
        user_id=current_user["id"]
    )
    return requests


@router.get("/sent", response_model=List[ConnectionRequestResponse])
async def get_sent_requests(
    current_user: dict = Depends(get_current_user),
    connection_service: ConnectionService = Depends(get_connection_service)
):
    """Get connection requests sent by current user"""
    requests = connection_service.get_sent_requests(
        user_id=current_user["id"]
    )
    return requests
