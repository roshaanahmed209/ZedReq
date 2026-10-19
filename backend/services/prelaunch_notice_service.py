"""Pre-launch login modal — read/write `app_site_settings` row."""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.orm.app_site_setting import AppSiteSetting
from schemas.prelaunch_notice import PRELAUNCH_NOTICE_KEY, PrelaunchNoticePublic


def _coerce_stored(raw: Any) -> Optional[Dict[str, Any]]:
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        import json

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return None


def merge_prelaunch(stored: Any) -> PrelaunchNoticePublic:
    base = PrelaunchNoticePublic().model_dump()
    data = _coerce_stored(stored)
    if not data:
        return PrelaunchNoticePublic()
    allowed = set(PrelaunchNoticePublic.model_fields.keys())
    filtered = {k: v for k, v in data.items() if k in allowed}
    merged = {**base, **filtered}
    try:
        return PrelaunchNoticePublic(**merged)
    except Exception:
        return PrelaunchNoticePublic()


def get_prelaunch_for_public(db: Session) -> PrelaunchNoticePublic:
    row = db.query(AppSiteSetting).filter_by(setting_key=PRELAUNCH_NOTICE_KEY).first()
    return merge_prelaunch(row.value if row else None)


def ensure_prelaunch_row_seeded(db: Session) -> None:
    """Insert defaults if missing (startup)."""
    row = db.query(AppSiteSetting).filter_by(setting_key=PRELAUNCH_NOTICE_KEY).first()
    if row is None:
        db.add(
            AppSiteSetting(
                setting_key=PRELAUNCH_NOTICE_KEY,
                value=PrelaunchNoticePublic().model_dump(),
            )
        )
        db.commit()
