"""Network Router - User discovery and suggestions using ORM"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from schemas.network import NetworkUserResponse, SuggestedUserResponse
from services.network_service import NetworkService
from dependencies.auth import get_current_user
from config.database_orm import get_db

router = APIRouter()


def get_network_service(db: Session = Depends(get_db)) -> NetworkService:
    """Dependency to get network service with ORM session"""
    return NetworkService(db)


@router.get("/discover", response_model=List[NetworkUserResponse])
async def discover_users(
    limit: int = Query(default=20, ge=1, le=100, description="Number of users to return"),
    current_user: dict = Depends(get_current_user),
    network_service: NetworkService = Depends(get_network_service)
):
    """
    Discover new users to connect with.
    Returns 20% of available users (excluding self and existing connections).
    """
    users = network_service.get_discover_users(
        current_user_id=current_user["id"],
        limit=limit
    )
    return users


@router.get("/suggestions", response_model=List[SuggestedUserResponse])
async def get_suggestions(
    limit: int = Query(default=20, ge=1, le=50, description="Number of suggestions"),
    current_user: dict = Depends(get_current_user),
    network_service: NetworkService = Depends(get_network_service)
):
    """
    Get friend-of-friend connection suggestions.
    Returns users connected to your connections, ranked by mutual connection count.
    """
    suggestions = network_service.get_suggestions(
        current_user_id=current_user["id"],
        limit=limit
    )
    return suggestions


@router.get("/connections", response_model=List[NetworkUserResponse])
async def get_my_connections(
    current_user: dict = Depends(get_current_user),
    network_service: NetworkService = Depends(get_network_service)
):
    """Get current user's accepted connections"""
    connections = network_service.get_user_connections(
        user_id=current_user["id"]
    )
    return connections
