"""Description (Profile) Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS description (
    desc_id SERIAL PRIMARY KEY,
    short_desc TEXT,
    about TEXT,
    certificates TEXT,
    proj_id INTEGER,
    skills TEXT,
    current_status VARCHAR(100),
    profile_pic TEXT,
    cover_pic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = []


class Description(BaseModel):
    """Description/Profile model"""
    table_name = 'description'
    
    def create(self, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO description (short_desc, about, certificates, proj_id, skills, current_status, profile_pic, cover_pic)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *''',
            (kwargs.get('short_desc'), kwargs.get('about'), kwargs.get('certificates'),
             kwargs.get('proj_id'), kwargs.get('skills'), kwargs.get('current_status'),
             kwargs.get('profile_pic'), kwargs.get('cover_pic'))
        )
    
    def get_by_id(self, desc_id: int) -> Optional[Dict[str, Any]]:
        """Get description by ID"""
        return self.db.fetch_one(
            'SELECT * FROM description WHERE desc_id = %s', (desc_id,)
        )
    
    def update(self, desc_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''UPDATE description SET 
               short_desc = COALESCE(%s, short_desc),
               about = COALESCE(%s, about),
               certificates = COALESCE(%s, certificates),
               skills = COALESCE(%s, skills),
               current_status = COALESCE(%s, current_status),
               profile_pic = COALESCE(%s, profile_pic),
               cover_pic = COALESCE(%s, cover_pic),
               updated_at = CURRENT_TIMESTAMP
               WHERE desc_id = %s RETURNING *''',
            (kwargs.get('short_desc'), kwargs.get('about'), kwargs.get('certificates'),
             kwargs.get('skills'), kwargs.get('current_status'),
             kwargs.get('profile_pic'), kwargs.get('cover_pic'), desc_id)
        )
