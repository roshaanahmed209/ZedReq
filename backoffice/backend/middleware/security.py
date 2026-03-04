"""Security middleware for headers, rate limiting, and input sanitization"""
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from collections import defaultdict
from typing import Dict, Tuple
import re
import logging

logger = logging.getLogger(__name__)

# Rate limiting storage (in-memory, use Redis in production)
_rate_limit_store: Dict[str, list] = defaultdict(list)
_rate_limit_cleanup_interval = 300  # Clean up every 5 minutes
_last_cleanup = time.time()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
    
    async def dispatch(self, request: Request, call_next):
        global _last_cleanup
        
        # Clean up old entries periodically
        current_time = time.time()
        if current_time - _last_cleanup > _rate_limit_cleanup_interval:
            self._cleanup_rate_limits()
            _last_cleanup = current_time
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Check rate limit
        if not self._check_rate_limit(client_id):
            logger.warning(f"Rate limit exceeded for {client_id}")
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": "60"}
            )
        
        response = await call_next(request)
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Use IP address as identifier
        if request.client:
            return request.client.host
        return "unknown"
    
    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        # Clean old entries for this client
        _rate_limit_store[client_id] = [
            timestamp for timestamp in _rate_limit_store[client_id]
            if timestamp > window_start
        ]
        
        # Check if limit exceeded
        if len(_rate_limit_store[client_id]) >= self.requests_per_minute:
            return False
        
        # Record this request
        _rate_limit_store[client_id].append(current_time)
        return True
    
    def _cleanup_rate_limits(self):
        """Clean up old rate limit entries"""
        current_time = time.time()
        window_start = current_time - 60
        
        for client_id in list(_rate_limit_store.keys()):
            _rate_limit_store[client_id] = [
                timestamp for timestamp in _rate_limit_store[client_id]
                if timestamp > window_start
            ]
            if not _rate_limit_store[client_id]:
                del _rate_limit_store[client_id]


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Sanitize input to prevent injection attacks"""
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"('|(\\')|(;)|(\|)|(\*))",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Only sanitize POST, PUT, PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Get request body
                body = await request.body()
                
                if body:
                    body_str = body.decode('utf-8', errors='ignore')
                    
                    # Check for SQL injection
                    for pattern in self.SQL_INJECTION_PATTERNS:
                        if re.search(pattern, body_str, re.IGNORECASE):
                            logger.warning(f"Potential SQL injection detected from {request.client.host if request.client else 'unknown'}")
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid input detected"
                            )
                    
                    # Check for XSS
                    for pattern in self.XSS_PATTERNS:
                        if re.search(pattern, body_str, re.IGNORECASE):
                            logger.warning(f"Potential XSS detected from {request.client.host if request.client else 'unknown'}")
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid input detected"
                            )
                
                # Recreate request with body
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request._receive = receive
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error in input sanitization: {e}")
        
        response = await call_next(request)
        return response
