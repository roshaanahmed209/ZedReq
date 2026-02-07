"""Interview Schemas for AI Mock Interview System"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Request Schemas
# ============================================================================

class InterviewStartRequest(BaseModel):
    """Schema for starting a new interview"""
    job_id: int = Field(..., description="Job ID to interview for")


# ============================================================================
# Response Schemas
# ============================================================================

class QuestionSchema(BaseModel):
    """Schema for interview question"""
    question_text: str
    question_type: str  # technical, behavioral, problem_solving, domain_knowledge
    answer_criteria: str
    expected_key_points: List[str]
    difficulty_level: str  # beginner, intermediate, advanced


class ScoreBreakdown(BaseModel):
    """Schema for detailed score breakdown"""
    technical_score: int = Field(..., ge=0, le=100)
    communication_score: int = Field(..., ge=0, le=100)
    problem_solving_score: int = Field(..., ge=0, le=100)
    domain_knowledge_score: int = Field(..., ge=0, le=100)


class QuestionScore(BaseModel):
    """Schema for individual question score"""
    question_index: int
    score: int = Field(..., ge=0, le=100)
    feedback: str


class InterviewStartResponse(BaseModel):
    """Schema for interview start response"""
    interview_id: int
    tavus_conversation_id: str
    questions: List[QuestionSchema]
    status: str
    attempt_number: int
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class InterviewResponse(BaseModel):
    """Schema for interview details"""
    interview_id: int
    user_id: int
    job_id: int
    tavus_conversation_id: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    user_responses: Optional[List[Dict[str, Any]]] = None
    overall_score: Optional[int] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    feedback: Optional[str] = None
    attempt_number: int
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    job_title: Optional[str] = None
    company_name: Optional[str] = None


class InterviewCompleteResponse(BaseModel):
    """Schema for interview completion response"""
    interview_id: int
    overall_score: int = Field(..., ge=0, le=100)
    score_breakdown: ScoreBreakdown
    question_scores: List[QuestionScore]
    detailed_feedback: str
    strengths: List[str]
    weaknesses: List[str]
    improvement_suggestions: List[str]
    attempt_number: int
    completed_at: datetime


class InterviewListResponse(BaseModel):
    """Schema for interview list response"""
    interviews: List[InterviewResponse]
    total: int


class InterviewRecommendationResponse(BaseModel):
    """Schema for job recommendations with attempt counts"""
    job_id: int
    title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    is_remote: bool = False
    experience_level: Optional[str] = None
    attempt_count: int = 0  # Number of times user has interviewed for this job
    best_score: Optional[int] = None  # Best score achieved (if any)
    similarity_score: Optional[float] = None
    composite_score: Optional[float] = None
