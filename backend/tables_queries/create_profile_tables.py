"""
Create Profile Feature Tables
Creates tables for experience, education, projects, recommendations, and interests
"""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Table creation SQL
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

USER_RECOMMENDATIONS_TABLE = '''
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

# Indexes for better query performance
CREATE_INDEXES = '''
CREATE INDEX IF NOT EXISTS idx_user_experience_user_id ON user_experience(user_id);
CREATE INDEX IF NOT EXISTS idx_user_education_user_id ON user_education(user_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_user_id ON user_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_user_recommendations_user_id ON user_recommendations(user_id);
CREATE INDEX IF NOT EXISTS idx_user_recommendations_recommender_id ON user_recommendations(recommender_id);
CREATE INDEX IF NOT EXISTS idx_user_interests_user_id ON user_interests(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interests_type ON user_interests(interest_type);
CREATE INDEX IF NOT EXISTS idx_profile_analytics_user_id ON profile_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_profile_analytics_viewer_id ON profile_analytics(viewer_id);
CREATE INDEX IF NOT EXISTS idx_profile_analytics_viewed_at ON profile_analytics(viewed_at);
CREATE INDEX IF NOT EXISTS idx_profile_analytics_user_viewed ON profile_analytics(user_id, viewed_at);
'''

def get_all_sql():
    """Get all CREATE TABLE SQL as a single string"""
    return '\n'.join([
        USER_EXPERIENCE_TABLE,
        USER_EDUCATION_TABLE,
        USER_PROJECTS_TABLE,
        USER_RECOMMENDATIONS_TABLE,
        USER_INTERESTS_TABLE,
        PROFILE_ANALYTICS_TABLE,
        CREATE_INDEXES
    ])

if __name__ == "__main__":
    from config.database import get_database
    
    db = get_database()
    if not db:
        print("Error: Could not connect to database")
        sys.exit(1)
    
    try:
        sql = get_all_sql()
        # Execute each statement separately
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for statement in statements:
            if statement:
                db.execute(statement)
        print("Profile tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if db:
            db.close()
