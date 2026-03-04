"""Application settings using Pydantic Settings - All values from backoffice/.env file"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache
from pathlib import Path

# Get backoffice root directory (parent of backend)
_backoffice_root = Path(__file__).parent.parent.parent
_env_file = _backoffice_root / ".env"


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


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
