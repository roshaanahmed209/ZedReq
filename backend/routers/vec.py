"""
Vec Agent Router - Vector Database Sync Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

from agents.Vec_agent import get_vec_agent
from dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class SyncRequest(BaseModel):
    force: Optional[bool] = False  # If True, re-index all entities


class SyncResponse(BaseModel):
    success: bool
    message: str
    result: Optional[Dict[str, Any]] = None


class StatusResponse(BaseModel):
    success: bool
    available: bool
    collections: Dict[str, bool]
    point_counts: Optional[Dict[str, int]] = None  # Collection name -> point count
    total_points: Optional[int] = None  # Total points across all collections
    message: str


# ============================================================================
# Vec Agent Endpoints
# ============================================================================

@router.post("/sync", response_model=SyncResponse)
async def trigger_vec_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Manually trigger Vec agent sync to populate Qdrant vector database
    
    This endpoint:
    1. Triggers indexing of jobs, users, and posts
    2. Can run in background or synchronously
    3. Returns statistics about indexed entities
    """
    try:
        vec_agent = get_vec_agent()
        
        if not vec_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vec agent is not available. Please check Qdrant and OpenAI configuration."
            )
        
        # Run sync (can be background task if needed)
        result = vec_agent.sync_all_entities(force=request.force or False)
        
        # Log detailed results for debugging
        logger.info(f"Vec sync result: {result}")
        if result.get('errors'):
            logger.warning(f"Vec sync had errors: {result.get('errors')}")
        
        return SyncResponse(
            success=result.get('success', True),
            message=f"Sync completed: {result.get('total_indexed', 0)} entities indexed. Jobs: {result.get('jobs_indexed', 0)}, Users: {result.get('users_indexed', 0)}, Posts: {result.get('posts_indexed', 0)}",
            result=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trigger_vec_sync: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/sync/background", response_model=SyncResponse)
async def trigger_vec_sync_background(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger Vec agent sync as a background task
    """
    try:
        vec_agent = get_vec_agent()
        
        if not vec_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vec agent is not available. Please check Qdrant and OpenAI configuration."
            )
        
        # Add background task
        def run_sync():
            try:
                vec_agent.sync_all_entities(force=request.force or False)
            except Exception as e:
                logger.error(f"Background sync failed: {e}")
        
        background_tasks.add_task(run_sync)
        
        return SyncResponse(
            success=True,
            message="Sync task started in background",
            result=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trigger_vec_sync_background: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/status", response_model=StatusResponse)
async def get_vec_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get Vec agent status and collection information
    """
    try:
        vec_agent = get_vec_agent()
        
        available = vec_agent.is_available()
        
        # Check collection existence and point counts
        collections_status = {}
        point_counts = {}
        total_points = 0
        
        if vec_agent.qdrant_available and vec_agent.qdrant_client:
            try:
                existing_collections = vec_agent.qdrant_client.get_collections()
                existing_names = [col.name for col in existing_collections.collections]
                
                # Get point counts for each collection
                for name in vec_agent.collections.values():
                    collections_status[name] = name in existing_names
                    
                    if name in existing_names:
                        try:
                            # Get collection info to retrieve point count
                            collection_info = vec_agent.qdrant_client.get_collection(name)
                            point_count = collection_info.points_count if hasattr(collection_info, 'points_count') else 0
                            point_counts[name] = point_count
                            total_points += point_count
                        except Exception as e:
                            # Collection might not exist yet (404 error is OK)
                            if '404' in str(e) or 'not found' in str(e).lower():
                                logger.debug(f"Collection {name} does not exist yet")
                            else:
                                logger.warning(f"Failed to get point count for collection {name}: {e}")
                            point_counts[name] = 0
                    else:
                        point_counts[name] = 0
            except Exception as e:
                logger.error(f"Failed to check collections: {e}")
                for name in vec_agent.collections.values():
                    collections_status[name] = False
                    point_counts[name] = 0
        else:
            for name in vec_agent.collections.values():
                collections_status[name] = False
                point_counts[name] = 0
        
        return StatusResponse(
            success=True,
            available=available,
            collections=collections_status,
            point_counts=point_counts,
            total_points=total_points,
            message="Vec agent status retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in get_vec_status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
