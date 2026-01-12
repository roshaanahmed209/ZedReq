"""LMS Domain Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS lms_domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = []


class LMSDomain(BaseModel):
    """LMS Domain model - learning categories"""
    table_name = 'lms_domains'
    
    def create(self, name: str, description: str = '', icon: str = '') -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO lms_domains (name, description, icon)
               VALUES (%s, %s, %s) RETURNING *''',
            (name, description, icon)
        )
    
    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one('SELECT * FROM lms_domains WHERE name = %s', (name,))

