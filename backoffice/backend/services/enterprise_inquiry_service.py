"""Read/update enterprise inquiries from main app database (MAIN_APP_DB_*)."""
from typing import Any, Dict, List, Optional
from sqlalchemy import text
from config.database_orm import get_main_app_engine
import logging

logger = logging.getLogger(__name__)


class EnterpriseInquiryService:
    """List and update enterprise_inquiries rows on the ZedReq main DB."""

    def list_inquiries(
        self,
        page: int = 1,
        limit: int = 50,
        status_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        offset = (page - 1) * limit
        engine = get_main_app_engine()
        try:
            where = "1=1"
            filter_params: Dict[str, Any] = {}
            if status_filter:
                where += " AND status = :st"
                filter_params["st"] = status_filter

            with engine.connect() as conn:
                total = conn.execute(
                    text(f"SELECT COUNT(*) FROM enterprise_inquiries WHERE {where}"),
                    filter_params,
                ).scalar() or 0

                list_params = {**filter_params, "limit": limit, "offset": offset}
                rows = conn.execute(
                    text(
                        f"""
                        SELECT id, user_id, contact_email, user_email, username, status, notes,
                               created_at, updated_at
                        FROM enterprise_inquiries
                        WHERE {where}
                        ORDER BY created_at DESC
                        LIMIT :limit OFFSET :offset
                        """
                    ),
                    list_params,
                ).mappings().all()

                items: List[Dict[str, Any]] = []
                for r in rows:
                    items.append(
                        {
                            "id": r["id"],
                            "user_id": r["user_id"],
                            "contact_email": r["contact_email"],
                            "user_email": r["user_email"],
                            "username": r["username"],
                            "status": r["status"],
                            "notes": r["notes"],
                            "created_at": r["created_at"].isoformat()
                            if r["created_at"]
                            else None,
                            "updated_at": r["updated_at"].isoformat()
                            if r["updated_at"]
                            else None,
                        }
                    )

                pages = (total + limit - 1) // limit if limit else 1
                return {
                    "items": items,
                    "total": total,
                    "page": page,
                    "limit": limit,
                    "pages": pages,
                }
        except Exception as e:
            logger.error("list enterprise inquiries: %s", e, exc_info=True)
            err = str(e).lower()
            if "does not exist" in err or "undefinedtable" in err.replace(" ", ""):
                raise RuntimeError(
                    "Table enterprise_inquiries not found on main app database. "
                    "Restart the main ZedReq API once so ORM can create the table, "
                    "or run migrations."
                ) from e
            raise

    def update_status(self, inquiry_id: int, status: str) -> Optional[Dict[str, Any]]:
        engine = get_main_app_engine()
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    UPDATE enterprise_inquiries
                    SET status = :status, updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                    RETURNING id, user_id, contact_email, user_email, username, status, notes,
                              created_at, updated_at
                    """
                ),
                {"status": status, "id": inquiry_id},
            ).mappings().first()
            if not result:
                return None
            r = dict(result)
            return {
                "id": r["id"],
                "user_id": r["user_id"],
                "contact_email": r["contact_email"],
                "user_email": r["user_email"],
                "username": r["username"],
                "status": r["status"],
                "notes": r["notes"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "updated_at": r["updated_at"].isoformat() if r["updated_at"] else None,
            }
