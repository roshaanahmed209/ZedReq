"""Response utility functions"""
from flask import jsonify
from typing import Any, Optional, Dict, List

def success_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """Create a success response"""
    response = {
        "success": True,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(message: str = "An error occurred", status_code: int = 500, errors: Optional[List] = None):
    """Create an error response"""
    response = {
        "success": False,
        "message": message
    }
    if errors:
        response["errors"] = errors
    return jsonify(response), status_code

def paginated_response(data: List[Any], pagination: Dict[str, Any], message: str = "Success"):
    """Create a paginated response"""
    return jsonify({
        "success": True,
        "message": message,
        "data": data,
        "pagination": pagination
    }), 200
