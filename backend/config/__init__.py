"""Configuration module for ZedRec Backend"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False  # Disabled due to Werkzeug 3.x compatibility (bytes vs string issue)
    
    # PostgreSQL settings
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5432))
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'zedreq')
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Connection pool settings
    DB_POOL_MIN = int(os.environ.get('DB_POOL_MIN', 1))
    DB_POOL_SIZE = int(os.environ.get('DB_POOL_SIZE', 5))
    
    # CORS - strip whitespace and trailing slashes from each origin
    CORS_ORIGINS = [
        origin.strip().rstrip('/') 
        for origin in os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
        if origin.strip()
    ]
    
    # Security
    BCRYPT_ROUNDS = int(os.environ.get('BCRYPT_ROUNDS', 12))
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.environ.get('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.environ.get('MAX_PAGE_SIZE', 100))
    
    # Redis Configuration (disabled by default for local dev - set REDIS_ENABLED=true to enable)
    REDIS_ENABLED = os.environ.get('REDIS_ENABLED', 'false').lower() == 'true'
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    REDIS_CACHE_TTL = int(os.environ.get('REDIS_CACHE_TTL', 300))  # 5 minutes default
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET', '')
    CLOUDINARY_UPLOAD_PRESET = os.environ.get('CLOUDINARY_UPLOAD_PRESET', '')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        """Production-specific initialization"""
        # Ensure secret key is set
        if app.config['SECRET_KEY'] == 'dev-secret-key-change-in-production':
            raise ValueError("SECRET_KEY must be set for production!")


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    POSTGRES_DB = os.environ.get('POSTGRES_TEST_DB', 'zedreq_test')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
