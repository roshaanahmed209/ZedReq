import psycopg2
from psycopg2 import pool, extras
import logging
import os
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class Database:
    """PostgreSQL database connection manager with connection pooling"""
    
    def __init__(self, connection_params: Dict[str, Any]):
        self.connection_params = connection_params
        self._pool: Optional[pool.ThreadedConnectionPool] = None
        self._min_connections = int(os.environ.get('DB_POOL_MIN', 1))
        self._max_connections = int(os.environ.get('DB_POOL_SIZE', 5))
    
    def connect(self):
        """Create database connection pool"""
        try:
            self._pool = pool.ThreadedConnectionPool(
                self._min_connections,
                self._max_connections,
                **self.connection_params
            )
            logger.info(f"Connected to PostgreSQL database: {self.connection_params.get('dbname')}")
            return self._pool
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool"""
        if self._pool is None:
            self.connect()
        
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self._pool.putconn(conn)
    
    def execute(self, query: str, params: tuple = ()) -> psycopg2.extensions.cursor:
        """Execute a query and return cursor"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(query, params)
            conn.commit()
            return cursor
    
    def execute_returning(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query with RETURNING clause and fetch the result"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(query, params)
            conn.commit()
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Fetch one row"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows"""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_many(self, query: str, params_list: List[tuple]):
        """Execute query with multiple parameter sets"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
    
    def close(self):
        """Close all database connections in the pool"""
        if self._pool:
            self._pool.closeall()
            self._pool = None
            logger.info("Database connection pool closed")


def get_connection_params() -> Dict[str, Any]:
    """Get PostgreSQL connection parameters from environment"""
    # Check for DATABASE_URL first (common in production/cloud environments)
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Parse DATABASE_URL if provided
        return {'dsn': database_url}
    
    # Otherwise use individual parameters
    return {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': int(os.environ.get('POSTGRES_PORT', 5432)),
        'dbname': os.environ.get('POSTGRES_DB', 'zedreq'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'database'),
    }


def init_database() -> Database:
    """Initialize database and create schema"""
    connection_params = get_connection_params()
    db = Database(connection_params)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Enable UUID extension
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        
        # Users table - using UUID as primary key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                headline VARCHAR(255),
                bio TEXT,
                avatar VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Posts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Connections table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id SERIAL PRIMARY KEY,
                user1_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                user2_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user1_id, user2_id)
            )
        ''')
        
        # Likes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS likes (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(post_id, user_id)
            )
        ''')
        
        # =============================================
        # LMS (Learning Management System) Tables
        # =============================================
        
        # LMS Dashboard - Main user LMS stats (linked to user via UUID)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_dashboard (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                wrong_answers INTEGER DEFAULT 0,
                overall_accuracy DECIMAL(5,2) DEFAULT 0.00,
                day_streak INTEGER DEFAULT 0,
                last_activity_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            )
        ''')
        
        # LMS Courses - Available courses in the system
        cursor.execute('''
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
            )
        ''')
        
        # LMS User Course Progress - Tracks each user's progress per course
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_user_courses (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
                progress INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'not_started',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                last_accessed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, course_id)
            )
        ''')
        
        # LMS Course Sections - Sections within a course
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_course_sections (
                id SERIAL PRIMARY KEY,
                course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                order_index INTEGER DEFAULT 0,
                total_items INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # LMS User Section Progress - Tracks user progress per section
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_user_section_progress (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                section_id INTEGER NOT NULL REFERENCES lms_course_sections(id) ON DELETE CASCADE,
                completed_items INTEGER DEFAULT 0,
                is_completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, section_id)
            )
        ''')
        
        # LMS Weekly Performance - Daily stats for weekly chart
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_weekly_performance (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                questions_answered INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                wrong_answers INTEGER DEFAULT 0,
                study_time_minutes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')
        
        # LMS Domains - Learning domains/categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_domains (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                icon VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # LMS User Domain Performance - User performance per domain
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_user_domain_performance (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                domain_id INTEGER NOT NULL REFERENCES lms_domains(id) ON DELETE CASCADE,
                questions_answered INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                accuracy_percentage DECIMAL(5,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, domain_id)
            )
        ''')
        
        # LMS Learning Activities - Recent activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_activities (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES lms_courses(id) ON DELETE SET NULL,
                activity_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                icon VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # LMS Course Questions - Questions for each course
        cursor.execute('''
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
            )
        ''')
        
        # LMS User Answers - User's answers to questions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_user_answers (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                question_id INTEGER NOT NULL REFERENCES lms_questions(id) ON DELETE CASCADE,
                answer_text TEXT,
                is_correct BOOLEAN,
                points_earned INTEGER DEFAULT 0,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                evaluated_at TIMESTAMP,
                feedback TEXT
            )
        ''')
        
        # LMS AI Recommendations - AI-generated course recommendations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_recommendations (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
                reason TEXT,
                priority INTEGER DEFAULT 0,
                is_dismissed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # LMS Deadlines - User's upcoming deadlines
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_deadlines (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER REFERENCES lms_courses(id) ON DELETE SET NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                due_date TIMESTAMP NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_at TIMESTAMP,
                reminder_sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # LMS Certificates - Earned certificates
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_certificates (
                id SERIAL PRIMARY KEY,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
                certificate_number VARCHAR(100) UNIQUE,
                title VARCHAR(255) NOT NULL,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                pdf_url VARCHAR(500),
                UNIQUE(user_id, course_id)
            )
        ''')
        
        # LMS Course Resources - Additional resources for courses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lms_course_resources (
                id SERIAL PRIMARY KEY,
                course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                resource_type VARCHAR(50) NOT NULL,
                url VARCHAR(500),
                description TEXT,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes (IF NOT EXISTS for indexes requires PostgreSQL 9.5+)
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_likes_post_id ON likes(post_id)',
            'CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_connections_user1 ON connections(user1_id)',
            'CREATE INDEX IF NOT EXISTS idx_connections_user2 ON connections(user2_id)',
            'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)',
            'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)',
            # LMS indexes
            'CREATE INDEX IF NOT EXISTS idx_lms_dashboard_user ON lms_dashboard(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_user ON lms_user_courses(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_course ON lms_user_courses(course_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_status ON lms_user_courses(status)',
            'CREATE INDEX IF NOT EXISTS idx_lms_weekly_perf_user_date ON lms_weekly_performance(user_id, date DESC)',
            'CREATE INDEX IF NOT EXISTS idx_lms_activities_user ON lms_activities(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_activities_created ON lms_activities(created_at DESC)',
            'CREATE INDEX IF NOT EXISTS idx_lms_questions_course ON lms_questions(course_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_user_answers_user ON lms_user_answers(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_user_answers_question ON lms_user_answers(question_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_recommendations_user ON lms_recommendations(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_deadlines_user_due ON lms_deadlines(user_id, due_date)',
            'CREATE INDEX IF NOT EXISTS idx_lms_certificates_user ON lms_certificates(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_lms_domain_perf_user ON lms_user_domain_performance(user_id)'
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        conn.commit()
        logger.info("PostgreSQL database initialized successfully")
    
    return db
