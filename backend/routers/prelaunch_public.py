"""Public read-only config for the main ZedReq web app."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database_orm import get_db
from schemas.prelaunch_notice import PrelaunchNoticePublic
from services.prelaunch_notice_service import get_prelaunch_for_public

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/prelaunch-notice", response_model=PrelaunchNoticePublic)
def read_prelaunch_notice(db: Session = Depends(get_db)):
    """Login modal copy and on/off flag (no authentication)."""
    return get_prelaunch_for_public(db)
