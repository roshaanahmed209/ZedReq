"""Authentication routes"""
from flask import Blueprint, request
from controllers.auth_controller import AuthController
from validators import validate_register, validate_login
from utils.errors import ValidationError, AuthenticationError
from utils.response import error_response


def create_auth_blueprint(db, limiter=None):
    """Create authentication blueprint with rate limiting"""
    auth_bp = Blueprint('auth', __name__)
    auth_controller = AuthController(db)
    
    # Rate limiting decorators (applied if limiter is provided)
    def apply_rate_limit(limit_string):
        """Helper to apply rate limiting if limiter exists"""
        if limiter:
            return limiter.limit(limit_string)
        return lambda f: f  # No-op decorator if no limiter
    
    @auth_bp.route('/register', methods=['POST'])
    @apply_rate_limit("5 per minute")  # Strict limit on registration
    def register():
        """User registration endpoint"""
        try:
            data = validate_register(request.get_json() or {})
            request.validated = data
            return auth_controller.register()
        except ValidationError as e:
            return error_response(e.message, e.status_code, getattr(e, 'errors', []))
        except Exception as e:
            return error_response(str(e), 400)
    
    @auth_bp.route('/login', methods=['POST'])
    @apply_rate_limit("10 per minute")  # Prevent brute force attacks
    def login():
        """User login endpoint"""
        try:
            data = validate_login(request.get_json() or {})
            request.validated = data
            return auth_controller.login()
        except ValidationError as e:
            return error_response(e.message, e.status_code, getattr(e, 'errors', []))
        except AuthenticationError as e:
            return error_response(e.message, e.status_code)
        except Exception as e:
            return error_response(str(e), 400)
    
    @auth_bp.route('/logout', methods=['GET', 'POST'])
    def logout():
        """User logout endpoint"""
        return auth_controller.logout()
    
    @auth_bp.route('/session', methods=['GET'])
    def check_session():
        """Check if user is authenticated and return session info"""
        return auth_controller.get_session()
    
    return auth_bp


# For backward compatibility
auth_bp = None
