"""LMS Service - Business logic for Learning Management System using SQLAlchemy ORM"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy import and_, or_, desc, func, Integer
from sqlalchemy.orm import Session, joinedload

# Import all LMS ORM models
from models.orm import (
    LMSCourse, LMSDomain, LMSCourseSection, LMSCourseResource,
    LMSQuestion, LMSUserCourse, LMSUserSectionProgress, LMSUserAnswer,
    LMSUserDomainPerformance, LMSUserCoursePerformance, LMSDashboard, LMSWeeklyPerformance,
    LMSActivity, LMSRecommendation, LMSDeadline, LMSCertificate
)

# Import cache functions
from config.cache import get_cached_dashboard, cache_dashboard, invalidate_dashboard_cache

logger = logging.getLogger(__name__)


class LMSService:
    """Service class for LMS operations using SQLAlchemy ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Course Operations
    # ========================================================================
    
    def get_all_courses(
        self,
        limit: int = 50,
        offset: int = 0,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_active: Optional[bool] = True,
        user_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all courses with optional filters"""
        query = self.db.query(LMSCourse)
        
        if is_active is not None:
            query = query.filter(LMSCourse.is_active == is_active)
        if category:
            query = query.filter(LMSCourse.category == category)
        if difficulty:
            query = query.filter(LMSCourse.difficulty == difficulty)
        
        courses = query.order_by(desc(LMSCourse.created_at)).limit(limit).offset(offset).all()
        
        # Bulk query user courses to avoid N+1 problem
        user_courses = {}
        if user_id and courses:
            course_ids = [c.id for c in courses]
            user_courses_query = (
                self.db.query(LMSUserCourse)
                .filter(
                    and_(
                        LMSUserCourse.user_id == user_id,
                        LMSUserCourse.course_id.in_(course_ids)
                    )
                )
                .all()
            )
            user_courses = {uc.course_id: uc for uc in user_courses_query}
        
        results = []
        for course in courses:
            data = course.to_dict(include_relations=True)
            
            # Add user progress if user_id provided
            if user_id:
                uc = user_courses.get(course.id)
                if uc:
                    data['progress'] = uc.progress
                    data['status'] = uc.status
                else:
                    data['progress'] = 0
                    data['status'] = 'not_started'
            
            results.append(data)
        
        return results
    
    def get_course(self, course_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get a single course with sections and resources"""
        course = (
            self.db.query(LMSCourse)
            .options(
                joinedload(LMSCourse.sections),
                joinedload(LMSCourse.resources),
                joinedload(LMSCourse.questions)
            )
            .filter(LMSCourse.id == course_id)
            .first()
        )
        
        if not course:
            return None
        
        data = course.to_dict(include_relations=True)
        
        # Add sections
        data['sections'] = [section.to_dict() for section in course.sections]
        
        # Add resources
        data['resources'] = [resource.to_dict() for resource in course.resources]
        
        # Add user progress if user_id provided
        if user_id:
            user_course = (
                self.db.query(LMSUserCourse)
                .filter(
                    and_(
                        LMSUserCourse.user_id == user_id,
                        LMSUserCourse.course_id == course_id
                    )
                )
                .first()
            )
            if user_course:
                data['progress'] = user_course.progress
                data['status'] = user_course.status
                data['started_at'] = user_course.started_at.isoformat() if user_course.started_at else None
                data['completed_at'] = user_course.completed_at.isoformat() if user_course.completed_at else None
        
        return data
    
    def create_course(self, course_data: dict) -> LMSCourse:
        """Create a new course"""
        course = LMSCourse(
            title=course_data['title'],
            description=course_data.get('description'),
            icon=course_data.get('icon'),
            lessons=course_data.get('lessons', 0),
            duration=course_data.get('duration'),
            category=course_data.get('category'),
            difficulty=course_data.get('difficulty', 'beginner'),
            is_active=course_data.get('is_active', True)
        )
        
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def update_course(self, course_id: int, course_data: dict) -> Optional[LMSCourse]:
        """Update a course"""
        course = self.db.query(LMSCourse).filter(LMSCourse.id == course_id).first()
        
        if not course:
            return None
        
        # Update fields
        for key, value in course_data.items():
            if value is not None and hasattr(course, key):
                setattr(course, key, value)
        
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def generate_course_from_idea(self, course_idea: dict) -> Optional[LMSCourse]:
        """
        Create a new course from a course idea (e.g., from LLM generation)
        
        Args:
            course_idea: Dictionary with course details (title, description, category, difficulty, etc.)
            
        Returns:
            Created LMSCourse or None if creation fails
        """
        try:
            # Generate icon from title (first 2 characters)
            title = course_idea.get('title', 'Untitled Course')
            icon = title[:2].upper() if len(title) >= 2 else '📚'
            
            course_data = {
                'title': title,
                'description': course_idea.get('description', ''),
                'icon': icon,
                'lessons': course_idea.get('estimated_lessons', course_idea.get('lessons', 0)),
                'duration': course_idea.get('duration'),
                'category': course_idea.get('category', 'General'),
                'difficulty': course_idea.get('difficulty', 'beginner'),
                'is_active': course_idea.get('is_active', True)
            }
            
            return self.create_course(course_data)
            
        except Exception as e:
            logger.error(f"Failed to generate course from idea: {e}", exc_info=True)
            return None
    
    def find_similar_courses(self, title: str, category: Optional[str] = None, threshold: float = 0.7) -> List[LMSCourse]:
        """
        Find existing courses similar to given title and category
        
        Args:
            title: Course title to match
            category: Course category to match (optional)
            threshold: Similarity threshold (0.0 to 1.0, default: 0.7)
            
        Returns:
            List of similar LMSCourse objects
        """
        try:
            from difflib import SequenceMatcher
            
            def calculate_similarity(str1: str, str2: str) -> float:
                return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
            
            # Get all active courses
            query = self.db.query(LMSCourse).filter(LMSCourse.is_active == True)
            
            if category:
                # First try exact category match
                category_matches = query.filter(LMSCourse.category == category).all()
            else:
                category_matches = query.all()
            
            similar_courses = []
            
            for course in category_matches:
                # Calculate title similarity
                title_score = calculate_similarity(title, course.title)
                
                # Calculate category similarity if category provided
                category_score = 0.0
                if category and course.category:
                    category_score = calculate_similarity(category, course.category)
                
                # Combined score (title weighted more)
                combined_score = (title_score * 0.7) + (category_score * 0.3)
                
                if combined_score >= threshold:
                    similar_courses.append(course)
            
            # Sort by similarity (highest first)
            similar_courses.sort(
                key=lambda c: calculate_similarity(title, c.title),
                reverse=True
            )
            
            return similar_courses
            
        except Exception as e:
            logger.error(f"Error finding similar courses: {e}", exc_info=True)
            return []
    
    def get_course_sections(self, course_id: int) -> List[Dict[str, Any]]:
        """Get sections for a course"""
        sections = (
            self.db.query(LMSCourseSection)
            .filter(LMSCourseSection.course_id == course_id)
            .order_by(LMSCourseSection.order_index)
            .all()
        )
        
        return [section.to_dict() for section in sections]
    
    def get_course_resources(self, course_id: int) -> List[Dict[str, Any]]:
        """Get resources for a course"""
        resources = (
            self.db.query(LMSCourseResource)
            .filter(LMSCourseResource.course_id == course_id)
            .order_by(LMSCourseResource.order_index)
            .all()
        )
        
        return [resource.to_dict() for resource in resources]
    
    # ========================================================================
    # User Course Operations
    # ========================================================================
    
    def enroll_in_course(self, user_id: int, course_id: int) -> Optional[LMSUserCourse]:
        """Enroll user in a course. Maximum 5 courses allowed per user."""
        # Check if course exists
        course = self.db.query(LMSCourse).filter(LMSCourse.id == course_id).first()
        if not course:
            raise ValueError("Course not found")
        if not course.is_active:
            raise ValueError("Course is not active")
        
        # Check if already enrolled
        existing = (
            self.db.query(LMSUserCourse)
            .filter(
                and_(
                    LMSUserCourse.user_id == user_id,
                    LMSUserCourse.course_id == course_id
                )
            )
            .first()
        )
        
        if existing:
            return existing  # Already enrolled
        
        # Check enrollment limit (max 5 courses)
        enrollment_count = (
            self.db.query(LMSUserCourse)
            .filter(LMSUserCourse.user_id == user_id)
            .count()
        )
        
        if enrollment_count >= 5:
            raise ValueError(f"You have reached the maximum enrollment limit of 5 courses. Please complete or drop a course before enrolling in a new one.")
        
        # Create enrollment
        user_course = LMSUserCourse(
            user_id=user_id,
            course_id=course_id,
            progress=0,
            status='in_progress',
            started_at=datetime.now()
        )
        
        self.db.add(user_course)
        self.db.commit()
        self.db.refresh(user_course)
        
        # Log activity
        self.log_activity(
            user_id=user_id,
            activity_type='enrollment',
            title=f'Enrolled in {course.title}',
            course_id=course_id,
            icon=course.icon
        )
        
        return user_course
    
    def get_user_courses(
        self,
        user_id: int,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's courses with optional status filter"""
        query = (
            self.db.query(LMSUserCourse)
            .options(joinedload(LMSUserCourse.course))
            .join(LMSCourse)
            .filter(LMSUserCourse.user_id == user_id)
        )
        
        if status:
            query = query.filter(LMSUserCourse.status == status)
        
        user_courses = (
            query.order_by(desc(LMSUserCourse.last_accessed_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        results = []
        for uc in user_courses:
            data = uc.to_dict(include_relations=True)
            results.append(data)
        
        return results
    
    def get_user_course(self, user_id: int, course_id: int) -> Optional[Dict[str, Any]]:
        """Get specific user course enrollment"""
        user_course = (
            self.db.query(LMSUserCourse)
            .join(LMSCourse)
            .filter(
                and_(
                    LMSUserCourse.user_id == user_id,
                    LMSUserCourse.course_id == course_id
                )
            )
            .first()
        )
        
        if not user_course:
            return None
        
        return user_course.to_dict(include_relations=True)
    
    def update_course_progress(
        self,
        user_id: int,
        course_id: int,
        progress: int
    ) -> Optional[LMSUserCourse]:
        """Update course progress (0-100)"""
        user_course = (
            self.db.query(LMSUserCourse)
            .filter(
                and_(
                    LMSUserCourse.user_id == user_id,
                    LMSUserCourse.course_id == course_id
                )
            )
            .first()
        )
        
        if not user_course:
            return None
        
        # Update progress
        user_course.progress = max(0, min(100, progress))
        user_course.status = 'completed' if progress >= 100 else 'in_progress'
        user_course.last_accessed_at = datetime.now()
        
        # Set completed_at if progress is 100%
        if progress >= 100 and not user_course.completed_at:
            user_course.completed_at = datetime.now()
            
            # Issue certificate
            course = self.db.query(LMSCourse).filter(LMSCourse.id == course_id).first()
            if course:
                self.issue_certificate(user_id, course_id, f"Certificate of Completion: {course.title}")
                
                # Log activity
                self.log_activity(
                    user_id=user_id,
                    activity_type='course_complete',
                    title=f'Completed {course.title}',
                    course_id=course_id,
                    icon=course.icon
                )
        
        self.db.commit()
        self.db.refresh(user_course)
        return user_course
    
    # ========================================================================
    # Dashboard Operations
    # ========================================================================
    
    def get_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get or create dashboard stats for user with Redis caching"""
        # Check cache first (returns None if Redis unavailable)
        cached = get_cached_dashboard(user_id)
        if cached:
            return cached
        
        # Calculate if not cached or Redis unavailable
        dashboard = (
            self.db.query(LMSDashboard)
            .filter(LMSDashboard.user_id == user_id)
            .first()
        )
        
        if not dashboard:
            # Create new dashboard
            dashboard = LMSDashboard(
                user_id=user_id,
                total_questions=0,
                correct_answers=0,
                wrong_answers=0,
                overall_accuracy=0.0,
                day_streak=0
            )
            self.db.add(dashboard)
            self.db.commit()
            self.db.refresh(dashboard)
        else:
            # Recalculate stats from answers (ensure accuracy)
            self._recalculate_dashboard_stats(user_id)
            self.db.refresh(dashboard)
        
        result = dashboard.to_dict()
        
        # Cache result (silently fails if Redis unavailable)
        cache_dashboard(user_id, result, ttl=300)
        
        return result
    
    def _recalculate_dashboard_stats(self, user_id: int):
        """Recalculate dashboard stats from user answers"""
        # Aggregate from lms_user_answers
        stats = (
            self.db.query(
                func.count(LMSUserAnswer.id).label('total'),
                func.sum(func.cast(LMSUserAnswer.is_correct, Integer)).label('correct'),
                func.count(LMSUserAnswer.id).label('total_count')
            )
            .filter(
                and_(
                    LMSUserAnswer.user_id == user_id,
                    LMSUserAnswer.is_correct.isnot(None)  # Only evaluated answers
                )
            )
            .first()
        )
        
        total = stats.total or 0
        correct = stats.correct or 0
        wrong = total - correct
        
        # Calculate accuracy
        accuracy = 0.0
        if total > 0:
            accuracy = round((correct / total) * 100, 2)
        
        # Get day streak
        streak = self._calculate_day_streak(user_id)
        
        # Get last activity date
        last_activity = (
            self.db.query(LMSActivity)
            .filter(LMSActivity.user_id == user_id)
            .order_by(desc(LMSActivity.created_at))
            .first()
        )
        last_activity_date = last_activity.created_at.date() if last_activity else None
        
        # Update dashboard
        dashboard = (
            self.db.query(LMSDashboard)
            .filter(LMSDashboard.user_id == user_id)
            .first()
        )
        
        if dashboard:
            dashboard.total_questions = total
            dashboard.correct_answers = correct
            dashboard.wrong_answers = wrong
            dashboard.overall_accuracy = accuracy
            dashboard.day_streak = streak
            dashboard.last_activity_date = last_activity_date
            self.db.commit()
        else:
            dashboard = LMSDashboard(
                user_id=user_id,
                total_questions=total,
                correct_answers=correct,
                wrong_answers=wrong,
                overall_accuracy=accuracy,
                day_streak=streak,
                last_activity_date=last_activity_date
            )
            self.db.add(dashboard)
            self.db.commit()
    
    def _calculate_day_streak(self, user_id: int) -> int:
        """Calculate consecutive days with learning activity using SQL"""
        today = date.today()
        
        # Get unique activity dates for last 365 days (reasonable limit)
        activity_dates = self.db.query(
            func.distinct(func.date(LMSActivity.created_at)).label('activity_date')
        ).filter(
            and_(
                LMSActivity.user_id == user_id,
                func.date(LMSActivity.created_at) >= today - timedelta(days=365)
            )
        ).order_by(desc('activity_date')).all()
        
        if not activity_dates:
            return 0
        
        # Convert to set of dates
        dates_set = {row.activity_date for row in activity_dates}
        
        # Calculate streak from today backwards
        streak = 0
        current_date = today
        
        while current_date in dates_set:
            streak += 1
            current_date -= timedelta(days=1)
            # Safety limit to prevent infinite loop
            if streak > 365:
                break
        
        return streak
    
    def update_dashboard_stats(self, user_id: int, stats: dict):
        """Update dashboard stats (called after answer submission)"""
        self._recalculate_dashboard_stats(user_id)
    
    # ========================================================================
    # Performance Operations
    # ========================================================================
    
    def get_weekly_performance(
        self,
        user_id: int,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get weekly/daily performance data"""
        start_date = date.today() - timedelta(days=days)
        
        performance = (
            self.db.query(LMSWeeklyPerformance)
            .filter(
                and_(
                    LMSWeeklyPerformance.user_id == user_id,
                    LMSWeeklyPerformance.date >= start_date
                )
            )
            .order_by(desc(LMSWeeklyPerformance.date))
            .all()
        )
        
        return [p.to_dict() for p in performance]
    
    def record_daily_performance(
        self,
        user_id: int,
        record_date: date,
        questions_answered: int = 0,
        correct_answers: int = 0,
        wrong_answers: int = 0,
        study_time_minutes: int = 0
    ) -> LMSWeeklyPerformance:
        """Record or update daily performance"""
        performance = (
            self.db.query(LMSWeeklyPerformance)
            .filter(
                and_(
                    LMSWeeklyPerformance.user_id == user_id,
                    LMSWeeklyPerformance.date == record_date
                )
            )
            .first()
        )
        
        if performance:
            # Update existing
            performance.questions_answered += questions_answered
            performance.correct_answers += correct_answers
            performance.wrong_answers += wrong_answers
            performance.study_time_minutes += study_time_minutes
        else:
            # Create new
            performance = LMSWeeklyPerformance(
                user_id=user_id,
                date=record_date,
                questions_answered=questions_answered,
                correct_answers=correct_answers,
                wrong_answers=wrong_answers,
                study_time_minutes=study_time_minutes
            )
            self.db.add(performance)
        
        self.db.commit()
        self.db.refresh(performance)
        return performance
    
    def get_domain_performance(self, user_id: int) -> List[Dict[str, Any]]:
        """Get performance by domain"""
        performances = (
            self.db.query(LMSUserDomainPerformance)
            .join(LMSDomain)
            .filter(LMSUserDomainPerformance.user_id == user_id)
            .order_by(desc(LMSUserDomainPerformance.accuracy_percentage))
            .all()
        )
        
        return [p.to_dict(include_relations=True) for p in performances]
    
    def get_course_performance(self, user_id: int, course_id: int) -> Optional[Dict[str, Any]]:
        """Get course-specific performance stats"""
        performance = (
            self.db.query(LMSUserCoursePerformance)
            .filter(
                and_(
                    LMSUserCoursePerformance.user_id == user_id,
                    LMSUserCoursePerformance.course_id == course_id
                )
            )
            .first()
        )
        
        if not performance:
            return None
        
        return performance.to_dict(include_relations=True)
    
    # ========================================================================
    # Question/Answer Operations
    # ========================================================================
    
    def get_course_questions(
        self,
        course_id: int,
        section_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get questions for a course or section"""
        query = self.db.query(LMSQuestion).filter(LMSQuestion.course_id == course_id)
        
        if section_id:
            query = query.filter(LMSQuestion.section_id == section_id)
        
        questions = query.order_by(LMSQuestion.order_index).all()
        
        return [q.to_dict() for q in questions]
    
    def get_question(self, question_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific question"""
        question = (
            self.db.query(LMSQuestion)
            .filter(LMSQuestion.id == question_id)
            .first()
        )
        
        if not question:
            return None
        
        return question.to_dict()
    
    def create_question(self, course_id: int, question_data: dict) -> LMSQuestion:
        """Create a new question"""
        question = LMSQuestion(
            course_id=course_id,
            section_id=question_data.get('section_id'),
            question_text=question_data['question_text'],
            question_type=question_data.get('question_type', 'text'),
            options=question_data.get('options'),
            correct_answer=question_data.get('correct_answer'),
            points=question_data.get('points', 1),
            order_index=question_data.get('order_index', 0)
        )
        
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question
    
    def submit_answer(
        self,
        user_id: int,
        question_id: int,
        answer_text: str
    ) -> LMSUserAnswer:
        """Submit an answer to a question"""
        # Check if question exists
        question = self.db.query(LMSQuestion).filter(LMSQuestion.id == question_id).first()
        if not question:
            raise ValueError("Question not found")
        
        # Create answer
        answer = LMSUserAnswer(
            user_id=user_id,
            question_id=question_id,
            answer_text=answer_text,
            submitted_at=datetime.now()
        )
        
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)
        
        # Log activity
        course = self.db.query(LMSCourse).filter(LMSCourse.id == question.course_id).first()
        if course:
            self.log_activity(
                user_id=user_id,
                activity_type='answer_submit',
                title=f'Submitted answer for {course.title}',
                course_id=question.course_id,
                icon=course.icon
            )
        
        return answer
    
    def evaluate_answer(
        self,
        answer_id: int,
        is_correct: bool,
        points: int = 0,
        feedback: Optional[str] = None
    ) -> Optional[LMSUserAnswer]:
        """Evaluate an answer (manual or AI)"""
        answer = (
            self.db.query(LMSUserAnswer)
            .filter(LMSUserAnswer.id == answer_id)
            .first()
        )
        
        if not answer:
            return None
        
        # Update answer
        answer.is_correct = is_correct
        answer.points_earned = points
        answer.feedback = feedback
        answer.evaluated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(answer)
        
        # Update dashboard stats
        self._recalculate_dashboard_stats(answer.user_id)
        
        # Update course performance
        question = self.db.query(LMSQuestion).filter(LMSQuestion.id == answer.question_id).first()
        if question:
            # Update course-specific performance
            self._update_course_performance(answer.user_id, question.course_id, is_correct, points)
            
            # Get course category as domain (or implement proper domain mapping)
            course = self.db.query(LMSCourse).filter(LMSCourse.id == question.course_id).first()
            if course and course.category:
                # Find or create domain
                domain = (
                    self.db.query(LMSDomain)
                    .filter(LMSDomain.name == course.category)
                    .first()
                )
                
                if domain:
                    self._update_domain_performance(answer.user_id, domain.id, is_correct)
        
        # Record daily performance
        today = date.today()
        self.record_daily_performance(
            user_id=answer.user_id,
            record_date=today,
            questions_answered=1,
            correct_answers=1 if is_correct else 0,
            wrong_answers=0 if is_correct else 1
        )
        
        return answer
    
    def _update_course_performance(self, user_id: int, course_id: int, is_correct: bool, points: int = 0):
        """Update course performance after answer evaluation"""
        performance = (
            self.db.query(LMSUserCoursePerformance)
            .filter(
                and_(
                    LMSUserCoursePerformance.user_id == user_id,
                    LMSUserCoursePerformance.course_id == course_id
                )
            )
            .first()
        )
        
        if performance:
            # Update existing
            performance.questions_answered += 1
            if is_correct:
                performance.correct_answers += 1
                performance.total_points_earned += points
            else:
                performance.wrong_answers += 1
            
            # Recalculate accuracy
            if performance.questions_answered > 0:
                performance.accuracy_percentage = round(
                    (performance.correct_answers / performance.questions_answered) * 100,
                    2
                )
            performance.last_activity_date = date.today()
        else:
            # Create new
            accuracy = 100.0 if is_correct else 0.0
            performance = LMSUserCoursePerformance(
                user_id=user_id,
                course_id=course_id,
                questions_answered=1,
                correct_answers=1 if is_correct else 0,
                wrong_answers=0 if is_correct else 1,
                accuracy_percentage=accuracy,
                total_points_earned=points if is_correct else 0,
                last_activity_date=date.today()
            )
            self.db.add(performance)
        
        self.db.commit()
    
    def _update_domain_performance(self, user_id: int, domain_id: int, is_correct: bool):
        """Update domain performance after answer evaluation"""
        performance = (
            self.db.query(LMSUserDomainPerformance)
            .filter(
                and_(
                    LMSUserDomainPerformance.user_id == user_id,
                    LMSUserDomainPerformance.domain_id == domain_id
                )
            )
            .first()
        )
        
        if performance:
            # Update existing
            performance.questions_answered += 1
            if is_correct:
                performance.correct_answers += 1
            
            # Recalculate accuracy
            if performance.questions_answered > 0:
                performance.accuracy_percentage = round(
                    (performance.correct_answers / performance.questions_answered) * 100,
                    2
                )
        else:
            # Create new
            accuracy = 100.0 if is_correct else 0.0
            performance = LMSUserDomainPerformance(
                user_id=user_id,
                domain_id=domain_id,
                questions_answered=1,
                correct_answers=1 if is_correct else 0,
                accuracy_percentage=accuracy
            )
            self.db.add(performance)
        
        self.db.commit()
    
    def get_user_answers(
        self,
        user_id: int,
        question_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's answers"""
        query = (
            self.db.query(LMSUserAnswer)
            .join(LMSQuestion)
            .filter(LMSUserAnswer.user_id == user_id)
        )
        
        if question_id:
            query = query.filter(LMSUserAnswer.question_id == question_id)
        
        answers = (
            query.order_by(desc(LMSUserAnswer.submitted_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [a.to_dict(include_relations=True) for a in answers]
    
    # ========================================================================
    # Activity Operations
    # ========================================================================
    
    def log_activity(
        self,
        user_id: int,
        activity_type: str,
        title: str,
        course_id: Optional[int] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None
    ) -> LMSActivity:
        """Log a learning activity"""
        activity = LMSActivity(
            user_id=user_id,
            course_id=course_id,
            activity_type=activity_type,
            title=title,
            description=description,
            icon=icon
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        # Update dashboard last_activity_date
        dashboard = (
            self.db.query(LMSDashboard)
            .filter(LMSDashboard.user_id == user_id)
            .first()
        )
        
        if dashboard:
            dashboard.last_activity_date = date.today()
            dashboard.day_streak = self._calculate_day_streak(user_id)
            self.db.commit()
        
        # Invalidate dashboard cache (silently fails if Redis unavailable)
        invalidate_dashboard_cache(user_id)
        
        return activity
    
    def get_recent_activities(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent activities for user"""
        activities = (
            self.db.query(LMSActivity)
            .join(LMSCourse, isouter=True)
            .filter(LMSActivity.user_id == user_id)
            .order_by(desc(LMSActivity.created_at))
            .limit(limit)
            .all()
        )
        
        results = []
        for activity in activities:
            data = activity.to_dict(include_relations=True)
            if activity.course:
                data['course_title'] = activity.course.title
                data['course_icon'] = activity.course.icon
            results.append(data)
        
        return results
    
    # ========================================================================
    # Recommendation Operations
    # ========================================================================
    
    def get_recommendations(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get AI recommendations for user"""
        recommendations = (
            self.db.query(LMSRecommendation)
            .join(LMSCourse)
            .filter(
                and_(
                    LMSRecommendation.user_id == user_id,
                    LMSRecommendation.is_dismissed == False
                )
            )
            .order_by(desc(LMSRecommendation.priority))
            .limit(limit)
            .all()
        )
        
        return [r.to_dict(include_relations=True) for r in recommendations]
    
    def create_recommendation(
        self,
        user_id: int,
        course_id: int,
        reason: str,
        priority: int = 0
    ) -> LMSRecommendation:
        """Create a recommendation"""
        recommendation = LMSRecommendation(
            user_id=user_id,
            course_id=course_id,
            reason=reason,
            priority=priority
        )
        
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
    
    def dismiss_recommendation(self, recommendation_id: int, user_id: int) -> bool:
        """Dismiss a recommendation"""
        recommendation = (
            self.db.query(LMSRecommendation)
            .filter(
                and_(
                    LMSRecommendation.id == recommendation_id,
                    LMSRecommendation.user_id == user_id
                )
            )
            .first()
        )
        
        if not recommendation:
            return False
        
        recommendation.is_dismissed = True
        self.db.commit()
        return True
    
    # ========================================================================
    # Deadline Operations
    # ========================================================================
    
    def get_upcoming_deadlines(
        self,
        user_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get upcoming deadlines for user"""
        deadlines = (
            self.db.query(LMSDeadline)
            .join(LMSCourse, isouter=True)
            .filter(
                and_(
                    LMSDeadline.user_id == user_id,
                    LMSDeadline.is_completed == False,
                    LMSDeadline.due_date >= datetime.now()
                )
            )
            .order_by(LMSDeadline.due_date)
            .limit(limit)
            .all()
        )
        
        results = []
        for deadline in deadlines:
            data = deadline.to_dict(include_relations=True)
            if deadline.course:
                data['course_title'] = deadline.course.title
                data['course_icon'] = deadline.course.icon
            results.append(data)
        
        return results
    
    def create_deadline(
        self,
        user_id: int,
        deadline_data: dict
    ) -> LMSDeadline:
        """Create a deadline"""
        deadline = LMSDeadline(
            user_id=user_id,
            course_id=deadline_data.get('course_id'),
            title=deadline_data['title'],
            description=deadline_data.get('description'),
            due_date=deadline_data['due_date']
        )
        
        self.db.add(deadline)
        self.db.commit()
        self.db.refresh(deadline)
        return deadline
    
    def complete_deadline(self, deadline_id: int, user_id: int) -> Optional[LMSDeadline]:
        """Mark deadline as completed"""
        deadline = (
            self.db.query(LMSDeadline)
            .filter(
                and_(
                    LMSDeadline.id == deadline_id,
                    LMSDeadline.user_id == user_id
                )
            )
            .first()
        )
        
        if not deadline:
            return None
        
        deadline.is_completed = True
        deadline.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(deadline)
        return deadline
    
    # ========================================================================
    # Certificate Operations
    # ========================================================================
    
    def get_user_certificates(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's certificates"""
        certificates = (
            self.db.query(LMSCertificate)
            .join(LMSCourse)
            .filter(LMSCertificate.user_id == user_id)
            .order_by(desc(LMSCertificate.issued_at))
            .all()
        )
        
        return [c.to_dict(include_relations=True) for c in certificates]
    
    def issue_certificate(
        self,
        user_id: int,
        course_id: int,
        title: str,
        pdf_url: Optional[str] = None,
        expiry_date: Optional[datetime] = None
    ) -> Optional[LMSCertificate]:
        """Issue a certificate for course completion"""
        # Check if already issued
        existing = (
            self.db.query(LMSCertificate)
            .filter(
                and_(
                    LMSCertificate.user_id == user_id,
                    LMSCertificate.course_id == course_id
                )
            )
            .first()
        )
        
        if existing:
            return existing  # Already issued
        
        # Generate certificate number
        import uuid
        cert_number = f"CERT-{uuid.uuid4().hex[:12].upper()}"
        
        certificate = LMSCertificate(
            user_id=user_id,
            course_id=course_id,
            certificate_number=cert_number,
            title=title,
            pdf_url=pdf_url,
            expiry_date=expiry_date
        )
        
        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)
        
        # Log activity
        course = self.db.query(LMSCourse).filter(LMSCourse.id == course_id).first()
        if course:
            self.log_activity(
                user_id=user_id,
                activity_type='certificate_earned',
                title=f'Earned certificate: {title}',
                course_id=course_id,
                icon=course.icon
            )
        
        return certificate
    
    def get_certificate_by_number(self, certificate_number: str) -> Optional[Dict[str, Any]]:
        """Get certificate by certificate number (for verification)"""
        certificate = (
            self.db.query(LMSCertificate)
            .join(LMSCourse)
            .filter(LMSCertificate.certificate_number == certificate_number)
            .first()
        )
        
        if not certificate:
            return None
        
        return certificate.to_dict(include_relations=True)
    
    # ========================================================================
    # Section Progress Operations
    # ========================================================================
    
    def get_section_progress(
        self,
        user_id: int,
        section_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get progress for a section"""
        progress = (
            self.db.query(LMSUserSectionProgress)
            .join(LMSCourseSection)
            .filter(
                and_(
                    LMSUserSectionProgress.user_id == user_id,
                    LMSUserSectionProgress.section_id == section_id
                )
            )
            .first()
        )
        
        if not progress:
            return None
        
        return progress.to_dict(include_relations=True)
    
    def update_section_progress(
        self,
        user_id: int,
        section_id: int,
        completed_items: int,
        total_items: int
    ) -> LMSUserSectionProgress:
        """Update section progress"""
        progress = (
            self.db.query(LMSUserSectionProgress)
            .filter(
                and_(
                    LMSUserSectionProgress.user_id == user_id,
                    LMSUserSectionProgress.section_id == section_id
                )
            )
            .first()
        )
        
        is_completed = completed_items >= total_items
        
        if progress:
            # Update existing
            progress.completed_items = completed_items
            progress.is_completed = is_completed
        else:
            # Create new
            progress = LMSUserSectionProgress(
                user_id=user_id,
                section_id=section_id,
                completed_items=completed_items,
                is_completed=is_completed
            )
            self.db.add(progress)
        
        self.db.commit()
        self.db.refresh(progress)
        
        # Update course progress if section completed
        if is_completed:
            section = self.db.query(LMSCourseSection).filter(LMSCourseSection.id == section_id).first()
            if section:
                self._update_course_progress_from_sections(user_id, section.course_id)
                
                # Log activity
                course = self.db.query(LMSCourse).filter(LMSCourse.id == section.course_id).first()
                if course:
                    self.log_activity(
                        user_id=user_id,
                        activity_type='section_complete',
                        title=f'Completed section: {section.title}',
                        course_id=section.course_id,
                        icon=course.icon
                    )
        
        return progress
    
    def _update_course_progress_from_sections(self, user_id: int, course_id: int):
        """Calculate and update course progress from section completions"""
        # Get all sections for course
        sections = (
            self.db.query(LMSCourseSection)
            .filter(LMSCourseSection.course_id == course_id)
            .all()
        )
        
        if not sections:
            return
        
        # Get user progress for all sections
        total_sections = len(sections)
        completed_sections = 0
        
        for section in sections:
            progress = (
                self.db.query(LMSUserSectionProgress)
                .filter(
                    and_(
                        LMSUserSectionProgress.user_id == user_id,
                        LMSUserSectionProgress.section_id == section.id,
                        LMSUserSectionProgress.is_completed == True
                    )
                )
                .first()
            )
            if progress:
                completed_sections += 1
        
        # Calculate progress percentage
        course_progress = round((completed_sections / total_sections) * 100) if total_sections > 0 else 0
        
        # Update user course progress
        user_course = (
            self.db.query(LMSUserCourse)
            .filter(
                and_(
                    LMSUserCourse.user_id == user_id,
                    LMSUserCourse.course_id == course_id
                )
            )
            .first()
        )
        
        if user_course:
            self.update_course_progress(user_id, course_id, course_progress)
