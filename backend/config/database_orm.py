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


def get_database_url() -> str:
    """Build PostgreSQL database URL. Uses settings when available (required POSTGRES_PASSWORD in production)."""
    try:
        from config.settings import get_settings
        s = get_settings()
        if s.DATABASE_URL:
            url = s.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url
        return f"postgresql://{s.POSTGRES_USER}:{s.POSTGRES_PASSWORD}@{s.POSTGRES_HOST}:{s.POSTGRES_PORT}/{s.POSTGRES_DB}"
    except Exception:
        pass
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    password = os.environ.get("POSTGRES_PASSWORD", "")
    if not password and os.environ.get("DEBUG", "true").lower() in ("false", "0"):
        raise ValueError("POSTGRES_PASSWORD must be set in production. Set DEBUG=true only for development.")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "ZedReq")
    user = os.environ.get("POSTGRES_USER", "postgres")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


# Create SQLAlchemy engine
DATABASE_URL = get_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_size=int(os.environ.get('DB_POOL_SIZE', 5)),
    max_overflow=int(os.environ.get('DB_POOL_MAX_OVERFLOW', 5)),
    pool_timeout=15,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 15},
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
    # Ensure models are registered on Base before create_all
    import models.orm.enterprise_inquiry  # noqa: F401
    import models.orm.app_site_setting  # noqa: F401
    import models.orm.paddle_webhook_event  # noqa: F401
    import models.orm.deleted_user_archive  # noqa: F401
    import models.orm.post_comment  # noqa: F401
    import models.orm.contact_submission  # noqa: F401
    Base.metadata.create_all(bind=engine)
