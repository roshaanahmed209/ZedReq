"""
API Security Utilities
API key validation, input sanitization, and secure request helpers
"""
import os
import re
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import quote

logger = logging.getLogger(__name__)


def validate_api_key(api_key: Optional[str], key_name: str = "API_KEY") -> bool:
    """
    Validate API key format and presence
    
    Args:
        api_key: API key to validate
        key_name: Name of the key for logging
    
    Returns:
        True if valid, False otherwise
    """
    if not api_key:
        logger.warning(f"{key_name} is missing or empty")
        return False
    
    # Basic validation: should be non-empty string
    if not isinstance(api_key, str) or len(api_key.strip()) == 0:
        logger.warning(f"{key_name} is invalid format")
        return False
    
    # Check for common placeholder values
    invalid_values = ['your_key_here', 'api_key', 'secret', 'password', 'none', 'null']
    if api_key.lower().strip() in invalid_values:
        logger.warning(f"{key_name} appears to be a placeholder value")
        return False
    
    return True


def get_api_key_from_env(key_name: str, required: bool = True) -> Optional[str]:
    """
    Safely get API key from environment variable
    
    Args:
        key_name: Environment variable name
        required: Whether key is required (raises error if missing)
    
    Returns:
        API key string or None if not required and missing
    
    Raises:
        ValueError: If required key is missing or invalid
    """
    api_key = os.environ.get(key_name)
    
    if not api_key and required:
        raise ValueError(f"Required environment variable {key_name} is not set")
    
    if api_key and not validate_api_key(api_key, key_name):
        if required:
            raise ValueError(f"Invalid {key_name} format")
        return None
    
    return api_key


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize input text for API calls
    
    Args:
        text: Input text to sanitize
        max_length: Maximum length (truncate if longer)
    
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove control characters except newlines and tabs
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
        logger.debug(f"Input truncated to {max_length} characters")
    
    return text.strip()


def sanitize_search_query(query: str) -> str:
    """
    Sanitize search query for external APIs
    
    Args:
        query: Search query string
    
    Returns:
        Sanitized query
    """
    # Basic sanitization
    query = sanitize_input(query, max_length=200)
    
    # Remove potentially dangerous characters
    query = re.sub(r'[<>"\']', '', query)
    
    # URL encode if needed (for safe transmission)
    # Note: Most APIs handle this, but we ensure it's safe
    return query


def sanitize_url(url: str) -> str:
    """
    Sanitize and validate URL
    
    Args:
        url: URL string
    
    Returns:
        Sanitized URL
    
    Raises:
        ValueError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    url = url.strip()
    
    # Basic URL validation
    if not re.match(r'^https?://', url, re.IGNORECASE):
        raise ValueError(f"URL must start with http:// or https://: {url[:50]}")
    
    # Remove dangerous characters
    url = re.sub(r'[\x00-\x1F\x7F]', '', url)
    
    return url


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask API key for logging (show only first/last few characters)
    
    Args:
        api_key: API key to mask
        visible_chars: Number of characters to show at start and end
    
    Returns:
        Masked API key string
    """
    if not api_key or len(api_key) <= visible_chars * 2:
        return "***"
    
    return f"{api_key[:visible_chars]}...{api_key[-visible_chars:]}"


def safe_log_api_call(
    service_name: str,
    endpoint: str,
    method: str = "POST",
    has_api_key: bool = True,
    **kwargs
):
    """
    Safely log API call information without exposing sensitive data
    
    Args:
        service_name: Name of the API service
        endpoint: API endpoint
        method: HTTP method
        has_api_key: Whether API key is being used
        **kwargs: Additional safe metadata to log
    """
    log_data = {
        'service': service_name,
        'endpoint': endpoint,
        'method': method,
        'authenticated': has_api_key
    }
    log_data.update({k: v for k, v in kwargs.items() if not _is_sensitive_key(k)})
    
    logger.debug(f"API call: {log_data}")


