"""Authentication validators"""
import re
from utils.errors import ValidationError

# Password requirements (must match auth.py)
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50


def validate_register(data: dict) -> dict:
    """Validate registration data"""
    errors = []
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()
    
    # Username validation
    if not username or len(username) < USERNAME_MIN_LENGTH:
        errors.append(f'Username must be at least {USERNAME_MIN_LENGTH} characters long')
    elif len(username) > USERNAME_MAX_LENGTH:
        errors.append(f'Username must be at most {USERNAME_MAX_LENGTH} characters')
    elif not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        errors.append('Username must start with a letter and contain only letters, numbers, underscores, or hyphens')
    elif username.lower() in ['admin', 'root', 'system', 'api', 'null', 'undefined']:
        errors.append('This username is reserved')
    
    # Email validation
    if not email or not is_valid_email(email):
        errors.append('Valid email is required')
    elif len(email) > 150:
        errors.append('Email is too long')
    
    # Password validation (must match auth.py requirements)
    if not password:
        errors.append('Password is required')
    elif len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f'Password must be at least {PASSWORD_MIN_LENGTH} characters long')
    elif len(password) > PASSWORD_MAX_LENGTH:
        errors.append(f'Password must be at most {PASSWORD_MAX_LENGTH} characters')
    else:
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one digit')
    
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
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
