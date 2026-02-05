"""
Initialize Database and Create All Tables
This script creates the database if it doesn't exist, then creates all tables.
"""

import os
import sys

# Add parent directory (backend) to path for imports
# Since this file is in backend/db/, we need to go up one level to access config
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# ============================================================================
# DATABASE CREATION
# ============================================================================

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    from dotenv import load_dotenv
    from pathlib import Path
    
    # Load .env from project root
    # File is at backend/db/init_database.py, so go up 3 levels to project root
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"
    load_dotenv(env_file)
    
    # Get database connection parameters (without database name)
    host = os.environ.get('POSTGRES_HOST', 'localhost')
    port = int(os.environ.get('POSTGRES_PORT', 5432))
    dbname = os.environ.get('POSTGRES_DB', 'ZedReq')
    user = os.environ.get('POSTGRES_USER', 'postgres')
    password = os.environ.get('POSTGRES_PASSWORD', '')
    
    # Connect to postgres database to create the target database
    try:
        import psycopg
        conn = psycopg.connect(
            host=host,
            port=port,
            dbname='postgres',  # Connect to default postgres database
            user=user,
            password=password
        )
        conn.autocommit = True
    except ImportError:
        import psycopg2
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname='postgres',
            user=user,
            password=password
        )
        conn.autocommit = True
    
    # Check if database exists
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (dbname,)
    )
    exists = cursor.fetchone()
    
    if not exists:
        print(f"Creating database '{dbname}'...")
        cursor.execute(f'CREATE DATABASE {dbname}')
        print(f"  [OK] Database '{dbname}' created successfully!")
    else:
        print(f"  [OK] Database '{dbname}' already exists")
    
    cursor.close()
    conn.close()
    return dbname

# ============================================================================
# TABLE CREATION SQL - Ordered by dependencies (parent tables first)
# ============================================================================

# Core tables (no foreign key dependencies)
USERS_TABLE = '''
CREATE TABLE IF NOT EXISTS users (
    uid SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    name VARCHAR(100) NOT NULL,
    user_email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    description_id INTEGER,
    pay_id INTEGER,
    job_id INTEGER,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

DESCRIPTION_TABLE = '''
CREATE TABLE IF NOT EXISTS description (
    desc_id SERIAL PRIMARY KEY,
    short_desc TEXT,
    about TEXT,
    certificates TEXT,
    proj_id INTEGER,
    skills TEXT,
    current_status VARCHAR(100),
    profile_pic TEXT,
    cover_pic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LMS_COURSES_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    lessons INTEGER DEFAULT 0,
    duration VARCHAR(50),
    category VARCHAR(100),
    difficulty VARCHAR(20) DEFAULT 'beginner',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LMS_DOMAINS_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

# Tables with foreign key to users
POST_TABLE = '''
CREATE TABLE IF NOT EXISTS post (
    post_id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    media_url TEXT,
    media_type VARCHAR(20),
    post_desc TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

JOB_TABLE = '''
CREATE TABLE IF NOT EXISTS job (
    job_id SERIAL PRIMARY KEY,
    job_desc TEXT NOT NULL,
    designation VARCHAR(100),
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LIKES_TABLE = '''
CREATE TABLE IF NOT EXISTS likes (
    like_id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES post(post_id) ON DELETE CASCADE,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, uid)
);
'''

CONNECTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS connections (
    connection_id SERIAL PRIMARY KEY,
    follower_uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    followed_uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (follower_uid, followed_uid)
);
'''

NETWORK_TABLE = '''
CREATE TABLE IF NOT EXISTS network (
    network_id SERIAL PRIMARY KEY,
    uid INTEGER UNIQUE REFERENCES users(uid) ON DELETE CASCADE,
    num_connections INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

PAYMENT_TABLE = '''
CREATE TABLE IF NOT EXISTS payment (
    pay_id SERIAL PRIMARY KEY,
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    
    -- Payment provider info (Stripe/PayPal tokens - NEVER store raw card numbers)
    payment_provider VARCHAR(50) NOT NULL DEFAULT 'stripe',
    provider_customer_id VARCHAR(255),
    provider_payment_method_id VARCHAR(255),
    
    -- Card display info only (last 4 digits for display)
    card_last_four CHAR(4),
    card_brand VARCHAR(20),
    card_exp_month INTEGER,
    card_exp_year INTEGER,
    
    -- Billing info
    billing_name VARCHAR(100),
    billing_email VARCHAR(150),
    
    -- Subscription status
    subscription_status VARCHAR(50) DEFAULT 'inactive',
    subscription_plan VARCHAR(50),
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    
    -- Trial info
    trial_taken BOOLEAN DEFAULT FALSE,
    trial_end TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

CONNECTION_REQUESTS_TABLE = '''
CREATE TABLE IF NOT EXISTS connection_requests (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    receiver_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sender_id, receiver_id)
);
'''

NOTIFICATIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    related_user_id INTEGER REFERENCES users(uid) ON DELETE SET NULL,
    related_request_id INTEGER REFERENCES connection_requests(id) ON DELETE SET NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

# LMS tables with user foreign key
LMS_DASHBOARD_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_dashboard (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    overall_accuracy DECIMAL(5,2) DEFAULT 0.00,
    day_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
'''

LMS_USER_COURSES_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_user_courses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    progress INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'not_started',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    last_accessed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)
);
'''

LMS_USER_DOMAIN_PERFORMANCE_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_user_domain_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    domain_id INTEGER NOT NULL REFERENCES lms_domains(id) ON DELETE CASCADE,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    accuracy_percentage DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, domain_id)
);
'''

