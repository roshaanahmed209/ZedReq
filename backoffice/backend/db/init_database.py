"""Initialize backoffice database with all required tables"""
from config.database import get_database, init_database
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Admin users table
ADMIN_USERS_TABLE = '''
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_admin_users_email ON admin_users(email);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);
'''

# Admin activity log table
ADMIN_ACTIVITY_LOG_TABLE = '''
CREATE TABLE IF NOT EXISTS admin_activity_log (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER REFERENCES admin_users(id) ON DELETE SET NULL,
    action_type VARCHAR(50) NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_admin_activity_admin ON admin_activity_log(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_activity_type ON admin_activity_log(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_activity_created ON admin_activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_admin_activity_target ON admin_activity_log(target_type, target_id);
'''

# Revenue transactions table
REVENUE_TRANSACTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS revenue_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    plan_type VARCHAR(50),
    provider VARCHAR(50),
    provider_transaction_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_revenue_user ON revenue_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_revenue_type ON revenue_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_revenue_status ON revenue_transactions(status);
CREATE INDEX IF NOT EXISTS idx_revenue_created ON revenue_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_revenue_provider ON revenue_transactions(provider, provider_transaction_id);
'''

# Cost transactions table
COST_TRANSACTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS cost_transactions (
    id SERIAL PRIMARY KEY,
    cost_category VARCHAR(50) NOT NULL,
    service_name VARCHAR(100),
    amount DECIMAL(10, 4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    unit_type VARCHAR(20),
    quantity DECIMAL(10, 2),
    user_id INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cost_category ON cost_transactions(cost_category);
CREATE INDEX IF NOT EXISTS idx_cost_user ON cost_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_cost_created ON cost_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cost_service ON cost_transactions(service_name);
'''

# Financial summaries table
FINANCIAL_SUMMARIES_TABLE = '''
CREATE TABLE IF NOT EXISTS financial_summaries (
    id SERIAL PRIMARY KEY,
    period_type VARCHAR(20) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_revenue DECIMAL(12, 2) DEFAULT 0,
    subscription_revenue DECIMAL(12, 2) DEFAULT 0,
    one_time_revenue DECIMAL(12, 2) DEFAULT 0,
    refunds DECIMAL(12, 2) DEFAULT 0,
    total_costs DECIMAL(12, 4) DEFAULT 0,
    openai_costs DECIMAL(12, 4) DEFAULT 0,
    tavus_costs DECIMAL(12, 4) DEFAULT 0,
    infrastructure_costs DECIMAL(12, 4) DEFAULT 0,
    storage_costs DECIMAL(12, 4) DEFAULT 0,
    other_costs DECIMAL(12, 4) DEFAULT 0,
    active_subscriptions INTEGER DEFAULT 0,
    new_subscriptions INTEGER DEFAULT 0,
    cancelled_subscriptions INTEGER DEFAULT 0,
    churn_rate DECIMAL(5, 2) DEFAULT 0,
    net_profit DECIMAL(12, 2) DEFAULT 0,
    profit_margin DECIMAL(5, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period_type, period_start)
);

CREATE INDEX IF NOT EXISTS idx_financial_period ON financial_summaries(period_type, period_start DESC);
CREATE INDEX IF NOT EXISTS idx_financial_start ON financial_summaries(period_start DESC);
'''

# Failed login attempts table (for security)
FAILED_LOGIN_ATTEMPTS_TABLE = '''
CREATE TABLE IF NOT EXISTS failed_login_attempts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_failed_login_username ON failed_login_attempts(username, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_failed_login_ip ON failed_login_attempts(ip_address, attempted_at DESC);
CREATE INDEX IF NOT EXISTS idx_failed_login_time ON failed_login_attempts(attempted_at DESC);
'''

# All table creation statements
TABLES = [
    ("admin_users", ADMIN_USERS_TABLE),
    ("admin_activity_log", ADMIN_ACTIVITY_LOG_TABLE),
    ("revenue_transactions", REVENUE_TRANSACTIONS_TABLE),
    ("cost_transactions", COST_TRANSACTIONS_TABLE),
    ("financial_summaries", FINANCIAL_SUMMARIES_TABLE),
    ("failed_login_attempts", FAILED_LOGIN_ATTEMPTS_TABLE),
]


def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    from config.settings import settings
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    # Connect to postgres database to create our database
    try:
        conn = psycopg2.connect(
            host=settings.BACKOFFICE_DB_HOST,
            port=settings.BACKOFFICE_DB_PORT,
            user=settings.BACKOFFICE_DB_USER,
            password=settings.BACKOFFICE_DB_PASSWORD,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (settings.BACKOFFICE_DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {settings.BACKOFFICE_DB_NAME}')
            logger.info(f"Database {settings.BACKOFFICE_DB_NAME} created")
        else:
            logger.info(f"Database {settings.BACKOFFICE_DB_NAME} already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.warning(f"Could not create database (may already exist): {e}")


def init_database_tables():
    """Initialize all database tables"""
    try:
        db = init_database()
        
        logger.info("Creating database tables...")
        
        for table_name, table_sql in TABLES:
            try:
                # Execute each statement separately
                statements = [s.strip() for s in table_sql.split(';') if s.strip()]
                for statement in statements:
                    if statement:
                        db.execute(statement)
                logger.info(f"✓ Table {table_name} created/verified")
            except Exception as e:
                logger.error(f"Error creating table {table_name}: {e}")
                raise
        
        logger.info("All tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Try to create database if it doesn't exist
        create_database_if_not_exists()
        
        # Initialize tables
        init_database_tables()
        
        print("✓ Database initialized successfully")
        sys.exit(0)
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)
