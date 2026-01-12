"""Network Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS network (
    network_id SERIAL PRIMARY KEY,
    uid INTEGER UNIQUE REFERENCES users(uid) ON DELETE CASCADE,
    num_connections INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_network_uid ON network(uid)'
]


class Network(BaseModel):
    """Network model"""
    table_name = 'network'
    
    def create(self, uid: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            'INSERT INTO network (uid) VALUES (%s) RETURNING *',
            (uid,)
        )
    
    def get_by_user(self, uid: int) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            'SELECT * FROM network WHERE uid = %s', (uid,)
        )
    
    def increment_connections(self, uid: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            'UPDATE network SET num_connections = num_connections + 1 WHERE uid = %s RETURNING *',
            (uid,)
        )
    
    def decrement_connections(self, uid: int) -> Optional[Dict[str, Any]]:
        return self.db.execute_returning(
            'UPDATE network SET num_connections = GREATEST(num_connections - 1, 0) WHERE uid = %s RETURNING *',
            (uid,)
        )

