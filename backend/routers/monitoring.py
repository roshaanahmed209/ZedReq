"""Monitoring endpoints for main ZedReq app"""
from fastapi import APIRouter, Depends, Request
from typing import Dict, Any
import psutil
import time
from datetime import datetime

from dependencies.auth import get_current_user

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/health")
async def detailed_health_check(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Detailed health check endpoint"""
    try:
        # Basic health
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0"
        }
        
        # Add system metrics
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            health_status["system"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024)
            }
        except:
            pass
        
        return health_status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/metrics")
async def current_metrics(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get current system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "percent": memory.percent,
                "used_mb": memory.used / (1024 * 1024),
                "total_mb": memory.total / (1024 * 1024),
                "available_mb": memory.available / (1024 * 1024)
            },
            "disk": {
                "percent": disk.percent,
                "used_gb": disk.used / (1024 * 1024 * 1024),
                "total_gb": disk.total / (1024 * 1024 * 1024),
                "free_gb": disk.free / (1024 * 1024 * 1024)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/stats")
async def request_stats(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get request statistics (placeholder - would need to query from backoffice)"""
    return {
        "message": "Request stats available from backoffice API",
        "endpoint": "/api/monitoring/performance",
        "timestamp": datetime.utcnow().isoformat()
    }
