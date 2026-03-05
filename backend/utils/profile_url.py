"""
Profile URL utilities for backend
Generates profile URLs in the format: {API_URL}/profile/{username}-{hashed_user_id}
"""
import os
from typing import Optional


def hash_user_id(user_id: int) -> Optional[str]:
    """
    Hash a user ID to a short, URL-safe string
    Uses base36 encoding to match frontend implementation
    """
    if not user_id or not isinstance(user_id, int):
        return None
    
    # Convert to base36 (0-9, a-z) - matches JavaScript's toString(36)
    def int_to_base36(n):
        """Convert integer to base36 string"""
        if n == 0:
            return "0"
        chars = "0123456789abcdefghijklmnopqrstuvwxyz"
        result = ""
        while n > 0:
            result = chars[n % 36] + result
            n //= 36
        return result
    
    # Encode user ID to base36
    encoded = int_to_base36(user_id)
    
    # Add a simple hash prefix to make it less predictable
    # Using a simple algorithm: multiply by a prime and encode (matches frontend)
    hash_value = (user_id * 7919) % 46656  # 7919 is a prime, 46656 is 36^3
    hash_part = int_to_base36(hash_value)
    hash_part = hash_part.zfill(3)  # Pad to 3 chars (matches frontend padStart)
    
    # Combine and limit to 8 chars total (matches frontend substring)
    return f"{hash_part}{encoded}"[:8]


def decode_user_id(hashed_id: str) -> Optional[int]:
    """
    Decode a hashed user ID back to the original user ID
    Note: This is a simplified version. For production, use a more robust encoding.
    """
    if not hashed_id or not isinstance(hashed_id, str):
        return None
    
    try:
        # The hash is in format: hash_part(3) + encoded(5)
        # For now, we'll need to store a mapping or use a reversible encoding
        # This is a placeholder - in production, you might want to use a lookup table
        # or a more sophisticated encoding scheme
        return None  # Not easily reversible without a lookup
    except Exception:
        return None


def generate_profile_path(user_id: int, username: str) -> Optional[str]:
    """
    Generate only the path part of profile URL: /profile/{username}-{hashed_user_id}
    This should be stored in the database instead of the full URL.
    
    Args:
        user_id: User ID
        username: Username
    
    Returns:
        Profile path string (e.g., "/profile/zain-ujv5") or None if invalid input
    """
    if not user_id or not username:
        return None
    
    # Hash the user ID
    hashed_id = hash_user_id(user_id)
    if not hashed_id:
        return None
    
    # Sanitize username for URL (remove special chars, keep alphanumeric, hyphens, underscores)
    sanitized_username = username.lower().replace(' ', '-')
    sanitized_username = ''.join(c for c in sanitized_username if c.isalnum() or c in ['-', '_'])
    sanitized_username = sanitized_username.strip('-').strip('_')
    
    if not sanitized_username:
        return None
    
    return f"/profile/{sanitized_username}-{hashed_id}"


def generate_profile_url(user_id: int, username: str, api_url: Optional[str] = None) -> Optional[str]:
    """
    Generate a full profile URL in the format: {API_URL}/profile/{username}-{hashed_user_id}
    This generates the full URL dynamically based on current environment.
    
    Args:
        user_id: User ID
        username: Username
        api_url: Base API URL (defaults to environment variable or http://localhost:5000)
    
    Returns:
        Full profile URL string or None if invalid input
    """
    # Get the path part
    path = generate_profile_path(user_id, username)
    if not path:
        return None
    
    # Get API URL from environment or use default
    if not api_url:
        api_url = os.environ.get('VITE_API_URL') or os.environ.get('API_URL') or 'http://localhost:5000'
    
    # Remove trailing slash if present
    api_url = api_url.rstrip('/')
    
    return f"{api_url}{path}"


def get_full_profile_url(profile_path: Optional[str], api_url: Optional[str] = None) -> Optional[str]:
    """
    Convert a stored profile path to a full URL using current environment.
    Use this when returning profile URLs in API responses.
    
    Args:
        profile_path: Stored profile path (e.g., "/profile/zain-ujv5")
        api_url: Base API URL (defaults to environment variable)
    
    Returns:
        Full profile URL or None if path is invalid
    """
    if not profile_path:
        return None
    
    # Ensure path starts with /
    if not profile_path.startswith('/'):
        profile_path = f"/{profile_path}"
    
    # Get API URL from environment or use default
    if not api_url:
        api_url = os.environ.get('VITE_API_URL') or os.environ.get('API_URL') or 'http://localhost:5000'
    
    # Remove trailing slash if present
    api_url = api_url.rstrip('/')
    
    return f"{api_url}{profile_path}"
