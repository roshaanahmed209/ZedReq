"""Reserved Seats Router"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

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


class ClientEmailFailedBody(BaseModel):
    promo_code: str = Field(..., min_length=3, max_length=64)
    reason: str | None = Field(None, max_length=200)


def get_reserved_seat_service(db: Session = Depends(get_db)) -> ReservedSeatService:
    """Dependency to get reserved seat service"""
    return ReservedSeatService(db)


@router.post("", response_model=ReserveSeatResponse, status_code=status.HTTP_201_CREATED)
async def reserve_seat(
    request: ReserveSeatRequest,
    service: ReservedSeatService = Depends(get_reserved_seat_service)
):
    """Reserve a seat: persist promo; confirmation email is sent from the client (EmailJS)."""
    logger.info(
        "reserved_seat request email_prefix=%s***",
        request.email[:3] if len(request.email) >= 3 else request.email,
    )
    try:
        result = service.reserve_seat(request.email)
        logger.info(
            "reserved_seat ok duplicate=%s promo=%s",
            result.get("already_reserved", False),
            result.get("promo_code"),
        )
        return result
    except ValueError as e:
        # ValueError from service contains user-friendly messages
        logger.warning("reserved_seat reject: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Don't expose internal error details
        logger.error("reserved_seat error %s", type(e).__name__, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to complete reservation. Please try again later."
        )


@router.post("/email-delivery-failed", status_code=status.HTTP_204_NO_CONTENT)
async def report_client_email_delivery_failed(
    body: ClientEmailFailedBody,
    service: ReservedSeatService = Depends(get_reserved_seat_service),
):
    """Browser-only EmailJS failed after reservation; log server-side for ops (FirstPage flow)."""
    service.report_client_email_failure(body.promo_code, body.reason)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
