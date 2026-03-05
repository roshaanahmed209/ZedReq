"""
Riz Agent - Post-Interview Coaching Feedback
AI-powered agent that provides personalized coaching feedback after interview completion
"""

import os
import logging
import json
from typing import Optional, Dict, Any, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from utils.api_security import (
    validate_api_key,
    sanitize_text_for_storage,
    sanitize_dict_for_logging
)

logger = logging.getLogger(__name__)

# Maximum context length to prevent token limit issues (approximately 8000 tokens)
MAX_CONTEXT_LENGTH = 20000  # characters
MAX_JOB_DESCRIPTION_LENGTH = 2000
MAX_FEEDBACK_LENGTH = 2000
MAX_QUESTION_TEXT_LENGTH = 500
MAX_RESPONSE_TEXT_LENGTH = 1000


# System prompt for post-interview coaching feedback
RIZ_COACHING_PROMPT = """You are Riz, an expert career coach specializing in interview performance improvement. Your role is to provide personalized, actionable coaching feedback to help candidates improve their interview skills.

## Your Coaching Philosophy

1. **Be Encouraging**: Focus on strengths while constructively addressing areas for improvement
2. **Be Specific**: Provide concrete, actionable recommendations rather than vague advice
3. **Be Contextual**: Tailor feedback to the specific job role and interview questions
4. **Be Practical**: Suggest realistic, achievable next steps

## Input Context

You will receive:
- Job description and requirements
- Interview questions that were asked
- Candidate's responses
- Performance scores from technical evaluation (Tav_check_agent)
- Detailed feedback from technical evaluation

## Output Format

Provide a comprehensive coaching feedback JSON object with:

{
  "summary": "A 2-3 sentence overall assessment of the interview performance",
  "strengths": [
    "Specific strength 1",
    "Specific strength 2",
    "Specific strength 3"
  ],
  "weaknesses": [
    "Specific area for improvement 1",
    "Specific area for improvement 2"
  ],
  "recommendations": [
    "Actionable recommendation 1",
    "Actionable recommendation 2",
    "Actionable recommendation 3"
  ],
  "next_steps": [
    "Immediate next step 1",
    "Immediate next step 2"
  ]
}

### Guidelines for Each Section

**Summary**: Provide a balanced overview that acknowledges both strengths and areas for growth.

**Strengths**: List 3-5 specific things the candidate did well. Be specific about what made their responses effective.

**Weaknesses**: List 2-4 areas where the candidate can improve. Frame these constructively, focusing on growth opportunities rather than failures.

**Recommendations**: Provide 3-5 actionable recommendations. Each should be:
- Specific to the interview performance
- Relevant to the job role
- Achievable and practical
- Include examples when helpful

**Next Steps**: Suggest 2-3 immediate actions the candidate can take to improve, such as:
- Practicing specific types of questions
- Learning particular technical concepts
- Improving communication techniques
- Preparing better examples/stories

Return ONLY the JSON object, no additional text."""


