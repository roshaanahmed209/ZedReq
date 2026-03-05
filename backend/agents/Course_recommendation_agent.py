"""
Course Recommendation Agent - AI-powered course recommendation system
Generates personalized course recommendations based on user's Zed context
"""

import os
import logging
import json
import re
from typing import Optional, List, Dict, Any
from difflib import SequenceMatcher

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from config.database import get_connection_params, Database
from config.database_orm import get_db
from models.orm.lms_course import LMSCourse
from models.orm.lms_recommendation import LMSRecommendation

logger = logging.getLogger(__name__)


# System prompt for extracting learning needs from Zed context
EXTRACT_LEARNING_NEEDS_PROMPT = """You are an AI assistant that analyzes user context to identify learning needs and interests.

Your task is to extract:
1. Technical skills the user wants to learn or improve
2. Career goals and professional interests
3. Knowledge gaps based on their current skills
4. Topics they've shown interest in (from highlighted topics section)

Return a JSON object with:
{
  "learning_interests": ["skill1", "skill2", ...],
  "career_goals": ["goal1", "goal2", ...],
  "knowledge_gaps": ["gap1", "gap2", ...],
  "highlighted_topics": ["topic1", "topic2", ...]
}

Return ONLY the JSON object, no additional text."""


# System prompt for generating course ideas
COURSE_GENERATION_PROMPT = """You are an AI assistant that generates educational course ideas based on user learning needs.

Based on the user's learning interests, career goals, knowledge gaps, and highlighted topics, generate course recommendations.

For each course, provide:
- A clear, specific course title (e.g., "Python for Data Science", "React Fundamentals")
- A detailed description explaining what the course covers
- A category (e.g., "Python", "Web Development", "Data Science", "Machine Learning")
- Appropriate difficulty level (beginner, intermediate, advanced, expert)
- Estimated number of lessons (reasonable estimate)
- A reason why this course matches the user's interests

Return a JSON array of course objects:
[
  {
    "title": "Course Title",
    "description": "Detailed course description...",
    "category": "Category Name",
    "difficulty": "beginner|intermediate|advanced|expert",
    "estimated_lessons": 10,
    "reason": "Why this course matches user interests..."
  },
  ...
]

Generate 3-5 courses that are:
- Relevant to user's interests and goals
- Cover different aspects of their learning needs
- Appropriate for their skill level
- Practical and actionable

Return ONLY the JSON array, no additional text."""


