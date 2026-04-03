"""Security headers middleware for main API"""
import os
import re
from typing import Optional
from urllib.parse import urlparse

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Fetch/XHR targets that must be allowed when the SPA is not same-origin as the API
# (e.g. Vite on :3000 + VITE_API_URL=http://localhost:5000) or when using Firebase Auth.
_FIREBASE_AND_GOOGLE_CONNECT = (
    "https://securetoken.googleapis.com "
    "https://identitytoolkit.googleapis.com "
    "https://www.googleapis.com "
    "https://firebase.googleapis.com "
    "https://firebaseinstallations.googleapis.com "
    "https://accounts.google.com "
    "https://www.google.com "
    "https://apis.google.com "
    "wss://*.firebaseio.com "
    "https://*.firebaseio.com"
)

# Paddle.js / checkout (when using billing)
# checkout-service.paddle.com is the actual transaction API endpoint hit during checkout
_PADDLE_CONNECT = (
    "https://cdn.paddle.com "
    "https://sandbox-cdn.paddle.com "
    "https://checkout.paddle.com "
    "https://sandbox-checkout.paddle.com "
    "https://checkout-service.paddle.com "
    "https://sandbox-checkout-service.paddle.com "
    "https://buy.paddle.com "
    "https://sandbox-buy.paddle.com "
    "https://*.paddle.com"
)


def _parse_origin(url: str) -> Optional[str]:
    """Return scheme://host:port (or host only) for CSP connect-src."""
    if not url or not url.strip():
        return None
    u = url.strip().rstrip("/")
    try:
        parsed = urlparse(u if "://" in u else f"https://{u}")
        if not parsed.netloc:
            return None
        scheme = parsed.scheme or "https"
        return f"{scheme}://{parsed.netloc}"
    except Exception:
        return None


def _websocket_connect_origins(http_origin: str) -> list[str]:
    """
    Browsers treat ws: and http: as different for connect-src.
    Allow WebSockets to the same host as the API URL.
    """
    try:
        p = urlparse(http_origin)
        if not p.netloc:
            return []
        if p.scheme == "http":
            return [f"ws://{p.netloc}"]
        if p.scheme == "https":
            return [f"wss://{p.netloc}"]
    except Exception:
        pass
    return []


def _host_header_connect_origins(request: Request) -> list[str]:
    """
    CSP connect-src 'self' is same scheme as the document (https), so it does NOT
    allow wss:// on the same host. Browsers block WebSockets unless wss:// is listed.
    Use Host + X-Forwarded-Proto (Render, etc.) so production same-origin WS works
    without relying on VITE_API_URL in the Python process.
    """
    host = (request.headers.get("host") or "").strip()
    if not host:
        return []
    proto = (request.headers.get("x-forwarded-proto") or request.url.scheme or "https").split(",")[0].strip().lower()
    if proto == "https":
        return [f"https://{host}", f"wss://{host}"]
    if proto == "http":
        return [f"http://{host}", f"ws://{host}"]
    return [f"https://{host}", f"wss://{host}"]


def _build_connect_src(request: Optional[Request] = None) -> str:
    parts: list[str] = ["'self'", _FIREBASE_AND_GOOGLE_CONNECT, _PADDLE_CONNECT]

    if request is not None:
        parts.extend(_host_header_connect_origins(request))

    # Extra origins from env (production API URL, staging, etc.) — space or comma separated
    extra = os.getenv("CSP_CONNECT_SRC_EXTRA", "").replace(",", " ").split()
    parts.extend(x for x in extra if x)

    # Derive API origin from same base URL the frontend uses (optional)
    api_url = os.getenv("VITE_API_URL") or os.getenv("PUBLIC_API_URL") or ""
    origin = _parse_origin(api_url)
    if origin:
        parts.append(origin)
        parts.extend(_websocket_connect_origins(origin))

    # Local dev: SPA on Vite (3000) calling API on 5000
    debug = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    if debug:
        parts.extend(
            [
                "http://localhost:5000",
                "http://127.0.0.1:5000",
                "ws://localhost:5000",
                "ws://127.0.0.1:5000",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        )

    # Collapse whitespace
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        connect_src = _build_connect_src(request)
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com https://www.gstatic.com https://cdn.paddle.com https://sandbox-cdn.paddle.com https://public.profitwell.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.paddle.com https://sandbox-cdn.paddle.com; "
            "img-src 'self' data: https: blob:; "
            "media-src 'self' data: https: blob:; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            f"connect-src {connect_src}; "
            "frame-src 'self' https://accounts.google.com https://*.firebaseapp.com https://*.google.com https://*.paddle.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response