class RizAgent:
    """AI Agent for generating post-interview coaching feedback"""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o-mini",
        timeout: float = 60.0
    ):
        """
        Initialize Riz Agent with OpenAI client
        
        Args:
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use
            timeout: Request timeout in seconds (default: 60.0)
        """
        # Initialize OpenAI API key
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        
        # Validate API key
        if not openai_api_key or not validate_api_key(openai_api_key, "OPENAI_API_KEY"):
            logger.warning("OpenAI API key not found or invalid. Riz agent will not work.")
            self.openai_available = False
            self.api_key = None
        else:
            self.openai_available = True
            self.api_key = openai_api_key
        
        self.timeout = max(10.0, min(120.0, timeout))  # Between 10s and 2min
        self.model_name = model_name
        
        # Initialize LangChain OpenAI client
        if self.openai_available:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.7,  # Slightly higher for more natural coaching tone
                    api_key=openai_api_key,
                    timeout=self.timeout
                )
                logger.info(f"Riz Agent initialized with model {model_name}")
            except Exception as e:
                logger.warning(f"LangChain OpenAI client initialization failed: {e}")
                self.llm = None
                self.openai_available = False
        else:
            self.llm = None
    
    def generate_feedback(
        self,
        job_title: str,
        company_name: str,
        job_description: Optional[str],
        questions: list,
        user_responses: list,
        overall_score: Optional[int],
        score_breakdown: Optional[Dict[str, Any]],
        tav_check_feedback: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate post-interview coaching feedback
        
        Args:
            job_title: Job title
            company_name: Company name
            job_description: Job description text
            questions: List of interview questions
            user_responses: List of user responses
            overall_score: Overall score from Tav_check_agent (0-100)
            score_breakdown: Score breakdown dictionary
            tav_check_feedback: Detailed feedback from Tav_check_agent
            
        Returns:
            Dictionary with coaching feedback structure
        """
        if not self.openai_available or not self.llm:
            logger.warning("OpenAI not available, cannot generate coaching feedback")
            return self._default_feedback()
        
        # Validate and sanitize inputs
        try:
            job_title = sanitize_text_for_storage(str(job_title), max_length=200) if job_title else "Unknown Position"
            company_name = sanitize_text_for_storage(str(company_name), max_length=200) if company_name else "Unknown Company"
            job_description = sanitize_text_for_storage(job_description, max_length=MAX_JOB_DESCRIPTION_LENGTH) if job_description else None
            tav_check_feedback = sanitize_text_for_storage(tav_check_feedback, max_length=MAX_FEEDBACK_LENGTH) if tav_check_feedback else None
            
            # Validate score
            if overall_score is not None:
                overall_score = max(0, min(100, int(overall_score)))
            
            # Validate and sanitize questions
            if not isinstance(questions, list):
                logger.warning("Questions must be a list, converting or using empty list")
                questions = []
            
            # Validate and sanitize user_responses
            if not isinstance(user_responses, list):
                logger.warning("User responses must be a list, converting or using empty list")
                user_responses = []
            
            # Log request (sanitized)
            logger.info(
                f"Generating Riz coaching feedback for {job_title} at {company_name} "
                f"(score: {overall_score}, questions: {len(questions)}, responses: {len(user_responses)})"
            )
            
        except Exception as e:
            logger.error(f"Input validation failed: {e}")
            return self._default_feedback()
        
        try:
            # Build context for coaching feedback
            context = self._build_coaching_context(
                job_title=job_title,
                company_name=company_name,
                job_description=job_description,
                questions=questions,
                user_responses=user_responses,
                overall_score=overall_score,
                score_breakdown=score_breakdown,
                tav_check_feedback=tav_check_feedback
            )
            
            # Check context length
            if len(context) > MAX_CONTEXT_LENGTH:
                logger.warning(f"Context length {len(context)} exceeds maximum {MAX_CONTEXT_LENGTH}, truncating")
                context = context[:MAX_CONTEXT_LENGTH] + "\n[... truncated ...]"
            
            # Generate coaching feedback using LLM
            messages = [
                SystemMessage(content=RIZ_COACHING_PROMPT),
                HumanMessage(content=context)
            ]
            
            logger.debug(f"Invoking LLM with context length: {len(context)}")
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Validate response content
            if not content:
                logger.warning("Empty response from LLM")
                return self._default_feedback()
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Validate JSON before parsing
            if not content or not content.strip().startswith('{'):
                logger.warning(f"Invalid JSON response format: {content[:200]}")
                return self._default_feedback()
            
            feedback = json.loads(content)
            
            # Validate and ensure required fields
            validated_feedback = {
                'summary': sanitize_text_for_storage(
                    str(feedback.get('summary', 'No summary available')),
                    max_length=500
                ),
                'strengths': self._validate_list(feedback.get('strengths', []), max_items=5, max_length=200),
                'weaknesses': self._validate_list(feedback.get('weaknesses', []), max_items=4, max_length=200),
                'recommendations': self._validate_list(feedback.get('recommendations', []), max_items=5, max_length=300),
                'next_steps': self._validate_list(feedback.get('next_steps', []), max_items=3, max_length=200)
            }
            
            logger.info(f"Generated coaching feedback for {job_title} at {company_name}")
            return validated_feedback
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse coaching feedback JSON: {e}")
            logger.debug(f"Response content: {content[:500] if 'content' in locals() else 'N/A'}")
            return self._default_feedback()
        except Exception as e:
            logger.error(f"Failed to generate coaching feedback: {e}", exc_info=True)
            return self._default_feedback()
    
    def _validate_list(self, items: Any, max_items: int = 10, max_length: int = 500) -> List[str]:
        """
        Validate and sanitize list items
        
        Args:
            items: List or other iterable to validate
            max_items: Maximum number of items
            max_length: Maximum length per item
            
        Returns:
            Validated list of strings
        """
        if not isinstance(items, list):
            return []
        
        validated = []
        for item in items[:max_items]:
            if isinstance(item, str):
                sanitized = sanitize_text_for_storage(item, max_length=max_length)
                if sanitized:
                    validated.append(sanitized)
            elif item:
                # Convert to string if not already
                sanitized = sanitize_text_for_storage(str(item), max_length=max_length)
                if sanitized:
                    validated.append(sanitized)
        
        return validated
    
    def _build_coaching_context(
        self,
        job_title: str,
        company_name: str,
        job_description: Optional[str],
        questions: list,
        user_responses: list,
        overall_score: Optional[int],
        score_breakdown: Optional[Dict[str, Any]],
        tav_check_feedback: Optional[str]
    ) -> str:
        """
        Build context string for coaching feedback generation
        
        Args:
            job_title: Sanitized job title
            company_name: Sanitized company name
            job_description: Sanitized job description
            questions: List of questions (will be sanitized)
            user_responses: List of user responses (will be sanitized)
            overall_score: Overall score (0-100)
            score_breakdown: Score breakdown dictionary
            tav_check_feedback: Sanitized feedback text
            
        Returns:
            Context string for LLM
        """
        parts = []
        
        parts.append("## Job Information")
        parts.append(f"Position: {job_title}")
        parts.append(f"Company: {company_name}")
        if job_description:
            # Job description already sanitized, but truncate for context
            parts.append(f"\nJob Description:\n{job_description[:MAX_JOB_DESCRIPTION_LENGTH]}")
        
        parts.append("\n## Interview Performance")
        if overall_score is not None:
            parts.append(f"Overall Score: {overall_score}/100")
        
        if score_breakdown and isinstance(score_breakdown, dict):
            parts.append("\nScore Breakdown:")
            for category, score in list(score_breakdown.items())[:10]:  # Limit to 10 categories
                if isinstance(score, (int, float)):
                    score = max(0, min(100, int(score)))
                    category_sanitized = sanitize_text_for_storage(str(category), max_length=50)
                    parts.append(f"- {category_sanitized}: {score}/100")
        
        if tav_check_feedback:
            parts.append(f"\nTechnical Evaluation Feedback:\n{tav_check_feedback[:MAX_FEEDBACK_LENGTH]}")
        
        parts.append("\n## Interview Questions and Responses\n")
        
        # Match responses to questions (limit to prevent context overflow)
        max_questions = min(len(questions), len(user_responses) if user_responses else 0, 20)  # Max 20 questions
        
        for i in range(max_questions):
            question = questions[i] if i < len(questions) else None
            if not question:
                continue
                
            parts.append(f"\n--- Question {i + 1} ---")
            
            if isinstance(question, dict):
                question_text = question.get('question_text', question.get('text', ''))
                question_text = sanitize_text_for_storage(str(question_text), max_length=MAX_QUESTION_TEXT_LENGTH)
                parts.append(f"Question: {question_text}")
                
                question_type = sanitize_text_for_storage(
                    str(question.get('question_type', 'technical')),
                    max_length=50
                )
                parts.append(f"Type: {question_type}")
                
                if question.get('answer_criteria'):
                    criteria = sanitize_text_for_storage(
                        str(question.get('answer_criteria')),
                        max_length=300
                    )
                    parts.append(f"Answer Criteria: {criteria}")
            else:
                question_text = sanitize_text_for_storage(str(question), max_length=MAX_QUESTION_TEXT_LENGTH)
                parts.append(f"Question: {question_text}")
            
            # Find corresponding response
            response_text = "No response provided"
            if i < len(user_responses):
                response = user_responses[i]
                if isinstance(response, dict):
                    response_text = response.get('response', response.get('text', ''))
                elif isinstance(response, str):
                    response_text = response
                
                # Sanitize response
                response_text = sanitize_text_for_storage(str(response_text), max_length=MAX_RESPONSE_TEXT_LENGTH)
            
            parts.append(f"Candidate Response: {response_text}")
        
        context = "\n".join(parts)
        
        # Final length check
        if len(context) > MAX_CONTEXT_LENGTH:
            logger.warning(f"Context length {len(context)} exceeds maximum, truncating")
            context = context[:MAX_CONTEXT_LENGTH]
        
        return context
    
    def _default_feedback(self) -> Dict[str, Any]:
        """Return default feedback when LLM is unavailable"""
        return {
            'summary': 'Coaching feedback generation is currently unavailable. Please try again later.',
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'next_steps': []
        }
    
    def is_available(self) -> bool:
        """Check if agent is available (OpenAI working)"""
        return self.openai_available


# Global agent instance (lazy initialization)
_agent_instance: Optional[RizAgent] = None


def get_riz_agent() -> RizAgent:
    """Get or create global Riz agent instance"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = RizAgent()
    
    return _agent_instance
