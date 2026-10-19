"""Authentication utility functions"""
import secrets
import re
from typing import Optional, Tuple
import bcrypt as _bcrypt
from utils.errors import AuthenticationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string (includes salt automatically)
    """
    return _bcrypt.hashpw(password.encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored hash.

    Args:
        password: Plain text password to verify
        stored_hash: Stored hash from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        return _bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 150


def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    """
    Validate username format
    
    Args:
        username: Username to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username is too long (max 50 characters)"
    
    # Allow alphanumeric, underscores, and hyphens
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        return False, "Username must start with a letter and can only contain letters, numbers, underscores, and hyphens"
    
    # Reserved usernames
    reserved = ['admin', 'root', 'system', 'api', 'null', 'undefined']
    if username.lower() in reserved:
        return False, "This username is reserved"
    
    return True, None


def get_current_user_id() -> Optional[int]:
    return None


def get_current_username() -> Optional[str]:
    return None


def is_authenticated() -> bool:
    return False


def set_user_session(user_id: int, username: str, email: str = None) -> None:
    pass


def clear_user_session() -> None:
    pass


def generate_session_token() -> str:
    """
    Generate a secure session token
    
    Returns:
        Random 64-character hex string
    """
    return secrets.token_hex(32)


def generate_verification_token() -> str:
    """
    Generate a secure email verification token
    
    Returns:
        Random URL-safe token
    """
    return secrets.token_urlsafe(32)
