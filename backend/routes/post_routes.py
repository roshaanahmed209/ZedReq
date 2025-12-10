"""Post routes"""
from flask import Blueprint, request
from ..controllers.post_controller import PostController
from ..middleware.auth_middleware import require_auth
from ..validators import validate_create_post, validate_update_post
from ..utils.errors import ValidationError
from ..utils.response import error_response

def create_post_blueprint(db):
    """Create post blueprint"""
    post_bp = Blueprint('post', __name__, url_prefix='/api')
    post_controller = PostController(db)
    
    @post_bp.route('/posts', methods=['GET'])
    @require_auth
    def get_posts():
        return post_controller.get_posts()
    
    @post_bp.route('/posts', methods=['POST'])
    @require_auth
    def create_post():
        try:
            data = validate_create_post(request.get_json() or {})
            request.validated = data
            return post_controller.create_post()
        except ValidationError as e:
            return error_response(e.message, e.status_code, e.errors)
    
    @post_bp.route('/posts/<int:post_id>/like', methods=['POST'])
    @require_auth
    def toggle_like(post_id):
        return post_controller.toggle_like(post_id)
    
    @post_bp.route('/posts/<int:post_id>', methods=['PUT'])
    @require_auth
    def update_post(post_id):
        try:
            data = validate_update_post(request.get_json() or {})
            request.validated = data
            return post_controller.update_post(post_id)
        except ValidationError as e:
            return error_response(e.message, e.status_code, e.errors)
    
    @post_bp.route('/posts/<int:post_id>', methods=['DELETE'])
    @require_auth
    def delete_post(post_id):
        return post_controller.delete_post(post_id)
    
    return post_bp

# For backward compatibility
post_bp = None
