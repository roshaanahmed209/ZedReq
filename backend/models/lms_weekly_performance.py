"""LMS Weekly Performance Model"""
from typing import Optional, Dict, Any, List
from datetime import date
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS lms_weekly_performance (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    wrong_answers INTEGER DEFAULT 0,
    study_time_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_weekly_perf_user_date ON lms_weekly_performance(user_id, date DESC)'
]


class LMSWeeklyPerformance(BaseModel):
    """LMS Weekly Performance model"""
    table_name = 'lms_weekly_performance'
    
    def get_weekly(self, user_id: str, days: int = 7) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT * FROM lms_weekly_performance 
               WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '%s days'
               ORDER BY date DESC''',
            (user_id, days)
        )
    
    def record_day(self, user_id: str, record_date: date, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_weekly_performance (user_id, date, questions_answered, correct_answers, wrong_answers, study_time_minutes)
               VALUES (%s, %s, %s, %s, %s, %s)
               ON CONFLICT (user_id, date) DO UPDATE SET
               questions_answered = lms_weekly_performance.questions_answered + EXCLUDED.questions_answered,
               correct_answers = lms_weekly_performance.correct_answers + EXCLUDED.correct_answers,
               wrong_answers = lms_weekly_performance.wrong_answers + EXCLUDED.wrong_answers,
               study_time_minutes = lms_weekly_performance.study_time_minutes + EXCLUDED.study_time_minutes
               RETURNING *''',
            (user_id, record_date, kwargs.get('questions_answered', 0),
             kwargs.get('correct_answers', 0), kwargs.get('wrong_answers', 0),
             kwargs.get('study_time_minutes', 0))
        )

