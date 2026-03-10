"""FastAPI Application Entry Point - Backoffice System"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import HTTPException
from contextlib import asynccontextmanager
from pathlib import Path
import subprocess
import sys
import traceback
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dependencies.database import get_db
from services.infrastructure_collector import InfrastructureCollector
from services.uptime_monitor import UptimeMonitor
from services.database_collector import DatabaseCollector
from services.alerting_service import AlertingService

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
from config.database_orm import init_orm_tables
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.analytics import router as analytics_router
from routers.financial import router as financial_router
from routers.financial_tracking import router as financial_tracking_router
from routers.activity import router as activity_router
from routers.monitoring import router as monitoring_router
from routers.collector import router as collector_router
from middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    InputSanitizationMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_frontend():
    """Build the React frontend application"""
    # Get the backoffice root directory (parent of backend)
    backoffice_root = Path(__file__).parent.parent
    frontend_dir = backoffice_root / "frontend"
    dist_dir = frontend_dir / "dist"
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        logger.warning(f"Frontend directory not found at {frontend_dir}")
        return False
    
    # Check if dist directory already exists and contains index.html
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        logger.info(f"Frontend build already exists at {dist_dir}. Skipping build.")
        return True
    
    logger.info("Building React frontend...")
    try:
        # Check if node_modules exists, if not, install dependencies first
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            logger.info("Installing frontend dependencies...")
            install_result = subprocess.run(
                ["npm", "install"],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                shell=True if sys.platform == "win32" else False
            )
            if install_result.returncode != 0:
                logger.error(f"Error installing dependencies:")
                logger.error(f"STDOUT: {install_result.stdout}")
                logger.error(f"STDERR: {install_result.stderr}")
                return False
            logger.info("Dependencies installed successfully")
        
        # Build the frontend
        logger.info(f"Running 'npm run build' in {frontend_dir}...")
        build_result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(frontend_dir),
            capture_output=True,
            text=True,
            shell=True if sys.platform == "win32" else False
        )
        
        if build_result.returncode != 0:
            logger.error(f"Error building frontend:")
            logger.error(f"STDOUT: {build_result.stdout}")
            logger.error(f"STDERR: {build_result.stderr}")
            return False
        
        logger.info("Frontend built successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Exception while building frontend: {e}", exc_info=True)
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    logger.info("Starting up Backoffice FastAPI application...")
    
    try:
        # Build frontend first
        build_frontend()
        
        # Initialize database connection
        init_database()
        logger.info("Database connection initialized")
        
        # Initialize ORM tables (creates tables if they don't exist)
        init_orm_tables()
        logger.info("ORM tables initialized")
        
        # Start background collectors
        scheduler = AsyncIOScheduler()
        
        # Infrastructure collector
        def collect_infrastructure():
            try:
                from config.database_orm import SessionLocal
                db = SessionLocal()
                try:
                    collector = InfrastructureCollector(db)
                    collector.collect_metrics()
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error collecting infrastructure metrics: {e}")
        
        scheduler.add_job(
            collect_infrastructure,
            trigger=IntervalTrigger(seconds=settings.INFRASTRUCTURE_COLLECTION_INTERVAL),
            id='infrastructure_collector',
            replace_existing=True
        )
        
        # Uptime monitor
        def check_uptime():
            try:
                from config.database_orm import SessionLocal
                db = SessionLocal()
                try:
                    monitor = UptimeMonitor(db)
                    monitor.check_health()
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error checking uptime: {e}")
        
        scheduler.add_job(
            check_uptime,
            trigger=IntervalTrigger(seconds=settings.UPTIME_CHECK_INTERVAL),
            id='uptime_monitor',
            replace_existing=True
        )
        
        # Database collector
        def collect_database():
            try:
                from config.database_orm import SessionLocal
                db = SessionLocal()
                try:
                    collector = DatabaseCollector(db)
                    collector.collect_metrics()
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error collecting database metrics: {e}")
        
        scheduler.add_job(
            collect_database,
            trigger=IntervalTrigger(seconds=settings.DATABASE_COLLECTION_INTERVAL),
            id='database_collector',
            replace_existing=True
        )
        
        # Alert checker
        def check_alerts():
            try:
                from config.database_orm import SessionLocal
                db = SessionLocal()
                try:
                    alerting = AlertingService(db)
                    alerting.check_alerts()
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"Error checking alerts: {e}")
        
        scheduler.add_job(
            check_alerts,
            trigger=IntervalTrigger(seconds=settings.ALERT_CHECK_INTERVAL),
            id='alert_checker',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Background collectors started")
        app.state.scheduler = scheduler
        
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        print(f"Warning: Database initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Backoffice FastAPI application...")
    
    # Stop scheduler
    if hasattr(app.state, 'scheduler'):
        app.state.scheduler.shutdown()
        logger.info("Background collectors stopped")
    
    db = get_database()
    if db:
        db.close()


# Create FastAPI application
app = FastAPI(
    title="ZedReq Backoffice API",
    description="Admin backoffice system for ZedReq platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS from environment variables
cors_origins = None

# Try to get from settings first
if _settings_loaded and settings:
    try:
        cors_origins = settings.get_cors_origins()
    except Exception as e:
        logger.warning(f"Could not get CORS origins from settings: {e}")

# Final fallback: Use defaults
if not cors_origins:
    cors_origins = ["http://localhost:3001", "http://localhost:5173"]
    logger.warning("Using default CORS origins. Set BACKOFFICE_CORS_ORIGINS in .env file to configure.")

logger.info(f"CORS configured with origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "Accept"],
    expose_headers=["Content-Type", "X-Request-ID"],
    max_age=3600,
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
app.add_middleware(InputSanitizationMiddleware)

# Global exception handlers to ensure CORS headers are always included
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with CORS headers"""
    origin = request.headers.get("origin")
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
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    origin = request.headers.get("origin")
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

