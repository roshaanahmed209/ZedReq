"""
Seez Agent - Lenient Answer Checker
AI-powered agent that evaluates user answers with lenient scoring (0-10) and updates database
"""

import os
import logging
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config.database_orm import get_db
from models.orm import LMSUserAnswer, LMSQuestion
from services.lms_service import LMSService

logger = logging.getLogger(__name__)


# System prompt for lenient answer evaluation
SEEZ_EVALUATION_PROMPT = """You are Seez, a lenient and encouraging AI answer checker. Your role is to evaluate student answers with a generous, supportive approach.

## Your Evaluation Philosophy

1. **Be Lenient**: Give credit for partial understanding, even if the answer isn't perfect
2. **Be Encouraging**: Focus on what the student got right, not just what's wrong
3. **Be Fair**: Rate answers on a scale of 0-10 based on:
   - Correctness of core concepts
   - Understanding demonstrated (even if incomplete)
   - Effort and thoughtfulness
   - Partial credit for relevant information

## Evaluation Guidelines

### For Multiple Choice Questions:
- 10/10: Correct answer
- 7-9/10: Close answer with good reasoning
- 4-6/10: Partial understanding shown
- 1-3/10: Some relevant knowledge but incorrect
- 0/10: Completely wrong or no answer

### For Text/Essay Questions:
- 10/10: Complete, accurate, well-explained answer
- 8-9/10: Mostly correct with minor gaps
- 6-7/10: Core concepts correct but missing details
- 4-5/10: Partial understanding, some correct points
- 2-3/10: Minimal understanding, few correct points
- 0-1/10: Incorrect or irrelevant answer

### For True/False Questions:
- 10/10: Correct answer
- 5/10: Wrong answer but shows some reasoning
- 0/10: Wrong answer with no reasoning

## Output Format

For each answer, provide a JSON object with:
- score: Integer from 0 to 10
- is_correct: Boolean (true if score >= 7, false otherwise)
- feedback: Constructive, encouraging feedback (2-3 sentences)
- improvement_suggestions: List of specific, actionable suggestions for improvement (2-4 suggestions)
- points_earned: Integer (calculate based on score: score * question_points / 10)

### Improvement Suggestions Guidelines

For descriptive/text answers, provide improvement suggestions that:
1. Are specific and actionable (not vague)
2. Address gaps in understanding or explanation
3. Suggest ways to enhance the answer
4. Are encouraging and constructive
5. Focus on key concepts that were missed or could be expanded

Examples of good suggestions:
- "Consider explaining the relationship between X and Y more clearly"
- "Add more detail about how Z works in practice"
- "Include examples to illustrate your point"
- "Clarify the difference between A and B"

Return ONLY a JSON array of evaluation objects, no additional text."""


