"""
Tav_check_agent - Interview Response Analyzer
AI agent that analyzes user interview responses and provides scores and feedback
"""
import os
import logging
import json
from typing import Dict, Any, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


# System prompt for response analysis
ANALYSIS_PROMPT = """You are an expert interview evaluator. Analyze a candidate's interview responses and provide comprehensive scoring and feedback.

You will receive:
1. Interview questions with answer criteria
2. The candidate's responses to each question
3. Job context

For each question, evaluate:
- How well the response addresses the question
- Whether key points from answer_criteria are covered
- Technical accuracy and depth
- Communication clarity
- Problem-solving approach (if applicable)

Calculate scores for each question (0-100) and overall category scores:
- technical_score: Technical knowledge and accuracy
- communication_score: Clarity, articulation, professionalism
- problem_solving_score: Logical thinking, approach to problems
- domain_knowledge_score: Relevant experience and domain expertise

Generate an overall_score (0-100) as a weighted average:
- Technical: 35%
- Communication: 25%
- Problem-solving: 20%
- Domain Knowledge: 20%

Return ONLY a JSON object with this structure:
{
  "overall_score": 85,
  "score_breakdown": {
    "technical_score": 90,
    "communication_score": 80,
    "problem_solving_score": 85,
    "domain_knowledge_score": 85
  },
  "question_scores": [
    {
      "question_index": 0,
      "score": 88,
      "feedback": "Strong technical answer covering key concepts..."
    },
    ...
  ],
  "detailed_feedback": "Overall, the candidate demonstrated...",
  "strengths": ["Strong technical knowledge", "Clear communication"],
  "weaknesses": ["Could improve problem-solving approach", "Needs more domain examples"],
  "improvement_suggestions": ["Practice explaining complex concepts", "Prepare more real-world examples"]
}

Be thorough, constructive, and specific in your feedback."""


class TavCheckAgent:
    """AI Agent for analyzing interview responses and generating scores"""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o"
    ):
        """
        Initialize Tav_check_agent
        
        Args:
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use
        """
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Response analysis will not work.")
            self.llm = None
            self.available = False
        else:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.3,  # Lower temperature for more consistent evaluation
                    api_key=openai_api_key
                )
                self.available = True
                logger.info(f"Tav_check_agent initialized with model {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.llm = None
                self.available = False
    
    def analyze_interview_responses(
        self,
        questions: List[Dict[str, Any]],
        user_responses: List[Dict[str, Any]],
        job_context: str
    ) -> Dict[str, Any]:
        """
        Analyze interview responses and generate scores/feedback
        
        Args:
            questions: List of interview questions with criteria
            user_responses: List of user responses (from Tavus transcript)
            job_context: Job description and context
            
        Returns:
            Dictionary with scores, feedback, and analysis
        """
        if not self.available or not self.llm:
            logger.error("LLM not available for response analysis")
            return self._default_analysis()
        
        try:
            # Build analysis context
            analysis_context = self._build_analysis_context(
                questions, user_responses, job_context
            )
            
            # Generate analysis using LLM
            messages = [
                SystemMessage(content=ANALYSIS_PROMPT),
                HumanMessage(content=analysis_context)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content
            
            # Parse JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(content)
            
            # Validate and ensure required fields
            validated_analysis = {
                'overall_score': max(0, min(100, int(analysis.get('overall_score', 0)))),
                'score_breakdown': {
                    'technical_score': max(0, min(100, int(analysis.get('score_breakdown', {}).get('technical_score', 0)))),
                    'communication_score': max(0, min(100, int(analysis.get('score_breakdown', {}).get('communication_score', 0)))),
                    'problem_solving_score': max(0, min(100, int(analysis.get('score_breakdown', {}).get('problem_solving_score', 0)))),
                    'domain_knowledge_score': max(0, min(100, int(analysis.get('score_breakdown', {}).get('domain_knowledge_score', 0)))),
                },
                'question_scores': analysis.get('question_scores', []),
                'detailed_feedback': analysis.get('detailed_feedback', ''),
                'strengths': analysis.get('strengths', []),
                'weaknesses': analysis.get('weaknesses', []),
                'improvement_suggestions': analysis.get('improvement_suggestions', [])
            }
            
            logger.info(f"Analysis complete. Overall score: {validated_analysis['overall_score']}")
            return validated_analysis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content: {content[:500]}")
            return self._default_analysis()
        except Exception as e:
            logger.error(f"Failed to analyze interview responses: {e}")
            import traceback
            traceback.print_exc()
            return self._default_analysis()
    
    def _build_analysis_context(
        self,
        questions: List[Dict[str, Any]],
        user_responses: List[Dict[str, Any]],
        job_context: str
    ) -> str:
        """Build context string for analysis"""
        parts = []
        
        parts.append("## Job Context")
        parts.append(job_context)
        parts.append("\n## Interview Questions and Responses\n")
        
        # Match responses to questions
        for i, question in enumerate(questions):
            parts.append(f"\n--- Question {i + 1} ---")
            parts.append(f"Question: {question.get('question_text', '')}")
            parts.append(f"Type: {question.get('question_type', 'technical')}")
            parts.append(f"Answer Criteria: {question.get('answer_criteria', '')}")
            parts.append(f"Expected Key Points: {', '.join(question.get('expected_key_points', []))}")
            
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
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when LLM is unavailable"""
        return {
            'overall_score': 0,
            'score_breakdown': {
                'technical_score': 0,
                'communication_score': 0,
                'problem_solving_score': 0,
                'domain_knowledge_score': 0
            },
            'question_scores': [],
            'detailed_feedback': 'Analysis unavailable. Please try again later.',
            'strengths': [],
            'weaknesses': [],
            'improvement_suggestions': []
        }
