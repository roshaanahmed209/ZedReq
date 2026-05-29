"""Application settings using Pydantic Settings - All values from .env file"""
from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
from functools import lru_cache
from pathlib import Path
import logging
import random

_settings_logger = logging.getLogger(__name__)

# Get project root directory (parent of backend)
_project_root = Path(__file__).parent.parent.parent
_env_file = _project_root / ".env"


def parse_tavus_replica_ids_value(raw: str | None) -> List[str]:
    """
    Parse replica ID(s) from env: comma-separated and/or bracket-wrapped lists.

    Accepts e.g. ``rf1,rf2``, ``[rf1, rf2]``, or a single id. Strips quotes per token.
    """
    if not raw or not isinstance(raw, str):
        return []
    s = raw.strip()
    if not s:
        return []
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1].strip()
    out: List[str] = []
    for part in s.split(","):
        p = part.strip().strip("'\"")
        if p:
            out.append(p)
    return out


class Settings(BaseSettings):
    """Application configuration loaded from environment variables"""
    
    # Database - Required from .env
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DATABASE_URL: str | None = None
    
    # Database pool
    DB_POOL_MIN: int
    DB_POOL_SIZE: int
    
    # JWT Settings - Required from .env
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int
    
    # CORS - Required from .env
    CORS_ORIGINS: str  # Comma-separated string from env
    
    # Server
    DEBUG: bool
    
    # Tavus AI Configuration (optional)
    TAVUS_API_KEY: str | None = None
    TAVUS_PERSONA_ID: str | None = None  # Required for POST /v2/conversations (full pipeline)
    TAVUS_REPLICA_ID: str | None = None  # One id, or comma-separated / [id1, id2] list
    TAVUS_REPLICA_IDS: str | None = None  # Comma-separated or [id1, id2] (preferred for multiple)
    # Official v2 host: https://docs.tavus.io/api-reference/conversations/create-conversation
    TAVUS_API_URL: str = "https://tavusapi.com/v2"
    # Seconds with no participant before Tavus tears down the Daily room (Tavus default is 300).
    TAVUS_PARTICIPANT_ABSENT_TIMEOUT: int = 1800
    
    # Firebase Google Auth Configuration (separate from messaging Firebase)
    FIREBASE_AUTH_PROJECT_ID: str | None = None  # Firebase project ID for Google Auth
    FIREBASE_AUTH_API_KEY: str | None = None  # Firebase API key for Google Auth
    
    # Redis (optional — Render injects REDIS_URL; see config/cache.py)
    REDIS_URL: str | None = None
    REDIS_HOST: str | None = None
    REDIS_PORT: int | None = None
    REDIS_DB: int = 0
    REDIS_ENABLED: bool | None = None
    REDIS_CACHE_TTL: int = 300
    REDIS_REQUIRED: bool = False

    # Recommendation Cache Configuration
    RECOMMENDATION_CACHE_ENABLED: bool = True
    RECOMMENDATION_CACHE_TTL_HOURS: int = 24  # Optional TTL for cache expiration
    JOB_EMBEDDING_BACKFILL_BATCH_SIZE: int = 100

    # Backoffice → main app user purge (shared secret; must match backoffice BACKOFFICE_USER_PURGE_KEY)
    BACKOFFICE_USER_PURGE_KEY: str | None = None

    @validator("BACKOFFICE_USER_PURGE_KEY", pre=True, always=True)
    def validate_purge_key(cls, v, values):  # noqa: N805
        if not v:
            return v
        if len(v) < 32:
            debug = values.get("DEBUG", True)
            if not debug:
                raise ValueError(
                    "BACKOFFICE_USER_PURGE_KEY must be at least 32 characters in production"
                )
            _settings_logger.warning(
                "BACKOFFICE_USER_PURGE_KEY is shorter than 32 characters — use a longer secret in production"
            )
        return v

    # Paddle Billing (optional — webhooks + subscription cancel/change APIs)
    PADDLE_API_KEY: str | None = None
    PADDLE_WEBHOOK_SECRET: str | None = None
    # Sandbox API host differs; default production api.paddle.com
    PADDLE_SANDBOX: bool = False
    PADDLE_PRICE_PRO: str | None = None
    PADDLE_PRICE_PREMIUM: str | None = None
    # Max age (seconds) for webhook ts when verifying Paddle-Signature (SDK default 5 is strict)
    PADDLE_WEBHOOK_MAX_AGE_SECONDS: int = 30
    
    class Config:
        env_file = str(_env_file)
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def get_database_url(self) -> str:
        """Get database connection string"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"host={self.POSTGRES_HOST} port={self.POSTGRES_PORT} dbname={self.POSTGRES_DB} user={self.POSTGRES_USER} password={self.POSTGRES_PASSWORD}"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    def get_tavus_replica_ids(self) -> List[str]:
        """
        Get list of Tavus replica IDs.

        ``TAVUS_REPLICA_IDS`` wins if set; otherwise ``TAVUS_REPLICA_ID``.
        Each may be comma-separated or bracket-wrapped (e.g. ``[r1, r2]``).
        """
        if self.TAVUS_REPLICA_IDS:
            return parse_tavus_replica_ids_value(self.TAVUS_REPLICA_IDS)
        if self.TAVUS_REPLICA_ID:
            return parse_tavus_replica_ids_value(self.TAVUS_REPLICA_ID)
        return []
    
    def get_random_tavus_replica_id(self) -> Optional[str]:
        """
        Get a random Tavus replica ID from the configured list
        
        Returns:
            Randomly selected replica ID, or None if none configured
        """
        replica_ids = self.get_tavus_replica_ids()
        if not replica_ids:
            return None
        return random.choice(replica_ids)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
