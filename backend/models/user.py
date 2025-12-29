from typing import Optional, Dict, Any, List
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg
from ..config.database import Database

class User:
    """User model"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def create(self, username: str, email: str, password: str, full_name: str = '') -> Dict[str, Any]:
        """Create a new user"""
        hashed_password = generate_password_hash(password)
        
        try:
            return self.db.execute_returning(
                '''INSERT INTO users (username, email, password, full_name) 
                   VALUES (%s, %s, %s, %s)
                   RETURNING id, username, email, full_name, headline, bio, avatar, created_at, updated_at''',
                (username, email, hashed_password, full_name)
            )
        except psycopg.errors.UniqueViolation:
            raise ValueError('Username or email already exists')
        except Exception as e:
            if 'unique' in str(e).lower():
                raise ValueError('Username or email already exists')
            raise
    
    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by UUID"""
        return self.db.fetch_one(
            '''SELECT id, username, email, full_name, headline, bio, avatar, 
                      created_at, updated_at 
               FROM users WHERE id = %s''',
            (user_id,)
        )
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username"""
        return self.db.fetch_one(
            'SELECT * FROM users WHERE username = %s',
            (username,)
        )
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        return self.db.fetch_one(
            'SELECT * FROM users WHERE email = %s',
            (email,)
        )
    
    def find_by_username_or_email(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Find user by username or email"""
        return self.db.fetch_one(
            'SELECT * FROM users WHERE username = %s OR email = %s',
            (identifier, identifier)
        )
    
    def update(self, user_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user information"""
        allowed_fields = ['full_name', 'headline', 'bio', 'avatar']
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                updates.append(f"{key} = %s")
                values.append(value)
        
        if not updates:
            return self.find_by_id(user_id)
        
        updates.append('updated_at = CURRENT_TIMESTAMP')
        values.append(user_id)
        
        self.db.execute(
            f'''UPDATE users SET {', '.join(updates)} WHERE id = %s''',
            tuple(values)
        )
        
        return self.find_by_id(user_id)
    
    def search(self, query: str, exclude_user_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search users"""
        sql = '''SELECT id, username, full_name, headline, avatar 
                 FROM users 
                 WHERE (username ILIKE %s OR full_name ILIKE %s)'''
        params = [f'%{query}%', f'%{query}%']
        
        if exclude_user_id:
            sql += ' AND id != %s'
            params.append(exclude_user_id)
        
        sql += ' LIMIT %s'
        params.append(limit)
        
        return self.db.fetch_all(sql, tuple(params))
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password"""
        return check_password_hash(hashed_password, password)
