"""
Input Sanitization Utilities - OWASP Security Practices
Sanitizes user input to prevent injection attacks, XSS, and other security issues
"""
import re
import html
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Sanitizes user input following OWASP guidelines"""
    
    # Maximum input lengths
    MAX_MESSAGE_LENGTH = 5000  # 5KB max message
    MAX_SESSION_ID_LENGTH = 100
    
    # Patterns for dangerous content
    SCRIPT_PATTERN = re.compile(
        r'<script[^>]*>.*?</script>',
        re.IGNORECASE | re.DOTALL
    )
    JAVASCRIPT_PATTERN = re.compile(
        r'javascript:',
        re.IGNORECASE
    )
    ON_EVENT_PATTERN = re.compile(
        r'on\w+\s*=',
        re.IGNORECASE
    )
    SQL_INJECTION_PATTERN = re.compile(
        r'(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+',
        re.IGNORECASE
    )
    
    @staticmethod
    def sanitize_message(message: str) -> Optional[str]:
        """
        Sanitize chat message input
        
        Args:
            message: Raw user input
            
        Returns:
            Sanitized message or None if invalid
        """
        if not message or not isinstance(message, str):
            return None
        
        # Trim whitespace
        message = message.strip()
        
        # Check length
        if len(message) == 0:
            return None
        
        if len(message) > InputSanitizer.MAX_MESSAGE_LENGTH:
            logger.warning(f"Message too long: {len(message)} characters")
            message = message[:InputSanitizer.MAX_MESSAGE_LENGTH]
        
        # Remove null bytes
        message = message.replace('\x00', '')
        
        # Remove dangerous script tags
        message = InputSanitizer.SCRIPT_PATTERN.sub('', message)
        
        # Remove javascript: protocol
        message = InputSanitizer.JAVASCRIPT_PATTERN.sub('', message)
        
        # Remove event handlers
        message = InputSanitizer.ON_EVENT_PATTERN.sub('', message)
        
        # HTML escape to prevent XSS
        message = html.escape(message)
        
        # Decode HTML entities that are safe (for display)
        # This allows normal text but prevents XSS
        message = html.unescape(message)
        
        # Re-escape to be safe
        message = html.escape(message)
        
        return message
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validate session ID format (UUID)
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if valid, False otherwise
        """
        if not session_id or not isinstance(session_id, str):
            return False
        
        if len(session_id) > InputSanitizer.MAX_SESSION_ID_LENGTH:
            return False
        
        # UUID format: 8-4-4-4-12 hex digits
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        return bool(uuid_pattern.match(session_id))
    
    @staticmethod
    def sanitize_search_query(query: str) -> Optional[str]:
        """
        Sanitize search query input
        
        Args:
            query: Raw search query
            
        Returns:
            Sanitized query or None if invalid
        """
        if not query or not isinstance(query, str):
            return None
        
        query = query.strip()
        
        if len(query) == 0:
            return None
        
        # Limit length
        max_length = 500
        if len(query) > max_length:
            query = query[:max_length]
        
        # Remove null bytes
        query = query.replace('\x00', '')
        
        # Remove script tags
        query = InputSanitizer.SCRIPT_PATTERN.sub('', query)
        
        # HTML escape
        query = html.escape(query)
        
        return query
