"""LMS Activity Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_activities_user ON lms_activities(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_activities_created ON lms_activities(created_at DESC)'
]


class LMSActivity(BaseModel):
    """LMS Activity model - learning activity log"""
    table_name = 'lms_activities'
    
    def get_recent(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT a.*, c.title as course_title FROM lms_activities a
               LEFT JOIN lms_courses c ON a.course_id = c.id
               WHERE a.user_id = %s ORDER BY a.created_at DESC LIMIT %s''',
            (user_id, limit)
        )
    
    def log(self, user_id: str, activity_type: str, title: str, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_activities (user_id, course_id, activity_type, title, description, icon)
               VALUES (%s, %s, %s, %s, %s, %s) RETURNING *''',
            (user_id, kwargs.get('course_id'), activity_type, title,
             kwargs.get('description'), kwargs.get('icon'))
        )

