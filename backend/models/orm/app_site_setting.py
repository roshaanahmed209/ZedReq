"""Key/value site settings stored in the main app database (e.g. pre-launch notice)."""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from config.database_orm import Base


class AppSiteSetting(Base):
    __tablename__ = "app_site_settings"

    setting_key = Column(String(64), primary_key=True)
    value = Column(JSONB, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
