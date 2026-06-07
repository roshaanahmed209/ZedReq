"""Interviews Router - AI Mock Interview endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.auth import get_current_user
from dependencies.rate_limit import RateLimiter
from dependencies.subscription import require_interview_quota
from config.database_orm import get_db
from config.settings import settings
from services.interview_service import InterviewService
from services.recommendation_service import RecommendationService
from schemas.interview import (
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewResponse,
    InterviewCompleteResponse,
    InterviewListResponse,
    InterviewRecommendationResponse,
    InterviewTranscriptResponse,
)
from services.interview_service import InterviewNotFoundError

router = APIRouter()

# Rate limiters for interview endpoints
# Interview operations are resource-intensive (LLM calls, external API calls)
_interview_start_limiter = RateLimiter(requests_per_minute=10)  # Start interview: 10 req/min
_interview_complete_limiter = RateLimiter(requests_per_minute=5)  # Complete interview: 5 req/min
_riz_refresh_limiter = RateLimiter(requests_per_minute=3)  # Refresh Riz feedback: 3 req/min


def interview_start_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for starting interviews"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _interview_start_limiter.is_allowed(user_id):
        remaining = _interview_start_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many interview start requests. Please wait before starting another interview.",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": str(_interview_start_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user


def interview_complete_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for completing interviews"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _interview_complete_limiter.is_allowed(user_id):
        remaining = _interview_complete_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many interview completion requests. Please wait before completing another interview.",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": str(_interview_complete_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user


def riz_refresh_rate_limit(current_user: dict = Depends(get_current_user)):
    """Rate limit for refreshing Riz feedback"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not _riz_refresh_limiter.is_allowed(user_id):
        remaining = _riz_refresh_limiter.get_remaining(user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Too many Riz feedback refresh requests. Please wait before refreshing again.",
                "retry_after": 60,
                "remaining": remaining
            },
            headers={
                "X-RateLimit-Limit": str(_riz_refresh_limiter.requests_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "Retry-After": "60"
            }
        )
    
    return current_user


def get_interview_service(db: Session = Depends(get_db)) -> InterviewService:
    """Dependency to get InterviewService with database session"""
    return InterviewService(db)


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    """Dependency to get RecommendationService with database session"""
    return RecommendationService(db)


# ============================================================================
# Interview Endpoints
# ============================================================================

@router.post("/start", response_model=InterviewStartResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(
    request: InterviewStartRequest,
    http_request: Request,
    current_user: dict = Depends(interview_start_rate_limit),
    _quota_user: dict = Depends(require_interview_quota),
    service: InterviewService = Depends(get_interview_service)
):
    """
    Start a new mock interview for a job.
    
    Security:
    - Rate limit: 10 requests/minute (burst protection)
    - Quota: Monthly interview session limit per subscription plan (atomic server-side check)
    - max_call_duration is read from INTERVIEW_MAX_DURATION_SECONDS (env), via require_interview_quota
    """
    try:
        # Single source: INTERVIEW_MAX_DURATION_SECONDS in .env (via settings)
        max_duration = getattr(
            http_request.state,
            'max_interview_duration',
            settings.get_interview_max_duration_seconds(),
        )
        
        result = service.start_interview(
            user_id=current_user["id"],
            job_id=request.job_id,
            max_call_duration=max_duration
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview: {str(e)}"
        )


@router.get("/my-interviews", response_model=InterviewListResponse)
async def get_my_interviews(
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service)
):
    """Get current user's interview history"""
    interviews = service.get_user_interview_history(
        user_id=current_user["id"],
        job_id=job_id
    )
    
    return {
        "interviews": interviews,
        "total": len(interviews)
    }


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service)
):
    """Get interview details"""
    interview = service.get_interview(interview_id, user_id=current_user["id"])
    
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    return interview


@router.get("/{interview_id}/transcript", response_model=InterviewTranscriptResponse)
async def get_interview_transcript(
    interview_id: int,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
):
    """Get question-wise user responses from Tavus for an interview session."""
    try:
        return service.get_interview_transcript(interview_id, current_user["id"])
    except InterviewNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch interview transcript: {str(e)}",
        )


