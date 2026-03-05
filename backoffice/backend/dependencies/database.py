"""Database dependencies"""
from config.database_orm import get_db

# Re-export for convenience
__all__ = ["get_db"]
