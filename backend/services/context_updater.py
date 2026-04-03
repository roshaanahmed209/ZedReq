"""
Context Updater Service
Handles user activity context collection, summarization, and storage in runtime_context JSONB
"""

import os
import json
import logging
from typing import Optional
from sqlalchemy.orm import Session

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from models.orm import JobPosting, Post, User, Description, UsersContext
from utils.api_security import sanitize_text_for_storage
from agents.Zed_agent import get_zed_agent

logger = logging.getLogger(__name__)


# System prompts for summarization
JOB_SUMMARY_PROMPT = """You are a job analysis assistant. Extract and summarize job postings in a very short format (max 200 characters).

Extract:
- Job intensity/demand level (high/medium/low)
- Experience level required (entry/mid/senior)
- Key skills required (comma-separated, top 5)
- Location (city, country, remote status)

Return ONLY a concise summary in this format:
"[Intensity] [Level] role requiring [top 3-5 skills]. Location: [location/remote]"

Be brief and factual."""

POST_SUMMARY_PROMPT = """You are a content analysis assistant. Summarize posts in a very short format (max 150 characters).

Extract:
- Main topics/themes discussed
- Content type (technical, career advice, personal story, industry news, etc.)
- Key concepts mentioned

Return ONLY a concise summary in this format:
"[Content type] about [main topics]. Key concepts: [2-3 key concepts]"

Be brief and factual."""

PROFILE_SUMMARY_PROMPT = """You are a profile analysis assistant. Summarize user profiles in a very short format (max 200 characters).

Extract:
- Current professional status/role
- Key skills (top 5)
- Industry/domain
- Career level (entry/mid/senior)

Return ONLY a concise summary in this format:
"[Level] [Role/Status] in [industry]. Skills: [top 3-5 skills]"

Be brief and factual."""


