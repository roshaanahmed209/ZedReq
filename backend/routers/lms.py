"""LMS Router - Learning Management System endpoints using SQLAlchemy ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from dependencies.auth import get_current_user
from config.database_orm import get_db
from services.lms_service import LMSService
from models.orm import LMSCourse, LMSUserCourse, LMSUserAnswer
from schemas.lms import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse,
    UserCourseEnroll, UserCourseResponse, UserCourseListResponse, CourseProgressUpdate,
    DashboardResponse,
    WeeklyPerformanceResponse, WeeklyPerformanceListResponse,
    DomainPerformanceResponse, DomainPerformanceListResponse,
    ActivityResponse, ActivityListResponse,
    QuestionCreate, QuestionResponse, QuestionListResponse,
    AnswerSubmit, AnswerResponse, AnswerListResponse, AnswerEvaluate,
    RecommendationResponse, RecommendationListResponse,
    DeadlineCreate, DeadlineResponse, DeadlineListResponse,
    CertificateResponse, CertificateListResponse,
    SectionResponse, SectionListResponse,
    ResourceResponse, ResourceListResponse,
    SectionProgressResponse, SectionProgressUpdate
)

router = APIRouter()


def get_lms_service(db: Session = Depends(get_db)) -> LMSService:
    """Dependency to get LMS service with database session"""
    return LMSService(db)


# ============================================================================
# Course Endpoints
# ============================================================================

@router.get("/courses", response_model=CourseListResponse)
async def get_courses(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    is_active: Optional[bool] = Query(True, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get all courses with optional filters"""
    courses = service.get_all_courses(
        limit=limit,
        offset=offset,
        category=category,
        difficulty=difficulty,
        is_active=is_active,
        user_id=current_user["id"]
    )
    
    # Get total count
    total = service.db.query(LMSCourse).filter(
        LMSCourse.is_active == (is_active if is_active is not None else True)
    ).count()
    
    return {
        "courses": courses,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get course details with sections and resources"""
    course = service.get_course(course_id, current_user["id"])
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Create a new course (Admin only - add admin check if needed)"""
    course = service.create_course(course_data.model_dump())
    return course.to_dict(include_relations=True)


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_data: CourseUpdate,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Update a course (Admin only - add admin check if needed)"""
    course = service.update_course(course_id, course_data.model_dump(exclude_unset=True))
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return course.to_dict(include_relations=True)


@router.get("/courses/{course_id}/sections", response_model=SectionListResponse)
async def get_course_sections(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get sections for a course"""
    sections = service.get_course_sections(course_id)
    
    return {
        "sections": sections,
        "total": len(sections)
    }


@router.get("/courses/{course_id}/resources", response_model=ResourceListResponse)
async def get_course_resources(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get resources for a course"""
    resources = service.get_course_resources(course_id)
    
    return {
        "resources": resources,
        "total": len(resources)
    }


# ============================================================================
# User Course Endpoints
# ============================================================================

@router.post("/courses/{course_id}/enroll", response_model=UserCourseResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Enroll in a course"""
    try:
        user_course = service.enroll_in_course(current_user["id"], course_id)
        return user_course.to_dict(include_relations=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my-courses", response_model=UserCourseListResponse)
async def get_my_courses(
    status: Optional[str] = Query(None, description="Filter by status: all, in_progress, completed, not_started"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get user's courses"""
    courses = service.get_user_courses(
        user_id=current_user["id"],
        status=status,
        limit=limit,
        offset=offset
    )
    
    # Get total count
    query = service.db.query(LMSUserCourse).filter(LMSUserCourse.user_id == current_user["id"])
    if status:
        query = query.filter(LMSUserCourse.status == status)
    total = query.count()
    
    return {
        "courses": courses,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/my-courses/{course_id}", response_model=UserCourseResponse)
async def get_my_course(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get specific user course enrollment"""
    user_course = service.get_user_course(current_user["id"], course_id)
    
    if not user_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course enrollment not found"
        )
    
    return user_course


@router.put("/my-courses/{course_id}/progress", response_model=UserCourseResponse)
async def update_course_progress(
    course_id: int,
    progress_data: CourseProgressUpdate,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Update course progress"""
    user_course = service.update_course_progress(
        user_id=current_user["id"],
        course_id=course_id,
        progress=progress_data.progress
    )
    
    if not user_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course enrollment not found"
        )
    
    return user_course.to_dict(include_relations=True)


# ============================================================================
# Dashboard Endpoints
# ============================================================================

@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get dashboard stats"""
    dashboard = service.get_dashboard(current_user["id"])
    return dashboard


@router.get("/dashboard/weekly", response_model=WeeklyPerformanceListResponse)
async def get_weekly_performance(
    days: int = Query(7, ge=1, le=30, description="Number of days to retrieve"),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get weekly/daily performance data"""
    performance = service.get_weekly_performance(current_user["id"], days)
    
    return {
        "performance": performance,
        "total": len(performance)
    }


@router.get("/dashboard/domains", response_model=DomainPerformanceListResponse)
async def get_domain_performance(
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get domain-specific performance"""
    domains = service.get_domain_performance(current_user["id"])
    
    return {
        "domains": domains
    }


# ============================================================================
# Question/Answer Endpoints
# ============================================================================

@router.get("/courses/{course_id}/questions", response_model=QuestionListResponse)
async def get_course_questions(
    course_id: int,
    section_id: Optional[int] = Query(None, description="Filter by section"),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get questions for a course"""
    questions = service.get_course_questions(course_id, section_id)
    
    return {
        "questions": questions,
        "total": len(questions)
    }


@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get a specific question"""
    question = service.get_question(question_id)
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.post("/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Create a new question (Admin only - add admin check if needed)"""
    question = service.create_question(question_data.course_id, question_data.model_dump())
    return question.to_dict()


@router.post("/questions/{question_id}/answer", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    question_id: int,
    answer_data: AnswerSubmit,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Submit an answer to a question"""
    if answer_data.question_id != question_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question ID mismatch"
        )
    
    try:
        answer = service.submit_answer(
            user_id=current_user["id"],
            question_id=question_id,
            answer_text=answer_data.answer_text
        )
        return answer.to_dict(include_relations=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/answers/{answer_id}/evaluate", response_model=AnswerResponse)
async def evaluate_answer(
    answer_id: int,
    evaluation: AnswerEvaluate,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Evaluate an answer (manual or AI)"""
    answer = service.evaluate_answer(
        answer_id=answer_id,
        is_correct=evaluation.is_correct,
        points=evaluation.points,
        feedback=evaluation.feedback
    )
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    
    return answer.to_dict(include_relations=True)


@router.get("/my-answers", response_model=AnswerListResponse)
async def get_my_answers(
    question_id: Optional[int] = Query(None, description="Filter by question"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get user's answers"""
    answers = service.get_user_answers(
        user_id=current_user["id"],
        question_id=question_id,
        limit=limit,
        offset=offset
    )
    
    # Get total count
    query = service.db.query(LMSUserAnswer).filter(LMSUserAnswer.user_id == current_user["id"])
    if question_id:
        query = query.filter(LMSUserAnswer.question_id == question_id)
    total = query.count()
    
    return {
        "answers": answers,
        "total": total
    }


# ============================================================================
# Activity Endpoints
# ============================================================================

@router.get("/activities", response_model=ActivityListResponse)
async def get_activities(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get recent activities"""
    activities = service.get_recent_activities(current_user["id"], limit)
    
    return {
        "activities": activities,
        "total": len(activities)
    }


# ============================================================================
# Recommendation Endpoints
# ============================================================================

@router.get("/recommendations", response_model=RecommendationListResponse)
async def get_recommendations(
    limit: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get AI recommendations"""
    recommendations = service.get_recommendations(current_user["id"], limit)
    
    return {
        "recommendations": recommendations,
        "total": len(recommendations)
    }


@router.post("/recommendations/{recommendation_id}/dismiss")
async def dismiss_recommendation(
    recommendation_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Dismiss a recommendation"""
    success = service.dismiss_recommendation(recommendation_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return {"message": "Recommendation dismissed", "success": True}


# ============================================================================
# Deadline Endpoints
# ============================================================================

@router.get("/deadlines", response_model=DeadlineListResponse)
async def get_deadlines(
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get upcoming deadlines"""
    deadlines = service.get_upcoming_deadlines(current_user["id"], limit)
    
    return {
        "deadlines": deadlines,
        "total": len(deadlines)
    }


@router.post("/deadlines", response_model=DeadlineResponse, status_code=status.HTTP_201_CREATED)
async def create_deadline(
    deadline_data: DeadlineCreate,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Create a deadline"""
    deadline = service.create_deadline(current_user["id"], deadline_data.model_dump())
    return deadline.to_dict(include_relations=True)


@router.put("/deadlines/{deadline_id}/complete", response_model=DeadlineResponse)
async def complete_deadline(
    deadline_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Mark deadline as completed"""
    deadline = service.complete_deadline(deadline_id, current_user["id"])
    
    if not deadline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deadline not found"
        )
    
    return deadline.to_dict(include_relations=True)


# ============================================================================
# Certificate Endpoints
# ============================================================================

@router.get("/certificates", response_model=CertificateListResponse)
async def get_certificates(
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get user's certificates"""
    certificates = service.get_user_certificates(current_user["id"])
    
    return {
        "certificates": certificates,
        "total": len(certificates)
    }


@router.get("/certificates/{certificate_number}", response_model=CertificateResponse)
async def get_certificate_by_number(
    certificate_number: str,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Verify certificate by certificate number"""
    certificate = service.get_certificate_by_number(certificate_number)
    
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate not found"
        )
    
    return certificate


# ============================================================================
# Section Progress Endpoints
# ============================================================================

@router.get("/sections/{section_id}/progress", response_model=SectionProgressResponse)
async def get_section_progress(
    section_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get section progress"""
    progress = service.get_section_progress(current_user["id"], section_id)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section progress not found"
        )
    
    return progress


@router.put("/sections/{section_id}/progress", response_model=SectionProgressResponse)
async def update_section_progress(
    section_id: int,
    progress_data: SectionProgressUpdate,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Update section progress"""
    progress = service.update_section_progress(
        user_id=current_user["id"],
        section_id=section_id,
        completed_items=progress_data.completed_items,
        total_items=progress_data.total_items
    )
    
    return progress.to_dict(include_relations=True)
