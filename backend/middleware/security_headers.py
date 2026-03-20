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
_PADDLE_CONNECT = (
    "https://cdn.paddle.com "
    "https://sandbox-cdn.paddle.com "
    "https://checkout.paddle.com "
    "https://sandbox-checkout.paddle.com "
    "https://buy.paddle.com "
    "https://sandbox-buy.paddle.com"
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


def _build_connect_src() -> str:
    parts: list[str] = ["'self'", _FIREBASE_AND_GOOGLE_CONNECT, _PADDLE_CONNECT]

    # Extra origins from env (production API URL, staging, etc.) — space or comma separated
    extra = os.getenv("CSP_CONNECT_SRC_EXTRA", "").replace(",", " ").split()
    parts.extend(x for x in extra if x)

    # Derive API origin from same base URL the frontend uses (optional)
    api_url = os.getenv("VITE_API_URL") or os.getenv("PUBLIC_API_URL") or ""
    origin = _parse_origin(api_url)
    if origin:
        parts.append(origin)

    # Local dev: SPA on Vite (3000) calling API on 5000
    debug = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
    if debug:
        parts.extend(
            [
                "http://localhost:5000",
                "http://127.0.0.1:5000",
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

        connect_src = _build_connect_src()
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://apis.google.com https://www.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "img-src 'self' data: https: blob:; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            f"connect-src {connect_src}; "
            "frame-src 'self' https://accounts.google.com https://*.firebaseapp.com https://*.google.com https://checkout.paddle.com https://sandbox-checkout.paddle.com; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp

        return response