class ContextUpdater:
    """Service for updating user context from frontend actions"""
    
    def __init__(self, db: Session, openai_api_key: Optional[str] = None, model_name: str = "gpt-4o-mini"):
        """
        Initialize Context Updater
        
        Args:
            db: Database session
            openai_api_key: OpenAI API key (default: from env)
            model_name: OpenAI model to use for summarization
        """
        self.db = db
        openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        
        if not openai_api_key:
            logger.warning("OpenAI API key not found. Summarization will not work.")
            self.openai_available = False
            self.llm = None
        else:
            try:
                self.llm = ChatOpenAI(
                    model=model_name,
                    temperature=0.3,
                    api_key=openai_api_key
                )
                self.openai_available = True
                logger.info(f"ContextUpdater initialized with model {model_name}")
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e}")
                self.llm = None
                self.openai_available = False
    
    def _summarize_job(self, job: JobPosting) -> str:
        """
        Summarize job posting using LLM
        
        Args:
            job: JobPosting ORM object
            
        Returns:
            Summary string or fallback summary
        """
        if not self.openai_available or not self.llm:
            # Fallback summary without LLM
            skills = (job.skills_required or "")[:100] if job.skills_required else "Various skills"
            location = f"{job.location or 'Location not specified'}" + (" (Remote)" if job.is_remote else "")
            level = job.experience_level or "Not specified"
            return f"{level} role requiring {skills}. Location: {location}"
        
        try:
            job_text = f"""
Title: {job.title or ''}
Description: {job.description or ''}
Company: {job.company_name or ''}
Location: {job.location or ''}
Remote: {'Yes' if job.is_remote else 'No'}
Experience Level: {job.experience_level or 'Not specified'}
Skills Required: {job.skills_required or 'Not specified'}
Job Type: {job.job_type or 'Not specified'}
"""
            
            messages = [
                SystemMessage(content=JOB_SUMMARY_PROMPT),
                HumanMessage(content=f"Summarize this job posting:\n\n{job_text}")
            ]
            
            response = self.llm.invoke(messages)
            summary = response.content.strip()
            
            # Limit to 200 chars
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            return summary
        except Exception as e:
            logger.error(f"Failed to summarize job {job.job_id}: {e}")
            # Fallback
            skills = (job.skills_required or "")[:100] if job.skills_required else "Various skills"
            location = f"{job.location or 'Location not specified'}" + (" (Remote)" if job.is_remote else "")
            level = job.experience_level or "Not specified"
            return f"{level} role requiring {skills}. Location: {location}"
    
    def _summarize_post(self, post: Post) -> str:
        """
        Summarize post using LLM
        
        Args:
            post: Post ORM object
            
        Returns:
            Summary string or fallback summary
        """
        if not self.openai_available or not self.llm:
            # Fallback summary without LLM
            content = (post.post_desc or "")[:100] if post.post_desc else "Post content"
            return f"Post about: {content}"
        
        try:
            post_text = f"Post Description: {post.post_desc or 'No description'}"
            
            messages = [
                SystemMessage(content=POST_SUMMARY_PROMPT),
                HumanMessage(content=f"Summarize this post:\n\n{post_text}")
            ]
            
            response = self.llm.invoke(messages)
            summary = response.content.strip()
            
            # Limit to 150 chars
            if len(summary) > 150:
                summary = summary[:147] + "..."
            
            return summary
        except Exception as e:
            logger.error(f"Failed to summarize post {post.post_id}: {e}")
            # Fallback
            content = (post.post_desc or "")[:100] if post.post_desc else "Post content"
            return f"Post about: {content}"
    
    def _summarize_profile(self, user: User, description: Optional[Description] = None) -> str:
        """
        Summarize user profile using LLM
        
        Args:
            user: User ORM object
            description: Description ORM object (optional)
            
        Returns:
            Summary string or fallback summary
        """
        if not self.openai_available or not self.llm:
            # Fallback summary without LLM
            skills = (description.skills or "")[:100] if description and description.skills else "Various skills"
            status = description.current_status or "Professional" if description else "Professional"
            return f"{status} with skills: {skills}"
        
        try:
            about = description.about if description and description.about else ""
            skills = description.skills if description and description.skills else ""
            current_status = description.current_status if description and description.current_status else ""
            role = description.role if description and description.role else ""
            company = description.company if description and description.company else ""
            industry = description.industry if description and description.industry else ""
            
            profile_text = f"""
Name: {user.name or ''}
About: {about}
Skills: {skills}
Current Status: {current_status}
Role: {role}
Company: {company}
Industry: {industry}
"""
            
            messages = [
                SystemMessage(content=PROFILE_SUMMARY_PROMPT),
                HumanMessage(content=f"Summarize this user profile:\n\n{profile_text}")
            ]
            
            response = self.llm.invoke(messages)
            summary = response.content.strip()
            
            # Limit to 200 chars
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            return summary
        except Exception as e:
            logger.error(f"Failed to summarize profile for user {user.uid}: {e}")
            # Fallback
            skills = (description.skills or "")[:100] if description and description.skills else "Various skills"
            status = description.current_status or "Professional" if description else "Professional"
            return f"{status} with skills: {skills}"
    
    def _update_runtime_context(
        self, 
        user_id: int, 
        summary: str, 
        action_type: str, 
        entity_type: str, 
        entity_id: int
    ) -> bool:
        """
        Append summary to users_context.runtime_context JSONB
        
        Security & Scalability:
        - Limits runtime_context to max 1000 items (prevents unbounded growth)
        - Limits total size to ~500KB (prevents database bloat)
        - Removes oldest items when limit exceeded (FIFO)
        
        Args:
            user_id: User ID
            summary: Summary text to add
            action_type: Action type (apply, like, view)
            entity_type: Entity type (job, post, profile)
            entity_id: Entity ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sanitize summary before storing
            sanitized_summary = sanitize_text_for_storage(summary, max_length=500)
            
            # Get or create users_context record
            users_context = (
                self.db.query(UsersContext)
                .filter(UsersContext.user_id == user_id)
                .first()
            )
            
            new_item = [{
                "content": sanitized_summary,
                "action": action_type,
                "entity_type": entity_type,
                "entity_id": entity_id
            }]
            
            # Security: Limit runtime_context size to prevent abuse and database bloat
            MAX_CONTEXT_ITEMS = 1000  # Maximum number of items in runtime_context
            MAX_CONTEXT_SIZE_KB = 500  # Maximum size in KB (approximate)
            
            if users_context:
                # Update existing record - append to runtime_context
                if users_context.runtime_context:
                    # Convert JSONB to Python list, append, and save back
                    current_context = users_context.runtime_context
                    if isinstance(current_context, list):
                        # Check size limits before appending
                        import sys
                        current_size_kb = sys.getsizeof(str(current_context)) / 1024
                        
                        # Remove oldest items if we exceed max items
                        if len(current_context) >= MAX_CONTEXT_ITEMS:
                            # Keep only the most recent items (FIFO)
                            items_to_keep = MAX_CONTEXT_ITEMS - 1
                            current_context = current_context[-items_to_keep:]
                            logger.info(f"Trimmed runtime_context for user_id={user_id} to {items_to_keep} items")
                        
                        # Check size limit (approximate)
                        if current_size_kb >= MAX_CONTEXT_SIZE_KB:
                            # Remove oldest 10% of items
                            items_to_remove = max(1, len(current_context) // 10)
                            current_context = current_context[items_to_remove:]
                            logger.info(f"Trimmed runtime_context for user_id={user_id} by {items_to_remove} items due to size limit")
                        
                        # Append new item to existing list
                        users_context.runtime_context = current_context + new_item
                    else:
                        # If it's not a list, initialize with new item
                        users_context.runtime_context = new_item
                else:
                    # Initialize with new array
                    users_context.runtime_context = new_item
            else:
                # Create new record
                users_context = UsersContext(
                    user_id=user_id,
                    runtime_context=new_item
                )
                self.db.add(users_context)
            
            self.db.commit()
            logger.info(f"Updated runtime_context for user_id={user_id}, action={action_type}, entity={entity_type}:{entity_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update runtime_context for user_id={user_id}: {e}", exc_info=True)
            return False
    
    def update_context_from_action(
        self, 
        user_id: int, 
        action: str, 
        entity_type: str, 
        entity_id: int
    ) -> bool:
        """
        Update context from frontend action
        
        Security: Validates entity exists and is accessible before tracking
        
        Args:
            user_id: User ID performing the action
            action: Action type (apply, like, view)
            entity_type: Entity type (job, post, profile)
            entity_id: Entity ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Security: Validate entity_id is within reasonable bounds
            if entity_id <= 0 or entity_id > 2147483647:  # Max 32-bit int
                logger.warning(f"Invalid entity_id {entity_id} for user_id={user_id}")
                return False
            
            summary = None
            
            if entity_type == "job":
                # Fetch job from database
                job = (
                    self.db.query(JobPosting)
                    .filter(JobPosting.job_id == entity_id)
                    .filter(JobPosting.status == 'active')
                    .first()
                )
                
                if not job:
                    logger.warning(f"Job {entity_id} not found or not active for user_id={user_id}")
                    return False
                
                summary = self._summarize_job(job)
                
            elif entity_type == "post":
                # Fetch post from database
                post = (
                    self.db.query(Post)
                    .filter(Post.post_id == entity_id)
                    .filter(Post.not_deleted())
                    .first()
                )
                
                if not post:
                    logger.warning(f"Post {entity_id} not found or deleted for user_id={user_id}")
                    return False
                
                summary = self._summarize_post(post)
                
            elif entity_type == "profile":
                # Security: Prevent users from tracking their own profile views
                if entity_id == user_id:
                    logger.debug(f"User {user_id} attempted to track own profile view (skipped)")
                    return False
                
                # Fetch user and description from database
                user = (
                    self.db.query(User)
                    .filter(User.uid == entity_id)
                    .first()
                )
                
                if not user:
                    logger.warning(f"User {entity_id} not found for tracking by user_id={user_id}")
                    return False
                
                description = None
                if user.description_id:
                    description = (
                        self.db.query(Description)
                        .filter(Description.desc_id == user.description_id)
                        .first()
                    )
                
                summary = self._summarize_profile(user, description)
                
            else:
                logger.warning(f"Unknown entity_type: {entity_type} for user_id={user_id}")
                return False
            
            if summary:
                return self._update_runtime_context(
                    user_id=user_id,
                    summary=summary,
                    action_type=action,
                    entity_type=entity_type,
                    entity_id=entity_id
                )
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update context from action for user_id={user_id}, entity={entity_type}:{entity_id}: {e}", exc_info=True)
            return False
    
    def refresh_and_update_zed_context(self, user_id: int) -> bool:
        """
        Refresh runtime_context and trigger Zed Agent to update zed column
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get Zed Agent and trigger context update
            zed_agent = get_zed_agent()
            
            if not zed_agent.is_available():
                logger.warning("Zed Agent not available, cannot update zed context")
                return False
            
            # Call Zed Agent's update_context method
            # This will process runtime_context and merge it into zed column
            updated_context = zed_agent.update_context(user_id)
            
            if updated_context:
                logger.info(f"Successfully updated zed context for user_id={user_id} on logout")
                return True
            else:
                logger.warning(f"Zed Agent update_context returned None for user_id={user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to refresh and update zed context for user_id={user_id}: {e}")
            return False
