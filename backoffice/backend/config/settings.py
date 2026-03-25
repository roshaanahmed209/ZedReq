"""Application settings using Pydantic Settings — unified .env at repository root."""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
from pathlib import Path

# Repository root (parent of backoffice/) — same .env as main ZedReq backend
_repo_root = Path(__file__).resolve().parent.parent.parent.parent
_env_file = _repo_root / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from backoffice-specific environment variables"""
    
    # Database - Required from .env (BACKOFFICE_* prefixed)
    BACKOFFICE_DB_HOST: str = "localhost"
    BACKOFFICE_DB_PORT: int = 5432
    BACKOFFICE_DB_NAME: str = "zedreq_backoffice"
    BACKOFFICE_DB_USER: str = "postgres"
    BACKOFFICE_DB_PASSWORD: str = ""
    BACKOFFICE_DATABASE_URL: str | None = None
    
    # Database pool
    BACKOFFICE_DB_POOL_MIN: int = 5
    BACKOFFICE_DB_POOL_SIZE: int = 20
    
    # JWT Settings - Required from .env (Separate from main ZedReq)
    BACKOFFICE_JWT_SECRET_KEY: str
    BACKOFFICE_JWT_ALGORITHM: str = "HS256"
    BACKOFFICE_JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS - Required from .env
    BACKOFFICE_CORS_ORIGINS: str  # Comma-separated string from env
    
    # Server Configuration
    BACKOFFICE_SERVER_HOST: str = "127.0.0.1"
    BACKOFFICE_SERVER_PORT: int = 5001
    BACKOFFICE_DEBUG: bool = True
    
    # Frontend Configuration
    BACKOFFICE_FRONTEND_URL: str = "http://localhost:3001"
    
    # Main App Connection (for monitoring)
    MAIN_APP_DB_HOST: str = "localhost"
    MAIN_APP_DB_PORT: int = 5432
    MAIN_APP_DB_NAME: str = "zedreq"
    MAIN_APP_DB_USER: str = "postgres"
    MAIN_APP_DB_PASSWORD: str = ""
    MAIN_APP_API_URL: str = "http://localhost:5000"
    
    # Collection Intervals (in seconds)
    INFRASTRUCTURE_COLLECTION_INTERVAL: int = 300  # 5 minutes
    UPTIME_CHECK_INTERVAL: int = 60  # 1 minute
    DATABASE_COLLECTION_INTERVAL: int = 300  # 5 minutes
    ALERT_CHECK_INTERVAL: int = 60  # 1 minute
    
    # Alert Thresholds (defaults)
    ALERT_CPU_THRESHOLD: float = 85.0
    ALERT_RAM_THRESHOLD: float = 85.0
    ALERT_DISK_THRESHOLD: float = 90.0
    ALERT_ERROR_RATE_THRESHOLD: float = 5.0  # percentage
    ALERT_RESPONSE_TIME_THRESHOLD: int = 2000  # milliseconds
    ALERT_UPTIME_THRESHOLD: float = 99.9  # percentage
    
    # Email SMTP Settings (for alerts)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_TO_EMAILS: str = ""  # Comma-separated
    
    # Collector API Authentication
    COLLECTOR_API_KEY: str = ""  # Secret key for collector endpoints
    
    class Config:
        env_file = str(_env_file)
        env_file_encoding = "utf-8"
        extra = "ignore"
    
    def get_database_url(self) -> str:
        """Get database connection string"""
        if self.BACKOFFICE_DATABASE_URL:
            return self.BACKOFFICE_DATABASE_URL
        return f"host={self.BACKOFFICE_DB_HOST} port={self.BACKOFFICE_DB_PORT} dbname={self.BACKOFFICE_DB_NAME} user={self.BACKOFFICE_DB_USER} password={self.BACKOFFICE_DB_PASSWORD}"
    
    def get_database_url_sqlalchemy(self) -> str:
        """Get database URL for SQLAlchemy"""
        if self.BACKOFFICE_DATABASE_URL:
            # Handle Heroku-style postgres:// URLs
            if self.BACKOFFICE_DATABASE_URL.startswith('postgres://'):
                return self.BACKOFFICE_DATABASE_URL.replace('postgres://', 'postgresql://', 1)
            return self.BACKOFFICE_DATABASE_URL
        return f"postgresql://{self.BACKOFFICE_DB_USER}:{self.BACKOFFICE_DB_PASSWORD}@{self.BACKOFFICE_DB_HOST}:{self.BACKOFFICE_DB_PORT}/{self.BACKOFFICE_DB_NAME}"
    
    def get_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.BACKOFFICE_CORS_ORIGINS.split(",") if origin.strip()]
    
    def get_main_app_database_url(self) -> str:
        """Get main app database connection string (read-only)"""
        return f"host={self.MAIN_APP_DB_HOST} port={self.MAIN_APP_DB_PORT} dbname={self.MAIN_APP_DB_NAME} user={self.MAIN_APP_DB_USER} password={self.MAIN_APP_DB_PASSWORD}"
    
    def get_smtp_to_emails(self) -> List[str]:
        """Parse SMTP recipient emails from comma-separated string"""
        return [email.strip() for email in self.SMTP_TO_EMAILS.split(",") if email.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