def _is_sensitive_key(key: str) -> bool:
    """Check if a key name indicates sensitive data"""
    sensitive_keywords = [
        'key', 'secret', 'password', 'token', 'auth', 'credential',
        'api_key', 'access_token', 'refresh_token'
    ]
    key_lower = key.lower()
    return any(keyword in key_lower for keyword in sensitive_keywords)


def validate_request_timeout(timeout: Optional[float], default: float = 30.0) -> float:
    """
    Validate and get request timeout value
    
    Args:
        timeout: Timeout value in seconds
        default: Default timeout if not provided
    
    Returns:
        Valid timeout value
    """
    if timeout is None:
        timeout = default
    
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        logger.warning(f"Invalid timeout {timeout}, using default {default}")
        return default
    
    # Cap at reasonable maximum
    max_timeout = 300.0  # 5 minutes
    if timeout > max_timeout:
        logger.warning(f"Timeout {timeout}s exceeds maximum {max_timeout}s, capping")
        return max_timeout
    
    return float(timeout)


def ensure_https(url: str) -> str:
    """
    Ensure URL uses HTTPS (for security)
    
    Args:
        url: URL to check
    
    Returns:
        URL with HTTPS (if http://, converts to https://)
    
    Raises:
        ValueError: If URL is not http:// or https://
    """
    if url.startswith('http://'):
        logger.warning(f"Converting HTTP to HTTPS for security: {url[:50]}")
        return url.replace('http://', 'https://', 1)
    elif url.startswith('https://'):
        return url
    else:
        raise ValueError(f"URL must start with http:// or https://: {url[:50]}")


def sanitize_dict_for_logging(data: Dict[str, Any], max_value_length: int = 100) -> Dict[str, Any]:
    """
    Sanitize dictionary for safe logging (remove sensitive data, truncate long values)
    
    Args:
        data: Dictionary to sanitize
        max_value_length: Maximum length for string values
    
    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    
    for key, value in data.items():
        # Skip sensitive keys
        if _is_sensitive_key(key):
            sanitized[key] = "***REDACTED***"
            continue
        
        # Handle different value types
        if isinstance(value, str):
            if len(value) > max_value_length:
                sanitized[key] = value[:max_value_length] + "..."
            else:
                sanitized[key] = value
        elif isinstance(value, (int, float, bool, type(None))):
            sanitized[key] = value
        elif isinstance(value, (list, dict)):
            sanitized[key] = f"<{type(value).__name__} with {len(value)} items>"
        else:
            sanitized[key] = str(value)[:max_value_length]
    
    return sanitized


def sanitize_text_for_storage(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text input for safe storage (XSS prevention, HTML escaping)
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (truncate if longer)
    
    Returns:
        Sanitized text safe for storage
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove control characters except newlines, tabs, and carriage returns
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    
    # Remove script tags and event handlers (basic XSS prevention)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Normalize whitespace (but preserve intentional line breaks)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]
        logger.debug(f"Text truncated to {max_length} characters")
    
    return text.strip()


def validate_url_safe(url: str, allowed_schemes: List[str] = None) -> str:
    """
    Validate and sanitize URL for safe use
    
    Args:
        url: URL to validate
        allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])
    
    Returns:
        Sanitized URL
    
    Raises:
        ValueError: If URL is invalid or uses disallowed scheme
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    url = url.strip()
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    # Basic URL validation
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
        raise ValueError(f"URL must include a scheme (e.g., http:// or https://)")
    
    # Check scheme
    scheme = url.split('://')[0].lower()
    if scheme not in allowed_schemes:
        raise ValueError(f"URL scheme '{scheme}' is not allowed. Allowed schemes: {allowed_schemes}")
    
    # Remove dangerous characters
    url = re.sub(r'[\x00-\x1F\x7F]', '', url)
    
    # Basic length check
    if len(url) > 2048:
        raise ValueError("URL exceeds maximum length of 2048 characters")
    
    return url