"""Feed routes - Personalized feed endpoints"""
from flask import Blueprint
from controllers.feed_controller import FeedController
from middleware.auth_middleware import require_auth
from validators import validate_create_post
from utils.errors import ValidationError
from utils.response import error_response


def create_feed_blueprint(db, limiter=None):
    """Create feed blueprint with rate limiting"""
    feed_bp = Blueprint('feed', __name__, url_prefix='/api')
    feed_controller = FeedController(db)
    
    @feed_bp.route('/feed', methods=['GET'])
    @require_auth
    def get_feed():
        """
        Get personalized feed.
        Rate limit: 30 requests per minute
        """
        return feed_controller.get_feed()
    
    @feed_bp.route('/feed/posts', methods=['POST'])
    @require_auth
    def create_post():
        """
        Create a new post with optional media.
        Rate limit: 10 posts per minute
        """
        from flask import request
        try:
            data = validate_create_post(request.get_json() or {})
            request.validated = data
            return feed_controller.create_post()
        except ValidationError as e:
            return error_response(e.message, e.status_code, e.errors)
    
    # Apply rate limiting if limiter is provided
    if limiter:
        limiter.limit("30 per minute")(get_feed)
        limiter.limit("10 per minute")(create_post)
    
    return feed_bp
