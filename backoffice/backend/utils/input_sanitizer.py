"""Input sanitization utilities"""
import re
from typing import Any, Dict, List


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize a string input
    
    Args:
        value: Input string
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        return str(value)[:max_length]
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Truncate to max length
    if len(value) > max_length:
        value = value[:max_length]
    
    # Remove control characters except newlines and tabs
    value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
    
    return value.strip()


def sanitize_dict(data: Dict[str, Any], max_string_length: int = 1000) -> Dict[str, Any]:
    """
    Recursively sanitize dictionary values
    
    Args:
        data: Dictionary to sanitize
        max_string_length: Maximum string length
    
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    
    for key, value in data.items():
        # Sanitize key
        sanitized_key = sanitize_string(str(key), max_length=100)
        
        # Sanitize value
        if isinstance(value, str):
            sanitized[sanitized_key] = sanitize_string(value, max_string_length)
        elif isinstance(value, dict):
            sanitized[sanitized_key] = sanitize_dict(value, max_string_length)
        elif isinstance(value, list):
            sanitized[sanitized_key] = [
                sanitize_dict(item, max_string_length) if isinstance(item, dict)
                else sanitize_string(item, max_string_length) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            sanitized[sanitized_key] = value
    
    return sanitized


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 150


def validate_url(url: str) -> bool:
    """Validate URL format and prevent SSRF"""
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Block localhost and private IPs (SSRF prevention)
    blocked_patterns = [
        r'localhost',
        r'127\.0\.0\.1',
        r'0\.0\.0\.0',
        r'192\.168\.',
        r'10\.',
        r'172\.(1[6-9]|2[0-9]|3[0-1])\.',
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    
    return True


def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    if not isinstance(text, str):
        return str(text)
    
    html_escape_table = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
    }
    
    return "".join(html_escape_table.get(c, c) for c in text)
