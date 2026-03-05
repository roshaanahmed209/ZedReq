"""Job Portal Pydantic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    EXECUTIVE = "executive"


class JobStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    DRAFT = "draft"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    HIRED = "hired"


# ============================================================================
# Job Posting Schemas
# ============================================================================

class JobPostingCreate(BaseModel):
    """Schema for creating a job posting"""
    title: str = Field(..., min_length=1, max_length=150)
    description: str = Field(..., min_length=1)
    company_name: Optional[str] = Field(None, max_length=150)
    location: Optional[str] = Field(None, max_length=150)
    job_type: Optional[JobType] = JobType.FULL_TIME
    is_remote: Optional[bool] = False
    experience_level: Optional[ExperienceLevel] = None
    skills_required: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    status: Optional[JobStatus] = JobStatus.ACTIVE


class JobPostingUpdate(BaseModel):
    """Schema for updating a job posting"""
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = Field(None, min_length=1)
    company_name: Optional[str] = Field(None, max_length=150)
    location: Optional[str] = Field(None, max_length=150)
    job_type: Optional[JobType] = None
    is_remote: Optional[bool] = None
    experience_level: Optional[ExperienceLevel] = None
    skills_required: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    status: Optional[JobStatus] = None


class JobPostingResponse(BaseModel):
    """Schema for job posting response"""
    job_id: int
    poster_id: int
    title: str
    description: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    is_remote: bool = False
    experience_level: Optional[str] = None
    skills_required: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    poster_username: Optional[str] = None
    poster_name: Optional[str] = None
    application_count: Optional[int] = None
    is_saved: Optional[bool] = None
    has_applied: Optional[bool] = None

    class Config:
        from_attributes = True


class JobPostingListResponse(BaseModel):
    """Schema for paginated job postings list"""
    jobs: List[JobPostingResponse]
    total: int
    limit: int
    offset: int


# ============================================================================
# Job Application Schemas
# ============================================================================

class JobApplicationCreate(BaseModel):
    """Schema for creating a job application"""
    job_id: int
    cover_letter: Optional[str] = None


class JobApplicationUpdate(BaseModel):
    """Schema for updating application status"""
    status: ApplicationStatus


class JobApplicationResponse(BaseModel):
    """Schema for job application response"""
    application_id: int
    job_id: int
    applicant_id: int
    status: str = "pending"
    cover_letter: Optional[str] = None
    match_score: Optional[int] = None
    applied_at: datetime
    # Job info (when joined)
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    is_remote: Optional[bool] = None
    job_status: Optional[str] = None
    # Applicant info (when joined)
    applicant_username: Optional[str] = None
    applicant_name: Optional[str] = None
    applicant_email: Optional[str] = None
    profile_pic: Optional[str] = None
    skills: Optional[str] = None
    short_desc: Optional[str] = None

    class Config:
        from_attributes = True


class JobApplicationListResponse(BaseModel):
    """Schema for paginated applications list"""
    applications: List[JobApplicationResponse]
    total: int


# ============================================================================
# Job Saved Schemas
# ============================================================================

class JobSavedResponse(BaseModel):
    """Schema for saved job response"""
    saved_id: int
    job_id: int
    user_id: int
    saved_at: datetime
    # Job info (when joined)
    title: Optional[str] = None
    description: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class JobSavedToggleResponse(BaseModel):
    """Schema for toggle save response"""
    is_saved: bool
    message: str


# ============================================================================
# Search/Filter Schemas
# ============================================================================

class JobSearchParams(BaseModel):
    """Schema for job search parameters"""
    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    is_remote: Optional[bool] = None
    experience_level: Optional[ExperienceLevel] = None
    limit: Optional[int] = Field(50, ge=1, le=100)
    offset: Optional[int] = Field(0, ge=0)


# ============================================================================
# Job Recommendation Schemas
# ============================================================================

class JobRecommendationResponse(BaseModel):
    """Schema for job recommendation response with scores"""
    # Job data (from JobPostingResponse)
    job_id: int
    poster_id: int
    title: str
    description: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    is_remote: bool = False
    experience_level: Optional[str] = None
    skills_required: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: str = "active"
    created_at: datetime
    updated_at: datetime
    poster_username: Optional[str] = None
    poster_name: Optional[str] = None
    application_count: Optional[int] = None
    is_saved: Optional[bool] = None
    has_applied: Optional[bool] = None
    
    # Recommendation scores
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")
    skill_match_score: float = Field(..., ge=0.0, le=1.0, description="Skill overlap score")
    salary_match_score: float = Field(..., ge=0.0, le=1.0, description="Salary match score")
    recency_score: float = Field(..., ge=0.0, le=1.0, description="Job recency score")
    composite_score: float = Field(..., ge=0.0, le=1.0, description="Overall composite recommendation score")
    
    class Config:
        from_attributes = True


class JobRecommendationListResponse(BaseModel):
    """Schema for paginated job recommendations list"""
    recommendations: List[JobRecommendationResponse]
    total: int