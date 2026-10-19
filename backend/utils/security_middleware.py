"""
Security Middleware and Utilities
Enhanced security measures for API endpoints
"""
import time
import hashlib
from typing import Optional, Dict, Any, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server header (security through obscurity)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Limit request body size to prevent DoS attacks"""
    
    def __init__(self, app, max_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_size = max_size
    
    async def dispatch(self, request: Request, call_next: Callable):
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_size:
                    logger.warning(
                        f"Request size {size} exceeds limit {self.max_size} from {request.client.host}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request body too large. Maximum size: {self.max_size / (1024 * 1024):.1f}MB"
                    )
            except ValueError:
                pass  # Invalid content-length, let it proceed
        
        response = await call_next(request)
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enhanced rate limiting with IP-based tracking"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # ip -> list of timestamps
        self.cleanup_interval = 300  # Clean up every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove old request timestamps"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff = now - 60  # Remove requests older than 1 minute
        for ip in list(self.requests.keys()):
            self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]
            if not self.requests[ip]:
                del self.requests[ip]
        
        self.last_cleanup = now
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded IP (from proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/healthz", "/"]:
            return await call_next(request)
        
        # Cleanup old requests periodically
        self._cleanup_old_requests()
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        now = time.time()
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove requests outside the time window
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if now - t < 60  # 1 minute window
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Record this request
        self.requests[client_ip].append(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response


def generate_request_id() -> str:
    """Generate unique request ID for tracking"""
    return hashlib.sha256(
        f"{time.time()}{id(time)}".encode()
    ).hexdigest()[:16]


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests for tracking"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = generate_request_id()
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


def validate_content_type(request: Request, allowed_types: list = None) -> bool:
    """Validate request content type"""
    if allowed_types is None:
        allowed_types = ["application/json", "multipart/form-data", "application/x-www-form-urlencoded"]
    
    content_type = request.headers.get("content-type", "")
    
    # For multipart, check if it starts with the type
    if any(content_type.startswith(t) for t in allowed_types):
        return True
    
    # Allow requests without body
    if request.method in ["GET", "HEAD", "DELETE"]:
        return True
    
    return False
