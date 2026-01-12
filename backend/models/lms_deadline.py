"""LMS Deadline Model"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_deadlines_user_due ON lms_deadlines(user_id, due_date)'
]


class LMSDeadline(BaseModel):
    """LMS Deadline model"""
    table_name = 'lms_deadlines'
    
    def get_upcoming(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT d.*, c.title as course_title FROM lms_deadlines d
               LEFT JOIN lms_courses c ON d.course_id = c.id
               WHERE d.user_id = %s AND d.is_completed = FALSE AND d.due_date >= CURRENT_TIMESTAMP
               ORDER BY d.due_date ASC LIMIT %s''',
            (user_id, limit)
        )
    
    def create(self, user_id: str, title: str, due_date: datetime, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_deadlines (user_id, course_id, title, description, due_date)
               VALUES (%s, %s, %s, %s, %s) RETURNING *''',
            (user_id, kwargs.get('course_id'), title, kwargs.get('description'), due_date)
        )
    
    def complete(self, deadline_id: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''UPDATE lms_deadlines SET is_completed = TRUE, completed_at = CURRENT_TIMESTAMP
               WHERE id = %s RETURNING *''',
            (deadline_id,)
        )

