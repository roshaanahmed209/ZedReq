"""Enterprise inquiry leads (main app DB) — list and update status."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
import logging

from dependencies.auth import require_admin_role
from schemas.admin import (
    EnterpriseInquiryListResponse,
    EnterpriseInquiryItem,
    EnterpriseInquiryStatusUpdate,
)
from services.enterprise_inquiry_service import EnterpriseInquiryService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/enterprise-inquiries", tags=["Enterprise inquiries"])


def get_enterprise_inquiry_service() -> EnterpriseInquiryService:
    return EnterpriseInquiryService()


@router.get("", response_model=EnterpriseInquiryListResponse)
async def list_enterprise_inquiries(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    current_admin: dict = Depends(require_admin_role),
    service: EnterpriseInquiryService = Depends(get_enterprise_inquiry_service),
):
    """List enterprise form submissions (newest first)."""
    if status_filter and status_filter not in ("new", "contacted", "closed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status filter",
        )
    try:
        data = service.list_inquiries(page=page, limit=limit, status_filter=status_filter)
        return EnterpriseInquiryListResponse(**data)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except Exception as e:
        logger.error("list_enterprise_inquiries: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load enterprise inquiries",
        )


@router.patch("/{inquiry_id}", response_model=EnterpriseInquiryItem)
async def update_enterprise_inquiry_status(
    inquiry_id: int,
    body: EnterpriseInquiryStatusUpdate,
    current_admin: dict = Depends(require_admin_role),
    service: EnterpriseInquiryService = Depends(get_enterprise_inquiry_service),
):
    """Set workflow status (new / contacted / closed)."""
    if inquiry_id < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid id")
    try:
        updated = service.update_status(inquiry_id, body.status)
    except Exception as e:
        logger.error("update_enterprise_inquiry_status: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update inquiry",
        )
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inquiry not found")
    return EnterpriseInquiryItem(**updated)
