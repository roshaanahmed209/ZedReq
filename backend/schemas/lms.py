"""LMS Pydantic Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class CourseDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CourseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class QuestionType(str, Enum):
    TEXT = "text"
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    ESSAY = "essay"


class ActivityType(str, Enum):
    ENROLLMENT = "enrollment"
    SECTION_COMPLETE = "section_complete"
    ANSWER_SUBMIT = "answer_submit"
    COURSE_COMPLETE = "course_complete"
    CERTIFICATE_EARNED = "certificate_earned"
    LESSON_STARTED = "lesson_started"


class ResourceType(str, Enum):
    VIDEO = "video"
    DOCUMENT = "document"
    LINK = "link"
    PDF = "pdf"
    SLIDES = "slides"


# ============================================================================
# Course Schemas
# ============================================================================

class CourseCreate(BaseModel):
    """Schema for creating a course"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    lessons: Optional[int] = Field(0, ge=0)
    duration: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[CourseDifficulty] = CourseDifficulty.BEGINNER
    is_active: Optional[bool] = True


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    icon: Optional[str] = Field(None, max_length=10)
    lessons: Optional[int] = Field(None, ge=0)
    duration: Optional[str] = Field(None, max_length=50)
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[CourseDifficulty] = None
    is_active: Optional[bool] = None


class CourseResponse(BaseModel):
    """Schema for course response"""
    id: int
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    lessons: int = 0
    duration: Optional[str] = None
    category: Optional[str] = None
    difficulty: str = "beginner"
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    progress: Optional[int] = None  # For user courses
    sections_count: Optional[int] = None
    resources_count: Optional[int] = None

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    """Schema for paginated courses list"""
    courses: List[CourseResponse]
    total: int
    limit: int
    offset: int


# ============================================================================
# User Course Schemas
# ============================================================================

class UserCourseEnroll(BaseModel):
    """Schema for enrolling in a course"""
    course_id: int = Field(..., gt=0)


class UserCourseResponse(BaseModel):
    """Schema for user course enrollment response"""
    id: int
    user_id: int
    course_id: int
    progress: int = 0
    status: str = "not_started"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    course_title: Optional[str] = None
    course_icon: Optional[str] = None
    course_description: Optional[str] = None
    course_lessons: Optional[int] = None
    course_duration: Optional[str] = None

    class Config:
        from_attributes = True


class UserCourseListResponse(BaseModel):
    """Schema for paginated user courses list"""
    courses: List[UserCourseResponse]
    total: int
    limit: int
    offset: int


class CourseProgressUpdate(BaseModel):
    """Schema for updating course progress"""
    progress: int = Field(..., ge=0, le=100)


# ============================================================================
# Dashboard Schemas
# ============================================================================

class DashboardResponse(BaseModel):
    """Schema for dashboard stats response"""
    id: int
    user_id: int
    total_questions: int = 0
    correct_answers: int = 0
    wrong_answers: int = 0
    overall_accuracy: float = 0.0
    day_streak: int = 0
    last_activity_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Performance Schemas
# ============================================================================

class WeeklyPerformanceResponse(BaseModel):
    """Schema for weekly/daily performance"""
    id: int
    user_id: int
    date: date
    questions_answered: int = 0
    correct_answers: int = 0
    wrong_answers: int = 0
    study_time_minutes: int = 0
    accuracy: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


class WeeklyPerformanceListResponse(BaseModel):
    """Schema for weekly performance list"""
    performance: List[WeeklyPerformanceResponse]
    total: int


class DomainPerformanceResponse(BaseModel):
    """Schema for domain-specific performance"""
    id: int
    user_id: int
    domain_id: int
    questions_answered: int = 0
    correct_answers: int = 0
    accuracy_percentage: float = 0.0
    domain_name: Optional[str] = None
    domain_icon: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DomainPerformanceListResponse(BaseModel):
    """Schema for domain performance list"""
    domains: List[DomainPerformanceResponse]


class CoursePerformanceResponse(BaseModel):
    """Schema for course-specific performance"""
    id: int
    user_id: int
    course_id: int
    questions_answered: int = 0
    correct_answers: int = 0
    wrong_answers: int = 0
    accuracy_percentage: float = 0.0
    total_points_earned: int = 0
    last_activity_date: Optional[date] = None
    course_title: Optional[str] = None
    course_icon: Optional[str] = None
    course_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Section Performance Schemas
# ============================================================================

class SectionPerformanceItem(BaseModel):
    """Per-section evaluation metrics for a single level."""
    section_id: int
    title: str
    order_index: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    accuracy_percentage: float = 0.0
    total_points_earned: int = 0

    class Config:
        from_attributes = True


class SectionPerformanceResponse(BaseModel):
    """Wrapper response for per-section performance summary."""
    sections: List[SectionPerformanceItem] = []


# ============================================================================
# Activity Schemas
# ============================================================================

class ActivityResponse(BaseModel):
    """Schema for activity response"""
    id: int
    user_id: int
    course_id: Optional[int] = None
    activity_type: str
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    created_at: datetime
    course_title: Optional[str] = None
    course_icon: Optional[str] = None

    class Config:
        from_attributes = True


