"""Flask application factory"""
from flask import Flask, request, jsonify, make_response
from flask_session import Session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from config.database import init_database
from routes import create_auth_blueprint, create_user_blueprint, create_post_blueprint, create_feed_blueprint
from utils.logger import setup_logger
from utils.errors import AppError
import os
import traceback
import sys

logger = setup_logger(__name__)


class CORSMiddleware:
    """WSGI middleware to handle CORS at the lowest level"""
    
    def __init__(self, app, allowed_origins):
        self.app = app
        self.allowed_origins = [o.rstrip('/') for o in allowed_origins]
    
    def __call__(self, environ, start_response):
        origin = environ.get('HTTP_ORIGIN', '')
        clean_origin = origin.rstrip('/')
        
        # Check if origin is allowed
        if clean_origin in self.allowed_origins:
            cors_headers = [
                ('Access-Control-Allow-Origin', origin),
                ('Access-Control-Allow-Credentials', 'true'),
                ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With, Accept'),
                ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
                ('Access-Control-Max-Age', '3600'),
            ]
        else:
            cors_headers = []
        
        # Handle OPTIONS preflight
        if environ.get('REQUEST_METHOD') == 'OPTIONS':
            headers = [('Content-Type', 'text/plain'), ('Content-Length', '0')] + cors_headers
            start_response('200 OK', headers)
            return [b'']
        
        # Wrap start_response to add CORS headers
        def custom_start_response(status, response_headers, exc_info=None):
            # Add CORS headers to the response
            all_headers = list(response_headers) + cors_headers
            return start_response(status, all_headers, exc_info)
        
        try:
            return self.app(environ, custom_start_response)
        except Exception as e:
            # Even on exception, return with CORS headers
            logger.error(f"WSGI Error: {e}\n{traceback.format_exc()}")
            error_body = b'{"success": false, "message": "Internal server error"}'
            headers = [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body))),
            ] + cors_headers
            start_response('500 Internal Server Error', headers)
            return [error_body]

# Initialize rate limiter (will be attached to app in factory)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Call init_app if config class has it (for production checks)
    config_class = config[config_name]
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)
    
    # Initialize PostgreSQL database
    db = init_database()
    
    # Initialize Session
    Session(app)
    
    # Get allowed origins (already cleaned in config, but rstrip as safety)
    allowed_origins = [origin.strip().rstrip('/') for origin in app.config['CORS_ORIGINS'] if origin.strip()]
    logger.info(f"CORS allowed origins: {allowed_origins}")
    
    # Store for use in error handlers
    app.config['ALLOWED_ORIGINS'] = allowed_origins
    
    # ============================================================
    # NOTE: CORS is handled by CORSMiddleware at WSGI level
    # No need for additional Flask-level CORS handlers
    # ============================================================
    
    # ============================================================
    # Rate Limiter
    # ============================================================
    limiter.init_app(app)
    
    # Handle rate limit exceeded
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'success': False,
            'message': 'Rate limit exceeded. Please try again later.'
        }), 429
    
    # ============================================================
    # Register blueprints
    # ============================================================
    app.register_blueprint(create_auth_blueprint(db, limiter))
    app.register_blueprint(create_user_blueprint(db))
    app.register_blueprint(create_post_blueprint(db))
    app.register_blueprint(create_feed_blueprint(db, limiter))
    
    # Health check route
    @app.route('/')
    def index():
        return {
            'message': 'ZedReq API Server',
            'version': '1.0.0',
            'status': 'running'
        }
    
    # ============================================================
    # Error Handlers (CORS handled by CORSMiddleware)
    # ============================================================
    
    @app.errorhandler(400)
    def bad_request_handler(error):
        return jsonify({
            'success': False,
            'message': str(error.description) if hasattr(error, 'description') else 'Bad request'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized_handler(error):
        return jsonify({
            'success': False,
            'message': 'Not authenticated'
        }), 401
    
    @app.errorhandler(404)
    def not_found_handler(error):
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error_handler(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
    
    @app.errorhandler(Exception)
    def global_error_handler(error):
        """Handle all uncaught exceptions (CORS handled by middleware)"""
        if isinstance(error, AppError):
            logger.warning(f"AppError: {error.message} (Status: {error.status_code})")
            response_data = {'success': False, 'message': error.message}
            if hasattr(error, 'errors') and error.errors:
                response_data['errors'] = error.errors
            return jsonify(response_data), error.status_code
        else:
            # Log the full traceback for unexpected errors
            logger.error(f"Unexpected error: {error}\n{traceback.format_exc()}")
            return jsonify({
                'success': False,
                'message': 'Internal server error'
            }), 500
    
    logger.info(f"Application created successfully (env: {config_name})")
    return app


# Create app instance
app = create_app()

# Get allowed origins for WSGI middleware
allowed_origins = app.config.get('ALLOWED_ORIGINS', ['http://localhost:3000', 'http://localhost:5173'])

# Wrap with CORS middleware at WSGI level - handles CORS even when Flask fails
app.wsgi_app = CORSMiddleware(app.wsgi_app, allowed_origins)

if __name__ == '__main__':
    # Enable request logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    print(f"Starting server with CORS origins: {allowed_origins}", file=sys.stderr)
    app.run(debug=True, port=5000, host='127.0.0.1')
