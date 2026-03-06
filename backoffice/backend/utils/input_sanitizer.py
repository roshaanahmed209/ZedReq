"""Input sanitization utilities"""
import re
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


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
    if not isinstance(url, str) or len(url) > 2000:
        return False
    
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
        r'\[::1\]',  # IPv6 localhost
        r'\[::\]',   # IPv6 unspecified
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return False
    
    # Validate URL structure
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if not parsed.netloc:
            return False
        # Block IP addresses in netloc (should use domain names)
        if re.match(r'^\d+\.\d+\.\d+\.\d+', parsed.netloc):
            return False
    except Exception:
        return False
    
    return True


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format (IPv4 or IPv6)"""
    if not isinstance(ip, str):
        return False
    
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ipv4_pattern, ip):
        parts = ip.split('.')
        try:
            if all(0 <= int(part) <= 255 for part in parts):
                return True
        except ValueError:
            return False
    
    # IPv6 pattern (simplified - basic validation)
    ipv6_pattern = r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^::1$|^::$|^([0-9a-fA-F]{0,4}:){1,7}:?[0-9a-fA-F]{0,4}$'
    if re.match(ipv6_pattern, ip):
        return True
    
    return False


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
