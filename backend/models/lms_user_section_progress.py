"""LMS User Section Progress Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = []


class LMSUserSectionProgress(BaseModel):
    """LMS User Section Progress model"""
    table_name = 'lms_user_section_progress'
    
    def get_progress(self, user_id: str, section_id: int) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            'SELECT * FROM lms_user_section_progress WHERE user_id = %s AND section_id = %s',
            (user_id, section_id)
        )
    
    def update(self, user_id: str, section_id: int, completed_items: int, total_items: int) -> Optional[Dict[str, Any]]:
        is_completed = completed_items >= total_items
        return self.db.execute_returning(
            '''INSERT INTO lms_user_section_progress (user_id, section_id, completed_items, is_completed)
               VALUES (%s, %s, %s, %s)
               ON CONFLICT (user_id, section_id) DO UPDATE SET
               completed_items = EXCLUDED.completed_items,
               is_completed = EXCLUDED.is_completed,
               updated_at = CURRENT_TIMESTAMP
               RETURNING *''',
            (user_id, section_id, completed_items, is_completed)
        )

