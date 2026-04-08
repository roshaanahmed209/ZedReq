"""Append-only archive of purged user accounts — not used by product APIs."""
from sqlalchemy import Column, BigInteger, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class DeletedUserArchive(Base):
    __tablename__ = "deleted_user_archive"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    original_uid = Column(Integer, nullable=False, index=True)
    user_email = Column(String(150), index=True)
    deleted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deletion_source = Column(String(20), nullable=False)
    admin_id = Column(Integer, nullable=True)
    reason = Column(Text, nullable=True)
    user_snapshot = Column(JSONB, nullable=False)
    description_snapshot = Column(JSONB, nullable=True)
    subscriptions_snapshot = Column(JSONB, nullable=True)
    payments_snapshot = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
