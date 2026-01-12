"""User controller"""
from flask import request, session
from services.user_service import UserService
from middleware.auth_middleware import get_current_user_id
from utils.response import success_response

class UserController:
    """User request handlers"""
    
    def __init__(self, db):
        self.user_service = UserService(db)
    
    def get_current_user(self):
        """Get current authenticated user"""
        user_id = get_current_user_id()
        user = self.user_service.get_user_by_id(user_id)
        return success_response(user)
    
    def update_user(self):
        """Update current user"""
        user_id = get_current_user_id()
        update_data = getattr(request, 'validated', request.get_json() or {})
        user = self.user_service.update_user(user_id, update_data)
        return success_response(user, 'User updated successfully')
    
    def search_users(self):
        """Search users"""
        validated = getattr(request, 'validated', {})
        query = validated.get('query', request.args.get('q', '').strip())
        exclude_user_id = get_current_user_id()
        limit = int(request.args.get('limit', 10))
        
        users = self.user_service.search_users(query, exclude_user_id, limit)
        return success_response(users)
