"""Interview Schemas for AI Mock Interview System"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Request Schemas
# ============================================================================

class InterviewStartRequest(BaseModel):
    """Schema for starting a new interview"""
    job_id: int = Field(..., description="Job ID to interview for", gt=0)
    
    @field_validator('job_id')
    @classmethod
    def validate_job_id(cls, v: int) -> int:
        """Validate job_id is a positive integer"""
        if not isinstance(v, int) or v <= 0:
            raise ValueError("job_id must be a positive integer")
        return v


# ============================================================================
# Response Schemas
# ============================================================================

class QuestionSchema(BaseModel):
    """Schema for interview question"""
    question_text: str = Field(..., max_length=1000, description="Question text")
    question_type: str = Field(..., max_length=50, description="Question type: technical, behavioral, problem_solving, domain_knowledge")
    answer_criteria: str = Field(..., max_length=2000, description="Answer criteria")
    expected_key_points: List[str] = Field(..., max_length=20, description="Expected key points")
    difficulty_level: str = Field(..., max_length=20, description="Difficulty level: beginner, intermediate, advanced")
    
    @field_validator('question_type')
    @classmethod
    def validate_question_type(cls, v: str) -> str:
        """Validate question type"""
        allowed_types = ['technical', 'behavioral', 'problem_solving', 'domain_knowledge']
        if v.lower() not in allowed_types:
            raise ValueError(f"question_type must be one of: {', '.join(allowed_types)}")
        return v.lower()
    
    @field_validator('difficulty_level')
    @classmethod
    def validate_difficulty_level(cls, v: str) -> str:
        """Validate difficulty level"""
        allowed_levels = ['beginner', 'intermediate', 'advanced']
        if v.lower() not in allowed_levels:
            raise ValueError(f"difficulty_level must be one of: {', '.join(allowed_levels)}")
        return v.lower()
    
    @field_validator('expected_key_points')
    @classmethod
    def validate_key_points(cls, v: List[str]) -> List[str]:
        """Validate and limit key points"""
        if len(v) > 20:
            raise ValueError("expected_key_points cannot exceed 20 items")
        return [str(point)[:200] for point in v]  # Limit each point to 200 chars


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
    interview_id: int = Field(..., gt=0)
    tavus_conversation_id: str = Field(..., max_length=255)
    questions: List[QuestionSchema] = Field(..., min_length=1, max_length=20)
    status: str = Field(..., max_length=20)
    attempt_number: int = Field(..., ge=1)
    job_title: Optional[str] = Field(None, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate interview status"""
        allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if v.lower() not in allowed_statuses:
            raise ValueError(f"status must be one of: {', '.join(allowed_statuses)}")
        return v.lower()


class InterviewResponse(BaseModel):
    """Schema for interview details"""
    interview_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    job_id: int = Field(..., gt=0)
    tavus_conversation_id: Optional[str] = Field(None, max_length=255)
    questions: Optional[List[Dict[str, Any]]] = None
    user_responses: Optional[List[Dict[str, Any]]] = None
    overall_score: Optional[int] = Field(None, ge=0, le=100)
    score_breakdown: Optional[ScoreBreakdown] = None
    feedback: Optional[str] = Field(None, max_length=10000)
    riz_feedback: Optional[Dict[str, Any]] = None
    attempt_number: int = Field(..., ge=1)
    status: str = Field(..., max_length=20)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    job_title: Optional[str] = Field(None, max_length=200)
    company_name: Optional[str] = Field(None, max_length=200)
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate interview status"""
        allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'failed']
        if v.lower() not in allowed_statuses:
            raise ValueError(f"status must be one of: {', '.join(allowed_statuses)}")
        return v.lower()
    
    @field_validator('overall_score')
    @classmethod
    def validate_overall_score(cls, v: Optional[int]) -> Optional[int]:
        """Validate overall score is in valid range"""
        if v is not None and (v < 0 or v > 100):
            raise ValueError("overall_score must be between 0 and 100")
        return v
    
    @field_validator('started_at', 'completed_at', 'created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> Optional[datetime]:
        """Parse datetime from string or return datetime object"""
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                # Try parsing ISO format
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                # If parsing fails, try common formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                    try:
                        return datetime.strptime(v, fmt)
                    except ValueError:
                        continue
                raise ValueError(f"Invalid datetime format: {v}")
        return v
    
    @field_validator('score_breakdown', mode='before')
    @classmethod
    def parse_score_breakdown(cls, v: Any) -> Optional[ScoreBreakdown]:
        """Parse score_breakdown from dict or return ScoreBreakdown object"""
        if v is None:
            return None
        if isinstance(v, ScoreBreakdown):
            return v
        if isinstance(v, dict):
            try:
                return ScoreBreakdown(**v)
            except Exception:
                # If validation fails, return None instead of raising error
                return None
        return v
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class InterviewCompleteResponse(BaseModel):
    """Schema for interview completion response"""
    interview_id: int = Field(..., gt=0)
    overall_score: int = Field(..., ge=0, le=100)
    score_breakdown: ScoreBreakdown
    question_scores: List[QuestionScore] = Field(..., max_length=50)
    detailed_feedback: str = Field(..., max_length=5000)
    strengths: List[str] = Field(..., max_length=20)
    weaknesses: List[str] = Field(..., max_length=20)
    improvement_suggestions: List[str] = Field(..., max_length=20)
    attempt_number: int = Field(..., ge=1)
    completed_at: datetime
    
    @field_validator('strengths', 'weaknesses', 'improvement_suggestions')
    @classmethod
    def validate_list_items(cls, v: List[str]) -> List[str]:
        """Validate and limit list items"""
        if len(v) > 20:
            raise ValueError("List cannot exceed 20 items")
        return [str(item)[:500] for item in v]  # Limit each item to 500 chars


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