@router.post("/{interview_id}/complete", response_model=InterviewCompleteResponse)
async def complete_interview(
    interview_id: int,
    current_user: dict = Depends(interview_complete_rate_limit),
    service: InterviewService = Depends(get_interview_service)
):
    """Complete an interview and get analysis results"""
    # Verify ownership
    interview = service.get_interview(interview_id, user_id=current_user["id"])
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    try:
        result = service.complete_interview(interview_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete interview: {str(e)}"
        )


@router.get("/recommendations/{user_id}")
async def get_interview_recommendations(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    interview_service: InterviewService = Depends(get_interview_service)
):
    """
    Get job recommendations for interviews with attempt counts
    
    Users can only view their own recommendations.
    """
    # Verify user can only see their own recommendations
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot view other user's recommendations"
        )
    
    # Get recommendations
    recommendations = recommendation_service.get_recommendations(user_id, limit=limit)
    
    # Enrich with interview attempt counts and best scores
    enriched_recommendations = []
    for rec in recommendations:
        job_id = rec['job_id']
        
        # Get attempt count
        attempt_count = interview_service.get_interview_attempt_number(user_id, job_id)
        
        # Get best score
        from models.orm.live_interview import LiveInterview
        from sqlalchemy import func
        
        best_interview = db.query(
            func.max(LiveInterview.overall_score)
        ).filter(
            LiveInterview.user_id == user_id,
            LiveInterview.job_id == job_id,
            LiveInterview.status == 'completed'
        ).scalar()
        
        enriched_recommendations.append({
            **rec,
            'attempt_count': attempt_count,
            'best_score': best_interview if best_interview else None
        })
    
    return {
        "recommendations": enriched_recommendations,
        "total": len(enriched_recommendations)
    }


# ============================================================================
# Riz Agent Endpoints
# ============================================================================

@router.get("/{interview_id}/riz-feedback")
async def get_riz_feedback(
    interview_id: int,
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service),
    db: Session = Depends(get_db)
):
    """
    Get Riz coaching feedback for a completed interview
    """
    # Verify ownership
    interview = service.get_interview(interview_id, user_id=current_user["id"])
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check if interview is completed
    from models.orm.live_interview import LiveInterview
    interview_obj = db.query(LiveInterview).filter(
        LiveInterview.interview_id == interview_id
    ).first()
    
    if not interview_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview_obj.status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview must be completed before fetching Riz feedback"
        )
    
    # Return Riz feedback if available
    if interview_obj.riz_feedback:
        return {
            "interview_id": interview_id,
            "riz_feedback": interview_obj.riz_feedback
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Riz feedback not available for this interview"
        )


@router.post("/{interview_id}/riz-feedback/refresh")
async def refresh_riz_feedback(
    interview_id: int,
    current_user: dict = Depends(riz_refresh_rate_limit),
    service: InterviewService = Depends(get_interview_service),
    db: Session = Depends(get_db)
):
    """
    Regenerate Riz coaching feedback for a completed interview
    """
    from models.orm.live_interview import LiveInterview
    from models.orm.job_posting import JobPosting
    from agents.Riz_agent import get_riz_agent
    
    # Verify ownership
    interview_obj = db.query(LiveInterview).filter(
        LiveInterview.interview_id == interview_id,
        LiveInterview.user_id == current_user["id"]
    ).first()
    
    if not interview_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview_obj.status != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview must be completed before generating Riz feedback"
        )
    
    # Get job details
    job = db.query(JobPosting).filter(
        JobPosting.job_id == interview_obj.job_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Generate Riz feedback
    try:
        riz_agent = get_riz_agent()
        if not riz_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Riz agent is not available. Please check OpenAI configuration."
            )
        
        riz_feedback = riz_agent.generate_feedback(
            job_title=job.title,
            company_name=job.company_name,
            job_description=job.description,
            questions=interview_obj.questions or [],
            user_responses=interview_obj.user_responses or [],
            overall_score=interview_obj.overall_score,
            score_breakdown=interview_obj.score_breakdown,
            tav_check_feedback=interview_obj.feedback
        )
        
        # Update interview with new Riz feedback
        interview_obj.riz_feedback = riz_feedback
        db.commit()
        db.refresh(interview_obj)
        
        return {
            "interview_id": interview_id,
            "riz_feedback": riz_feedback,
            "message": "Riz feedback regenerated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate Riz feedback: {str(e)}"
        )