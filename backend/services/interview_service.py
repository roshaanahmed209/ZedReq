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
from agents.Riz_agent import get_riz_agent
from config.settings import settings
from utils.api_security import sanitize_text_for_storage, sanitize_dict_for_logging

logger = logging.getLogger(__name__)


# Custom exception classes for better error handling
class InterviewError(Exception):
    """Base exception for interview-related errors"""
    pass


class InterviewNotFoundError(InterviewError):
    """Interview not found"""
    pass


class InterviewStateError(InterviewError):
    """Invalid interview state transition"""
    pass


class JobNotFoundError(InterviewError):
    """Job not found"""
    pass


class JobNotActiveError(InterviewError):
    """Job is not active"""
    pass


class TavusServiceError(InterviewError):
    """Tavus service error"""
    pass


class InterviewService:
    """Service for managing interview sessions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.tavus_service = TavusService()
        self.question_service = InterviewQuestionService()
        self.check_agent = TavCheckAgent()
    
    def start_interview(self, user_id: int, job_id: int, max_call_duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Start a new interview session
        
        Args:
            user_id: User ID
            job_id: Job ID to interview for
            max_call_duration: Maximum call duration in seconds (from subscription plan, server-controlled)
            
        Returns:
            Dictionary with interview details
            
        Raises:
            JobNotFoundError: If job not found
            JobNotActiveError: If job is not active
            TavusServiceError: If Tavus service fails
            ValueError: If configuration is invalid
        """
        # Validate inputs
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("user_id must be a positive integer")
        if not isinstance(job_id, int) or job_id <= 0:
            raise ValueError("job_id must be a positive integer")
        
        try:
            # Log security event
            logger.info(f"Interview start requested: user_id={user_id}, job_id={job_id}")
            
            # Get job details
            job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
            if not job:
                logger.warning(f"Job not found: job_id={job_id}, user_id={user_id}")
                raise JobNotFoundError(f"Job {job_id} not found")
            
            if job.status != 'active':
                logger.warning(f"Job not active: job_id={job_id}, status={job.status}, user_id={user_id}")
                raise JobNotActiveError("Job is not active")
            
            # Calculate attempt number
            attempt_number = self.get_interview_attempt_number(user_id, job_id) + 1
            logger.debug(f"Interview attempt number: {attempt_number} for user {user_id}, job {job_id}")
            
            # Generate interview questions
            logger.debug("Generating interview questions...")
            questions = self.question_service.generate_interview_questions(job)
            if not questions:
                logger.error(f"Failed to generate interview questions for job {job_id}")
                raise ValueError("Failed to generate interview questions")
            
            logger.info(f"Generated {len(questions)} interview questions")
            
            # Generate system prompt
            system_prompt = self.question_service.generate_system_prompt(job, questions)
            
            # Create Tavus conversation - randomly select replica ID from list
            replica_id = settings.get_random_tavus_replica_id()
            if not replica_id:
                logger.error("TAVUS_REPLICA_ID or TAVUS_REPLICA_IDS not configured")
                raise ValueError("TAVUS_REPLICA_ID or TAVUS_REPLICA_IDS not configured")
            
            persona_id = settings.TAVUS_PERSONA_ID
            if not persona_id or not str(persona_id).strip():
                logger.error("TAVUS_PERSONA_ID not configured")
                raise ValueError("TAVUS_PERSONA_ID not configured")
            
            logger.debug(f"Selected replica ID: {replica_id} (from {len(settings.get_tavus_replica_ids())} available)")
            
            # Sanitize conversation name
            conversation_name = sanitize_text_for_storage(
                f"{job.title} Interview - Attempt {attempt_number}",
                max_length=255
            )
            first_message = "Hello! Welcome to your mock interview. I'm here to help you practice for this position. Let's begin with a few questions. Are you ready?"
            
            logger.debug("Creating Tavus conversation...")
            try:
                tavus_response = self.tavus_service.create_conversation(
                    replica_id=replica_id,
                    persona_id=str(persona_id).strip(),
                    conversation_name=conversation_name,
                    system_prompt=system_prompt,
                    first_message=first_message,
                    max_call_duration=max_call_duration
                )
            except Exception as e:
                logger.error(f"Tavus service error: {e}", exc_info=True)
                raise TavusServiceError(f"Failed to create Tavus conversation: {str(e)}")
            
            tavus_conversation_id = tavus_response.get('conversation_id')
            if not tavus_conversation_id:
                logger.error("Tavus conversation created but no conversation_id returned")
                raise TavusServiceError("Failed to create Tavus conversation: no conversation_id")
            
            logger.info(f"Tavus conversation created: {tavus_conversation_id}")
            
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
            
            # Log success (sanitized)
            logger.info(
                f"Interview started successfully: interview_id={interview.interview_id}, "
                f"user_id={user_id}, job_id={job_id}, attempt={attempt_number}"
            )
            
            return {
                'interview_id': interview.interview_id,
                'tavus_conversation_id': tavus_conversation_id,
                'tavus_conversation_url': tavus_response.get('conversation_url'),
                'tavus_meeting_token': tavus_response.get('meeting_token'),
                'questions': questions,
                'status': interview.status,
                'attempt_number': attempt_number,
                'job_title': job.title,
                'company_name': job.company_name
            }
            
        except (JobNotFoundError, JobNotActiveError, TavusServiceError):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Failed to start interview: user_id={user_id}, job_id={job_id}, error={e}", exc_info=True)
            self.db.rollback()
            raise
    
    def complete_interview(self, interview_id: int) -> Dict[str, Any]:
        """
        Complete an interview and analyze responses
        
        Args:
            interview_id: Interview ID
            
        Returns:
            Dictionary with scores and feedback
            
        Raises:
            InterviewNotFoundError: If interview not found
            InterviewStateError: If interview is in invalid state
            TavusServiceError: If Tavus service fails
        """
        # Validate input
        if not isinstance(interview_id, int) or interview_id <= 0:
            raise ValueError("interview_id must be a positive integer")
        
        try:
            # Log security event
            logger.info(f"Interview completion requested: interview_id={interview_id}")
            
            # Get interview
            interview = self.db.query(LiveInterview).filter(
                LiveInterview.interview_id == interview_id
            ).first()
            
            if not interview:
                logger.warning(f"Interview not found: interview_id={interview_id}")
                raise InterviewNotFoundError(f"Interview {interview_id} not found")
            
            # Validate interview state
            if interview.status == 'completed':
                logger.info(f"Interview already completed, returning existing results: interview_id={interview_id}")
                return self._format_complete_response(interview)
            
            if interview.status not in ['in_progress', 'pending']:
                logger.warning(
                    f"Invalid interview state for completion: interview_id={interview_id}, "
                    f"status={interview.status}"
                )
                raise InterviewStateError(
                    f"Cannot complete interview in '{interview.status}' state. "
                    f"Interview must be 'in_progress' or 'pending'."
                )
            
            # Get Tavus transcript
            if not interview.tavus_conversation_id:
                logger.error(f"Tavus conversation ID not found: interview_id={interview_id}")
                raise ValueError("Tavus conversation ID not found")
            
            logger.debug(f"Fetching Tavus transcript: conversation_id={interview.tavus_conversation_id}")
            try:
                transcript = self.tavus_service.get_conversation_transcript(
                    interview.tavus_conversation_id
                )
            except Exception as e:
                logger.error(f"Tavus service error: {e}", exc_info=True)
                raise TavusServiceError(f"Failed to get Tavus transcript: {str(e)}")
            
            # Extract user responses from transcript
            logger.debug("Extracting user responses from transcript...")
            user_responses = self._extract_user_responses(transcript)
            logger.info(f"Extracted {len(user_responses)} user responses")
            
            # Get job context
            job = self.db.query(JobPosting).filter(
                JobPosting.job_id == interview.job_id
            ).first()
            
            job_context = self.question_service._build_job_context(job) if job else ""
            
            # Analyze responses using Tav_check_agent
            logger.debug("Analyzing interview responses...")
            try:
                analysis = self.check_agent.analyze_interview_responses(
                    questions=interview.questions or [],
                    user_responses=user_responses,
                    job_context=job_context
                )
                logger.info(f"Analysis complete: overall_score={analysis.get('overall_score')}")
            except Exception as e:
                logger.error(f"Failed to analyze interview responses: {e}", exc_info=True)
                raise ValueError(f"Failed to analyze interview responses: {str(e)}")
            
            # Sanitize feedback before storage
            detailed_feedback = sanitize_text_for_storage(
                analysis.get('detailed_feedback', ''),
                max_length=10000
            )
            
            # Update interview record
            interview.user_responses = user_responses
            interview.overall_score = analysis['overall_score']
            interview.score_breakdown = analysis['score_breakdown']
            interview.feedback = detailed_feedback
            interview.status = 'completed'
            interview.completed_at = datetime.now()
            
            # Generate Riz coaching feedback
            logger.debug("Generating Riz coaching feedback...")
            try:
                riz_agent = get_riz_agent()
                if riz_agent.is_available():
                    job_description = job.description if job else None
                    riz_feedback = riz_agent.generate_feedback(
                        job_title=job.title if job else "Unknown Position",
                        company_name=job.company_name if job else "Unknown Company",
                        job_description=job_description,
                        questions=interview.questions or [],
                        user_responses=user_responses,
                        overall_score=analysis['overall_score'],
                        score_breakdown=analysis['score_breakdown'],
                        tav_check_feedback=detailed_feedback
                    )
                    interview.riz_feedback = riz_feedback
                    logger.info(f"Generated Riz coaching feedback for interview {interview_id}")
                else:
                    logger.warning("Riz agent not available, skipping coaching feedback generation")
            except Exception as e:
                logger.error(f"Failed to generate Riz coaching feedback: {e}", exc_info=True)
                # Don't fail the interview completion if Riz fails
            
            self.db.commit()
            self.db.refresh(interview)
            
            # Log success (sanitized)
            logger.info(
                f"Interview completed successfully: interview_id={interview_id}, "
                f"score={analysis['overall_score']}, user_id={interview.user_id}"
            )
            
            result = {
                'interview_id': interview.interview_id,
                'overall_score': analysis['overall_score'],
                'score_breakdown': analysis['score_breakdown'],
                'question_scores': analysis.get('question_scores', []),
                'detailed_feedback': detailed_feedback,
                'strengths': analysis.get('strengths', []),
                'weaknesses': analysis.get('weaknesses', []),
                'improvement_suggestions': analysis.get('improvement_suggestions', []),
                'attempt_number': interview.attempt_number,
                'completed_at': interview.completed_at
            }
            
            # Include Riz feedback if available
            if interview.riz_feedback:
                result['riz_feedback'] = interview.riz_feedback
            
            return result
            
        except (InterviewNotFoundError, InterviewStateError, TavusServiceError):
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Failed to complete interview {interview_id}: {e}", exc_info=True)
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
        
        Supports multiple transcript formats and provides fallback parsing strategies.
        
        Args:
            transcript: Tavus conversation transcript (dict or list)
            
        Returns:
            List of user response dictionaries with sanitized content
        """
        responses = []
        
        if not transcript:
            logger.warning("Empty transcript provided")
            return responses
        
        # Strategy 1: Try 'messages' array (most common format)
        if isinstance(transcript, dict):
            messages = transcript.get('messages', transcript.get('transcript', transcript.get('data', [])))
        elif isinstance(transcript, list):
            messages = transcript
        else:
            logger.warning(f"Unexpected transcript type: {type(transcript)}")
            return responses
        
        if not isinstance(messages, list):
            logger.warning(f"Messages is not a list: {type(messages)}")
            return responses
        
        logger.debug(f"Processing {len(messages)} messages from transcript")
        
        # Extract user responses
        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                logger.debug(f"Skipping non-dict message at index {idx}")
                continue
            
            # Try different role field names
            role = (
                msg.get('role', '') or 
                msg.get('speaker', '') or 
                msg.get('type', '')
            ).lower()
            
            # Check if this is a user/candidate message
            if role in ['user', 'candidate', 'interviewee', 'participant']:
                # Try different content field names
                content = (
                    msg.get('content') or 
                    msg.get('text') or 
                    msg.get('message') or 
                    msg.get('transcript') or 
                    msg.get('value') or 
                    ''
                )
                
                # Sanitize content
                if content:
                    content = sanitize_text_for_storage(str(content), max_length=5000)
                    
                    response_dict = {
                        'response': content,
                        'timestamp': msg.get('timestamp') or msg.get('time') or msg.get('created_at')
                    }
                    
                    # Add question index if available
                    if 'question_index' in msg:
                        response_dict['question_index'] = msg.get('question_index')
                    
                    responses.append(response_dict)
                    logger.debug(f"Extracted response {len(responses)}: {len(content)} chars")
        
        # Strategy 2: If no responses found, try alternative structure
        if not responses and isinstance(transcript, dict):
            # Try 'responses' array
            alt_responses = transcript.get('responses', transcript.get('user_responses', []))
            if isinstance(alt_responses, list):
                logger.debug("Trying alternative response structure")
                for idx, resp in enumerate(alt_responses):
                    if isinstance(resp, dict):
                        content = resp.get('text') or resp.get('content') or resp.get('response') or ''
                        if content:
                            content = sanitize_text_for_storage(str(content), max_length=5000)
                            responses.append({
                                'response': content,
                                'timestamp': resp.get('timestamp')
                            })
                    elif isinstance(resp, str):
                        content = sanitize_text_for_storage(resp, max_length=5000)
                        responses.append({
                            'response': content,
                            'timestamp': None
                        })
        
        logger.info(f"Extracted {len(responses)} user responses from transcript")
        
        if not responses:
            logger.warning("No user responses found in transcript. Transcript structure may be unexpected.")
            logger.debug(f"Transcript keys: {list(transcript.keys()) if isinstance(transcript, dict) else 'N/A'}")
        
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