LMS_USER_COURSE_PERFORMANCE_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_user_course_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    accuracy_percentage DECIMAL(5,2) DEFAULT 0.00,
    total_points_earned INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id)
);
'''

LMS_WEEKLY_PERFORMANCE_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_weekly_performance (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    date DATE NOT NULL,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    study_time_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
'''

LMS_ACTIVITIES_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER REFERENCES lms_courses(id) ON DELETE SET NULL,
    activity_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LMS_DEADLINES_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_deadlines (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER REFERENCES lms_courses(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LMS_CERTIFICATES_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_certificates (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    certificate_number VARCHAR(100) UNIQUE,
    title VARCHAR(255) NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,
    pdf_url VARCHAR(500),
    UNIQUE(user_id, course_id)
);
'''

LMS_RECOMMENDATIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    reason TEXT,
    priority INTEGER DEFAULT 0,
    is_dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

# LMS tables with course foreign key
LMS_COURSE_SECTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_course_sections (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    total_items INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LMS_COURSE_RESOURCES_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_course_resources (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    url VARCHAR(500),
    description TEXT,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

# LMS tables with section foreign key (depends on lms_course_sections)
LMS_QUESTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_questions (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    section_id INTEGER REFERENCES lms_course_sections(id) ON DELETE SET NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'text',
    options JSONB,
    correct_answer TEXT,
    points INTEGER DEFAULT 1,
    order_index INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

LMS_USER_SECTION_PROGRESS_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_user_section_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    section_id INTEGER NOT NULL REFERENCES lms_course_sections(id) ON DELETE CASCADE,
    completed_items INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, section_id)
);
'''

# LMS tables with question foreign key (depends on lms_questions)
LMS_USER_ANSWERS_TABLE = '''
CREATE TABLE IF NOT EXISTS lms_user_answers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES lms_questions(id) ON DELETE CASCADE,
    answer_text TEXT,
    is_correct BOOLEAN,
    points_earned INTEGER DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    evaluated_at TIMESTAMP,
    feedback TEXT
);
'''

# Azel agent tables (depends on users and lms_courses)
AZEL_SEARCH_URLS_TABLE = '''
CREATE TABLE IF NOT EXISTS azel_search_urls (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    url_id VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    title VARCHAR(500),
    snippet TEXT,
    search_query TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, course_id, url_id)
);
'''

# ORM Job Tables (using SQLAlchemy models)
JOB_POSTINGS_TABLE = '''
CREATE TABLE IF NOT EXISTS job_postings (
    job_id SERIAL PRIMARY KEY,
    poster_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    company_name VARCHAR(150),
    location VARCHAR(150),
    job_type VARCHAR(50) DEFAULT 'full-time',
    is_remote BOOLEAN DEFAULT FALSE,
    experience_level VARCHAR(50),
    skills_required TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

JOB_APPLICATIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS job_applications (
    application_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    applicant_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    status VARCHAR(30) DEFAULT 'pending',
    cover_letter TEXT,
    match_score INTEGER,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, applicant_id)
);
'''

JOB_SAVED_TABLE = '''
CREATE TABLE IF NOT EXISTS job_saved (
    saved_id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(job_id, user_id)
);
'''

# ============================================================================
# INDEX CREATION SQL
# ============================================================================

INDEXES = [
    # Users indexes
    'CREATE INDEX IF NOT EXISTS idx_users_email ON users(user_email)',
    'CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)',
    'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
    
    # Post indexes
    'CREATE INDEX IF NOT EXISTS idx_post_uid ON post(uid)',
    'CREATE INDEX IF NOT EXISTS idx_post_created ON post(created_at DESC)',
    'CREATE INDEX IF NOT EXISTS idx_post_uid_created_deleted ON post(uid, created_at DESC, is_deleted)',
    'CREATE INDEX IF NOT EXISTS idx_post_feed ON post(created_at DESC, post_id DESC) WHERE is_deleted = FALSE',
    'CREATE INDEX IF NOT EXISTS idx_post_media ON post(media_url) WHERE media_url IS NOT NULL',
    
    # Job indexes
    'CREATE INDEX IF NOT EXISTS idx_job_uid ON job(uid)',
    
    # Likes indexes
    'CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id)',
    'CREATE INDEX IF NOT EXISTS idx_likes_user ON likes(uid)',
    'CREATE INDEX IF NOT EXISTS idx_likes_post_user ON likes(post_id, uid)',
    
    # Connections indexes
    'CREATE INDEX IF NOT EXISTS idx_connections_follower ON connections(follower_uid)',
    'CREATE INDEX IF NOT EXISTS idx_connections_followed ON connections(followed_uid)',
    
    # Network indexes
    'CREATE INDEX IF NOT EXISTS idx_network_uid ON network(uid)',
    
    # Payment indexes
    'CREATE INDEX IF NOT EXISTS idx_payment_uid ON payment(uid)',
    'CREATE INDEX IF NOT EXISTS idx_payment_provider_customer ON payment(provider_customer_id)',
    'CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(subscription_status)',
    
    # Connection requests indexes
    'CREATE INDEX IF NOT EXISTS idx_conn_req_sender ON connection_requests(sender_id)',
    'CREATE INDEX IF NOT EXISTS idx_conn_req_receiver ON connection_requests(receiver_id)',
    'CREATE INDEX IF NOT EXISTS idx_conn_req_status ON connection_requests(status)',
    
    # Notifications indexes
    'CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_notif_unread ON notifications(user_id, is_read) WHERE is_read = FALSE',
    
    # LMS Dashboard indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_dashboard_user ON lms_dashboard(user_id)',
    
    # LMS User Courses indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_user ON lms_user_courses(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_course ON lms_user_courses(course_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_status ON lms_user_courses(status)',
    
    # LMS User Domain Performance indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_domain_perf_user ON lms_user_domain_performance(user_id)',
    
    # LMS User Course Performance indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_course_perf_user ON lms_user_course_performance(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_course_perf_course ON lms_user_course_performance(course_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_course_perf_user_course ON lms_user_course_performance(user_id, course_id)',
    
    # LMS Weekly Performance indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_weekly_perf_user_date ON lms_weekly_performance(user_id, date DESC)',
    
    # LMS Activities indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_activities_user ON lms_activities(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_activities_created ON lms_activities(created_at DESC)',
    
    # LMS Deadlines indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_deadlines_user_due ON lms_deadlines(user_id, due_date)',
    
    # LMS Certificates indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_certificates_user ON lms_certificates(user_id)',
    
    # LMS Recommendations indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_recommendations_user ON lms_recommendations(user_id)',
    
    # LMS Questions indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_questions_course ON lms_questions(course_id)',
    
    # LMS User Answers indexes
    'CREATE INDEX IF NOT EXISTS idx_lms_user_answers_user ON lms_user_answers(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_user_answers_question ON lms_user_answers(question_id)',
    
    # Job Postings indexes
    'CREATE INDEX IF NOT EXISTS idx_job_postings_poster ON job_postings(poster_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_location ON job_postings(location)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_type ON job_postings(job_type)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_remote_active ON job_postings(is_remote, status)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_created_desc ON job_postings(created_at DESC)',
    
    # Job Applications indexes
    'CREATE INDEX IF NOT EXISTS idx_job_applications_job ON job_applications(job_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_applications_applicant ON job_applications(applicant_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_applications_job_status ON job_applications(job_id, status)',
    
    # Job Saved indexes
    'CREATE INDEX IF NOT EXISTS idx_job_saved_job ON job_saved(job_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_saved_user ON job_saved(user_id)',
]

# ============================================================================
# ORDERED TABLE LIST (for creation in correct dependency order)
# ============================================================================

TABLES_IN_ORDER = [
    # Level 0: No dependencies
    ("users", USERS_TABLE),
    ("description", DESCRIPTION_TABLE),
    ("lms_courses", LMS_COURSES_TABLE),
    ("lms_domains", LMS_DOMAINS_TABLE),
    
    # Level 1: Depends on users
    ("post", POST_TABLE),
    ("job", JOB_TABLE),
    ("likes", LIKES_TABLE),  # Depends on post
    ("connections", CONNECTIONS_TABLE),
    ("network", NETWORK_TABLE),
    ("payment", PAYMENT_TABLE),
    ("connection_requests", CONNECTION_REQUESTS_TABLE),
    ("notifications", NOTIFICATIONS_TABLE),  # Depends on connection_requests
    ("lms_dashboard", LMS_DASHBOARD_TABLE),
    
    # Level 2: Depends on users and lms_courses
    ("lms_user_courses", LMS_USER_COURSES_TABLE),
    ("lms_activities", LMS_ACTIVITIES_TABLE),
    ("lms_deadlines", LMS_DEADLINES_TABLE),
    ("lms_certificates", LMS_CERTIFICATES_TABLE),
    ("lms_recommendations", LMS_RECOMMENDATIONS_TABLE),
    ("lms_course_sections", LMS_COURSE_SECTIONS_TABLE),
    ("lms_course_resources", LMS_COURSE_RESOURCES_TABLE),
    ("azel_search_urls", AZEL_SEARCH_URLS_TABLE),
    
    # Level 3: Depends on users and lms_domains
    ("lms_user_domain_performance", LMS_USER_DOMAIN_PERFORMANCE_TABLE),
    ("lms_weekly_performance", LMS_WEEKLY_PERFORMANCE_TABLE),
    ("lms_user_course_performance", LMS_USER_COURSE_PERFORMANCE_TABLE),
    
    # Level 4: Depends on lms_course_sections
    ("lms_questions", LMS_QUESTIONS_TABLE),
    ("lms_user_section_progress", LMS_USER_SECTION_PROGRESS_TABLE),
    
    # Level 5: Depends on lms_questions
    ("lms_user_answers", LMS_USER_ANSWERS_TABLE),
    
    # Level 6: Job portal tables (depends on users)
    ("job_postings", JOB_POSTINGS_TABLE),
    ("job_applications", JOB_APPLICATIONS_TABLE),  # Depends on job_postings
    ("job_saved", JOB_SAVED_TABLE),  # Depends on job_postings
]

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def get_db():
    """Get database connection"""
    from config.database import get_connection_params, Database
    params = get_connection_params()
    return Database(params)


def create_all_tables(db=None):
    """Create all tables in the correct order"""
    close_db = False
    if db is None:
        db = get_db()
        close_db = True
    
    print("=" * 60)
    print("Creating all tables for ZedReq database...")
    print("=" * 60)
    
    success_count = 0
    error_count = 0
    
    for table_name, sql in TABLES_IN_ORDER:
        try:
            db.execute(sql)
            print(f"  [OK] Created table: {table_name}")
            success_count += 1
        except Exception as e:
            print(f"  [ERROR] Error creating {table_name}: {e}")
            error_count += 1
    
    print("-" * 60)
    print("Creating indexes...")
    print("-" * 60)
    
    index_success = 0
    index_error = 0
    
    for index_sql in INDEXES:
        try:
            db.execute(index_sql)
            index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
            print(f"  [OK] Created index: {index_name}")
            index_success += 1
        except Exception as e:
            print(f"  [ERROR] Error creating index: {e}")
            index_error += 1
    
    print("=" * 60)
    print(f"Table creation complete: {success_count} succeeded, {error_count} failed")
    print(f"Index creation complete: {index_success} succeeded, {index_error} failed")
    print("=" * 60)
    
    if close_db:
        db.close()
    
    return error_count == 0 and index_error == 0


def init_database():
    """Initialize database and create all tables"""
    print("=" * 60)
    print("ZedReq Database Initialization")
    print("=" * 60)
    print()
    
    # Step 1: Create database if it doesn't exist
    print("[Step 1/2] Checking/Creating database...")
    try:
        create_database_if_not_exists()
        print()
    except Exception as e:
        print(f"  [ERROR] Failed to create database: {e}")
        return False
    
    # Step 2: Create all tables
    print("[Step 2/2] Creating all tables...")
    try:
        success = create_all_tables()
        print()
        if success:
            print("=" * 60)
            print("✅ Database initialization completed successfully!")
            print("=" * 60)
        else:
            print("=" * 60)
            print("⚠️  Database initialization completed with errors")
            print("=" * 60)
        return success
    except Exception as e:
        print(f"  [ERROR] Failed to create tables: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize database and create all tables')
    parser.add_argument('--skip-db', action='store_true', help='Skip database creation (assume it exists)')
    
    args = parser.parse_args()
    
    if args.skip_db:
        # Just create tables
        create_all_tables()
    else:
        # Full initialization
        init_database()
