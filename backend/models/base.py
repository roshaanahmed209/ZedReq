"""Base Model Class"""
from typing import Optional, Dict, Any, List


class BaseModel:
    """Base class for all models"""
    table_name = ''
    
    def __init__(self, db):
        self.db = db
    
    def find_by_id(self, id: int) -> Optional[Dict[str, Any]]:
        return self.db.fetch_one(
            f'SELECT * FROM {self.table_name} WHERE id = %s', (id,)
        )
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        return self.db.fetch_all(
            f'SELECT * FROM {self.table_name} LIMIT %s OFFSET %s', (limit, offset)
        )
    
    def delete(self, id: int) -> bool:
        cursor = self.db.execute(
            f'DELETE FROM {self.table_name} WHERE id = %s', (id,)
        )
        return cursor.rowcount > 0

