"""Idempotency store for Paddle Billing webhook deliveries."""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func

from config.database_orm import Base


class PaddleWebhookEvent(Base):
    __tablename__ = "paddle_webhook_events"

    event_id = Column(String(128), primary_key=True)
    event_type = Column(String(128), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
