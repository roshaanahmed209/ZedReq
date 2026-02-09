"""
Riz Agent - Post-Interview Coaching Feedback
AI-powered agent that provides personalized coaching feedback after interview completion
"""

import os
import logging
import json
from typing import Optional, Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


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
        model_name: str = "gpt-4o-mini"
    ):
        """
        Initialize Riz Agent with OpenAI client
        
        Args:
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use
        """
        # Initialize OpenAI API key
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Riz agent will not work.")
            self.openai_available = False
        else:
            self.openai_available = True
        
        # Initialize LangChain OpenAI client
        if self.openai_available:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.7,  # Slightly higher for more natural coaching tone
                    api_key=openai_api_key
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
            
            # Generate coaching feedback using LLM
            messages = [
                SystemMessage(content=RIZ_COACHING_PROMPT),
                HumanMessage(content=context)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Try to extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            feedback = json.loads(content)
            
            # Validate and ensure required fields
            validated_feedback = {
                'summary': feedback.get('summary', 'No summary available'),
                'strengths': feedback.get('strengths', []),
                'weaknesses': feedback.get('weaknesses', []),
                'recommendations': feedback.get('recommendations', []),
                'next_steps': feedback.get('next_steps', [])
            }
            
            # Ensure lists are actually lists
            for key in ['strengths', 'weaknesses', 'recommendations', 'next_steps']:
                if not isinstance(validated_feedback[key], list):
                    validated_feedback[key] = []
            
            logger.info(f"Generated coaching feedback for {job_title} at {company_name}")
            return validated_feedback
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse coaching feedback JSON: {e}")
            logger.debug(f"Response content: {content[:500]}")
            return self._default_feedback()
        except Exception as e:
            logger.error(f"Failed to generate coaching feedback: {e}")
            return self._default_feedback()
    
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
        """Build context string for coaching feedback generation"""
        parts = []
        
        parts.append("## Job Information")
        parts.append(f"Position: {job_title}")
        parts.append(f"Company: {company_name}")
        if job_description:
            parts.append(f"\nJob Description:\n{job_description[:1000]}")
        
        parts.append("\n## Interview Performance")
        if overall_score is not None:
            parts.append(f"Overall Score: {overall_score}/100")
        
        if score_breakdown:
            parts.append("\nScore Breakdown:")
            for category, score in score_breakdown.items():
                parts.append(f"- {category}: {score}/100")
        
        if tav_check_feedback:
            parts.append(f"\nTechnical Evaluation Feedback:\n{tav_check_feedback[:1500]}")
        
        parts.append("\n## Interview Questions and Responses\n")
        
        # Match responses to questions
        for i, question in enumerate(questions):
            parts.append(f"\n--- Question {i + 1} ---")
            if isinstance(question, dict):
                parts.append(f"Question: {question.get('question_text', question.get('text', ''))}")
                parts.append(f"Type: {question.get('question_type', 'technical')}")
                if question.get('answer_criteria'):
                    parts.append(f"Answer Criteria: {question.get('answer_criteria')}")
            else:
                parts.append(f"Question: {question}")
            
            # Find corresponding response
            response_text = ""
            if i < len(user_responses):
                response = user_responses[i]
                if isinstance(response, dict):
                    response_text = response.get('response', response.get('text', ''))
                elif isinstance(response, str):
                    response_text = response
            else:
                response_text = "No response provided"
            
            parts.append(f"Candidate Response: {response_text}")
        
        return "\n".join(parts)
    
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
