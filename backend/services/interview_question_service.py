"""
Interview Question Service
Generates interview questions and system prompts for Tavus interviews
"""
import os
import logging
import json
from typing import List, Dict, Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from models.orm.job_posting import JobPosting

logger = logging.getLogger(__name__)


# System prompt for question generation
QUESTION_GENERATION_PROMPT = """You are an expert technical interviewer. Generate comprehensive interview questions for a job position.

Based on the job description provided, create 5-7 interview questions that cover:
1. Technical skills and knowledge
2. Problem-solving abilities
3. Domain expertise
4. Behavioral/experience-based questions

For each question, provide:
- question_text: The actual question to ask
- question_type: One of "technical", "behavioral", "problem_solving", or "domain_knowledge"
- answer_criteria: What to look for in a good answer (key points, concepts, skills)
- expected_key_points: List of important points the answer should cover
- difficulty_level: "beginner", "intermediate", or "advanced"

Return ONLY a JSON array of question objects. Format:
[
  {
    "question_text": "...",
    "question_type": "technical",
    "answer_criteria": "...",
    "expected_key_points": ["point1", "point2", ...],
    "difficulty_level": "intermediate"
  },
  ...
]

Generate questions that are specific to the job requirements and will effectively assess the candidate's suitability."""


class InterviewQuestionService:
    """Service for generating interview questions and system prompts"""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-4o"
    ):
        """
        Initialize interview question service
        
        Args:
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use
        """
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Question generation will not work.")
            self.llm = None
            self.available = False
        else:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.7,
                    api_key=openai_api_key
                )
                self.available = True
                logger.info(f"InterviewQuestionService initialized with model {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.llm = None
                self.available = False
    
    def generate_interview_questions(self, job: JobPosting) -> List[Dict[str, Any]]:
        """
        Generate interview questions based on job description
        
        Args:
            job: JobPosting object
            
        Returns:
            List of question dictionaries with all required fields
        """
        if not self.available or not self.llm:
            logger.error("LLM not available for question generation")
            return []
        
        try:
            # Build job context
            job_context = self._build_job_context(job)
            
            # Generate questions using LLM
            messages = [
                SystemMessage(content=QUESTION_GENERATION_PROMPT),
                HumanMessage(content=job_context)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content
            
            # Parse JSON response
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            questions = json.loads(content)
            
            # Validate and ensure all required fields
            validated_questions = []
            for q in questions:
                if isinstance(q, dict) and 'question_text' in q:
                    validated_questions.append({
                        'question_text': q.get('question_text', ''),
                        'question_type': q.get('question_type', 'technical'),
                        'answer_criteria': q.get('answer_criteria', ''),
                        'expected_key_points': q.get('expected_key_points', []),
                        'difficulty_level': q.get('difficulty_level', 'intermediate')
                    })
            
            logger.info(f"Generated {len(validated_questions)} interview questions for job {job.job_id}")
            return validated_questions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response content: {content[:500]}")
            return []
        except Exception as e:
            logger.error(f"Failed to generate interview questions: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def generate_system_prompt(
        self,
        job: JobPosting,
        questions: List[Dict[str, Any]]
    ) -> str:
        """
        Generate system prompt for Tavus interviewer
        
        Args:
            job: JobPosting object
            questions: List of generated interview questions
            
        Returns:
            Comprehensive system prompt string
        """
        # Build job context
        job_context = self._build_job_context(job)
        
        # Format questions with criteria
        questions_text = ""
        for i, q in enumerate(questions, 1):
            questions_text += f"\n\nQuestion {i}: {q['question_text']}\n"
            questions_text += f"Type: {q['question_type']}\n"
            questions_text += f"Answer Criteria: {q['answer_criteria']}\n"
            questions_text += f"Expected Key Points: {', '.join(q.get('expected_key_points', []))}\n"
            questions_text += f"Difficulty: {q.get('difficulty_level', 'intermediate')}"
        
        system_prompt = f"""You are a professional technical interviewer conducting a mock interview for a job position.

## Job Context
{job_context}

## Interview Questions
You will ask the following questions during the interview:
{questions_text}

## Your Role
- Conduct a professional, friendly interview
- Ask each question clearly and give the candidate time to respond
- Listen actively to the candidate's responses
- If the candidate's answer is unclear, ask follow-up questions
- Maintain a professional and encouraging tone
- After all questions, thank the candidate and conclude the interview

## Evaluation Guidelines
While conducting the interview, pay attention to:
1. Technical Knowledge: Does the candidate demonstrate understanding of required skills?
2. Communication: Is the candidate clear, articulate, and professional?
3. Problem-Solving: Does the candidate show logical thinking and problem-solving approach?
4. Domain Expertise: Does the candidate have relevant experience and knowledge?

## Conversation Flow
1. Greet the candidate warmly
2. Introduce yourself and the interview format
3. Ask each question in order, allowing time for responses
4. Ask follow-up questions if needed for clarification
5. Conclude professionally after all questions

Remember: This is a mock interview to help the candidate practice. Be supportive while maintaining professional standards."""

        return system_prompt
    
    def _build_job_context(self, job: JobPosting) -> str:
        """Build comprehensive job context string"""
        parts = []
        
        parts.append(f"Job Title: {job.title}")
        
        if job.company_name:
            parts.append(f"Company: {job.company_name}")
        
        if job.description:
            parts.append(f"\nJob Description:\n{job.description}")
        
        if job.location:
            parts.append(f"Location: {job.location}")
        
        if job.job_type:
            parts.append(f"Job Type: {job.job_type}")
        
        if job.is_remote:
            parts.append("Remote: Yes")
        
        if job.experience_level:
            parts.append(f"Experience Level: {job.experience_level}")
        
        if job.skills_required:
            parts.append(f"\nRequired Skills:\n{job.skills_required}")
        
        if job.salary_min or job.salary_max:
            salary_parts = []
            if job.salary_min:
                salary_parts.append(f"${job.salary_min:,}")
            if job.salary_max:
                salary_parts.append(f"${job.salary_max:,}")
            parts.append(f"Salary Range: {' - '.join(salary_parts)}")
        
        return "\n".join(parts)
