"""Enterprise sales inquiry — stored when user submits work email from app."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from config.database_orm import Base


class EnterpriseInquiry(Base):
    """
    One row per enterprise form submission (main app DB).
    Backoffice reads via MAIN_APP_DB_* connection.
    """

    __tablename__ = "enterprise_inquiries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.uid", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_email = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=True)
    username = Column(String(100), nullable=True)
    status = Column(String(32), nullable=False, default="new", index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<EnterpriseInquiry(id={self.id}, user_id={self.user_id}, contact_email={self.contact_email!r})>"
