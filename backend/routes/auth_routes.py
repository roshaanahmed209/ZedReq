"""Authentication routes"""
from flask import Blueprint, request
from ..controllers.auth_controller import AuthController
from ..validators import validate_register, validate_login
from ..utils.errors import ValidationError
from ..utils.response import error_response

def create_auth_blueprint(db):
    """Create authentication blueprint"""
    auth_bp = Blueprint('auth', __name__)
    auth_controller = AuthController(db)
    
    @auth_bp.route('/register', methods=['POST'])
    def register():
        try:
            data = validate_register(request.get_json() or {})
            request.validated = data
            return auth_controller.register()
        except ValidationError as e:
            return error_response(e.message, e.status_code, e.errors)
    
    @auth_bp.route('/login', methods=['POST'])
    def login():
        try:
            data = validate_login(request.get_json() or {})
            request.validated = data
            return auth_controller.login()
        except ValidationError as e:
            return error_response(e.message, e.status_code, e.errors)
    
    @auth_bp.route('/logout', methods=['GET'])
    def logout():
        return auth_controller.logout()
    
    return auth_bp

# For backward compatibility
auth_bp = None
