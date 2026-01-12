"""LMS User Answer Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
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
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_user_answers_user ON lms_user_answers(user_id)',
    'CREATE INDEX IF NOT EXISTS idx_lms_user_answers_question ON lms_user_answers(question_id)'
]


class LMSUserAnswer(BaseModel):
    """LMS User Answer model"""
    table_name = 'lms_user_answers'
    
    def submit(self, user_id: str, question_id: int, answer_text: str) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_user_answers (user_id, question_id, answer_text)
               VALUES (%s, %s, %s) RETURNING *''',
            (user_id, question_id, answer_text)
        )
    
    def evaluate(self, answer_id: int, is_correct: bool, points: int, feedback: str = '') -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''UPDATE lms_user_answers 
               SET is_correct = %s, points_earned = %s, feedback = %s, evaluated_at = CURRENT_TIMESTAMP
               WHERE id = %s RETURNING *''',
            (is_correct, points, feedback, answer_id)
        )
    
    def get_user_answers(self, user_id: str, question_id: int = None) -> List[Dict[str, Any]]:
        if question_id:
            return self.db.fetch_all(
                'SELECT * FROM lms_user_answers WHERE user_id = %s AND question_id = %s',
                (user_id, question_id)
            )
        return self.db.fetch_all(
            'SELECT * FROM lms_user_answers WHERE user_id = %s ORDER BY submitted_at DESC',
            (user_id,)
        )

