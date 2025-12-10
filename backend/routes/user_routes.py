"""User routes"""
from flask import Blueprint, request
from ..controllers.user_controller import UserController
from ..middleware.auth_middleware import require_auth
from ..validators import validate_user_search, validate_user_update
from ..utils.errors import ValidationError
from ..utils.response import error_response

def create_user_blueprint(db):
    """Create user blueprint"""
    user_bp = Blueprint('user', __name__, url_prefix='/api')
    user_controller = UserController(db)
    
    @user_bp.route('/user', methods=['GET'])
    @require_auth
    def get_current_user():
        return user_controller.get_current_user()
    
    @user_bp.route('/user', methods=['PUT'])
    @require_auth
    def update_user():
        try:
            data = validate_user_update(request.get_json() or {})
            request.validated = data
            return user_controller.update_user()
        except ValidationError as e:
            return error_response(e.message, e.status_code, e.errors)
    
    @user_bp.route('/users/search', methods=['GET'])
    @require_auth
    def search_users():
        query = validate_user_search(request.args.get('q', ''))
        request.validated = {'query': query}
        return user_controller.search_users()
    
    return user_bp

# For backward compatibility
user_bp = None
