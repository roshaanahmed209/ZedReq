"""LMS Question Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_questions_course ON lms_questions(course_id)'
]


class LMSQuestion(BaseModel):
    """LMS Question model"""
    table_name = 'lms_questions'
    
    def get_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            'SELECT * FROM lms_questions WHERE course_id = %s ORDER BY order_index',
            (course_id,)
        )
    
    def create(self, course_id: int, question_text: str, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_questions (course_id, section_id, question_text, question_type, options, correct_answer, points)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *''',
            (course_id, kwargs.get('section_id'), question_text, kwargs.get('question_type', 'text'),
             kwargs.get('options'), kwargs.get('correct_answer'), kwargs.get('points', 1))
        )

