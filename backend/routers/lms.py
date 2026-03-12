"""LMS Router - Learning Management System endpoints using SQLAlchemy ORM"""
import os
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

logger = logging.getLogger(__name__)

from dependencies.auth import get_current_user
from dependencies.subscription import require_lms_quota
from config.database_orm import get_db
from services.lms_service import LMSService
from models.orm import LMSCourse, LMSUserCourse, LMSUserAnswer, LMSRecommendation
from agents.Azel_agent import get_azel_agent
from agents.Seez_agent import get_seez_agent
from schemas.lms import (
    CourseCreate, CourseUpdate, CourseResponse, CourseListResponse,
    UserCourseEnroll, UserCourseResponse, UserCourseListResponse, CourseProgressUpdate,
    DashboardResponse,
    WeeklyPerformanceResponse, WeeklyPerformanceListResponse,
    DomainPerformanceResponse, DomainPerformanceListResponse,
    CoursePerformanceResponse,
    SectionPerformanceResponse,
    ActivityResponse, ActivityListResponse,
    QuestionCreate, QuestionResponse, QuestionListResponse,
    AnswerSubmit, AnswerResponse, AnswerListResponse, AnswerEvaluate,
    RecommendationResponse, RecommendationListResponse,
    DeadlineCreate, DeadlineResponse, DeadlineListResponse,
    CertificateResponse, CertificateListResponse,
    SectionResponse, SectionListResponse,
    ResourceResponse, ResourceListResponse,
    SectionProgressResponse, SectionProgressUpdate,
    ProcessCourseRequest,
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
    """Get sections for a course. Lazily seeds default level sections (idempotent).
    
    Note: backfill of orphan questions is handled by the POST azel/process-course
    endpoint to keep this GET side-effect free beyond idempotent seeding.
    """
    # Idempotent: creates Basic/Intermediate/Expert only if no sections exist
    service.ensure_default_level_sections(course_id)
    
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
    current_user: dict = Depends(require_lms_quota),
    service: LMSService = Depends(get_lms_service)
):
    """
    Enroll in a course.
    
    Security: require_lms_quota dependency atomically checks and increments
    the monthly course enrollment quota BEFORE this code runs.
    If quota is exceeded, a 403 is raised and enrollment never proceeds.
    """
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
    """Get user's courses. If no enrollments exist, checks for recommendations and generates them if needed."""
    user_id = current_user["id"]
    logger.info(f"[LMS] get_my_courses: Fetching courses for user_id={user_id}, status={status}, limit={limit}, offset={offset}")
    
    courses = service.get_user_courses(
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    # Derive total from the fetched list when within a single page, otherwise query
    total = len(courses)
    if total >= limit:
        # There may be more rows beyond this page -- run a count
        count_query = service.db.query(LMSUserCourse).filter(LMSUserCourse.user_id == user_id)
        if status:
            count_query = count_query.filter(LMSUserCourse.status == status)
        total = count_query.count()
    
    logger.info(f"[LMS] get_my_courses: Retrieved {len(courses)} courses, total={total}")
    
    # If no enrolled courses, check for recommendations and generate if needed
    if total == 0:
        logger.info(f"[LMS] get_my_courses: User has no enrolled courses. Checking for recommendations...")
        
        # Check if recommendations exist
        recommendation_count = service.db.query(LMSRecommendation).filter(
            LMSRecommendation.user_id == user_id,
            LMSRecommendation.is_dismissed == False
        ).count()
        
        logger.info(f"[LMS] get_my_courses: User has {recommendation_count} active recommendations")
        
        # If no recommendations, try to generate them (if feature enabled)
        if recommendation_count == 0:
            recommendation_enabled = os.environ.get('COURSE_RECOMMENDATION_ENABLED', 'true').lower() == 'true'
            if recommendation_enabled:
                logger.info(f"[LMS] get_my_courses: No recommendations found. Attempting to generate recommendations...")
                try:
                    from agents.Course_recommendation_agent import get_course_recommendation_agent
                    agent = get_course_recommendation_agent()
                    
                    if agent.is_available():
                        recommendation_limit = int(os.environ.get('COURSE_RECOMMENDATION_LIMIT', '5'))
                        result = agent.generate_course_recommendations(user_id, limit=recommendation_limit)
                        
                        if result.get('success'):
                            logger.info(f"[LMS] get_my_courses: Generated {result.get('recommendations_created', 0)} recommendations")
                        else:
                            logger.warning(f"[LMS] get_my_courses: Failed to generate recommendations: {result.get('error')}")
                    else:
                        logger.warning(f"[LMS] get_my_courses: Course Recommendation Agent not available")
                except Exception as e:
                    logger.error(f"[LMS] get_my_courses: Error generating recommendations: {e}", exc_info=True)
            else:
                logger.info(f"[LMS] get_my_courses: Course recommendation feature is disabled")
    
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

@router.get("/dashboard/all")
async def get_dashboard_all(
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get ALL dashboard data in a single request.
    
    Returns courses, dashboard stats, weekly performance, domain performance,
    activities, recommendations, deadlines, and certificates in one payload.
    This replaces the 8 parallel API calls the frontend used to make.
    """
    return service.get_dashboard_all(current_user["id"])


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


@router.get("/dashboard/courses/{course_id}", response_model=CoursePerformanceResponse)
async def get_course_performance(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Get course-specific performance stats"""
    performance = service.get_course_performance(current_user["id"], course_id)
    
    if not performance:
        # Return empty stats if no performance record exists
        return {
            "id": 0,
            "user_id": current_user["id"],
            "course_id": course_id,
            "questions_answered": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "accuracy_percentage": 0.0,
            "total_points_earned": 0,
            "last_activity_date": None,
            "course_title": None,
            "course_icon": None,
            "course_category": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    
    return performance


@router.get("/courses/{course_id}/section-performance", response_model=SectionPerformanceResponse)
async def get_section_performance_summary(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service),
):
    """
    Get per-section evaluation metrics for the authenticated user in a course.
    Returns accuracy, questions_answered, correct_answers, and points for each
    section (Basic / Intermediate / Expert).
    """
    user_id = current_user.get("id") or current_user.get("uid")
    if not service.is_user_enrolled(user_id, course_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be enrolled in this course to view section performance.",
        )
    summary = service.get_section_performance_summary(user_id, course_id)
    return {"sections": summary}


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


@router.post("/generate-recommendations")
async def generate_recommendations(
    limit: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service)
):
    """Regenerate AI course recommendations for the current user.

    Dismisses all existing (non-dismissed) recommendations, then runs the
    CourseRecommendationAgent with the latest user profile + Zed context to
    produce fresh, personalised recommendations.
    """
    user_id = current_user["id"]
    logger.info(f"[LMS] generate-recommendations: user_id={user_id}, limit={limit}")

    # 1. Dismiss existing non-dismissed recommendations so the agent creates fresh ones
    service.dismiss_all_recommendations(user_id)

    # 2. Invalidate dashboard cache so the next load reflects new recs
    from config.cache import invalidate_dashboard_cache
    invalidate_dashboard_cache(user_id)

    # 3. Trigger the Course Recommendation Agent
    recommendation_enabled = os.environ.get('COURSE_RECOMMENDATION_ENABLED', 'true').lower() == 'true'
    if not recommendation_enabled:
        return {"success": False, "error": "Course recommendation feature is disabled", "recommendations": []}

    try:
        from agents.Course_recommendation_agent import get_course_recommendation_agent
        agent = get_course_recommendation_agent()

        if not agent.is_available():
            return {"success": False, "error": "Course Recommendation Agent not available", "recommendations": []}

        result = agent.generate_course_recommendations(user_id, limit=limit)

        if result.get('success'):
            logger.info(f"[LMS] generate-recommendations: Created {result.get('recommendations_created', 0)} recs")
        else:
            logger.warning(f"[LMS] generate-recommendations: Agent returned: {result.get('error')}")

        # Return fresh recommendations
        fresh_recs = service.get_recommendations(user_id, limit=limit)
        return {
            "success": result.get('success', False),
            "recommendations_created": result.get('recommendations_created', 0),
            "recommendations": fresh_recs,
            "total": len(fresh_recs),
        }
    except Exception as e:
        logger.error(f"[LMS] generate-recommendations error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


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


# ============================================================================
# Azel Agent Endpoints
# ============================================================================

@router.post("/azel/process-course/{course_id}")
async def trigger_azel_agent(
    course_id: int,
    body: Optional[ProcessCourseRequest] = None,
    current_user: dict = Depends(get_current_user),
    service: LMSService = Depends(get_lms_service),
):
    """
    Trigger Azel agent to process course context and generate questions
    scoped to a specific section (level).
    
    Body (optional):
        section_id: int – section to generate questions for.
                     If omitted, falls back to the first (Basic) section.
    
    This endpoint:
    1. Verifies the user is enrolled in the course
    2. Ensures the course has default level sections
    3. Backfills any orphan questions into the default section
    4. Retrieves Zed context for the user
    5. Extracts highlighted topics of interest
    6. Performs web searches
    7. Saves URLs to database
    8. Creates Qdrant knowledge base (30-minute TTL)
    9. Generates questions with detailed answers (difficulty matches section)
    10. Saves questions to database with section_id set
    
    Note: This is a long-running operation (can take 30-120 seconds)
    """
    from models.orm.lms_course_section import LMSCourseSection
    
    try:
        # Verify course exists
        course = service.db.query(LMSCourse).filter(LMSCourse.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # --- Security: user must be enrolled in the course ---
        user_id = current_user.get('id') or current_user.get('uid')
        if not service.is_user_enrolled(user_id, course_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled in this course to generate questions"
            )
        
        # --- Seed sections + backfill orphan questions (POST is mutation-safe) ---
        sections = service.ensure_default_level_sections(course_id)
        service.backfill_orphan_questions(course_id)
        
        section_id = body.section_id if body else None
        
        if section_id:
            # Validate the section belongs to this course
            section = service.db.query(LMSCourseSection).filter(
                LMSCourseSection.id == section_id,
                LMSCourseSection.course_id == course_id
            ).first()
            if not section:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Section {section_id} does not belong to course {course_id}"
                )
        else:
            # Default to the first section (Basic)
            section = sections[0] if sections else None
            section_id = section.id if section else None
        
        section_title = section.title if section else "Basic"
        
        # Get Azel agent and check availability
        azel_agent = get_azel_agent()
        
        if not azel_agent.is_available():
            error_details = []
            if not azel_agent.qdrant_available:
                error_details.append("Qdrant vector database is not available")
            if not azel_agent.openai_available:
                error_details.append("OpenAI API is not available")
            
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Azel agent is not available. {'; '.join(error_details)}. Please check your configuration."
            )
        
        # Process course context
        logger.info(f"Starting Azel agent processing for user_id={user_id}, course_id={course_id}, section_id={section_id} ({section_title})")
        
        result = azel_agent.process_course_context(
            user_id=user_id,
            course_id=course_id,
            section_id=section_id,
            level=section_title,
            course_title=course.title,
        )
        
        # Always return result, even if not fully successful
        # This allows frontend to show partial results
        if not result.get('success'):
            logger.warning(f"Azel agent processing completed with errors: {result.get('error')}")
            return {
                "message": "Course context processing completed with errors",
                "result": result,
                "success": False
            }
        
        logger.info(f"Azel agent processing completed successfully for user_id={user_id}, course_id={course_id}, section_id={section_id}")
        return {
            "message": "Course context processed successfully",
            "result": result,
            "success": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Log full details server-side; expose only a safe message to the client
        logger.error(f"Error in trigger_azel_agent: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the course. Please try again later."
        )


# ============================================================================
# Seez Agent Endpoints
# ============================================================================

@router.post("/seez/evaluate-course/{course_id}")
async def trigger_seez_agent_course(
    course_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger Seez agent to evaluate all unevaluated answers for a course
    
    This endpoint:
    1. Retrieves all unevaluated answers for the user in the specified course
    2. Evaluates each answer leniently (0-10 score)
    3. Updates all answers in database
    4. Calculates average score using simple averaging
    5. Updates course performance stats
    """
    try:
        # Verify course exists
        course = db.query(LMSCourse).filter(LMSCourse.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
        
        # Get Seez agent
        seez_agent = get_seez_agent()
        
        if not seez_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Seez agent is not available. Please check OpenAI configuration."
            )
        
        # Get user ID
        user_id = current_user.get('id') or current_user.get('uid')
        
        # Evaluate all course answers
        result = seez_agent.evaluate_course_answers(
            user_id=user_id,
            course_id=course_id,
            db_session=db
        )
        
        # Handle case where no unevaluated answers are found (not an error)
        if not result.get('success'):
            error_msg = result.get('error', 'Failed to evaluate answers')
            if 'No unevaluated answers found' in error_msg:
                # Return success response with info message
                return {
                    "message": "No unevaluated answers found for this course",
                    "result": result
                }
            else:
                # Actual error occurred
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_msg
                )
        
        return {
            "message": "Answers evaluated successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trigger_seez_agent_course: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/seez/evaluate-answers")
async def trigger_seez_agent_batch(
    answer_ids: List[int],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger Seez agent to evaluate specific answers by IDs
    
    This endpoint:
    1. Evaluates specified answers leniently (0-10 score)
    2. Updates all answers in database
    3. Calculates average score using simple averaging
    """
    try:
        if not answer_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No answer IDs provided"
            )
        
        # Get Seez agent
        seez_agent = get_seez_agent()
        
        if not seez_agent.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Seez agent is not available. Please check OpenAI configuration."
            )
        
        # Evaluate answers batch
        result = seez_agent.evaluate_answers_batch(
            answer_ids=answer_ids,
            db_session=db
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get('error', 'Failed to evaluate answers')
            )
        
        return {
            "message": "Answers evaluated successfully",
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in trigger_seez_agent_batch: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
