"""Monitoring middleware for main ZedReq app"""
import time
import logging
import httpx
import traceback
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message
from typing import Callable
import os

logger = logging.getLogger(__name__)

# Backoffice collector API URL
BACKOFFICE_COLLECTOR_URL = os.getenv("BACKOFFICE_COLLECTOR_URL", "http://localhost:5001/api/collect")
COLLECTOR_API_KEY = os.getenv("COLLECTOR_API_KEY", "")


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to track API requests and send metrics to backoffice"""
    
    def __init__(self, app, collector_url: str = None, api_key: str = None):
        super().__init__(app)
        self.collector_url = collector_url or BACKOFFICE_COLLECTOR_URL
        self.api_key = api_key or COLLECTOR_API_KEY
        self._metrics_buffer = []
        self._buffer_size = 10
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and track metrics"""
        start_time = time.time()
        
        # Skip monitoring endpoints to avoid recursion.
        # /api/analytics is skipped too: it is a high-volume beacon endpoint, and
        # recording an API metric for every batch would swamp the metrics table
        # without telling us anything the analytics stream does not already say.
        if (
            request.url.path.startswith("/api/monitoring")
            or request.url.path.startswith("/api/analytics")
            or request.url.path.startswith("/health")
        ):
            return await call_next(request)
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            error_message = None
        except Exception as e:
            # Log error
            status_code = 500
            error_message = str(e)
            logger.error(f"Request error: {e}", exc_info=True)
            
            # Send error to backoffice
            try:
                await self._send_error({
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "stack_trace": traceback.format_exc(),
                    "endpoint": request.url.path,
                    "method": request.method,
                    "ip_address": request.client.host if request.client else None,
                    "severity": "error"
                })
            except:
                pass
            
            # Re-raise to let FastAPI handle it
            raise
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Get user ID from request if available
        user_id = None
        if hasattr(request.state, "user"):
            user_id = getattr(request.state.user, "uid", None)
        
        # Collect metric
        metric = {
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "user_id": user_id,
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "error_message": error_message
        }
        
        # Add to buffer
        self._metrics_buffer.append(metric)
        
        # Send batch if buffer is full
        if len(self._metrics_buffer) >= self._buffer_size:
            await self._send_metrics(self._metrics_buffer.copy())
            self._metrics_buffer.clear()
        
        return response
    
    async def _send_metrics(self, metrics: list):
        """Send metrics to backoffice collector"""
        try:
            # Limit batch size
            if len(metrics) > 100:
                metrics = metrics[:100]
            
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{self.collector_url}/metrics",
                    json=metrics,
                    headers=headers
                )
        except httpx.TimeoutException:
            logger.debug("Timeout sending metrics to backoffice")
        except Exception as e:
            logger.debug(f"Failed to send metrics to backoffice: {e}")
    
    async def _send_error(self, error_data: dict):
        """Send error to backoffice collector"""
        try:
            # Sanitize error data - don't send full stack traces
            sanitized_error = {
                "error_type": error_data.get("error_type", "Unknown"),
                "error_message": error_data.get("error_message", "Unknown error")[:500],  # Limit length
                "endpoint": error_data.get("endpoint", "unknown"),
                "method": error_data.get("method", "unknown"),
                "ip_address": error_data.get("ip_address"),
                "severity": error_data.get("severity", "error")
            }
            # Don't send full stack traces to prevent information disclosure
            
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(
                    f"{self.collector_url}/errors",
                    json=[sanitized_error],
                    headers=headers
                )
        except httpx.TimeoutException:
            logger.debug("Timeout sending error to backoffice")
        except Exception as e:
            logger.debug(f"Failed to send error to backoffice: {e}")
