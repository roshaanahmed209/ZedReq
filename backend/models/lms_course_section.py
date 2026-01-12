"""LMS Course Section Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS lms_course_sections (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER DEFAULT 0,
    total_items INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = []


class LMSCourseSection(BaseModel):
    """LMS Course Section model"""
    table_name = 'lms_course_sections'
    
    def get_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            'SELECT * FROM lms_course_sections WHERE course_id = %s ORDER BY order_index',
            (course_id,)
        )
    
    def create(self, course_id: int, title: str, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_course_sections (course_id, title, description, order_index, total_items)
               VALUES (%s, %s, %s, %s, %s) RETURNING *''',
            (course_id, title, kwargs.get('description'), kwargs.get('order_index', 0), kwargs.get('total_items', 0))
        )

