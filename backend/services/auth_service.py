"""Authentication Service with JWT"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import hashlib
import hmac
import secrets
import re

from models.user import User
from config.settings import settings


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    # Generate a random salt
    salt = secrets.token_hex(16)
    # Hash password with salt
    password_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    # Store as salt$hash format
    return f"sha256${salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Supports:
    - sha256 (new passwords)
    - pbkdf2:sha256 (existing Werkzeug passwords, for backward compatibility)
    """
    if not hashed_password:
        return False
    
    try:
        # Check if it's our new SHA-256 format: sha256$salt$hash
        if hashed_password.startswith('sha256$'):
            parts = hashed_password.split('$')
            if len(parts) == 3:
                _, salt, stored_hash = parts
                computed_hash = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
                return hmac.compare_digest(computed_hash, stored_hash)
        
        # Werkzeug pbkdf2 format: pbkdf2:sha256:iterations$salt$hash
        if hashed_password.startswith('pbkdf2:'):
            method_part, rest = hashed_password.split('$', 1)
            salt, hash_value = rest.rsplit('$', 1)
            
            # Parse iterations from method (pbkdf2:sha256:iterations)
            parts = method_part.split(':')
            iterations = int(parts[2]) if len(parts) >= 3 else 260000
            
            # Compute and compare hash
            computed = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), iterations)
            return hmac.compare_digest(computed.hex(), hash_value)
        
        # Werkzeug scrypt format: scrypt:n:r:p$salt$hash
        if hashed_password.startswith('scrypt:'):
            method_part, salt, hash_value = hashed_password.split('$')
            parts = method_part.split(':')
            n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
            computed = hashlib.scrypt(plain_password.encode('utf-8'), salt=salt.encode('utf-8'), n=n, r=r, p=p)
            return hmac.compare_digest(computed.hex(), hash_value)
        
        return False
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets requirements: 8-25 chars, at least one uppercase"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 25:
        return False, "Password must not exceed 25 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


class AuthService:
    """Authentication business logic with JWT"""
    
    def __init__(self, db):
        self.user_model = User(db)
    
    def _create_access_token(self, user_id: str, username: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "username": username,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def _create_tokens(self, user: dict) -> dict:
        """Create both access and refresh tokens"""
        user_id = str(user["id"])
        access_token = self._create_access_token(user_id, user["username"])
        refresh_token = self._create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "name": user["name"],
                "profile_pic": user.get("profile_pic"),
                "bio": user.get("bio"),
                "job_title": user.get("job_title"),
                "company": user.get("company"),
                "created_at": user.get("created_at")
            }
        }
    
    def register(self, user_data: dict) -> dict:
        """Register a new user and return tokens"""
        username = user_data.get('username', '').strip()
        email = user_data.get('email', '').strip()
        password = user_data.get('password', '')
        full_name = user_data.get('full_name', '').strip() or username
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate email
        if not validate_email(email):
            raise ValueError('Please provide a valid email address')
        
        # Validate password
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check if username already exists
        if self.user_model.username_exists(username):
            raise ValueError('Username already exists')
        
        # Check if email already exists
        if self.user_model.email_exists(email):
            raise ValueError('Email already exists')
        
        # Hash password and create user
        password_hash = hash_password(password)
        user = self.user_model.create(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )
        
        if not user:
            raise Exception('Failed to create user')
        
        # Return tokens
        return self._create_tokens(user)
    
    def login(self, identifier: str, password: str) -> dict:
        """Login user and return tokens"""
        if not identifier or not password:
            raise ValueError('Username/email and password are required')
        
        # Find user by username or email
        user = self.user_model.find_by_username_or_email(identifier.strip())
        
        if not user:
            raise ValueError('Invalid username or password')
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            raise ValueError('Invalid username or password')
        
        # Update last login
        self.user_model.update_last_login(user['id'])
        
        # Return tokens
        return self._create_tokens(user)
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token")
            
            # Get user
            user = self.user_model.find_by_id(int(user_id))
            if not user:
                raise ValueError("User not found")
            
            # Create new tokens
            return self._create_tokens(user)
            
        except JWTError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    def verify_token(self, token: str) -> dict:
        """Verify access token and return user info"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token")
            
            # Get user
            user = self.user_model.find_by_id(int(user_id))
            if not user:
                raise ValueError("User not found")
            
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "name": user["name"]
            }
            
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        user = self.user_model.find_by_id(user_id)
        if not user:
            return None
        
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "name": user["name"],
            "profile_pic": user.get("profile_pic"),
            "bio": user.get("bio"),
            "job_title": user.get("job_title"),
            "company": user.get("company"),
            "created_at": user.get("created_at")
        }
