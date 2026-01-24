"""FastAPI Application Entry Point"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import traceback

# Import settings with error handling
try:
    from config.settings import settings
    _settings_loaded = True
except Exception as e:
    print(f"Warning: Could not load settings: {e}")
    print("Using default configuration...")
    _settings_loaded = False
    settings = None

from config.database import init_database, get_database
import os
from routers import (
    auth_router,
    network_router,
    connections_router,
    notifications_router,
    websocket_router,
    user_router,
    feed_router,
    posts_router,
    jobs_router,
    messaging_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    print("Starting up FastAPI application...")
    init_database()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down FastAPI application...")
    db = get_database()
    if db:
        db.close()


# Create FastAPI application
app = FastAPI(
    title="ZedReq API",
    description="Professional Networking Platform API",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS with fallback
if _settings_loaded and settings:
    try:
        cors_origins = settings.get_cors_origins()
    except Exception as e:
        print(f"Warning: Could not get CORS origins from settings: {e}")
        cors_origins = ["http://localhost:3000", "http://localhost:5173"]
else:
    # Default CORS origins if settings not loaded
    cors_origins = ["http://localhost:3000", "http://localhost:5173"]

print(f"CORS configured with origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handlers to ensure CORS headers are always included
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers"""
    origin = request.headers.get("origin")
    # Check if origin is in allowed origins
    if origin in cors_origins:
        cors_origin = origin
    else:
        cors_origin = cors_origins[0] if cors_origins else "*"
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code
        },
        headers={
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Credentials": "true",
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with CORS headers"""
    origin = request.headers.get("origin")
    # Check if origin is in allowed origins
    if origin in cors_origins:
        cors_origin = origin
    else:
        cors_origin = cors_origins[0] if cors_origins else "*"
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors(),
            "status_code": 422
        },
        headers={
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Credentials": "true",
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions with CORS headers"""
    print(f"Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    origin = request.headers.get("origin")
    # Check if origin is in allowed origins
    if origin in cors_origins:
        cors_origin = origin
    else:
        cors_origin = cors_origins[0] if cors_origins else "*"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Internal server error",
            "status_code": 500
        },
        headers={
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Credentials": "true",
        }
    )

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(network_router, prefix="/api/network", tags=["Network"])
app.include_router(connections_router, prefix="/api/connections", tags=["Connections"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(websocket_router, prefix="/ws", tags=["WebSocket"])
app.include_router(user_router, prefix="/api/user", tags=["User"])
app.include_router(feed_router, prefix="/api/feed", tags=["Feed"])
app.include_router(posts_router, prefix="/api/posts", tags=["Posts"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(messaging_router, prefix="/api/messaging", tags=["Messaging"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "ZedReq API Server",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    if _settings_loaded and settings:
        try:
            debug_mode = settings.DEBUG
        except:
            debug_mode = True
    else:
        debug_mode = True  # Default to debug mode if settings can't be loaded
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=5000,
        reload=debug_mode
    )
