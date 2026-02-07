"""
Nemz Agent Router - AI Career Assistant Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from agents.Nemz_agent import get_nemz_agent
from dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class SearchRequest(BaseModel):
    query: str
    search_type: Optional[str] = None  # "jobs", "profiles", "posts", or None for auto-detect
    limit: Optional[int] = 10


class SearchResponse(BaseModel):
    success: bool
    query: str
    search_type: str
    jobs: List[Dict[str, Any]] = []
    profiles: List[Dict[str, Any]] = []
    posts: List[Dict[str, Any]] = []
    total_results: int
    message: Optional[str] = None


# ============================================================================
# Nemz Agent Endpoints
# ============================================================================

@router.post("/search", response_model=SearchResponse)
async def search_all(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search across jobs, profiles, and posts using AI career assistant
    
    This endpoint:
    1. Determines query intent (if search_type not provided)
    2. Searches appropriate Qdrant collections
    3. Returns unified results with match scores
    """
    try:
        nemz_agent = get_nemz_agent()
        
        if not nemz_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nemz agent is not available. Please check Qdrant and OpenAI configuration."
            )
        
        # Process query
        results = nemz_agent.process_query(
            user_query=request.query,
            search_type=request.search_type,
            limit=request.limit or 10
        )
        
        return SearchResponse(
            success=True,
            query=results['query'],
            search_type=results['search_type'],
            jobs=results['jobs'],
            profiles=results['profiles'],
            posts=results['posts'],
            total_results=results['total_results'],
            message="Search completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_all: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search/jobs", response_model=SearchResponse)
async def search_jobs(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search for jobs matching the query
    """
    try:
        nemz_agent = get_nemz_agent()
        
        if not nemz_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nemz agent is not available. Please check Qdrant and OpenAI configuration."
            )
        
        # Search jobs only
        jobs = nemz_agent.search_jobs(
            query=request.query,
            limit=request.limit or 10
        )
        
        return SearchResponse(
            success=True,
            query=request.query,
            search_type="jobs",
            jobs=jobs,
            profiles=[],
            posts=[],
            total_results=len(jobs),
            message="Job search completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search/profiles", response_model=SearchResponse)
async def search_profiles(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search for user profiles matching the query
    """
    try:
        nemz_agent = get_nemz_agent()
        
        if not nemz_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nemz agent is not available. Please check Qdrant and OpenAI configuration."
            )
        
        # Search profiles only
        profiles = nemz_agent.search_profiles(
            query=request.query,
            limit=request.limit or 10
        )
        
        return SearchResponse(
            success=True,
            query=request.query,
            search_type="profiles",
            jobs=[],
            profiles=profiles,
            posts=[],
            total_results=len(profiles),
            message="Profile search completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_profiles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/search/posts", response_model=SearchResponse)
async def search_posts(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Search for posts matching the query
    """
    try:
        nemz_agent = get_nemz_agent()
        
        if not nemz_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nemz agent is not available. Please check Qdrant and OpenAI configuration."
            )
        
        # Search posts only
        posts = nemz_agent.search_posts(
            query=request.query,
            limit=request.limit or 10
        )
        
        return SearchResponse(
            success=True,
            query=request.query,
            search_type="posts",
            jobs=[],
            profiles=[],
            posts=posts,
            total_results=len(posts),
            message="Post search completed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search_posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
