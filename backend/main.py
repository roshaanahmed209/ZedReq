"""FastAPI Application Entry Point"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
import traceback
import subprocess
import sys
from pathlib import Path

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
from utils.scheduler import start_scheduler, stop_scheduler
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
    messaging_router,
    lms_router,
    nemz_router,
    vec_router,
    interviews_router,
    profile_features_router,
    context_router
)
from routers.reserved_seats import router as reserved_seats_router
from routers.monitoring import router as monitoring_router
from middleware.monitoring_middleware import MonitoringMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.body_limit import BodySizeLimitMiddleware


def build_frontend():
    """Build the React frontend application"""
    # Get the project root directory (parent of backend)
    project_root = Path(__file__).parent.parent
    frontend_dir = project_root / "frontend"
    dist_dir = frontend_dir / "dist"
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print(f"Warning: Frontend directory not found at {frontend_dir}")
        return False
    
    # Check if dist directory already exists and contains index.html
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        print(f"Frontend build already exists at {dist_dir}. Skipping build.")
        return True
    
    print("Building React frontend...")
    try:
        # Check if node_modules exists, if not, install dependencies first
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            print("Installing frontend dependencies...")
            install_result = subprocess.run(
                ["npm", "install"],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                shell=True if sys.platform == "win32" else False
            )
            if install_result.returncode != 0:
                print(f"Error installing dependencies:")
                print(f"STDOUT: {install_result.stdout}")
                print(f"STDERR: {install_result.stderr}")
                return False
            print("Dependencies installed successfully")
        
        # Build the frontend
        print(f"Running 'npm run build' in {frontend_dir}...")
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(frontend_dir),
            capture_output=True,
            text=True,
            shell=True if sys.platform == "win32" else False
        )
        
        if build_result.returncode != 0:
            print(f"Error building frontend:")
            print(f"STDOUT: {build_result.stdout}")
            print(f"STDERR: {build_result.stderr}")
            return False
        
        # Verify dist directory was created
        if not dist_dir.exists():
            print(f"Warning: Build completed but dist directory not found at {dist_dir}")
            return False
        
        print(f"Frontend built successfully! Dist directory: {dist_dir}")
        return True
    except Exception as e:
        print(f"Error building frontend: {e}")
        import traceback
        traceback.print_exc()
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    print("Starting up FastAPI application...")
    
    # Build frontend before starting
    build_success = build_frontend()
    
    # Setup frontend routes after build
    if build_success:
        setup_frontend_routes()
        print("Frontend routes configured")
    else:
        print("Warning: Frontend build failed or skipped. Frontend routes may not work.")
    
    try:
        init_database()
        print("Database initialized")
    except Exception as e:
        print(f"[WARN] Database init failed: {e} — continuing startup")

    # Initialize ORM tables and seed subscription plans
    try:
        from config.database_orm import init_orm_tables, SessionLocal
        init_orm_tables()
        print("ORM tables initialized")

        from services.subscription_service import SubscriptionService
        seed_db = SessionLocal()
        try:
            SubscriptionService.seed_plans(seed_db)
            print("Subscription plans seeded successfully")
        finally:
            seed_db.close()
    except Exception as e:
        print(f"Warning: Could not seed subscription plans: {e}")
        import traceback
        traceback.print_exc()

    # Initialize Firebase (for messaging service)
    try:
        from utils.firebase_client import initialize_firebase, get_firebase_db
        import logging
        firebase_logger = logging.getLogger('utils.firebase_client')
        firebase_logger.setLevel(logging.INFO)  # Ensure we see Firebase logs
        
        print("Initializing Firebase Realtime Database...")
        firebase_app = initialize_firebase()
        if firebase_app:
            print("Firebase Admin SDK app created, getting database reference...")
            db_ref = get_firebase_db()
            if db_ref:
                print("[OK] Firebase Realtime Database initialized successfully (using Admin SDK)")
            else:
                print("[WARN] Firebase app created but database reference unavailable (will use REST API)")
                print("  This usually means there's an issue with the database connection")
        else:
            print("[WARN] Firebase Admin SDK not available (will use REST API fallback)")
            print("  Check that FIREBASE_CREDENTIALS_PATH is set or credentials.json exists in backend/firebase/")
    except Exception as e:
        print(f"[WARN] Firebase initialization failed: {e}")
        import traceback
        traceback.print_exc()
        print("Messaging service will use REST API fallback")
    
    # Start Vec agent scheduler
    try:
        start_scheduler()
        print("Vec agent scheduler started")
    except Exception as e:
        print(f"Warning: Failed to start Vec agent scheduler: {e}")
    
    yield
    # Shutdown
    print("Shutting down FastAPI application...")
    
    # Stop Vec agent scheduler
    try:
        stop_scheduler()
        print("Vec agent scheduler stopped")
    except Exception as e:
        print(f"Warning: Failed to stop Vec agent scheduler: {e}")
    
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

# Configure CORS from environment variables
cors_origins = None

# Try to get from settings first
if _settings_loaded and settings:
    try:
        cors_origins = settings.get_cors_origins()
    except Exception as e:
        print(f"Warning: Could not get CORS origins from settings: {e}")

# Fallback: Try reading directly from environment variable
if not cors_origins:
    cors_origins_str = os.environ.get("CORS_ORIGINS")
    if cors_origins_str:
        cors_origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

# Final fallback: Use defaults
if not cors_origins:
    cors_origins = ["http://localhost:3000", "http://localhost:5173"]
    print("Warning: Using default CORS origins. Set CORS_ORIGINS in .env file to configure.")

print(f"CORS configured with origins: {cors_origins}")
print("Note: Make sure CORS_ORIGINS in .env includes the server's own origin (e.g., http://localhost:5000) if frontend is served from the same server")

# Add monitoring middleware (before CORS to track all requests)
app.add_middleware(
    MonitoringMiddleware,
    collector_url=os.getenv("BACKOFFICE_COLLECTOR_URL", "http://localhost:5001/api/collect"),
    api_key=os.getenv("COLLECTOR_API_KEY", "")
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With", "X-API-Key"],
    expose_headers=["*"],
    max_age=3600,
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(BodySizeLimitMiddleware)

server_origins = cors_origins + ["http://localhost:5000", "http://localhost:5173"]
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
app.include_router(lms_router, prefix="/api/lms", tags=["LMS"])
app.include_router(nemz_router, prefix="/api/nemz", tags=["Nemz Agent"])
app.include_router(vec_router, prefix="/api/vec", tags=["Vec Agent"])
app.include_router(interviews_router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(profile_features_router, prefix="/api/profile", tags=["Profile Features"])
app.include_router(context_router, prefix="/api/context", tags=["Context"])
app.include_router(reserved_seats_router)
app.include_router(monitoring_router)


# Get paths for static files
project_root = Path(__file__).parent.parent
frontend_dist = project_root / "frontend" / "dist"
frontend_static = project_root / "frontend" / "static"

# Health check endpoint (must be before catch-all)
@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "2.0.0"
    }

# Track if assets are mounted
_assets_mounted = False
_static_mounted = False

# Mount static directory (for videos, images, etc. from frontend/static/)
if frontend_static.exists():
    try:
        app.mount("/static", StaticFiles(directory=str(frontend_static)), name="static")
        _static_mounted = True
        print(f"Static files mounted from {frontend_static}")
    except Exception as e:
        print(f"Warning: Could not mount static files at startup: {e}")

# Mount assets directory if it exists at startup (mounts take precedence over routes)
if frontend_dist.exists() and (frontend_dist / "assets").exists():
    try:
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
        _assets_mounted = True
        print(f"Assets mounted from {frontend_dist / 'assets'}")
    except Exception as e:
        print(f"Warning: Could not mount assets at startup: {e}")

# Function to setup frontend serving routes (called after build)
def setup_frontend_routes():
    """Setup routes for serving the frontend after build"""
    global _assets_mounted, _static_mounted
    
    if not frontend_dist.exists():
        return False
    
    # Mount static directory if not already mounted
    if frontend_static.exists() and not _static_mounted:
        try:
            app.mount("/static", StaticFiles(directory=str(frontend_static)), name="static")
            _static_mounted = True
            print(f"Static files mounted from {frontend_static}")
        except Exception as e:
            print(f"Warning: Could not mount static files: {e}")
    
    # Mount assets directory for JS, CSS, and other assets if not already mounted
    if (frontend_dist / "assets").exists() and not _assets_mounted:
        try:
            app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
            _assets_mounted = True
            print(f"Assets mounted from {frontend_dist / 'assets'}")
        except Exception as e:
            print(f"Warning: Could not mount assets: {e}")
    
    return True

# Serve root path - dynamically checks if frontend is built
@app.get("/")
async def serve_root():
    """Serve React app index.html for root path or fallback message"""
    if frontend_dist.exists():
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
    
    # Fallback if frontend not built
    return {
        "message": "ZedReq API Server",
        "version": "2.0.0",
        "status": "running",
        "note": "Frontend not built. Building now or check build logs."
    }

# Serve static files from dist root and handle React Router client-side routes
@app.get("/{file_path:path}")
async def serve_frontend(request: Request, file_path: str):
    """Serve frontend files or index.html for React Router"""
    # Exclude API routes, WebSocket routes, health endpoint, assets, and static
    # Assets and static are handled by mounts, but if mounts don't exist yet, we'll handle them here
    if (file_path.startswith("api/") or 
        file_path.startswith("ws/") or 
        file_path == "health"):
        raise StarletteHTTPException(status_code=404, detail="Not found")
    
    # Only serve if dist exists
    if not frontend_dist.exists():
        raise StarletteHTTPException(status_code=404, detail="Frontend not built")
    
    # Handle static files if mount doesn't exist (fallback)
    if file_path.startswith("static/"):
        static_file = frontend_static / file_path.replace("static/", "", 1)
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
        raise StarletteHTTPException(status_code=404, detail="Static file not found")
    
    # Handle assets if mount doesn't exist (fallback)
    if file_path.startswith("assets/"):
        assets_file = frontend_dist / file_path
        if assets_file.exists() and assets_file.is_file():
            return FileResponse(str(assets_file))
        raise StarletteHTTPException(status_code=404, detail="Asset not found")
    
    # Check if it's a static file request (like logo.svg, favicon, etc.) from dist root
    file_path_obj = frontend_dist / file_path
    if file_path_obj.exists() and file_path_obj.is_file():
        return FileResponse(str(file_path_obj))
    
    # For all other routes (React Router client-side routes), serve index.html
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    raise StarletteHTTPException(status_code=404, detail="Not found")


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
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        reload=debug_mode
    )
