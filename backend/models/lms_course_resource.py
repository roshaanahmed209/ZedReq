"""LMS Course Resource Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = []


class LMSCourseResource(BaseModel):
    """LMS Course Resource model"""
    table_name = 'lms_course_resources'
    
    def get_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            'SELECT * FROM lms_course_resources WHERE course_id = %s ORDER BY order_index',
            (course_id,)
        )
    
    def create(self, course_id: int, title: str, resource_type: str, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_course_resources (course_id, title, resource_type, url, description, order_index)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING *''',
            (course_id, title, resource_type, kwargs.get('url'), kwargs.get('description'), kwargs.get('order_index', 0))
        )

