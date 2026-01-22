"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from config.database import init_database, get_database
from routers import (
    auth_router,
    network_router,
    connections_router,
    notifications_router,
    websocket_router,
    user_router,
    feed_router,
    posts_router,
    jobs_router
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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=5000,
        reload=settings.DEBUG
    )
