"""Authentication controller"""
from flask import request, session
from ..services.auth_service import AuthService
from ..utils.response import success_response
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class AuthController:
    """Authentication request handlers"""
    
    def __init__(self, db):
        self.auth_service = AuthService(db)
    
    def register(self):
        """Handle user registration"""
        user_data = getattr(request, 'validated', request.get_json() or {})
        user = self.auth_service.register(user_data)
        
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return success_response(user, 'Registration successful', 201)
    
    def login(self):
        """Handle user login"""
        login_data = getattr(request, 'validated', request.get_json() or {})
        result = self.auth_service.login(
            login_data['username'],
            login_data['password'],
            auto_create=True
        )
        
        # Set session
        session['user_id'] = result['id']
        session['username'] = result['username']
        
        return success_response({
            'id': result['id'],
            'username': result['username']
        }, result['message'])
    
    def logout(self):
        """Handle user logout"""
        session.clear()
        return success_response(None, 'Logged out successfully')
