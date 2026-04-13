"""Contact form submissions from Settings page (Help Center and Enterprise modals)."""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class ContactSubmission(Base):
    """
    One row per contact form submission from the main app Settings page.
    Backoffice reads via MAIN_APP_DB_* connection.
    """

    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.uid", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    submission_type = Column(String(32), nullable=False, index=True)  # 'help' | 'enterprise'
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    extra = Column(JSONB, nullable=True)  # category, company, role, etc.
    status = Column(String(32), nullable=False, default="new", index=True)  # 'new' | 'reviewed' | 'closed'
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ContactSubmission(id={self.id}, type={self.submission_type!r}, user_id={self.user_id})>"
