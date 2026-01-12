"""LMS Dashboard Model"""
from typing import Optional, Dict, Any
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS lms_dashboard (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    overall_accuracy DECIMAL(5,2) DEFAULT 0.00,
    day_streak INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_dashboard_user ON lms_dashboard(user_id)'
]


class LMSDashboard(BaseModel):
    """LMS Dashboard model - stores user learning stats"""
    table_name = 'lms_dashboard'
    
    def get_by_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            'SELECT * FROM lms_dashboard WHERE user_id = %s', (user_id,)
        )
    
    def create_or_update(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_dashboard (user_id, total_questions, correct_answers, wrong_answers, overall_accuracy, day_streak, last_activity_date)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (user_id) DO UPDATE SET
               total_questions = EXCLUDED.total_questions,
               correct_answers = EXCLUDED.correct_answers,
               wrong_answers = EXCLUDED.wrong_answers,
               overall_accuracy = EXCLUDED.overall_accuracy,
               day_streak = EXCLUDED.day_streak,
               last_activity_date = EXCLUDED.last_activity_date,
               updated_at = CURRENT_TIMESTAMP
               RETURNING *''',
            (user_id, kwargs.get('total_questions', 0), kwargs.get('correct_answers', 0),
             kwargs.get('wrong_answers', 0), kwargs.get('overall_accuracy', 0),
             kwargs.get('day_streak', 0), kwargs.get('last_activity_date'))
        )

