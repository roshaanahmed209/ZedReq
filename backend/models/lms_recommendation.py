"""LMS Recommendation Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS lms_recommendations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES lms_courses(id) ON DELETE CASCADE,
    reason TEXT,
    priority INTEGER DEFAULT 0,
    is_dismissed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_lms_recommendations_user ON lms_recommendations(user_id)'
]


class LMSRecommendation(BaseModel):
    """LMS Recommendation model - AI course recommendations"""
    table_name = 'lms_recommendations'
    
    def get_for_user(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            '''SELECT r.*, c.title, c.icon, c.description FROM lms_recommendations r
               JOIN lms_courses c ON r.course_id = c.id
               WHERE r.user_id = %s AND r.is_dismissed = FALSE
               ORDER BY r.priority DESC LIMIT %s''',
            (user_id, limit)
        )
    
    def create(self, user_id: str, course_id: int, reason: str, priority: int = 0) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_recommendations (user_id, course_id, reason, priority)
               VALUES (%s, %s, %s, %s) RETURNING *''',
            (user_id, course_id, reason, priority)
        )
    
    def dismiss(self, recommendation_id: int) -> bool:
        cursor = self.db.execute(
            'UPDATE lms_recommendations SET is_dismissed = TRUE WHERE id = %s',
            (recommendation_id,)
        )
        return cursor.rowcount > 0

