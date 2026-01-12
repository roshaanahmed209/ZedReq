"""Job Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS job (
    job_id SERIAL PRIMARY KEY,
    job_desc TEXT NOT NULL,
    designation VARCHAR(100),
    uid INTEGER REFERENCES users(uid) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_job_uid ON job(uid)'
]


class Job(BaseModel):
    """Job model"""
    table_name = 'job'
    
    def create(self, uid: int, job_desc: str, designation: str = None) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''INSERT INTO job (uid, job_desc, designation)
               VALUES (%s, %s, %s) RETURNING *''',
            (uid, job_desc, designation)
        )
    
    def get_by_id(self, job_id: int) -> Optional[Dict[str, Any]]:
        """Get job by ID"""
        return self.db.fetch_one(
            'SELECT * FROM job WHERE job_id = %s', (job_id,)
        )
    
    def get_by_user(self, uid: int) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            'SELECT * FROM job WHERE uid = %s ORDER BY created_at DESC', (uid,)
        )
    
    def update(self, job_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            '''UPDATE job SET job_desc = COALESCE(%s, job_desc),
               designation = COALESCE(%s, designation),
               updated_at = CURRENT_TIMESTAMP
               WHERE job_id = %s RETURNING *''',
            (kwargs.get('job_desc'), kwargs.get('designation'), job_id)
        )
    
    def delete(self, job_id: int, uid: int) -> bool:
        """Delete job (only by owner)"""
        result = self.db.execute_returning(
            'DELETE FROM job WHERE job_id = %s AND uid = %s RETURNING job_id',
            (job_id, uid)
        )
        return result is not None
