"""User Model - Uses existing schema with uid SERIAL PRIMARY KEY"""
from typing import Optional, Dict, Any, List
from .base import BaseModel


def normalize_user(user: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Normalize user dict to use consistent field names (id, email)"""
    if not user:
        return None
    normalized = dict(user)
    # Map uid -> id for consistency
    if 'uid' in normalized and 'id' not in normalized:
        normalized['id'] = normalized['uid']
    # Map user_email -> email for consistency
    if 'user_email' in normalized and 'email' not in normalized:
        normalized['email'] = normalized['user_email']
    return normalized


class User(BaseModel):
    """User model using existing schema with uid SERIAL PRIMARY KEY"""
    table_name = 'users'
    
    def create(self, username: str, email: str, password_hash: str, full_name: str = None, verification_token: str = None) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        name = full_name or username
        result = self.db.execute_returning(
            '''INSERT INTO users (username, name, user_email, password_hash, verification_token)
               VALUES (%s, %s, %s, %s, %s) 
               RETURNING uid, username, name, user_email, email_verified, created_at''',
            (username, name, email.lower(), password_hash, verification_token)
        )
        return normalize_user(result)
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email address"""
        result = self.db.fetch_one(
            'SELECT * FROM users WHERE LOWER(user_email) = LOWER(%s)', (email,)
        )
        return normalize_user(result)
    
    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Find user by username"""
        result = self.db.fetch_one(
            'SELECT * FROM users WHERE LOWER(username) = LOWER(%s)', (username,)
        )
        return normalize_user(result)
    
    def find_by_username_or_email(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Find user by username or email"""
        result = self.db.fetch_one(
            '''SELECT * FROM users 
               WHERE LOWER(username) = LOWER(%s) OR LOWER(user_email) = LOWER(%s)''',
            (identifier, identifier)
        )
        return normalize_user(result)
    
    def find_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Find user by ID (excludes password_hash for security)"""
        result = self.db.fetch_one(
            '''SELECT uid, username, name, user_email, email_verified, 
                      description_id, last_login, created_at, updated_at 
               FROM users WHERE uid = %s''', 
            (user_id,)
        )
        return normalize_user(result)
    
    def find_by_id_with_password(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Find user by ID including password_hash"""
        result = self.db.fetch_one(
            'SELECT * FROM users WHERE uid = %s', (user_id,)
        )
        return normalize_user(result)
    
    def verify_email(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify user's email with token"""
        result = self.db.execute_returning(
            '''UPDATE users SET email_verified = TRUE, verification_token = NULL, updated_at = CURRENT_TIMESTAMP
               WHERE verification_token = %s AND email_verified = FALSE
               RETURNING uid, username, user_email''',
            (token,)
        )
        return normalize_user(result)
    
    def update_password(self, user_id: int, password_hash: str) -> Optional[Dict[str, Any]]:
        """Update user's password"""
        result = self.db.execute_returning(
            '''UPDATE users SET password_hash = %s, updated_at = CURRENT_TIMESTAMP 
               WHERE uid = %s RETURNING uid, username, name, user_email''',
            (password_hash, user_id)
        )
        return normalize_user(result)
    
    def update_last_login(self, user_id: int) -> None:
        """Update user's last login timestamp"""
        self.db.execute(
            'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE uid = %s',
            (user_id,)
        )
    
    def update_profile(self, user_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update user profile information"""
        result = self.db.execute_returning(
            '''UPDATE users SET 
               name = COALESCE(%s, name),
               updated_at = CURRENT_TIMESTAMP
               WHERE uid = %s 
               RETURNING uid, username, name, user_email''',
            (
                kwargs.get('name'),
                user_id
            )
        )
        return normalize_user(result)
    
    def search_users(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search users by username or name"""
        search_pattern = f"%{query}%"
        results = self.db.fetch_all(
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
        return [normalize_user(r) for r in results]
    
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
    
    def get_total_count(self) -> int:
        """Get total number of users"""
        result = self.db.fetch_one('SELECT COUNT(*) as count FROM users')
        return result['count'] if result else 0
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile with description info"""
        result = self.db.fetch_one(
            '''SELECT u.uid, u.username, u.name, u.user_email, u.email_verified,
                      u.created_at, d.short_desc, d.about, d.profile_pic, d.skills, d.current_status
               FROM users u
               LEFT JOIN description d ON u.description_id = d.desc_id
               WHERE u.uid = %s''',
            (user_id,)
        )
        return normalize_user(result)