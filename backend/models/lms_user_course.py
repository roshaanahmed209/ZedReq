"""LMS User Course Progress Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_user ON lms_user_courses(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_course ON lms_user_courses(course_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_user_courses_status ON lms_user_courses(status)'
]


class LMSUserCourse(BaseModel):
    """LMS User Course Progress model"""
    table_name = 'lms_user_courses'
    
    def get_user_courses(self, user_id: str, status: str = None) -> List[Dict[str, Any]]:
        if status:
            return self.db.fetch_all(
                '''SELECT uc.*, c.title, c.icon, c.lessons, c.duration 
                   FROM lms_user_courses uc 
                   JOIN lms_courses c ON uc.course_id = c.id 
                   WHERE uc.user_id = %s AND uc.status = %s''',
                (user_id, status)
            )
        return self.db.fetch_all(
            '''SELECT uc.*, c.title, c.icon, c.lessons, c.duration 
               FROM lms_user_courses uc 
               JOIN lms_courses c ON uc.course_id = c.id 
               WHERE uc.user_id = %s''',
            (user_id,)
        )
    
    def enroll(self, user_id: str, course_id: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_user_courses (user_id, course_id, status, started_at)
               VALUES (%s, %s, 'in_progress', CURRENT_TIMESTAMP)
               ON CONFLICT (user_id, course_id) DO NOTHING
               RETURNING *''',
            (user_id, course_id)
        )
    
    def update_progress(self, user_id: str, course_id: int, progress: int) -> Optional[Dict[str, Any]]:
        status = 'completed' if progress >= 100 else 'in_progress'
        return self.db.execute_returning(
            '''UPDATE lms_user_courses 
               SET progress = %s, status = %s, last_accessed_at = CURRENT_TIMESTAMP,
               completed_at = CASE WHEN %s >= 100 THEN CURRENT_TIMESTAMP ELSE completed_at END,
               updated_at = CURRENT_TIMESTAMP
               WHERE user_id = %s AND course_id = %s
               RETURNING *''',
            (progress, status, progress, user_id, course_id)
        )

