"""
Create all backoffice database tables using connection details from env/settings.

Loads BACKOFFICE_* DB variables from backoffice/.env (or BACKOFFICE_DATABASE_URL),
then creates every table defined by the ORM models (admin_users, admin_activity_log,
revenue_transactions, cost_transactions, financial_summaries, failed_login_attempts).

Run from the backend directory:
  python -m table_queries.create_tables

Or from the backoffice directory:
  python backend/table_queries/create_tables.py
"""
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure backoffice backend is on the path when run as script
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# Load .env from backoffice root before any config imports
_backoffice_root = _backend_dir.parent
_env_file = _backoffice_root / ".env"
if _env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_file)
    logging.info("Loaded env from %s", _env_file)
else:
    logging.warning("No .env at %s; using process environment.", _env_file)

# Now import config (uses env) and ORM models
from config.database_orm import Base, engine, init_orm_tables
from models.orm import (  # noqa: F401 - register all models with Base
    AdminUser,
    AdminActivityLog,
    RevenueTransaction,
    CostTransaction,
    FinancialSummary,
    FailedLoginAttempt,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Create all tables in the backoffice database from env/settings."""
    try:
        # Get connection URL from engine for logging (hide password)
        url = str(engine.url)
        if engine.url.password:
            url = url.replace(engine.url.password, "****", 1)
        logger.info("Database: %s", url)

        init_orm_tables()
        table_names = sorted(Base.metadata.tables.keys())
        logger.info("Tables created or already exist: %s", ", ".join(table_names))
    except Exception as e:
        logger.exception("Failed to create tables: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
