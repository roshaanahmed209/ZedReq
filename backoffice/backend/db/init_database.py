"""Initialize backoffice database with all required tables"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from config.database import get_database, init_database
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

# User payment summary table
USER_PAYMENT_SUMMARY_TABLE = '''
CREATE TABLE IF NOT EXISTS user_payment_summary (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    plan_id INTEGER,
    total_amount_paid DECIMAL(12, 2) NOT NULL DEFAULT 0,
    total_refunded DECIMAL(12, 2) NOT NULL DEFAULT 0,
    last_paid_amount DECIMAL(12, 2),
    last_payment_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_payment_summary_user_id ON user_payment_summary(user_id);
'''

# Bearable costs table
BEARABLE_COSTS_TABLE = '''
CREATE TABLE IF NOT EXISTS bearable_costs (
    id SERIAL PRIMARY KEY,
    cost_name VARCHAR(100) UNIQUE NOT NULL,
    amount DECIMAL(10, 4) NOT NULL,
    is_fixed BOOLEAN NOT NULL DEFAULT FALSE,
    unit_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
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

# Infrastructure metrics table
INFRASTRUCTURE_METRICS_TABLE = '''
CREATE TABLE IF NOT EXISTS infrastructure_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cpu_percent DECIMAL(5, 2) NOT NULL,
    ram_percent DECIMAL(5, 2) NOT NULL,
    ram_used_mb DECIMAL(10, 2) NOT NULL,
    ram_total_mb DECIMAL(10, 2) NOT NULL,
    disk_percent DECIMAL(5, 2) NOT NULL,
    disk_used_gb DECIMAL(10, 2) NOT NULL,
    disk_total_gb DECIMAL(10, 2) NOT NULL,
    network_in_mb DECIMAL(10, 2) DEFAULT 0,
    network_out_mb DECIMAL(10, 2) DEFAULT 0,
    server_name VARCHAR(100) DEFAULT 'main'
);

CREATE INDEX IF NOT EXISTS idx_infrastructure_timestamp ON infrastructure_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_infrastructure_server ON infrastructure_metrics(server_name, timestamp DESC);
'''

# Uptime incidents table
UPTIME_INCIDENTS_TABLE = '''
CREATE TABLE IF NOT EXISTS uptime_incidents (
    id SERIAL PRIMARY KEY,
    incident_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    description TEXT,
    affected_services TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_uptime_start ON uptime_incidents(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_uptime_status ON uptime_incidents(status);
CREATE INDEX IF NOT EXISTS idx_uptime_type ON uptime_incidents(incident_type);
'''

# API metrics table
API_METRICS_TABLE = '''
CREATE TABLE IF NOT EXISTS api_metrics (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    user_id INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_api_endpoint ON api_metrics(endpoint, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_status ON api_metrics(status_code, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_timestamp ON api_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_user ON api_metrics(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_api_method ON api_metrics(method, endpoint);
'''

# User sessions table
USER_SESSIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    page_views INTEGER DEFAULT 0,
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    country VARCHAR(100),
    ip_address VARCHAR(45)
);

CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_session ON user_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_start ON user_sessions(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions(last_activity DESC) WHERE end_time IS NULL;
'''

# Page views table
PAGE_VIEWS_TABLE = '''
CREATE TABLE IF NOT EXISTS page_views (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(255),
    page_path VARCHAR(500) NOT NULL,
    page_title VARCHAR(255),
    referrer VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    load_time_ms INTEGER
);

CREATE INDEX IF NOT EXISTS idx_pageviews_user ON page_views(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_pageviews_session ON page_views(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_pageviews_path ON page_views(page_path, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_pageviews_timestamp ON page_views(timestamp DESC);
'''

# Link clicks table
LINK_CLICKS_TABLE = '''
CREATE TABLE IF NOT EXISTS link_clicks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(255),
    link_url VARCHAR(1000) NOT NULL,
    link_text VARCHAR(500),
    page_path VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_external BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_linkclicks_user ON link_clicks(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_linkclicks_session ON link_clicks(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_linkclicks_url ON link_clicks(link_url, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_linkclicks_timestamp ON link_clicks(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_linkclicks_external ON link_clicks(is_external, timestamp DESC);
'''

# User interactions table
USER_INTERACTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    session_id VARCHAR(255),
    interaction_type VARCHAR(50) NOT NULL,
    element_id VARCHAR(255),
    element_type VARCHAR(50),
    page_path VARCHAR(500),
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_interactions_user ON user_interactions(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_session ON user_interactions(session_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_type ON user_interactions(interaction_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON user_interactions(timestamp DESC);
'''

# Error logs table
ERROR_LOGS_TABLE = '''
CREATE TABLE IF NOT EXISTS error_logs (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    endpoint VARCHAR(255),
    user_id INTEGER,
    ip_address VARCHAR(45),
    severity VARCHAR(20) DEFAULT 'error',
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_errors_type ON error_logs(error_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_errors_severity ON error_logs(severity, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_errors_resolved ON error_logs(resolved, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON error_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_errors_endpoint ON error_logs(endpoint, timestamp DESC);
'''

# Security events table
SECURITY_EVENTS_TABLE = '''
CREATE TABLE IF NOT EXISTS security_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    user_id INTEGER,
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    severity VARCHAR(20) DEFAULT 'medium',
    blocked BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_security_type ON security_events(event_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_security_user ON security_events(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_security_ip ON security_events(ip_address, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_security_severity ON security_events(severity, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_security_timestamp ON security_events(timestamp DESC);
'''

# Deployment logs table
DEPLOYMENT_LOGS_TABLE = '''
CREATE TABLE IF NOT EXISTS deployment_logs (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL,
    deployment_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'in_progress',
    success BOOLEAN,
    rollback BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_deployment_version ON deployment_logs(version, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_deployment_status ON deployment_logs(status, start_time DESC);
CREATE INDEX IF NOT EXISTS idx_deployment_start ON deployment_logs(start_time DESC);
'''

# Database metrics table
DATABASE_METRICS_TABLE = '''
CREATE TABLE IF NOT EXISTS database_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    query_time_ms DECIMAL(10, 2),
    slow_queries_count INTEGER DEFAULT 0,
    connection_pool_usage INTEGER DEFAULT 0,
    active_connections INTEGER DEFAULT 0,
    database_size_mb DECIMAL(10, 2),
    replication_lag_ms INTEGER,
    database_name VARCHAR(100) DEFAULT 'main'
);

CREATE INDEX IF NOT EXISTS idx_dbmetrics_timestamp ON database_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dbmetrics_dbname ON database_metrics(database_name, timestamp DESC);
'''

# Alert rules table
ALERT_RULES_TABLE = '''
CREATE TABLE IF NOT EXISTS alert_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) UNIQUE NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    threshold DECIMAL(10, 2) NOT NULL,
    condition VARCHAR(20) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    channels TEXT[] DEFAULT ARRAY['email'],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alertrules_enabled ON alert_rules(enabled, metric_type);
CREATE INDEX IF NOT EXISTS idx_alertrules_type ON alert_rules(metric_type);
'''

# Alert history table
ALERT_HISTORY_TABLE = '''
CREATE TABLE IF NOT EXISTS alert_history (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES alert_rules(id) ON DELETE SET NULL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metric_value DECIMAL(10, 2) NOT NULL,
    message TEXT NOT NULL,
    channel VARCHAR(50) NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerthistory_rule ON alert_history(rule_id, triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerthistory_triggered ON alert_history(triggered_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerthistory_sent ON alert_history(sent, triggered_at DESC);
'''

# All table creation statements
TABLES = [
    ("admin_users", ADMIN_USERS_TABLE),
    ("admin_activity_log", ADMIN_ACTIVITY_LOG_TABLE),
    ("revenue_transactions", REVENUE_TRANSACTIONS_TABLE),
    ("cost_transactions", COST_TRANSACTIONS_TABLE),
    ("financial_summaries", FINANCIAL_SUMMARIES_TABLE),
    ("user_payment_summary", USER_PAYMENT_SUMMARY_TABLE),
    ("bearable_costs", BEARABLE_COSTS_TABLE),
    ("failed_login_attempts", FAILED_LOGIN_ATTEMPTS_TABLE),
    ("infrastructure_metrics", INFRASTRUCTURE_METRICS_TABLE),
    ("uptime_incidents", UPTIME_INCIDENTS_TABLE),
    ("api_metrics", API_METRICS_TABLE),
    ("user_sessions", USER_SESSIONS_TABLE),
    ("page_views", PAGE_VIEWS_TABLE),
    ("link_clicks", LINK_CLICKS_TABLE),
    ("user_interactions", USER_INTERACTIONS_TABLE),
    ("error_logs", ERROR_LOGS_TABLE),
    ("security_events", SECURITY_EVENTS_TABLE),
    ("deployment_logs", DEPLOYMENT_LOGS_TABLE),
    ("database_metrics", DATABASE_METRICS_TABLE),
    ("alert_rules", ALERT_RULES_TABLE),
    ("alert_history", ALERT_HISTORY_TABLE),
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
