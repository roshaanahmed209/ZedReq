"""Request body size limit middleware for main API"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject request bodies larger than 10MB to mitigate DoS."""

    async def dispatch(self, request: Request, call_next):
        if request.method not in ("POST", "PUT", "PATCH"):
            return await call_next(request)
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_BODY_SIZE:
                    return JSONResponse(
                        status_code=413,
                        content={"detail": "Request body too large (max 10MB)"},
                    )
            except ValueError:
                pass
        # Consume body and enforce size for streaming
        body = await request.body()
        if len(body) > MAX_BODY_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large (max 10MB)"},
            )

        async def receive():
            return {"type": "http.request", "body": body}

        request._receive = receive
        return await call_next(request)
