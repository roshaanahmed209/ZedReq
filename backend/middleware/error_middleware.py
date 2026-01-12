"""Error handling middleware"""
from flask import jsonify
from utils.errors import AppError
from utils.response import error_response
from utils.logger import setup_logger

logger = setup_logger(__name__)

def error_handler(error):
    """Global error handler"""
    if isinstance(error, AppError):
        logger.warning(f"AppError: {error.message} (Status: {error.status_code})")
        return error_response(error.message, error.status_code, getattr(error, 'errors', None))
    
    # Log unexpected errors
    logger.error(f"Unexpected error: {error}", exc_info=True)
    return error_response('Internal server error', 500)

def not_found_handler(error):
    """404 handler"""
    return error_response('Resource not found', 404)
