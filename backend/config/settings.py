"""Application settings using Pydantic Settings - All values from .env file"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache
from pathlib import Path
import random

# Get project root directory (parent of backend)
_project_root = Path(__file__).parent.parent.parent
_env_file = _project_root / ".env"


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
    TAVUS_REPLICA_ID: str | None = None  # Single replica ID (for backward compatibility)
    TAVUS_REPLICA_IDS: str | None = None  # Comma-separated list of replica IDs
    TAVUS_API_URL: str = "https://api.tavus.ai/v2"
    
    # Firebase Google Auth Configuration (separate from messaging Firebase)
    FIREBASE_AUTH_PROJECT_ID: str | None = None  # Firebase project ID for Google Auth
    FIREBASE_AUTH_API_KEY: str | None = None  # Firebase API key for Google Auth
    
    # Recommendation Cache Configuration
    RECOMMENDATION_CACHE_ENABLED: bool = True
    RECOMMENDATION_CACHE_TTL_HOURS: int = 24  # Optional TTL for cache expiration
    JOB_EMBEDDING_BACKFILL_BATCH_SIZE: int = 100
    
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
        Get list of Tavus replica IDs
        
        Returns:
            List of replica IDs. Supports both TAVUS_REPLICA_IDS (comma-separated)
            and TAVUS_REPLICA_ID (single ID for backward compatibility)
        """
        replica_ids = []
        
        # First, try TAVUS_REPLICA_IDS (comma-separated list)
        if self.TAVUS_REPLICA_IDS:
            replica_ids = [rid.strip() for rid in self.TAVUS_REPLICA_IDS.split(",") if rid.strip()]
        
        # If no list, fall back to single TAVUS_REPLICA_ID (backward compatibility)
        if not replica_ids and self.TAVUS_REPLICA_ID:
            replica_ids = [self.TAVUS_REPLICA_ID]
        
        return replica_ids
    
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
