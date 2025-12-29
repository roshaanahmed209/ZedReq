"""Flask application factory"""
from flask import Flask
from flask_session import Session
from flask_cors import CORS
from config import config
from config.database import init_database
from routes import create_auth_blueprint, create_user_blueprint, create_post_blueprint
from middleware.error_middleware import error_handler, not_found_handler
from utils.logger import setup_logger
import os

logger = setup_logger(__name__)

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize PostgreSQL database
    db = init_database()
    
    # Initialize extensions
    Session(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Register blueprints
    app.register_blueprint(create_auth_blueprint(db))
    app.register_blueprint(create_user_blueprint(db))
    app.register_blueprint(create_post_blueprint(db))
    
    # Health check route
    @app.route('/')
    def index():
        return {
            'message': 'ZedReq API Server',
            'version': '1.0.0',
            'status': 'running'
        }
    
    # Error handlers
    app.register_error_handler(404, not_found_handler)
    app.register_error_handler(Exception, error_handler)
    
    logger.info("Application created successfully")
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
