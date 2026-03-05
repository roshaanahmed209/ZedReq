"""Authentication utilities for admin users"""
import secrets
import re
from typing import Optional, Tuple
<<<<<<< HEAD
from passlib.context import CryptContext
=======
import bcrypt
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config.settings import settings

<<<<<<< HEAD
# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
=======
# Bcrypt has a 72-byte limit; we truncate before hashing/verifying
BCRYPT_MAX_BYTES = 72
# Max password length allowed by validation/schemas (longer values truncated for hashing)
MAX_PASSWORD_LENGTH = 512


def _to_bcrypt_bytes(password: str) -> bytes:
    """Return password as bytes, truncated to 72 bytes (UTF-8), so bcrypt never raises."""
    if not password:
        return b""
    encoded = password.encode("utf-8")
    return encoded[:BCRYPT_MAX_BYTES] if len(encoded) > BCRYPT_MAX_BYTES else encoded
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe


def hash_password(password: str) -> str:
    """
<<<<<<< HEAD
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)
=======
    Hash a password using bcrypt.
    Passwords longer than 72 bytes are truncated (bcrypt limit).
    """
    return bcrypt.hashpw(_to_bcrypt_bytes(password), bcrypt.gensalt()).decode("ascii")
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
<<<<<<< HEAD
    Verify a password against a stored hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Stored hash from database
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
=======
    Verify a password against a stored hash.
    Uses the same 72-byte truncation as hash_password.
    """
    try:
        return bcrypt.checkpw(
            _to_bcrypt_bytes(plain_password),
            hashed_password.encode("ascii"),
        )
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe
    except Exception:
        return False


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    
    Requirements:
    - At least 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
<<<<<<< HEAD
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
=======
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password is too long (max {MAX_PASSWORD_LENGTH} characters)"
>>>>>>> d402dd046008aff3e043894ed95943e6112c0cfe
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
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


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Optional expiration time delta
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.BACKOFFICE_JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.BACKOFFICE_JWT_SECRET_KEY,
        algorithm=settings.BACKOFFICE_JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT access token
    
    Args:
        token: JWT token to decode
    
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.BACKOFFICE_JWT_SECRET_KEY,
            algorithms=[settings.BACKOFFICE_JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_session_token() -> str:
    """
    Generate a secure session token
    
    Returns:
        Random 64-character hex string
    """
    return secrets.token_hex(32)