class SeezAgent:
    """AI Agent for lenient answer evaluation with 0-10 scoring"""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini"
    ):
        """
        Initialize Seez Agent with OpenAI client
        
        Args:
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use
        """
        # Initialize OpenAI API key
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Answer evaluation will not work.")
            self.openai_available = False
        else:
            self.openai_available = True
        
        # Initialize LangChain OpenAI client
        if self.openai_available:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.3,  # Lower temperature for consistent evaluation
                    api_key=openai_api_key
                )
                logger.info(f"Seez Agent initialized with model {model_name}")
            except Exception as e:
                logger.warning(f"LangChain OpenAI client initialization failed: {e}")
                self.llm = None
                self.openai_available = False
        else:
            self.llm = None
    
    def _evaluate_single_answer(
        self,
        question: LMSQuestion,
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single answer using LLM
        
        Args:
            question: LMSQuestion object
            user_answer: User's answer text
            
        Returns:
            Dictionary with score, is_correct, feedback, points_earned
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot evaluate answer")
            return {
                'score': 0,
                'is_correct': False,
                'feedback': 'Evaluation service unavailable',
                'improvement_suggestions': [],
                'points_earned': 0
            }
        
        try:
            # Build evaluation prompt
            question_type = question.question_type or 'text'
            correct_answer = question.correct_answer or ''
            question_points = question.points or 1
            
            # Format options for multiple choice
            options_text = ""
            if question_type == 'multiple_choice' and question.options:
                options_text = "\nOptions:\n"
                for key, value in question.options.items():
                    options_text += f"{key}: {value}\n"
            
            prompt = f"""Evaluate the following descriptive answer with lenient, encouraging scoring (0-10):

Question Type: {question_type}
Question: {question.question_text}
{options_text}
Correct Answer: {correct_answer}
Question Points: {question_points}

Student's Answer:
{user_answer}

Evaluate this answer leniently. Give credit for:
- Partial understanding
- Relevant concepts mentioned
- Effort and thoughtfulness
- Close approximations

For descriptive/text answers, provide:
1. A score (0-10) based on correctness and completeness
2. Constructive feedback highlighting what's good and what needs improvement
3. Specific, actionable improvement suggestions (2-4 suggestions) that help the student enhance their answer

Return a JSON object with: score (0-10), is_correct (boolean), feedback (string), improvement_suggestions (array of strings), points_earned (integer)."""
            
            messages = [
                SystemMessage(content=SEEZ_EVALUATION_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            evaluation = json.loads(content)
            
            # Ensure score is between 0-10
            score = max(0, min(10, int(evaluation.get('score', 0))))
            
            # Calculate points earned
            points_earned = int((score / 10) * question_points)
            
            # Determine is_correct (score >= 7 is considered correct for lenient checking)
            is_correct = score >= 7
            
            # Extract improvement suggestions
            improvement_suggestions = evaluation.get('improvement_suggestions', [])
            if isinstance(improvement_suggestions, str):
                # If it's a string, try to parse it or split by newlines
                improvement_suggestions = [s.strip() for s in improvement_suggestions.split('\n') if s.strip()]
            elif not isinstance(improvement_suggestions, list):
                improvement_suggestions = []
            
            # Format feedback with improvement suggestions
            feedback = evaluation.get('feedback', 'No feedback provided')
            if improvement_suggestions:
                suggestions_text = "\n\nImprovement Suggestions:\n" + "\n".join(f"• {s}" for s in improvement_suggestions)
                feedback = feedback + suggestions_text
            
            result = {
                'score': score,
                'is_correct': is_correct,
                'feedback': feedback,
                'improvement_suggestions': improvement_suggestions,
                'points_earned': points_earned
            }
            
            logger.info(f"Evaluated answer: score={score}/10, correct={is_correct}, points={points_earned}")
            return result
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse evaluation JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return {
                'score': 0,
                'is_correct': False,
                'feedback': 'Error parsing evaluation response',
                'improvement_suggestions': [],
                'points_earned': 0
            }
        except Exception as e:
            logger.error(f"Failed to evaluate answer: {e}")
            return {
                'score': 0,
                'is_correct': False,
                'feedback': f'Evaluation error: {str(e)}',
                'improvement_suggestions': [],
                'points_earned': 0
            }
    
    def evaluate_answers_batch(
        self,
        answer_ids: List[int],
        db_session = None
    ) -> Dict[str, Any]:
        """
        Evaluate multiple answers in batch using parallel processing with rate limiting
        
        Args:
            answer_ids: List of answer IDs to evaluate
            db_session: Database session (optional, will create if not provided)
            
        Returns:
            Dictionary with evaluation results and statistics
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import os
        
        if not answer_ids:
            return {
                'success': False,
                'error': 'No answer IDs provided',
                'evaluated_count': 0,
                'average_score': 0.0
            }
        
        # Get database session for initial query
        should_close = False
        if db_session is None:
            from config.database_orm import get_db
            db = next(get_db())
            should_close = True
        else:
            db = db_session
        
        try:
            # Get all answers with their questions
            answers = (
                db.query(LMSUserAnswer)
                .join(LMSQuestion)
                .filter(LMSUserAnswer.id.in_(answer_ids))
                .filter(LMSUserAnswer.evaluated_at.is_(None))  # Only unevaluated answers
                .all()
            )
            
            if not answers:
                return {
                    'success': False,
                    'error': 'No unevaluated answers found',
                    'evaluated_count': 0,
                    'average_score': 0.0
                }
            
            # Import utilities for rate limiting, retry, and circuit breaker
            from utils.rate_limiter import get_openai_limiter
            from utils.api_retry import retry_with_backoff
            from utils.circuit_breaker import get_circuit_breaker, CircuitBreakerOpenError
            from utils.api_security import sanitize_input
            
            # Get rate limiter and circuit breaker
            rate_limiter = get_openai_limiter()
            circuit_breaker = get_circuit_breaker('openai_api')
            
            # Get max workers from environment
            max_workers = int(os.environ.get('SEEZ_EVAL_MAX_WORKERS', 5))
            
            # Thread-safe collections for results
            evaluations = []
            scores = []
            errors = []
            lock = threading.Lock()
            
            def evaluate_single_answer_with_db(answer):
                """Evaluate a single answer with its own database session"""
                # Create new database session for this thread
                from config.database_orm import get_db
                thread_db = next(get_db())
                thread_service = LMSService(thread_db)
                
                try:
                    if not answer.answer_text:
                        logger.warning(f"Answer {answer.id} has no answer_text, skipping")
                        return None
                    
                    # Sanitize input
                    sanitized_answer = sanitize_input(answer.answer_text, max_length=5000)
                    
                    # Evaluate with rate limiting, retry, and circuit breaker
                    def evaluate_with_protection():
                        with rate_limiter.acquire():
                            return self._evaluate_single_answer(answer.question, sanitized_answer)
                    
                    try:
                        evaluation = circuit_breaker.call(evaluate_with_protection)
                    except CircuitBreakerOpenError as e:
                        logger.error(f"Circuit breaker open for answer {answer.id}: {e}")
                        return {'error': 'Service temporarily unavailable', 'answer_id': answer.id}
                    except Exception as e:
                        logger.error(f"Failed to evaluate answer {answer.id}: {e}")
                        return {'error': str(e), 'answer_id': answer.id}
                    
                    # Update answer in database
                    try:
                        updated_answer = thread_service.evaluate_answer(
                            answer_id=answer.id,
                            is_correct=evaluation['is_correct'],
                            points=evaluation['points_earned'],
                            feedback=evaluation['feedback']
                        )
                        
                        if updated_answer:
                            result = {
                                'answer_id': answer.id,
                                'question_id': answer.question_id,
                                'score': evaluation['score'],
                                'is_correct': evaluation['is_correct'],
                                'points_earned': evaluation['points_earned'],
                                'feedback': evaluation['feedback'],
                                'improvement_suggestions': evaluation.get('improvement_suggestions', [])
                            }
                            return result
                        else:
                            return {'error': 'Database update failed', 'answer_id': answer.id}
                    except Exception as e:
                        logger.error(f"Failed to update answer {answer.id} in database: {e}")
                        return {'error': f'Database error: {str(e)}', 'answer_id': answer.id}
                
                finally:
                    thread_db.close()
            
            # Evaluate answers in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_answer = {
                    executor.submit(evaluate_single_answer_with_db, answer): answer
                    for answer in answers
                }
                
                for future in as_completed(future_to_answer):
                    answer = future_to_answer[future]
                    try:
                        result = future.result()
                        if result and 'error' not in result:
                            with lock:
                                evaluations.append(result)
                                scores.append(result['score'])
                        elif result and 'error' in result:
                            with lock:
                                errors.append(result)
                    except Exception as e:
                        logger.error(f"Error processing answer {answer.id}: {e}", exc_info=True)
                        with lock:
                            errors.append({'error': str(e), 'answer_id': answer.id})
            
            # Calculate average score
            average_score = sum(scores) / len(scores) if scores else 0.0
            
            result = {
                'success': len(errors) < len(answers),  # Success if at least some evaluations succeeded
                'evaluated_count': len(evaluations),
                'total_answers': len(answers),
                'average_score': round(average_score, 2),
                'evaluations': evaluations
            }
            
            if errors:
                result['errors'] = errors
                logger.warning(f"Evaluated {len(evaluations)}/{len(answers)} answers with {len(errors)} errors")
            else:
                logger.info(f"Evaluated {len(evaluations)} answers, average score: {average_score:.2f}/10")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to evaluate answers batch: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'evaluated_count': 0,
                'average_score': 0.0
            }
        finally:
            if should_close:
                db.close()
    
    def evaluate_course_answers(
        self,
        user_id: int,
        course_id: int,
        db_session = None
    ) -> Dict[str, Any]:
        """
        Evaluate all unevaluated answers for a user in a specific course
        
        Args:
            user_id: User ID
            course_id: Course ID
            db_session: Database session (optional)
            
        Returns:
            Dictionary with evaluation results and statistics
        """
        # Get database session
        should_close = False
        if db_session is None:
            from config.database_orm import get_db
            db = next(get_db())
            should_close = True
        else:
            db = db_session
        
        try:
            # Get all unevaluated answers for this user and course
            answers = (
                db.query(LMSUserAnswer)
                .join(LMSQuestion)
                .filter(
                    LMSUserAnswer.user_id == user_id,
                    LMSQuestion.course_id == course_id,
                    LMSUserAnswer.evaluated_at.is_(None)  # Only unevaluated
                )
                .all()
            )
            
            if not answers:
                return {
                    'success': False,
                    'error': 'No unevaluated answers found for this course',
                    'evaluated_count': 0,
                    'average_score': 0.0
                }
            
            # Extract answer IDs
            answer_ids = [answer.id for answer in answers]
            
            # Evaluate batch
            return self.evaluate_answers_batch(answer_ids, db_session=db)
            
        except Exception as e:
            logger.error(f"Failed to evaluate course answers: {e}")
            return {
                'success': False,
                'error': str(e),
                'evaluated_count': 0,
                'average_score': 0.0
            }
        finally:
            if should_close:
                db.close()
    
    def is_available(self) -> bool:
        """Check if agent is available (OpenAI working)"""
        return self.openai_available


# Global agent instance (lazy initialization)
_agent_instance: Optional[SeezAgent] = None


def get_seez_agent() -> SeezAgent:
    """Get or create global Seez agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = SeezAgent()
    
    return _agent_instance
