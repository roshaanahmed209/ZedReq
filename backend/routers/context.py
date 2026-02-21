"""Context Router - Generic context update endpoint"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Literal
import logging

from dependencies.auth import get_current_user
from dependencies.rate_limit import write_rate_limit
from config.database_orm import get_db
from services.context_updater import ContextUpdater
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# Rate limiter for context updates (30 requests per minute per user)
_context_rate_limiter = None

def get_context_rate_limiter():
    """Get or create context rate limiter"""
    global _context_rate_limiter
    if _context_rate_limiter is None:
        from dependencies.rate_limit import RateLimiter
        _context_rate_limiter = RateLimiter(requests_per_minute=30)
    return _context_rate_limiter


def context_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for context updates"""
    limiter = get_context_rate_limiter()
    if not limiter.is_allowed(current_user["id"]):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many context update requests. Please try again later."
        )
    return current_user


class ContextUpdateRequest(BaseModel):
    """Request model for context update"""
    action: Literal["apply", "like", "view"] = Field(..., description="Action type")
    entity_type: Literal["job", "post", "profile"] = Field(..., description="Entity type")
    entity_id: int = Field(..., gt=0, le=2147483647, description="Entity ID (max 32-bit int)")


@router.post("/update")
async def update_context(
    request: ContextUpdateRequest,
    current_user: dict = Depends(context_rate_limit),  # Rate limited
    db: Session = Depends(get_db)
):
    """
    Generic endpoint to update user context based on actions
    
    Actions:
    - apply: User applied to a job
    - like: User liked a post
    - view: User viewed a job, post, or profile
    """
    try:
        context_updater = ContextUpdater(db)
        
        success = context_updater.update_context_from_action(
            user_id=current_user["id"],
            action=request.action,
            entity_type=request.entity_type,
            entity_id=request.entity_id
        )
        
        if not success:
            logger.warning(
                f"Context update failed for user_id={current_user['id']}, "
                f"action={request.action}, entity_type={request.entity_type}, "
                f"entity_id={request.entity_id}"
            )
            # Don't fail the request, just log the warning
            return {
                "success": False,
                "message": "Context update completed with warnings"
            }
        
        return {
            "success": True,
            "message": "Context updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error updating context: {e}", exc_info=True)
        # Don't fail the request, context updates are non-critical
        return {
            "success": False,
            "message": "Context update failed, but action was recorded"
        }
