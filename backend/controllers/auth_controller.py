"""Authentication controller"""
from flask import request, session
from services.auth_service import AuthService
from utils.response import success_response, error_response
from utils.auth import set_user_session, clear_user_session, is_authenticated
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthController:
    """Authentication request handlers"""
    
    def __init__(self, db):
        self.auth_service = AuthService(db)
    
    def register(self):
        """Handle user registration"""
        user_data = getattr(request, 'validated', request.get_json() or {})
        user = self.auth_service.register(user_data)
        
        # Set session after successful registration
        set_user_session(
            user_id=user['id'],
            username=user['username'],
            email=user['email']
        )
        
        return success_response(user, 'Registration successful', 201)
    
    def login(self):
        """Handle user login"""
        login_data = getattr(request, 'validated', request.get_json() or {})
        result = self.auth_service.login(
            login_data['username'],
            login_data['password']
        )
        
        # Set session after successful login
        set_user_session(
            user_id=result['id'],
            username=result['username'],
            email=result['email']
        )
        
        return success_response({
            'id': result['id'],
            'username': result['username'],
            'email': result['email'],
            'full_name': result['full_name']
        }, result['message'])
    
    def logout(self):
        """Handle user logout"""
        clear_user_session()
        return success_response(None, 'Logged out successfully')
    
    def get_session(self):
        """Check if user is logged in and return session info"""
        if not is_authenticated():
            return error_response('Not authenticated', 401)
        
        try:
            user_id = session.get('user_id')
            user = self.auth_service.get_user_by_id(user_id)
            return success_response(user, 'Session active')
        except Exception as e:
            logger.error(f"Session check error: {e}")
            clear_user_session()
            return error_response('Session expired', 401)
