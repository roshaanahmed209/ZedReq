"""
Interview Service
Orchestrates the interview process: starting interviews, completing them, and managing history
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from models.orm.live_interview import LiveInterview
from models.orm.job_posting import JobPosting
from services.tavus_service import TavusService
from services.interview_question_service import InterviewQuestionService
from agents.Tav_check_agent import TavCheckAgent
from config.settings import settings

logger = logging.getLogger(__name__)


class InterviewService:
    """Service for managing interview sessions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tavus_service = TavusService()
        self.question_service = InterviewQuestionService()
        self.check_agent = TavCheckAgent()
    
    def start_interview(self, user_id: int, job_id: int) -> Dict[str, Any]:
        """
        Start a new interview session
        
        Args:
            user_id: User ID
            job_id: Job ID to interview for
            
        Returns:
            Dictionary with interview details
        """
        try:
            # Get job details
            job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
            if not job:
                raise ValueError(f"Job {job_id} not found")
            
            if job.status != 'active':
                raise ValueError("Job is not active")
            
            # Calculate attempt number
            attempt_number = self.get_interview_attempt_number(user_id, job_id) + 1
            
            # Generate interview questions
            questions = self.question_service.generate_interview_questions(job)
            if not questions:
                raise ValueError("Failed to generate interview questions")
            
            # Generate system prompt
            system_prompt = self.question_service.generate_system_prompt(job, questions)
            
            # Create Tavus conversation
            replica_id = settings.TAVUS_REPLICA_ID
            if not replica_id:
                raise ValueError("TAVUS_REPLICA_ID not configured")
            
            conversation_name = f"{job.title} Interview - Attempt {attempt_number}"
            first_message = "Hello! Welcome to your mock interview. I'm here to help you practice for this position. Let's begin with a few questions. Are you ready?"
            
            tavus_response = self.tavus_service.create_conversation(
                replica_id=replica_id,
                conversation_name=conversation_name,
                system_prompt=system_prompt,
                first_message=first_message
            )
            
            tavus_conversation_id = tavus_response.get('conversation_id')
            if not tavus_conversation_id:
                raise ValueError("Failed to create Tavus conversation")
            
            # Create interview record
            interview = LiveInterview(
                user_id=user_id,
                job_id=job_id,
                tavus_conversation_id=tavus_conversation_id,
                tavus_response=tavus_response,
                questions=questions,
                attempt_number=attempt_number,
                status='in_progress',
                started_at=datetime.now()
            )
            
            self.db.add(interview)
            self.db.commit()
            self.db.refresh(interview)
            
            logger.info(f"Started interview {interview.interview_id} for user {user_id}, job {job_id}")
            
            return {
                'interview_id': interview.interview_id,
                'tavus_conversation_id': tavus_conversation_id,
                'questions': questions,
                'status': interview.status,
                'attempt_number': attempt_number,
                'job_title': job.title,
                'company_name': job.company_name
            }
            
        except Exception as e:
            logger.error(f"Failed to start interview: {e}")
            self.db.rollback()
            raise
    
    def complete_interview(self, interview_id: int) -> Dict[str, Any]:
        """
        Complete an interview and analyze responses
        
        Args:
            interview_id: Interview ID
            
        Returns:
            Dictionary with scores and feedback
        """
        try:
            # Get interview
            interview = self.db.query(LiveInterview).filter(
                LiveInterview.interview_id == interview_id
            ).first()
            
            if not interview:
                raise ValueError(f"Interview {interview_id} not found")
            
            if interview.status == 'completed':
                # Return existing results
                return self._format_complete_response(interview)
            
            # Get Tavus transcript
            if not interview.tavus_conversation_id:
                raise ValueError("Tavus conversation ID not found")
            
            transcript = self.tavus_service.get_conversation_transcript(
                interview.tavus_conversation_id
            )
            
            # Extract user responses from transcript
            user_responses = self._extract_user_responses(transcript)
            
            # Get job context
            job = self.db.query(JobPosting).filter(
                JobPosting.job_id == interview.job_id
            ).first()
            
            job_context = self.question_service._build_job_context(job) if job else ""
            
            # Analyze responses using Tav_check_agent
            analysis = self.check_agent.analyze_interview_responses(
                questions=interview.questions or [],
                user_responses=user_responses,
                job_context=job_context
            )
            
            # Update interview record
            interview.user_responses = user_responses
            interview.overall_score = analysis['overall_score']
            interview.score_breakdown = analysis['score_breakdown']
            interview.feedback = analysis['detailed_feedback']
            interview.status = 'completed'
            interview.completed_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(interview)
            
            logger.info(f"Completed interview {interview_id}. Score: {analysis['overall_score']}")
            
            return {
                'interview_id': interview.interview_id,
                'overall_score': analysis['overall_score'],
                'score_breakdown': analysis['score_breakdown'],
                'question_scores': analysis.get('question_scores', []),
                'detailed_feedback': analysis['detailed_feedback'],
                'strengths': analysis.get('strengths', []),
                'weaknesses': analysis.get('weaknesses', []),
                'improvement_suggestions': analysis.get('improvement_suggestions', []),
                'attempt_number': interview.attempt_number,
                'completed_at': interview.completed_at
            }
            
        except Exception as e:
            logger.error(f"Failed to complete interview {interview_id}: {e}")
            self.db.rollback()
            raise
    
    def get_interview(self, interview_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get interview details
        
        Args:
            interview_id: Interview ID
            user_id: Optional user ID to verify ownership
            
        Returns:
            Interview details dictionary or None
        """
        query = self.db.query(LiveInterview).filter(
            LiveInterview.interview_id == interview_id
        )
        
        if user_id:
            query = query.filter(LiveInterview.user_id == user_id)
        
        interview = query.first()
        
        if not interview:
            return None
        
        result = interview.to_dict(include_relations=True)
        
        # Get job details
        job = self.db.query(JobPosting).filter(
            JobPosting.job_id == interview.job_id
        ).first()
        
        if job:
            result['job_title'] = job.title
            result['company_name'] = job.company_name
        
        return result
    
    def get_user_interview_history(
        self,
        user_id: int,
        job_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's interview history
        
        Args:
            user_id: User ID
            job_id: Optional job ID to filter by
            
        Returns:
            List of interview dictionaries
        """
        query = self.db.query(LiveInterview).filter(
            LiveInterview.user_id == user_id
        )
        
        if job_id:
            query = query.filter(LiveInterview.job_id == job_id)
        
        interviews = query.order_by(desc(LiveInterview.created_at)).all()
        
        results = []
        for interview in interviews:
            result = interview.to_dict()
            
            # Get job details
            job = self.db.query(JobPosting).filter(
                JobPosting.job_id == interview.job_id
            ).first()
            
            if job:
                result['job_title'] = job.title
                result['company_name'] = job.company_name
            
            results.append(result)
        
        return results
    
    def get_interview_attempt_number(self, user_id: int, job_id: int) -> int:
        """
        Get the number of attempts user has made for a specific job
        
        Args:
            user_id: User ID
            job_id: Job ID
            
        Returns:
            Number of previous attempts
        """
        count = self.db.query(func.max(LiveInterview.attempt_number)).filter(
            LiveInterview.user_id == user_id,
            LiveInterview.job_id == job_id
        ).scalar()
        
        return count or 0
    
    def _extract_user_responses(self, transcript: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract user responses from Tavus transcript
        
        Args:
            transcript: Tavus conversation transcript
            
        Returns:
            List of user response dictionaries
        """
        # Tavus transcript structure may vary
        # This is a generic extraction - adjust based on actual Tavus API response format
        responses = []
        
        if isinstance(transcript, dict):
            # Try common transcript formats
            messages = transcript.get('messages', transcript.get('transcript', []))
            
            for msg in messages:
                if isinstance(msg, dict):
                    role = msg.get('role', '').lower()
                    if role in ['user', 'candidate', 'interviewee']:
                        responses.append({
                            'response': msg.get('content', msg.get('text', '')),
                            'timestamp': msg.get('timestamp')
                        })
        
        return responses
    
    def _format_complete_response(self, interview: LiveInterview) -> Dict[str, Any]:
        """Format completed interview response"""
        return {
            'interview_id': interview.interview_id,
            'overall_score': interview.overall_score,
            'score_breakdown': interview.score_breakdown,
            'question_scores': [],  # Could be extracted from feedback if stored separately
            'detailed_feedback': interview.feedback or '',
            'strengths': [],
            'weaknesses': [],
            'improvement_suggestions': [],
            'attempt_number': interview.attempt_number,
            'completed_at': interview.completed_at
        }
