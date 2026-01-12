"""User Model"""
from typing import Optional, Dict, Any, List
from .base import BaseModel

TABLE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS users (
    uid SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    name VARCHAR(100) NOT NULL,
    user_email VARCHAR(150) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    description_id INTEGER,
    pay_id INTEGER,
    job_id INTEGER,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_users_email ON users(user_email)',
    'CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)',
    'CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)'
]


class User(BaseModel):
    """User model"""
    table_name = 'users'
    
    def create(self, username: str, email: str, password_hash: str, full_name: str = None, verification_token: str = None) -> Optional[Dict[str, Any]]:
        """
        Create a new user
        
        Args:
            username: Unique username
            email: User's email address
            password_hash: Hashed password (use auth.hash_password)
            full_name: User's full name (optional, defaults to username)
            verification_token: Email verification token
        
        Returns:
            Created user dict or None
        """
        name = full_name or username
        return self.db.execute_returning(
            '''INSERT INTO users (username, name, user_email, password_hash, verification_token)
               VALUES (%s, %s, %s, %s, %s) 
               RETURNING uid, username, name, user_email, email_verified, created_at''',
            (username, name, email.lower(), password_hash, verification_token)
        )
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email address"""
        return self.db.fetch_one(
            'SELECT * FROM users WHERE LOWER(user_email) = LOWER(%s)', (email,)
        )
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username"""
        return self.db.fetch_one(
            'SELECT * FROM users WHERE LOWER(username) = LOWER(%s)', (username,)
        )
    
    def find_by_username_or_email(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Find user by username or email
        
        Args:
            identifier: Username or email address
        
        Returns:
            User dict or None
        """
        return self.db.fetch_one(
            '''SELECT * FROM users 
               WHERE LOWER(username) = LOWER(%s) OR LOWER(user_email) = LOWER(%s)''',
            (identifier, identifier)
        )
    
    def find_by_uid(self, uid: int) -> Optional[Dict[str, Any]]:
        """Find user by UID (excludes password_hash for security)"""
        return self.db.fetch_one(
            '''SELECT uid, username, name, user_email, email_verified, 
                      description_id, pay_id, job_id, last_login, created_at, updated_at 
               FROM users WHERE uid = %s''', 
            (uid,)
        )
    
    def verify_email(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify user's email with token"""
        return self.db.execute_returning(
            '''UPDATE users SET email_verified = TRUE, verification_token = NULL, updated_at = CURRENT_TIMESTAMP
               WHERE verification_token = %s AND email_verified = FALSE
               RETURNING uid, username, user_email''',
            (token,)
        )
    
    def update_password(self, uid: int, password_hash: str) -> Optional[Dict[str, Any]]:
        """Update user's password"""
        return self.db.execute_returning(
            '''UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE uid = %s RETURNING uid, username, name, user_email''',
            (password_hash, uid)
        )
    
    def update_last_login(self, uid: int) -> None:
        """Update user's last login timestamp"""
        self.db.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE uid = %s',
            (uid,)
        )
    
    def update_profile(self, uid: int, name: str = None, username: str = None) -> Optional[Dict[str, Any]]:
        """Update user profile information"""
        return self.db.execute_returning(
            '''UPDATE users SET 
               name = COALESCE(%s, name),
               username = COALESCE(%s, username),
               updated_at = CURRENT_TIMESTAMP
               WHERE uid = %s 
               RETURNING uid, username, name, user_email''',
            (name, username, uid)
        )
    
    def update_profile_links(self, uid: int, description_id: int = None, pay_id: int = None, job_id: int = None) -> Optional[Dict[str, Any]]:
        """Update user's linked profile IDs"""
        return self.db.execute_returning(
            '''UPDATE users SET 
               description_id = COALESCE(%s, description_id),
               pay_id = COALESCE(%s, pay_id), 
               job_id = COALESCE(%s, job_id),
               updated_at = CURRENT_TIMESTAMP
               WHERE uid = %s RETURNING uid, username, name, description_id, pay_id, job_id''',
            (description_id, pay_id, job_id, uid)
        )
    
    def search_users(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search users by username or name
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of matching users
        """
        search_pattern = f"%{query}%"
        return self.db.fetch_all(
            '''SELECT uid, username, name, user_email, created_at 
               FROM users 
               WHERE LOWER(username) LIKE LOWER(%s) OR LOWER(name) LIKE LOWER(%s)
               ORDER BY 
                   CASE WHEN LOWER(username) = LOWER(%s) THEN 0
                        WHEN LOWER(username) LIKE LOWER(%s) THEN 1
                        ELSE 2 END
               LIMIT %s''',
            (search_pattern, search_pattern, query, f"{query}%", limit)
        )
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        result = self.db.fetch_one(
            'SELECT 1 FROM users WHERE LOWER(username) = LOWER(%s)', (username,)
        )
        return result is not None
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        result = self.db.fetch_one(
            'SELECT 1 FROM users WHERE LOWER(user_email) = LOWER(%s)', (email,)
        )
        return result is not None
