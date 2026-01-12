"""Authentication middleware"""
from functools import wraps
from flask import session, request
from utils.response import error_response
from utils.errors import AuthenticationError

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return error_response('Authentication required', 401)
        return f(*args, **kwargs)
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Allow request to proceed even if not authenticated
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id() -> int:
    """Get current user ID from session"""
    return session.get('user_id')
