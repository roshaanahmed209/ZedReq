"""Post controller"""
from flask import request, session
from ..services.post_service import PostService
from ..middleware.auth_middleware import get_current_user_id
from ..utils.response import success_response

class PostController:
    """Post request handlers"""
    
    def __init__(self, db):
        self.post_service = PostService(db)
    
    def create_post(self):
        """Create a new post"""
        user_id = get_current_user_id()
        post_data = getattr(request, 'validated', request.get_json() or {})
        post = self.post_service.create_post(user_id, post_data['content'])
        return success_response({'post_id': post['id']}, 'Post created successfully', 201)
    
    def get_posts(self):
        """Get all posts"""
        user_id = get_current_user_id()
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        posts = self.post_service.get_posts(user_id, limit, offset)
        return success_response(posts)
    
    def toggle_like(self, post_id: int):
        """Toggle like on a post"""
        user_id = get_current_user_id()
        result = self.post_service.toggle_like(post_id, user_id)
        return success_response(result)
    
    def update_post(self, post_id: int):
        """Update a post"""
        user_id = get_current_user_id()
        post_data = getattr(request, 'validated', request.get_json() or {})
        post = self.post_service.update_post(post_id, user_id, post_data['content'])
        return success_response(post, 'Post updated successfully')
    
    def delete_post(self, post_id: int):
        """Delete a post"""
        user_id = get_current_user_id()
        self.post_service.delete_post(post_id, user_id)
        return success_response(None, 'Post deleted successfully')
