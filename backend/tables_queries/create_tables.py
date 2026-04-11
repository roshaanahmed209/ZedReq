"""
Create All Tables for ZedReq Database
Generates SQL for creating all tables and indexes in the correct order (respecting foreign keys).

Consolidates schema from init_database.py, create_profile_tables.py, and db/migrations/.
Requires PostgreSQL with the pgvector extension for embedding columns on description and job_postings.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret TEXT,
    two_factor_backup_codes TEXT,
    two_factor_verified BOOLEAN DEFAULT FALSE,
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
    resume TEXT,
    profile_version INTEGER DEFAULT 1,
    city VARCHAR(150),
    country VARCHAR(150),
    embedding vector(3072),
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
    post_link TEXT,
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

POST_COMMENT_TABLE = '''
CREATE TABLE IF NOT EXISTS post_comment (
    comment_id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES post(post_id) ON DELETE CASCADE,
    uid INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    -- Subscription status (synced copy — authoritative source is user_subscriptions)
    subscription_status VARCHAR(50) DEFAULT 'inactive',
    subscription_plan VARCHAR(50),
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    
    -- FK link to user_subscriptions (set when plan changes, used for future payment linkage)
    subscription_id INTEGER REFERENCES user_subscriptions(subscription_id) ON DELETE SET NULL,
    
    -- Payment amount and transaction details
    amount NUMERIC(10, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    payment_date TIMESTAMP,
    transaction_id VARCHAR(255),
    last_payment_date TIMESTAMP,
    
    -- Trial info
    trial_taken BOOLEAN DEFAULT FALSE,
    trial_end TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    accuracy_percentage NUMERIC(5,2) DEFAULT 0.00,
    total_points_earned INTEGER DEFAULT 0,
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

# ============================================================================
# SUBSCRIPTION & USAGE TABLES
# ============================================================================

SUBSCRIPTION_PLANS_TABLE = '''
CREATE TABLE IF NOT EXISTS subscription_plans (
    plan_id SERIAL PRIMARY KEY,
    plan_name VARCHAR(50) UNIQUE NOT NULL,
    ai_messages_per_month INTEGER NOT NULL DEFAULT 0,
    course_enrollments_per_month INTEGER NOT NULL DEFAULT 0,
    interview_sessions_per_month INTEGER NOT NULL DEFAULT 0,
    interview_max_duration_seconds INTEGER NOT NULL DEFAULT 60,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USER_SUBSCRIPTIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS user_subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    plan_id INTEGER NOT NULL REFERENCES subscription_plans(plan_id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    assigned_by VARCHAR(50) NOT NULL DEFAULT 'system',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USAGE_TRACKING_TABLE = '''
CREATE TABLE IF NOT EXISTS usage_tracking (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    feature VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    usage_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, feature, period_start)
);
'''

# Profile feature tables (LinkedIn-style sections; see create_profile_tables.py)
USER_EXPERIENCE_TABLE = '''
CREATE TABLE IF NOT EXISTS user_experience (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    company VARCHAR(150) NOT NULL,
    location VARCHAR(150),
    start_date DATE NOT NULL,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    description TEXT,
    employment_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USER_EDUCATION_TABLE = '''
CREATE TABLE IF NOT EXISTS user_education (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    school VARCHAR(200) NOT NULL,
    degree VARCHAR(150),
    field_of_study VARCHAR(150),
    start_year INTEGER,
    end_year INTEGER,
    grade VARCHAR(50),
    activities TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USER_PROJECTS_TABLE = '''
CREATE TABLE IF NOT EXISTS user_projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    url TEXT,
    start_date DATE,
    end_date DATE,
    associated_with VARCHAR(200),
    technologies JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USER_PROFILE_RECOMMENDATIONS_TABLE = '''
CREATE TABLE IF NOT EXISTS user_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    recommender_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    relationship VARCHAR(100),
    recommendation_text TEXT NOT NULL,
    is_visible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USER_INTERESTS_TABLE = '''
CREATE TABLE IF NOT EXISTS user_interests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    interest_type VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

PROFILE_ANALYTICS_TABLE = '''
CREATE TABLE IF NOT EXISTS profile_analytics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    viewer_id INTEGER REFERENCES users(uid) ON DELETE SET NULL,
    view_type VARCHAR(50) NOT NULL,
    source VARCHAR(50),
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

JOB_POSTINGS_TABLE = '''
CREATE TABLE IF NOT EXISTS job_postings (
    job_id SERIAL PRIMARY KEY,
    poster_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    company_name VARCHAR(150),
    location VARCHAR(150),
    city VARCHAR(150),
    country VARCHAR(150),
    job_type VARCHAR(50) DEFAULT 'full-time',
    is_remote BOOLEAN DEFAULT FALSE,
    experience_level VARCHAR(50),
    skills_required TEXT,
    salary_min INTEGER,
    salary_max INTEGER,
    status VARCHAR(20) DEFAULT 'active',
    job_link TEXT,
    embedding vector(3072),
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

LIVE_INTERVIEWS_TABLE = '''
CREATE TABLE IF NOT EXISTS live_interviews (
    interview_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES job_postings(job_id) ON DELETE CASCADE,
    tavus_conversation_id VARCHAR(255),
    tavus_response JSONB,
    questions JSONB,
    user_responses JSONB,
    overall_score INTEGER,
    score_breakdown JSONB,
    feedback TEXT,
    riz_feedback JSONB,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USER_JOB_PREFERENCES_TABLE = '''
CREATE TABLE IF NOT EXISTS user_job_preferences (
    user_id INTEGER PRIMARY KEY REFERENCES users(uid) ON DELETE CASCADE,
    preferred_location TEXT,
    preferred_job_type VARCHAR(50),
    preferred_remote BOOLEAN,
    salary_expectation_min INTEGER,
    salary_expectation_max INTEGER,
    experience_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

USER_JOB_RECOMMENDATIONS_CACHE_TABLE = '''
CREATE TABLE IF NOT EXISTS user_job_recommendations_cache (
    user_id INTEGER PRIMARY KEY REFERENCES users(uid) ON DELETE CASCADE,
    recommendations JSONB NOT NULL,
    cache_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);
'''

RESERVED_SEATS_TABLE = '''
CREATE TABLE IF NOT EXISTS reserved_seats (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    user_id INTEGER REFERENCES users(uid) ON DELETE SET NULL,
    promo_code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
'''

AZEL_JOBS_TABLE = '''
CREATE TABLE IF NOT EXISTS azel_jobs (
    job_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'queued',
    response JSONB,
    error TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
'''

DELETED_USER_ARCHIVE_TABLE = '''
CREATE TABLE IF NOT EXISTS deleted_user_archive (
    id BIGSERIAL PRIMARY KEY,
    original_uid INTEGER NOT NULL,
    user_email VARCHAR(150),
    deleted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deletion_source VARCHAR(20) NOT NULL,
    admin_id INTEGER,
    reason TEXT,
    user_snapshot JSONB NOT NULL,
    description_snapshot JSONB,
    subscriptions_snapshot JSONB,
    payments_snapshot JSONB
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

    # Post comments
    'CREATE INDEX IF NOT EXISTS idx_post_comment_post ON post_comment(post_id)',
    'CREATE INDEX IF NOT EXISTS idx_post_comment_post_created ON post_comment(post_id, created_at DESC)',
    
    # Connections indexes
    'CREATE INDEX IF NOT EXISTS idx_connections_follower ON connections(follower_uid)',
    'CREATE INDEX IF NOT EXISTS idx_connections_followed ON connections(followed_uid)',
    
    # Network indexes
    'CREATE INDEX IF NOT EXISTS idx_network_uid ON network(uid)',
    
    # Payment indexes
    'CREATE INDEX IF NOT EXISTS idx_payment_uid ON payment(uid)',
    'CREATE INDEX IF NOT EXISTS idx_payment_provider_customer ON payment(provider_customer_id)',
    'CREATE INDEX IF NOT EXISTS idx_payment_status ON payment(subscription_status)',
    'CREATE INDEX IF NOT EXISTS idx_payment_subscription_id ON payment(subscription_id)',
    'CREATE INDEX IF NOT EXISTS idx_payment_transaction_id ON payment(transaction_id)',
    'CREATE INDEX IF NOT EXISTS idx_payment_payment_date ON payment(payment_date)',
    
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
    
    # Azel Search URLs indexes
    'CREATE INDEX IF NOT EXISTS idx_azel_search_urls_user_course ON azel_search_urls(user_id, course_id)',
    'CREATE INDEX IF NOT EXISTS idx_azel_search_urls_created ON azel_search_urls(created_at DESC)',

    # Subscription & Usage indexes
    'CREATE INDEX IF NOT EXISTS idx_subscription_plans_name ON subscription_plans(plan_name)',
    'CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user ON user_subscriptions(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_subscriptions_plan ON user_subscriptions(plan_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(status)',
    'CREATE INDEX IF NOT EXISTS idx_usage_tracking_lookup ON usage_tracking(user_id, feature, period_start)',

    # Connection requests & notifications
    'CREATE INDEX IF NOT EXISTS idx_conn_req_sender ON connection_requests(sender_id)',
    'CREATE INDEX IF NOT EXISTS idx_conn_req_receiver ON connection_requests(receiver_id)',
    'CREATE INDEX IF NOT EXISTS idx_conn_req_status ON connection_requests(status)',
    'CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_notif_unread ON notifications(user_id, is_read) WHERE is_read = FALSE',

    # Profile feature tables
    'CREATE INDEX IF NOT EXISTS idx_user_experience_user_id ON user_experience(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_education_user_id ON user_education(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_projects_user_id ON user_projects(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_recommendations_user_id ON user_recommendations(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_recommendations_recommender_id ON user_recommendations(recommender_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_interests_user_id ON user_interests(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_interests_type ON user_interests(interest_type)',
    'CREATE INDEX IF NOT EXISTS idx_profile_analytics_user_id ON profile_analytics(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_profile_analytics_viewer_id ON profile_analytics(viewer_id)',
    'CREATE INDEX IF NOT EXISTS idx_profile_analytics_viewed_at ON profile_analytics(viewed_at)',
    'CREATE INDEX IF NOT EXISTS idx_profile_analytics_user_viewed ON profile_analytics(user_id, viewed_at)',

    # Job portal
    'CREATE INDEX IF NOT EXISTS idx_job_postings_poster ON job_postings(poster_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_location ON job_postings(location)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_type ON job_postings(job_type)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_remote_active ON job_postings(is_remote, status)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_created_desc ON job_postings(created_at DESC)',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_city ON job_postings(city) WHERE city IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_country ON job_postings(country) WHERE country IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_job_postings_city_country ON job_postings(city, country) WHERE city IS NOT NULL AND country IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_job_applications_job ON job_applications(job_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_applications_applicant ON job_applications(applicant_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_applications_job_status ON job_applications(job_id, status)',
    'CREATE INDEX IF NOT EXISTS idx_job_saved_job ON job_saved(job_id)',
    'CREATE INDEX IF NOT EXISTS idx_job_saved_user ON job_saved(user_id)',

    # Live interviews
    'CREATE INDEX IF NOT EXISTS idx_live_interviews_user_id ON live_interviews(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_live_interviews_job_id ON live_interviews(job_id)',
    'CREATE INDEX IF NOT EXISTS idx_live_interviews_user_job ON live_interviews(user_id, job_id)',
    'CREATE INDEX IF NOT EXISTS idx_live_interviews_status ON live_interviews(status) WHERE status IN (\'pending\', \'in_progress\')',
    'CREATE INDEX IF NOT EXISTS idx_live_interviews_tavus_conversation_id ON live_interviews(tavus_conversation_id) WHERE tavus_conversation_id IS NOT NULL',

    # Recommendations cache & preferences
    'CREATE INDEX IF NOT EXISTS idx_recommendations_cache_user_id ON user_job_recommendations_cache(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_recommendations_cache_expires ON user_job_recommendations_cache(expires_at) WHERE expires_at IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_description_profile_version ON description(profile_version) WHERE profile_version IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_user_job_preferences_user_id ON user_job_preferences(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_user_job_preferences_location ON user_job_preferences(preferred_location) WHERE preferred_location IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_user_job_preferences_job_type ON user_job_preferences(preferred_job_type) WHERE preferred_job_type IS NOT NULL',

    # Reserved seats & Azel jobs
    'CREATE INDEX IF NOT EXISTS idx_reserved_seats_email ON reserved_seats(email)',
    'CREATE INDEX IF NOT EXISTS idx_reserved_seats_user_id ON reserved_seats(user_id) WHERE user_id IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_reserved_seats_promo_code ON reserved_seats(promo_code)',
    'CREATE INDEX IF NOT EXISTS idx_reserved_seats_created_at ON reserved_seats(created_at)',
    'CREATE INDEX IF NOT EXISTS idx_azel_jobs_user_id ON azel_jobs(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_azel_jobs_status ON azel_jobs(status)',
    'CREATE INDEX IF NOT EXISTS idx_azel_jobs_created_at ON azel_jobs(created_at)',

    # Deleted user archive (no FK to users — retention only)
    'CREATE INDEX IF NOT EXISTS idx_deleted_user_archive_original_uid ON deleted_user_archive(original_uid)',
    'CREATE INDEX IF NOT EXISTS idx_deleted_user_archive_user_email ON deleted_user_archive(user_email)',
    'CREATE INDEX IF NOT EXISTS idx_deleted_user_archive_deleted_at ON deleted_user_archive(deleted_at DESC)',

    # pgvector IVFFLAT (may fail until extension exists or with empty tables — safe to re-run later)
    'CREATE INDEX IF NOT EXISTS idx_job_embeddings ON job_postings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)',
    'CREATE INDEX IF NOT EXISTS idx_description_embeddings ON description USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)',

    # User location on description
    'CREATE INDEX IF NOT EXISTS idx_description_city ON description(city) WHERE city IS NOT NULL',
    'CREATE INDEX IF NOT EXISTS idx_description_country ON description(country) WHERE country IS NOT NULL',
]

# ============================================================================
# ORDERED TABLE LIST (for creation in correct dependency order)
# ============================================================================

TABLES_IN_ORDER = [
    # Level 0: No dependencies (description uses vector — requires pgvector extension)
    ("users", USERS_TABLE),
    ("description", DESCRIPTION_TABLE),
    ("lms_courses", LMS_COURSES_TABLE),
    ("lms_domains", LMS_DOMAINS_TABLE),
    ("subscription_plans", SUBSCRIPTION_PLANS_TABLE),
    ("user_subscriptions", USER_SUBSCRIPTIONS_TABLE),
    ("usage_tracking", USAGE_TRACKING_TABLE),
    ("user_job_preferences", USER_JOB_PREFERENCES_TABLE),

    # Level 1: Depends on users (and post before likes)
    ("post", POST_TABLE),
    ("job", JOB_TABLE),
    ("likes", LIKES_TABLE),
    ("post_comment", POST_COMMENT_TABLE),
    ("connections", CONNECTIONS_TABLE),
    ("network", NETWORK_TABLE),
    ("connection_requests", CONNECTION_REQUESTS_TABLE),
    ("notifications", NOTIFICATIONS_TABLE),
    ("lms_dashboard", LMS_DASHBOARD_TABLE),

    ("user_experience", USER_EXPERIENCE_TABLE),
    ("user_education", USER_EDUCATION_TABLE),
    ("user_projects", USER_PROJECTS_TABLE),
    ("user_recommendations", USER_PROFILE_RECOMMENDATIONS_TABLE),
    ("user_interests", USER_INTERESTS_TABLE),
    ("profile_analytics", PROFILE_ANALYTICS_TABLE),

    # Payment (depends on users + user_subscriptions via subscription_id FK)
    ("payment", PAYMENT_TABLE),

    # LMS: users + lms_courses
    ("lms_user_courses", LMS_USER_COURSES_TABLE),
    ("lms_activities", LMS_ACTIVITIES_TABLE),
    ("lms_deadlines", LMS_DEADLINES_TABLE),
    ("lms_certificates", LMS_CERTIFICATES_TABLE),
    ("lms_recommendations", LMS_RECOMMENDATIONS_TABLE),
    ("lms_course_sections", LMS_COURSE_SECTIONS_TABLE),
    ("lms_course_resources", LMS_COURSE_RESOURCES_TABLE),
    ("azel_search_urls", AZEL_SEARCH_URLS_TABLE),

    ("lms_user_domain_performance", LMS_USER_DOMAIN_PERFORMANCE_TABLE),
    ("lms_weekly_performance", LMS_WEEKLY_PERFORMANCE_TABLE),
    ("lms_user_course_performance", LMS_USER_COURSE_PERFORMANCE_TABLE),

    ("lms_questions", LMS_QUESTIONS_TABLE),
    ("lms_user_section_progress", LMS_USER_SECTION_PROGRESS_TABLE),
    ("lms_user_answers", LMS_USER_ANSWERS_TABLE),

    # Job portal + related
    ("job_postings", JOB_POSTINGS_TABLE),
    ("job_applications", JOB_APPLICATIONS_TABLE),
    ("job_saved", JOB_SAVED_TABLE),
    ("live_interviews", LIVE_INTERVIEWS_TABLE),
    ("user_job_recommendations_cache", USER_JOB_RECOMMENDATIONS_CACHE_TABLE),
    ("reserved_seats", RESERVED_SEATS_TABLE),
    ("azel_jobs", AZEL_JOBS_TABLE),
    ("deleted_user_archive", DELETED_USER_ARCHIVE_TABLE),
]


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

    try:
        db.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("  [OK] pgvector extension available (embedding columns enabled)")
    except Exception as e:
        print(f"  [WARN] pgvector extension: {e}")
        print("  [INFO] Install pgvector or use a pgvector image; CREATE TABLE may fail on embedding columns.")

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
    
    for index_sql in INDEXES:
        try:
            db.execute(index_sql)
            index_name = index_sql.split("EXISTS")[1].split("ON")[0].strip()
            print(f"  [OK] Created index: {index_name}")
        except Exception as e:
            print(f"  [ERROR] Error creating index: {e}")
    
    print("=" * 60)
    print(f"Table creation complete: {success_count} succeeded, {error_count} failed")
    print("=" * 60)
    
    if close_db:
        db.close()
    
    return error_count == 0


def get_create_sql():
    """Get all CREATE TABLE SQL as a single string"""
    sql_parts = [
        "-- ZedReq Database Schema",
        "-- Generated table creation script",
        "-- Requires: CREATE EXTENSION IF NOT EXISTS vector;\n",
        "CREATE EXTENSION IF NOT EXISTS vector;\n",
    ]
    
    for table_name, sql in TABLES_IN_ORDER:
        sql_parts.append(f"-- Table: {table_name}")
        sql_parts.append(sql.strip())
        sql_parts.append("")
    
    sql_parts.append("\n-- Indexes")
    for index_sql in INDEXES:
        sql_parts.append(f"{index_sql};")
    
    return "\n".join(sql_parts)


def export_sql(filename: str = "create_tables.sql"):
    """Export all CREATE TABLE SQL to a file"""
    sql = get_create_sql()
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w') as f:
        f.write(sql)
    
    print(f"SQL exported to: {filepath}")
    return filepath


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create all database tables')
    parser.add_argument('--export', action='store_true', help='Export SQL to file instead of executing')
    parser.add_argument('--print', action='store_true', dest='print_sql', help='Print SQL to console')
    
    args = parser.parse_args()
    
    if args.export:
        export_sql()
    elif args.print_sql:
        print(get_create_sql())
    else:
        create_all_tables()