class CourseRecommendationAgent:
    """AI Agent for generating personalized course recommendations from Zed context"""
    
    def __init__(self, openai_api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        """
        Initialize Course Recommendation Agent
        
        Args:
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model_name: LLM model to use (default: gpt-4o-mini)
        """
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.model_name = model_name
        self.llm = None
        self.openai_available = False
        
        if self.openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=self.openai_api_key,
                    temperature=0.7
                )
                self.openai_available = True
                logger.info(f"Course Recommendation Agent initialized with model: {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI for Course Recommendation Agent: {e}")
                self.openai_available = False
        else:
            logger.warning("OpenAI API key not found, Course Recommendation Agent unavailable")
    
    def is_available(self) -> bool:
        """Check if agent is available (OpenAI configured)"""
        return self.openai_available and self.llm is not None
    
    def _get_zed_context(self, user_id: int) -> Optional[str]:
        """
        Retrieve Zed context from database
        
        Args:
            user_id: User ID
            
        Returns:
            Zed context text or None
        """
        try:
            db = Database(get_connection_params())
            result = db.fetch_one(
                "SELECT zed FROM users_context WHERE user_id = %s",
                (user_id,)
            )
            db.close()
            
            if result and result.get('zed'):
                logger.info(f"[COURSE-REC] Retrieved Zed context for user_id={user_id} ({len(result['zed'])} chars)")
                return result['zed']
            
            logger.warning(f"[COURSE-REC] No Zed context found for user_id={user_id}")
            return None
        except Exception as e:
            logger.error(f"[COURSE-REC] Failed to retrieve Zed context for user_id={user_id}: {e}", exc_info=True)
            return None
    
    def _extract_learning_needs(self, context: str) -> Dict[str, Any]:
        """
        Extract learning needs from Zed context using LLM
        
        Args:
            context: Zed context text
            
        Returns:
            Dictionary with learning_interests, career_goals, knowledge_gaps, highlighted_topics
        """
        if not self.is_available():
            logger.error("[COURSE-REC] LLM not available for extracting learning needs")
            return {}
        
        try:
            # Limit context length to avoid token limits
            context_preview = context[:3000] if len(context) > 3000 else context
            
            prompt = f"""Analyze the following user context and extract learning needs:

{context_preview}

Extract:
1. Technical skills they want to learn or improve
2. Career goals and professional interests
3. Knowledge gaps (what they need to learn)
4. Highlighted topics of interest (if mentioned in a "Preferred Topics" or "Highlighted Topics" section)

Return a JSON object with learning_interests, career_goals, knowledge_gaps, and highlighted_topics arrays."""
            
            messages = [
                SystemMessage(content=EXTRACT_LEARNING_NEEDS_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            learning_needs = json.loads(content)
            logger.info(f"[COURSE-REC] Extracted learning needs: {len(learning_needs.get('learning_interests', []))} interests, {len(learning_needs.get('career_goals', []))} goals")
            return learning_needs
            
        except json.JSONDecodeError as e:
            logger.error(f"[COURSE-REC] Failed to parse learning needs JSON: {e}")
            logger.debug(f"[COURSE-REC] Response content: {content[:500]}")
            return {}
        except Exception as e:
            logger.error(f"[COURSE-REC] Failed to extract learning needs: {e}", exc_info=True)
            return {}
    
    def _generate_course_ideas(self, learning_needs: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generate course ideas from learning needs using LLM
        
        Args:
            learning_needs: Dictionary with learning interests, career goals, etc.
            limit: Maximum number of courses to generate
            
        Returns:
            List of course idea dictionaries
        """
        if not self.is_available():
            logger.error("[COURSE-REC] LLM not available for generating course ideas")
            return []
        
        try:
            # Build prompt from learning needs
            interests = learning_needs.get('learning_interests', [])
            goals = learning_needs.get('career_goals', [])
            gaps = learning_needs.get('knowledge_gaps', [])
            topics = learning_needs.get('highlighted_topics', [])
            
            prompt_parts = []
            if interests:
                prompt_parts.append(f"Learning Interests: {', '.join(interests[:10])}")
            if goals:
                prompt_parts.append(f"Career Goals: {', '.join(goals[:10])}")
            if gaps:
                prompt_parts.append(f"Knowledge Gaps: {', '.join(gaps[:10])}")
            if topics:
                prompt_parts.append(f"Highlighted Topics: {', '.join(topics[:10])}")
            
            if not prompt_parts:
                logger.warning("[COURSE-REC] No learning needs found, cannot generate courses")
                return []
            
            prompt = f"""Generate {limit} personalized course recommendations based on:

{chr(10).join(prompt_parts)}

Generate courses that are practical, relevant, and match the user's learning needs."""
            
            messages = [
                SystemMessage(content=COURSE_GENERATION_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            courses = json.loads(content)
            if isinstance(courses, list):
                logger.info(f"[COURSE-REC] Generated {len(courses)} course ideas")
                return courses[:limit]  # Ensure we don't exceed limit
            else:
                logger.warning(f"[COURSE-REC] Unexpected course format: {type(courses)}")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"[COURSE-REC] Failed to parse course ideas JSON: {e}")
            logger.debug(f"[COURSE-REC] Response content: {content[:500]}")
            return []
        except Exception as e:
            logger.error(f"[COURSE-REC] Failed to generate course ideas: {e}", exc_info=True)
            return []
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _find_similar_course(self, title: str, category: str, db_session) -> Optional[LMSCourse]:
        """
        Find existing course with similar title or category
        
        Args:
            title: Course title to match
            category: Course category to match
            db_session: Database session
            
        Returns:
            Matching LMSCourse or None
        """
        try:
            threshold = float(os.environ.get('COURSE_MATCH_SIMILARITY_THRESHOLD', '0.7'))
            
            # Get all active courses
            all_courses = db_session.query(LMSCourse).filter(LMSCourse.is_active == True).all()
            
            best_match = None
            best_score = 0.0
            
            for course in all_courses:
                # Calculate title similarity
                title_score = self._calculate_similarity(title, course.title)
                
                # Calculate category similarity if category matches
                category_score = 0.0
                if category and course.category:
                    category_score = self._calculate_similarity(category, course.category)
                
                # Combined score (title weighted more)
                combined_score = (title_score * 0.7) + (category_score * 0.3)
                
                if combined_score > best_score and combined_score >= threshold:
                    best_score = combined_score
                    best_match = course
            
            if best_match:
                logger.info(f"[COURSE-REC] Found similar course: '{best_match.title}' (similarity: {best_score:.2f})")
            
            return best_match
            
        except Exception as e:
            logger.error(f"[COURSE-REC] Error finding similar course: {e}", exc_info=True)
            return None
    
    def _create_course(self, course_idea: Dict[str, Any], db_session) -> Optional[LMSCourse]:
        """
        Create a new course from course idea
        
        Args:
            course_idea: Course idea dictionary from LLM
            db_session: Database session
            
        Returns:
            Created LMSCourse or None
        """
        try:
            # Generate icon from title (first 2 characters)
            icon = course_idea.get('title', '📚')[:2].upper() if len(course_idea.get('title', '')) >= 2 else '📚'
            
            course = LMSCourse(
                title=course_idea.get('title', 'Untitled Course'),
                description=course_idea.get('description', ''),
                icon=icon,
                lessons=course_idea.get('estimated_lessons', 0),
                duration=None,  # Can be calculated later
                category=course_idea.get('category', 'General'),
                difficulty=course_idea.get('difficulty', 'beginner'),
                is_active=True
            )
            
            db_session.add(course)
            db_session.commit()
            db_session.refresh(course)
            
            logger.info(f"[COURSE-REC] Created new course: '{course.title}' (id={course.id})")
            return course
            
        except Exception as e:
            logger.error(f"[COURSE-REC] Failed to create course: {e}", exc_info=True)
            db_session.rollback()
            return None
    
    def _match_or_create_courses(self, course_ideas: List[Dict[str, Any]], db_session) -> List[Dict[str, Any]]:
        """
        Match course ideas to existing courses or create new ones
        
        Args:
            course_ideas: List of course idea dictionaries
            db_session: Database session
            
        Returns:
            List of dictionaries with 'course' (LMSCourse) and 'reason' (str)
        """
        matched_courses = []
        
        for idea in course_ideas:
            try:
                title = idea.get('title', '')
                category = idea.get('category', '')
                reason = idea.get('reason', 'Based on your interests')
                
                # Try to find similar existing course
                existing_course = self._find_similar_course(title, category, db_session)
                
                if existing_course:
                    # Use existing course
                    matched_courses.append({
                        'course': existing_course,
                        'reason': reason,
                        'is_new': False
                    })
                    logger.info(f"[COURSE-REC] Matched to existing course: '{existing_course.title}'")
                else:
                    # Create new course
                    new_course = self._create_course(idea, db_session)
                    if new_course:
                        matched_courses.append({
                            'course': new_course,
                            'reason': reason,
                            'is_new': True
                        })
                    else:
                        logger.warning(f"[COURSE-REC] Failed to create course for idea: '{title}'")
                        
            except Exception as e:
                logger.error(f"[COURSE-REC] Error processing course idea: {e}", exc_info=True)
                continue
        
        return matched_courses
    
    def _create_recommendations(self, user_id: int, matched_courses: List[Dict[str, Any]], db_session) -> int:
        """
        Create recommendation records in database
        
        Args:
            user_id: User ID
            matched_courses: List of matched courses with reasons
            db_session: Database session
            
        Returns:
            Number of recommendations created
        """
        created_count = 0
        
        for item in matched_courses:
            try:
                course = item['course']
                reason = item['reason']
                
                # Check if recommendation already exists
                existing = db_session.query(LMSRecommendation).filter(
                    LMSRecommendation.user_id == user_id,
                    LMSRecommendation.course_id == course.id,
                    LMSRecommendation.is_dismissed == False
                ).first()
                
                if existing:
                    logger.debug(f"[COURSE-REC] Recommendation already exists for user_id={user_id}, course_id={course.id}")
                    continue
                
                # Calculate priority based on position (first courses have higher priority)
                priority = 10 - created_count  # Higher priority for earlier recommendations
                
                recommendation = LMSRecommendation(
                    user_id=user_id,
                    course_id=course.id,
                    reason=reason,
                    priority=priority,
                    is_dismissed=False
                )
                
                db_session.add(recommendation)
                created_count += 1
                
            except Exception as e:
                logger.error(f"[COURSE-REC] Failed to create recommendation: {e}", exc_info=True)
                continue
        
        try:
            db_session.commit()
            logger.info(f"[COURSE-REC] Created {created_count} recommendations for user_id={user_id}")
        except Exception as e:
            logger.error(f"[COURSE-REC] Failed to commit recommendations: {e}", exc_info=True)
            db_session.rollback()
            created_count = 0
        
        return created_count
    
    def generate_course_recommendations(self, user_id: int, limit: int = 5) -> Dict[str, Any]:
        """
        Main method: Generate course recommendations for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations to generate
            
        Returns:
            Dictionary with success status, recommendations count, and details
        """
        result = {
            'success': False,
            'user_id': user_id,
            'recommendations_created': 0,
            'courses_created': 0,
            'courses_matched': 0,
            'error': None
        }
        
        logger.info(f"[COURSE-REC] ===== START: Generating recommendations for user_id={user_id} =====")
        
        if not self.is_available():
            result['error'] = "Course Recommendation Agent not available (OpenAI not configured)"
            logger.error("[COURSE-REC] Agent not available")
            return result
        
        try:
            # Step 1: Get Zed context
            context = self._get_zed_context(user_id)
            if not context:
                result['error'] = "No Zed context found for user"
                logger.warning(f"[COURSE-REC] No Zed context for user_id={user_id}")
                return result
            
            # Step 2: Extract learning needs
            learning_needs = self._extract_learning_needs(context)
            if not learning_needs:
                result['error'] = "Could not extract learning needs from context"
                logger.warning(f"[COURSE-REC] No learning needs extracted for user_id={user_id}")
                return result
            
            # Step 3: Generate course ideas
            course_ideas = self._generate_course_ideas(learning_needs, limit=limit)
            if not course_ideas:
                result['error'] = "Could not generate course ideas"
                logger.warning(f"[COURSE-REC] No course ideas generated for user_id={user_id}")
                return result
            
            # Step 4: Match or create courses
            db_session = next(get_db())
            try:
                matched_courses = self._match_or_create_courses(course_ideas, db_session)
                
                if not matched_courses:
                    result['error'] = "Could not match or create courses"
                    logger.warning(f"[COURSE-REC] No courses matched/created for user_id={user_id}")
                    return result
                
                # Count new vs matched courses
                courses_created = sum(1 for item in matched_courses if item.get('is_new', False))
                courses_matched = len(matched_courses) - courses_created
                
                # Step 5: Create recommendations
                recommendations_created = self._create_recommendations(user_id, matched_courses, db_session)
                
                result['success'] = True
                result['recommendations_created'] = recommendations_created
                result['courses_created'] = courses_created
                result['courses_matched'] = courses_matched
                
                logger.info(f"[COURSE-REC] ===== SUCCESS: Created {recommendations_created} recommendations ({courses_created} new courses, {courses_matched} matched) =====")
                
            finally:
                db_session.close()
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"[COURSE-REC] ===== ERROR: Failed to generate recommendations: {e} =====", exc_info=True)
        
        return result


# Singleton pattern for agent instance
_course_recommendation_agent_instance: Optional[CourseRecommendationAgent] = None


def get_course_recommendation_agent() -> CourseRecommendationAgent:
    """Get singleton instance of Course Recommendation Agent"""
    global _course_recommendation_agent_instance
    
    if _course_recommendation_agent_instance is None:
        _course_recommendation_agent_instance = CourseRecommendationAgent()
    
    return _course_recommendation_agent_instance
