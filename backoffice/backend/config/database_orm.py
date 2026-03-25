"""SQLAlchemy ORM Database Configuration - Backoffice specific"""
import os
from typing import Generator
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv

# Unified .env at repository root (same as main ZedReq backend)
_repo_root = Path(__file__).resolve().parent.parent.parent.parent
_env_file = _repo_root / ".env"
load_dotenv(_env_file)

# Build database URL
def get_database_url() -> str:
    """Build PostgreSQL database URL from backoffice environment variables"""
    database_url = os.environ.get('BACKOFFICE_DATABASE_URL')
    if database_url:
        # Handle Heroku-style postgres:// URLs
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    host = os.environ.get('BACKOFFICE_DB_HOST', 'localhost')
    port = os.environ.get('BACKOFFICE_DB_PORT', '5432')
    db = os.environ.get('BACKOFFICE_DB_NAME', 'zedreq_backoffice')
    user = os.environ.get('BACKOFFICE_DB_USER', 'postgres')
    password = os.environ.get('BACKOFFICE_DB_PASSWORD', '')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# Create SQLAlchemy engine
DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.environ.get('BACKOFFICE_DB_POOL_SIZE', 20)),
    max_overflow=int(os.environ.get('BACKOFFICE_DB_POOL_MAX_OVERFLOW', 40)),
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.environ.get('SQL_ECHO', 'false').lower() == 'true'
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Use with FastAPI's Depends().
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_orm_tables():
    """Create all ORM tables (if they don't exist)"""
    Base.metadata.create_all(bind=engine)


# Main App Database Connection (Read-Only)
def get_main_app_database_url() -> str:
    """Build PostgreSQL database URL for main app (read-only)"""
    from config.settings import settings
    
    host = settings.MAIN_APP_DB_HOST
    port = settings.MAIN_APP_DB_PORT
    db = settings.MAIN_APP_DB_NAME
    user = settings.MAIN_APP_DB_USER
    password = settings.MAIN_APP_DB_PASSWORD
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# Main app database engine (read-only, separate connection pool)
_main_app_engine = None

def get_main_app_engine():
    """Get or create main app database engine (read-only)"""
    global _main_app_engine
    if _main_app_engine is None:
        from config.settings import settings
        main_app_url = get_main_app_database_url()
        _main_app_engine = create_engine(
            main_app_url,
            pool_size=5,  # Smaller pool for read-only
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False
        )
    return _main_app_engine


def get_main_app_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a read-only session to main app database.
    Use with FastAPI's Depends().
    
    Usage:
        @router.get("/items")
        def get_items(db: Session = Depends(get_main_app_db)):
            return db.execute(text("SELECT * FROM users")).fetchall()
    """
    engine = get_main_app_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
