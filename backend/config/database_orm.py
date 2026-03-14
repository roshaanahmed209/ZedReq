"""SQLAlchemy ORM Database Configuration"""
import os
from typing import Generator
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from dotenv import load_dotenv

# Load .env from project root
_project_root = Path(__file__).parent.parent.parent
_env_file = _project_root / ".env"
load_dotenv(_env_file)

# Build database URL
def get_database_url() -> str:
    """Build PostgreSQL database URL from environment variables"""
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Handle Heroku-style postgres:// URLs
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    port = os.environ.get('POSTGRES_PORT', '5432')
    db = os.environ.get('POSTGRES_DB', 'ZedReq')
    user = os.environ.get('POSTGRES_USER', 'postgres')
    password = os.environ.get('POSTGRES_PASSWORD', '')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# Create SQLAlchemy engine
DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.environ.get('DB_POOL_SIZE', 50)),
    max_overflow=int(os.environ.get('DB_POOL_MAX_OVERFLOW', 100)),
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,  # Verify connections before using
    echo=os.environ.get('SQL_ECHO', 'false').lower() == 'true'
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Background-task session factory
# ─────────────────────────────────────────────────────────────────────────────
# Used exclusively by background workers (e.g. LMS dashboard pre-warmer) that
# should NOT interfere with normal OLTP traffic:
#
#   autoflush=False  – prevents accidental implicit writes / flushes that would
#                      hold row-level locks while the query is running.
#   autocommit=False – keeps the session inside an explicit transaction so that
#                      SET statement_timeout applies for the entire session life.
#
# The underlying engine is **shared** (same connection pool) so background reads
# benefit from pool_pre_ping and pool_recycle settings already configured above.
# Concurrency is controlled externally (semaphore in lms_preloader.py).
BackgroundSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

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