class ActivityListResponse(BaseModel):
    """Schema for activities list"""
    activities: List[ActivityResponse]
    total: int


# ============================================================================
# Question/Answer Schemas
# ============================================================================

class QuestionCreate(BaseModel):
    """Schema for creating a question"""
    course_id: int = Field(..., gt=0)
    section_id: Optional[int] = Field(None, gt=0)
    question_text: str = Field(..., min_length=1)
    question_type: Optional[QuestionType] = QuestionType.TEXT
    options: Optional[Dict[str, Any]] = None  # For multiple choice
    correct_answer: Optional[str] = None
    points: Optional[int] = Field(1, ge=1)
    order_index: Optional[int] = Field(0, ge=0)


class QuestionResponse(BaseModel):
    """Schema for question response"""
    id: int
    course_id: int
    section_id: Optional[int] = None
    question_text: str
    question_type: str = "text"
    options: Optional[Dict[str, Any]] = None
    correct_answer: Optional[str] = None
    points: int = 1
    order_index: int = 0
    created_at: datetime
    answers_count: Optional[int] = None

    class Config:
        from_attributes = True


class QuestionListResponse(BaseModel):
    """Schema for questions list"""
    questions: List[QuestionResponse]
    total: int


class AnswerSubmit(BaseModel):
    """Schema for submitting an answer"""
    question_id: int = Field(..., gt=0)
    answer_text: str = Field(..., min_length=1)


class AnswerEvaluate(BaseModel):
    """Schema for evaluating an answer"""
    is_correct: bool
    points: int = Field(0, ge=0)
    feedback: Optional[str] = None


class AnswerResponse(BaseModel):
    """Schema for answer response"""
    id: int
    user_id: int
    question_id: int
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    points_earned: int = 0
    feedback: Optional[str] = None
    submitted_at: datetime
    evaluated_at: Optional[datetime] = None
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    points: Optional[int] = None

    class Config:
        from_attributes = True


class AnswerListResponse(BaseModel):
    """Schema for answers list"""
    answers: List[AnswerResponse]
    total: int


# ============================================================================
# Recommendation Schemas
# ============================================================================

class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""
    id: int
    user_id: int
    course_id: int
    reason: Optional[str] = None
    priority: int = 0
    is_dismissed: bool = False
    created_at: datetime
    course_title: Optional[str] = None
    course_icon: Optional[str] = None
    course_description: Optional[str] = None

    class Config:
        from_attributes = True


class RecommendationListResponse(BaseModel):
    """Schema for recommendations list"""
    recommendations: List[RecommendationResponse]
    total: int


# ============================================================================
# Deadline Schemas
# ============================================================================

class DeadlineCreate(BaseModel):
    """Schema for creating a deadline"""
    course_id: Optional[int] = Field(None, gt=0)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: datetime


class DeadlineResponse(BaseModel):
    """Schema for deadline response"""
    id: int
    user_id: int
    course_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    due_date: datetime
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    reminder_sent: bool = False
    created_at: datetime
    course_title: Optional[str] = None
    course_icon: Optional[str] = None

    class Config:
        from_attributes = True


class DeadlineListResponse(BaseModel):
    """Schema for deadlines list"""
    deadlines: List[DeadlineResponse]
    total: int


# ============================================================================
# Certificate Schemas
# ============================================================================

class CertificateResponse(BaseModel):
    """Schema for certificate response"""
    id: int
    user_id: int
    course_id: int
    certificate_number: str
    title: str
    issued_at: datetime
    expiry_date: Optional[datetime] = None
    pdf_url: Optional[str] = None
    course_title: Optional[str] = None
    course_icon: Optional[str] = None

    class Config:
        from_attributes = True


class CertificateListResponse(BaseModel):
    """Schema for certificates list"""
    certificates: List[CertificateResponse]
    total: int


# ============================================================================
# Section/Resource Schemas
# ============================================================================

class SectionResponse(BaseModel):
    """Schema for section response"""
    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    order_index: int = 0
    total_items: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class SectionListResponse(BaseModel):
    """Schema for sections list"""
    sections: List[SectionResponse]
    total: int


class ResourceResponse(BaseModel):
    """Schema for resource response"""
    id: int
    course_id: int
    title: str
    resource_type: str
    url: Optional[str] = None
    description: Optional[str] = None
    order_index: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceListResponse(BaseModel):
    """Schema for resources list"""
    resources: List[ResourceResponse]
    total: int


# ============================================================================
# Section Progress Schemas
# ============================================================================

class SectionProgressResponse(BaseModel):
    """Schema for section progress response"""
    id: int
    user_id: int
    section_id: int
    completed_items: int = 0
    is_completed: bool = False
    section_title: Optional[str] = None
    section_total_items: Optional[int] = None
    progress_percentage: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SectionProgressUpdate(BaseModel):
    """Schema for updating section progress"""
    completed_items: int = Field(..., ge=0)
    total_items: int = Field(..., gt=0)


# ============================================================================
# Azel Agent Schemas
# ============================================================================

class ProcessCourseRequest(BaseModel):
    """Schema for triggering Azel question generation scoped to a section"""
    section_id: Optional[int] = Field(None, gt=0, description="Section to generate questions for")