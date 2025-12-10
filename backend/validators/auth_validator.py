"""Authentication validators"""
import re
from ..utils.errors import ValidationError

def validate_register(data: dict) -> dict:
    """Validate registration data"""
    errors = []
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    
    if not username or len(username) < 3:
        errors.append('Username must be at least 3 characters long')
    
    if not email or not is_valid_email(email):
        errors.append('Valid email is required')
    
    if not password or len(password) < 6:
        errors.append('Password must be at least 6 characters long')
    
    if errors:
        raise ValidationError('Validation failed', errors)
    
    return {
        'username': username,
        'email': email.lower(),
        'password': password,
        'full_name': full_name
    }

def validate_login(data: dict) -> dict:
    """Validate login data"""
    errors = []
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username:
        errors.append('Username or email is required')
    
    if not password:
        errors.append('Password is required')
    
    if errors:
        raise ValidationError('Validation failed', errors)
    
    return {
        'username': username,
        'password': password
    }

def is_valid_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))
