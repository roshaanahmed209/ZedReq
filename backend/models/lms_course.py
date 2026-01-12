"""LMS Course Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = []


class LMSCourse(BaseModel):
    """LMS Course model"""
    table_name = 'lms_courses'
    
    def create(self, title: str, description: str = '', **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_courses (title, description, icon, lessons, duration, category, difficulty)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *''',
            (title, description, kwargs.get('icon'), kwargs.get('lessons', 0),
             kwargs.get('duration'), kwargs.get('category'), kwargs.get('difficulty', 'beginner'))
        )
    
    def find_by_category(self, category: str) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            'SELECT * FROM lms_courses WHERE category = %s AND is_active = TRUE', (category,)
        )
    
    def find_active(self) -> List[Dict[str, Any]]:
        return self.db.fetch_all('SELECT * FROM lms_courses WHERE is_active = TRUE')

