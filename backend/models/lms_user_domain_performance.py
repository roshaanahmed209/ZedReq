"""LMS User Domain Performance Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS lms_user_domain_performance (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    domain_id INTEGER NOT NULL REFERENCES lms_domains(id) ON DELETE CASCADE,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    accuracy_percentage DECIMAL(5,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, domain_id)
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_domain_perf_user ON lms_user_domain_performance(user_id)'
]


class LMSUserDomainPerformance(BaseModel):
    """LMS User Domain Performance model"""
    table_name = 'lms_user_domain_performance'
    
    def get_all_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT p.*, d.name as domain_name, d.icon FROM lms_user_domain_performance p
               JOIN lms_domains d ON p.domain_id = d.id
               WHERE p.user_id = %s ORDER BY p.accuracy_percentage DESC''',
            (user_id,)
        )
    
    def update(self, user_id: str, domain_id: int, correct: bool) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_user_domain_performance (user_id, domain_id, questions_answered, correct_answers, accuracy_percentage)
               VALUES (%s, %s, 1, %s, %s)
               ON CONFLICT (user_id, domain_id) DO UPDATE SET
               questions_answered = lms_user_domain_performance.questions_answered + 1,
               correct_answers = lms_user_domain_performance.correct_answers + %s,
               accuracy_percentage = ROUND((lms_user_domain_performance.correct_answers + %s)::numeric / 
                                          (lms_user_domain_performance.questions_answered + 1) * 100, 2),
               updated_at = CURRENT_TIMESTAMP
               RETURNING *''',
            (user_id, domain_id, 1 if correct else 0, 100.0 if correct else 0.0, 
             1 if correct else 0, 1 if correct else 0)
        )

