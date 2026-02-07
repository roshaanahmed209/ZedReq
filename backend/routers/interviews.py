"""Interviews Router - AI Mock Interview endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.auth import get_current_user
from config.database_orm import get_db
from services.interview_service import InterviewService
from services.recommendation_service import RecommendationService
from schemas.interview import (
    InterviewStartRequest,
    InterviewStartResponse,
    InterviewResponse,
    InterviewCompleteResponse,
    InterviewListResponse,
    InterviewRecommendationResponse
)

router = APIRouter()


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
    current_user: dict = Depends(get_current_user),
    service: InterviewService = Depends(get_interview_service)
):
    """Start a new mock interview for a job"""
    try:
        result = service.start_interview(
            user_id=current_user["id"],
            job_id=request.job_id
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


@router.post("/{interview_id}/complete", response_model=InterviewCompleteResponse)
async def complete_interview(
    interview_id: int,
    current_user: dict = Depends(get_current_user),
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
