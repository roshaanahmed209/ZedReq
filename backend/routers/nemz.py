"""
Nemz Agent Router - AI Career Assistant Endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends, Header
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import logging

from agents.Nemz_agent import get_nemz_agent
from dependencies.auth import get_current_user
from dependencies.rate_limit import RateLimiter
from services.chat_session_manager import get_session_manager
from utils.input_sanitizer import InputSanitizer

logger = logging.getLogger(__name__)

router = APIRouter()

# Rate limiter for chat endpoints (20 requests per minute per user)
_chat_rate_limiter = RateLimiter(requests_per_minute=20)


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


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: Optional[str] = Field(None, description="Chat session ID (optional, will create if not provided)")
    
    @validator('message')
    def validate_message(cls, v):
        """Validate and sanitize message"""
        sanitized = InputSanitizer.sanitize_message(v)
        if not sanitized:
            raise ValueError("Invalid message: empty or contains dangerous content")
        return sanitized
    
    @validator('session_id')
    def validate_session_id(cls, v):
        """Validate session ID format if provided"""
        if v is not None and not InputSanitizer.validate_session_id(v):
            raise ValueError("Invalid session ID format")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Hello, can you help me find software engineering jobs?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ChatResponse(BaseModel):
    success: bool
    response: str
    should_search: bool
    search_type: Optional[str] = None
    search_query: Optional[str] = None
    session_id: str
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


def chat_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for chat endpoints"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _chat_rate_limiter.is_allowed(user_id):
        remaining = _chat_rate_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many chat requests. Please wait before trying again.",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": "20",
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(chat_rate_limit)
):
    """
    Conversational chat endpoint with session management.
    
    Features:
    - Session-based conversation isolation (no context leakage)
    - Automatic session creation if not provided
    - Rate limiting (20 requests/minute per user)
    - Input sanitization (OWASP security practices)
    - The AI decides when to use search as a tool
    
    This endpoint:
    1. Validates and sanitizes input
    2. Gets or creates chat session
    3. Processes user message conversationally
    4. LLM decides if search is needed
    5. Returns response and search instructions if needed
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Get session manager
        session_manager = get_session_manager()
        
        # Get or create session
        session_id = request.session_id
        if not session_id:
            # Create new session
            session_id = session_manager.create_session(user_id)
        else:
            # Validate existing session belongs to user
            session = session_manager.get_session(session_id, user_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found or expired. A new session will be created."
                )
        
        # Get conversation history from session
        conversation_history = session_manager.get_history(session_id, user_id)
        
        # Get Nemz agent
        nemz_agent = get_nemz_agent()
        
        if not nemz_agent.openai_available:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Nemz agent is not available. Please check OpenAI configuration."
            )
        
        # Get conversational response with user context (only for logged-in users)
        chat_result = nemz_agent.chat(
            user_message=request.message,
            conversation_history=conversation_history,
            user_id=user_id  # Pass user_id to fetch Zed context from database
        )
        
        # Store user message in session
        session_manager.add_message(session_id, user_id, "user", request.message)
        
        # Store assistant response in session
        session_manager.add_message(session_id, user_id, "assistant", chat_result["response"])
        
        return ChatResponse(
            success=True,
            response=chat_result["response"],
            should_search=chat_result["should_search"],
            search_type=chat_result["search_type"],
            search_query=chat_result["search_query"],
            session_id=session_id,
            message="Chat response generated successfully"
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        # Input validation errors
        logger.warning(f"Input validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error. Please try again."
        )


@router.delete("/chat/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a chat session
    
    Security: Only the session owner can delete their session
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Validate session ID format
        if not InputSanitizer.validate_session_id(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID format"
            )
        
        session_manager = get_session_manager()
        success = session_manager.remove_session(session_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or you don't have permission to delete it"
            )
        
        return {
            "success": True,
            "message": "Session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
