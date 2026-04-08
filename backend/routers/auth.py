"""Authentication Router - JWT based authentication using ORM"""
import time
from collections import defaultdict
from threading import Lock
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest
)
from pydantic import BaseModel, Field
from typing import Literal
from schemas.two_factor import (
    TwoFactorVerify,
    TwoFactorVerifySetup
)
from services.auth_service import AuthService
from services.two_factor_service import TwoFactorService
from services.context_updater import ContextUpdater
from services.lms_preloader import schedule_lms_preload
from dependencies.auth import get_current_user
from config.database_orm import get_db
from utils.errors import NotFoundError, ValidationError, GoogleSignInNoAccountError
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()
security = HTTPBearer()


# ---------------------------------------------------------------------------
# IP-based rate limiter for unauthenticated auth endpoints
# Falls back to in-memory when Redis is unavailable.
# ---------------------------------------------------------------------------

class _IpRateLimiter:
    """Sliding-window rate limiter keyed by (ip, action)."""

    def __init__(self):
        self._lock = Lock()
        self._memory: dict[str, list[float]] = defaultdict(list)

    def _redis_check(self, key: str, limit: int, window: int) -> bool:
        try:
            from config.cache import _init_redis
            client, available = _init_redis()
            if available and client is not None:
                pipe = client.pipeline()
                pipe.incr(key)
                pipe.expire(key, window, nx=True)
                count, _ = pipe.execute()
                return int(count) <= limit
        except Exception as exc:
            logger.debug("IP rate-limit Redis error: %s", exc)
        return None  # signal: fall back to memory

    def check(self, ip: str, action: str, limit: int, window: int) -> None:
        """Raise HTTP 429 if the IP has exceeded *limit* calls within *window* seconds."""
        key = f"rl:auth:{action}:{ip}"
        result = self._redis_check(key, limit, window)
        if result is None:
            # Memory fallback
            now = time.time()
            with self._lock:
                calls = self._memory[key]
                calls[:] = [t for t in calls if now - t < window]
                if len(calls) >= limit:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests. Please try again later.",
                        headers={"Retry-After": str(window)},
                    )
                calls.append(now)
        elif not result:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(window)},
            )


_ip_limiter = _IpRateLimiter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Dependency to get auth service with ORM session"""
    return AuthService(db)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    _ip_limiter.check(request.client.host, "register", limit=5, window=600)
    try:
        result = auth_service.register(user_data.model_dump())
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    credentials: UserLogin,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and return JWT tokens.

    After a successful login (no 2FA required) the LMS dashboard data is
    pre-warmed in a background thread so the user's first visit to the
    dashboard is instant.
    """
    _ip_limiter.check(request.client.host, "login", limit=10, window=300)
    try:
        result = auth_service.login(credentials.username, credentials.password)

        # Only schedule the preload when the login is complete (2FA not pending).
        # When 2FA is required, the preload is triggered in /2fa/verify instead.
        if not result.get("requires_2fa"):
            user_id = result.get("user", {}).get("id")
            if user_id:
                background_tasks.add_task(schedule_lms_preload, user_id)

        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token"""
    _ip_limiter.check(request.client.host, "refresh", limit=20, window=60)
    try:
        result = auth_service.refresh_token(refresh_data.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user information"""
    return UserResponse(**current_user)


def get_two_factor_service(db: Session = Depends(get_db)) -> TwoFactorService:
    """Dependency to get 2FA service"""
    return TwoFactorService(db)


@router.post("/2fa/verify")
async def verify_2fa_login(
    verify_data: TwoFactorVerify,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify 2FA code and complete login.

    Once 2FA is confirmed and the full token pair is issued, the LMS dashboard
    is pre-warmed in a background thread.
    """
    try:
        result = auth_service.verify_2fa_and_login(
            verify_data.temp_token,
            verify_data.code
        )

        # Schedule LMS pre-warm now that login is fully complete.
        user_id = result.get("user", {}).get("id")
        if user_id:
            background_tasks.add_task(schedule_lms_preload, user_id)

        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"2FA verification error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="2FA verification failed"
        )


class GoogleAuthRequest(BaseModel):
    """Google authentication request"""
    id_token: str
    intent: Literal["login", "signup"] = Field(
        default="signup",
        description="'login' requires an existing ZedReq user; 'signup' creates one if needed.",
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    google_data: GoogleAuthRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user with Google ID token.

    After a successful Google sign-in the LMS dashboard is pre-warmed in a
    background thread so the first visit is served straight from cache.
    """
    try:
        result = auth_service.verify_google_token(
            google_data.id_token, google_data.intent
        )

        # Schedule LMS pre-warm after successful Google auth.
        user_id = result.get("user", {}).get("id")
        if user_id:
            background_tasks.add_task(schedule_lms_preload, user_id)

        return TokenResponse(**result)
    except GoogleSignInNoAccountError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Google auth error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google authentication failed"
        )


def _run_zed_context_update(user_id: int):
    """Background task: refresh context and trigger Zed Agent update (non-blocking)."""
    from config.database_orm import SessionLocal
    db = SessionLocal()
    try:
        context_updater = ContextUpdater(db)
        context_updater.refresh_and_update_zed_context(user_id=user_id)
        logger.info(f"Background zed context update completed for user_id={user_id}")
    except Exception as e:
        logger.error(f"Background zed context update failed for user_id={user_id}: {e}", exc_info=True)
    finally:
        db.close()


@router.post("/logout")
async def logout(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """Logout user, revoke the current access token, and schedule context refresh."""
    # Revoke the current access token so it cannot be reused
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        raw_token = auth_header[len("Bearer "):]
        try:
            from jose import jwt as _jwt
            from config.settings import settings as _settings
            payload = _jwt.decode(
                raw_token,
                _settings.JWT_SECRET_KEY,
                algorithms=[_settings.JWT_ALGORITHM],
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                ttl = max(0, int(exp - time.time()))
                from utils.token_denylist import revoke as _revoke
                _revoke(jti, ttl)
        except Exception as revoke_err:
            logger.warning("Token revocation on logout failed: %s", revoke_err)

    # Schedule the heavy context update to run AFTER the response is sent
    background_tasks.add_task(_run_zed_context_update, current_user["id"])

    return {
        "message": "Logged out successfully",
        "context_updated": "scheduled"
    }
