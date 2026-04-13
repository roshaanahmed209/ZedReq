"""Contact form submission endpoint (authenticated users)."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from config.database_orm import get_db
from dependencies.auth import get_current_user
from models.orm.contact_submission import ContactSubmission
from schemas.contact_submissions import ContactSubmitRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/submit")
async def submit_contact(
    body: ContactSubmitRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a contact/support submission from an authenticated user."""
    uid = current_user.get("id")
    try:
        row = ContactSubmission(
            user_id=int(uid),
            submission_type=body.submission_type,
            subject=body.subject[:200],
            message=body.message[:5000],
            extra=body.extra or {},
            status="new",
        )
        db.add(row)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("contact_submission persist failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save your submission. Please try again.",
        )
    logger.info(
        "contact_submission user_id=%s type=%s subject=%r",
        uid,
        body.submission_type,
        body.subject,
    )
    return {"success": True, "message": "Your message has been received. We'll get back to you soon."}
