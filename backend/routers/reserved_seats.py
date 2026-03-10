"""Reserved Seats Router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import logging

from config.database_orm import get_db
from services.reserved_seat_service import ReservedSeatService
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/reserved-seats", tags=["reserved-seats"])


class ReserveSeatRequest(BaseModel):
    email: EmailStr


class ReserveSeatResponse(BaseModel):
    success: bool
    message: str
    promo_code: str | None = None
    already_reserved: bool = False


def get_reserved_seat_service(db: Session = Depends(get_db)) -> ReservedSeatService:
    """Dependency to get reserved seat service"""
    return ReservedSeatService(db)


@router.post("", response_model=ReserveSeatResponse, status_code=status.HTTP_201_CREATED)
async def reserve_seat(
    request: ReserveSeatRequest,
    service: ReservedSeatService = Depends(get_reserved_seat_service)
):
    """
    Reserve a seat for early access
    
    - Checks if email already exists
    - Generates promo code
    - Sends confirmation email
    - Stores in database
    """
    logger.info(f"Received seat reservation request for email: {request.email[:3]}***")
    try:
        result = service.reserve_seat(request.email)
        
        # Log the result
        if result.get('already_reserved'):
            logger.info(f"✓ Reservation request completed | Status: Already Reserved | Promo Code: {result.get('promo_code')}")
        else:
            email_status = "Email status logged in service"
            logger.info(f"✓ Reservation request completed | Status: New Reservation | Promo Code: {result.get('promo_code')} | {email_status}")
        
        return result
    except ValueError as e:
        # ValueError from service contains user-friendly messages
        logger.warning(f"✗ Reservation request failed: Validation error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Don't expose internal error details
        logger.error(f"✗ Reservation request failed: Unexpected error - {type(e).__name__}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete reservation. Please try again later."
        )