# Health check endpoint (must be before catch-all route)
@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "backoffice",
        "version": "1.0.0"
    }

# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(analytics_router)
app.include_router(financial_router)
app.include_router(financial_tracking_router)
app.include_router(activity_router)
app.include_router(monitoring_router)
app.include_router(collector_router)

# Serve static files from frontend build
backoffice_root = Path(__file__).parent.parent
frontend_dist = backoffice_root / "frontend" / "dist"

if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    # Mount static files (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    # Serve static files from root
    static_files = StaticFiles(directory=str(frontend_dist), html=True)
    app.mount("/static", static_files, name="static")
    
    # Explicit route for root path
    @app.get("/")
    async def serve_root():
        """Serve index.html for root path"""
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        raise HTTPException(status_code=404, detail="Frontend not found")
    
    # Catch-all route to serve index.html for React Router
    # Note: This will only match if no other route matches (FastAPI matches specific routes first)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str, request: Request):
        """
        Serve React app for all non-API routes.
        This allows React Router to handle client-side routing.
        """
        # Don't serve frontend for FastAPI docs routes (these are handled by FastAPI)
        if full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Handle empty path (shouldn't happen due to root route, but just in case)
        if not full_path or full_path == "/":
            index_path = frontend_dist / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
        
        # Check if it's a file request (has extension)
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        
        # Otherwise serve index.html for React Router (SPA routing)
        index_path = frontend_dist / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        
        raise HTTPException(status_code=404, detail="Not found")
    
    logger.info(f"Frontend static files mounted from {frontend_dist}")
else:
    logger.warning(f"Frontend build not found at {frontend_dist}. Frontend will not be served.")
    logger.warning("Run 'npm run build' in the frontend directory to build the frontend.")


if __name__ == "__main__":
    import uvicorn
    
    if _settings_loaded and settings:
        try:
            debug_mode = settings.BACKOFFICE_DEBUG
            host = settings.BACKOFFICE_SERVER_HOST
            port = settings.BACKOFFICE_SERVER_PORT
        except:
            debug_mode = True
            host = "127.0.0.1"
            port = 5001
    else:
        debug_mode = True
        host = "127.0.0.1"
        port = 5001
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug_mode
    )
