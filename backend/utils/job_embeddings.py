"""
Job Embedding Utilities
Functions for generating embeddings for jobs and user profiles
"""
import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from langchain_openai import OpenAIEmbeddings
from models.orm.job_posting import JobPosting
from config.database import get_database

logger = logging.getLogger(__name__)

# Initialize OpenAI embeddings client
_embeddings_client: Optional[OpenAIEmbeddings] = None

def get_embeddings_client() -> Optional[OpenAIEmbeddings]:
    """Get or create OpenAI embeddings client"""
    global _embeddings_client
    if _embeddings_client is None:
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not found. Embedding generation will not work.")
            return None
        try:
            _embeddings_client = OpenAIEmbeddings(
                model="text-embedding-3-large",
                api_key=openai_api_key
            )
            logger.info("OpenAI embeddings client initialized (text-embedding-3-large)")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI embeddings client: {e}")
            return None
    return _embeddings_client


def job_to_text(job: JobPosting) -> str:
    """
    Convert a JobPosting object to a structured text representation for embedding.
    
    Args:
        job: JobPosting ORM object
        
    Returns:
        Structured text string combining all relevant job information
    """
    parts = []
    
    # Title
    if job.title:
        parts.append(f"Job Title: {job.title}")
    
    # Company
    if job.company_name:
        parts.append(f"Company: {job.company_name}")
    
    # Description
    if job.description:
        parts.append(f"Description: {job.description}")
    
    # Location
    if job.location:
        parts.append(f"Location: {job.location}")
    
    # Job Type
    if job.job_type:
        parts.append(f"Job Type: {job.job_type}")
    
    # Remote status
    if job.is_remote:
        parts.append("Remote: Yes")
    else:
        parts.append("Remote: No")
    
    # Experience Level
    if job.experience_level:
        parts.append(f"Experience Level: {job.experience_level}")
    
    # Skills Required
    if job.skills_required:
        parts.append(f"Required Skills: {job.skills_required}")
    
    # Salary Range (if available)
    if job.salary_min or job.salary_max:
        salary_parts = []
        if job.salary_min:
            salary_parts.append(f"${job.salary_min:,}")
        if job.salary_max:
            salary_parts.append(f"${job.salary_max:,}")
        parts.append(f"Salary Range: {' - '.join(salary_parts)}")
    
    return "\n".join(parts)


def generate_job_embedding(job: JobPosting) -> Optional[List[float]]:
    """
    Generate embedding for a job posting using OpenAI text-embedding-3-large.
    
    Args:
        job: JobPosting ORM object
        
    Returns:
        3072-dimensional embedding vector or None if generation fails
    """
    embeddings_client = get_embeddings_client()
    if not embeddings_client:
        logger.error("Embeddings client not available")
        return None
    
    try:
        # Convert job to text
        job_text = job_to_text(job)
        
        # Generate embedding
        embedding = embeddings_client.embed_query(job_text)
        
        # Verify dimension
        if len(embedding) != 3072:
            logger.warning(f"Expected 3072 dimensions, got {len(embedding)}")
        
        logger.debug(f"Generated embedding for job {job.job_id}")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding for job {job.job_id}: {e}")
        return None


def generate_user_profile_embedding(user_id: int, db: Session) -> Optional[List[float]]:
    """
    Generate embedding for a user profile based on comprehensive profile data.
    
    Includes:
    - Resume/CV text (parsed from uploaded documents)
    - About section and short description
    - Skills, certifications, current role/company
    - Job preferences (location, remote, salary, experience level)
    
    Args:
        user_id: User ID
        db: SQLAlchemy database session
        
    Returns:
        3072-dimensional embedding vector or None if generation fails
    """
    embeddings_client = get_embeddings_client()
    if not embeddings_client:
        logger.error("Embeddings client not available")
        return None
    
    try:
        # Fetch user data
        from models.orm.user import User
        from models.orm.description import Description
        from services.user_preferences_service import UserPreferencesService
        
        user = db.query(User).filter(User.uid == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return None
        
        # Get user description/profile data (fetch once, reuse)
        description = None
        if user.description_id:
            description = db.query(Description).filter(Description.desc_id == user.description_id).first()
        
        # Get user preferences
        prefs_service = UserPreferencesService(db)
        preferences = prefs_service.get_user_preferences(user_id)
        
        # Build user profile text with comprehensive information
        parts = []
        
        # Resume/CV text (most comprehensive - includes experience, education, projects, etc.)
        # Limit to ~3000 chars to avoid token limits while keeping key information
        if description and description.resume:
            resume_text = description.resume.strip()
            if len(resume_text) > 3000:
                # Truncate but try to keep complete sentences
                truncated = resume_text[:3000]
                last_period = truncated.rfind('.')
                if last_period > 2500:  # Only truncate at sentence if we have enough content
                    resume_text = truncated[:last_period + 1]
                else:
                    resume_text = truncated + "..."
            parts.append(f"Resume/CV: {resume_text}")
        
        # About section (user's self-description)
        if description and description.about:
            about_text = description.about.strip()
            if len(about_text) > 1000:
                about_text = about_text[:1000] + "..."
            parts.append(f"About: {about_text}")
        
        # Short description
        if description and description.short_desc:
            parts.append(f"Summary: {description.short_desc.strip()}")
        
        # Current role and company
        if description:
            role_parts = []
            if description.role:
                role_parts.append(description.role)
            if description.company:
                role_parts.append(f"at {description.company}")
            if role_parts:
                parts.append(f"Current Position: {' '.join(role_parts)}")
        
        # Skills (from description)
        if description and description.skills:
            parts.append(f"Skills: {description.skills.strip()}")
        
        # Certifications
        if description and description.certificates:
            certs_text = description.certificates.strip()
            if len(certs_text) > 500:
                certs_text = certs_text[:500] + "..."
            parts.append(f"Certifications: {certs_text}")
        
        # Current status/experience level
        if preferences.get('experience_level'):
            parts.append(f"Experience Level: {preferences['experience_level']}")
        elif description and description.current_status:
            parts.append(f"Current Status: {description.current_status}")
        
        # Preferred Job Type
        if preferences.get('preferred_job_type'):
            parts.append(f"Preferred Job Type: {preferences['preferred_job_type']}")
        
        # Preferred Location
        if preferences.get('preferred_location'):
            parts.append(f"Preferred Location: {preferences['preferred_location']}")
        
        # Remote Preference
        if preferences.get('preferred_remote') is not None:
            parts.append(f"Remote Preference: {'Yes' if preferences['preferred_remote'] else 'No'}")
        
        # Salary Expectation
        if preferences.get('salary_expectation_min') or preferences.get('salary_expectation_max'):
            salary_parts = []
            if preferences.get('salary_expectation_min'):
                salary_parts.append(f"${preferences['salary_expectation_min']:,}")
            if preferences.get('salary_expectation_max'):
                salary_parts.append(f"${preferences['salary_expectation_max']:,}")
            parts.append(f"Salary Expectation: {' - '.join(salary_parts)}")
        
        # Fallback if no profile data at all
        if not parts:
            parts.append(f"User Profile: {user.name or 'User'}")
            if description and description.skills:
                parts.append(f"Skills: {description.skills.strip()}")
        
        user_profile_text = "\n".join(parts) if parts else "User profile"
        
        # Generate embedding
        embedding = embeddings_client.embed_query(user_profile_text)
        
        # Verify dimension
        if len(embedding) != 3072:
            logger.warning(f"Expected 3072 dimensions, got {len(embedding)}")
        
        logger.debug(f"Generated embedding for user {user_id}")
        return embedding
    except Exception as e:
        logger.error(f"Failed to generate embedding for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return None


def store_job_embedding(job_id: int, embedding: List[float], db: Session) -> bool:
    """
    Store job embedding in PostgreSQL using raw SQL (pgvector support).
    
    Args:
        job_id: Job ID
        embedding: 3072-dimensional embedding vector
        db: SQLAlchemy database session
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert embedding to PostgreSQL vector format
        # pgvector expects a string representation: '[0.1, 0.2, ...]'
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        # Use raw SQL to update embedding
        # SQLAlchemy doesn't natively support pgvector, so we use raw SQL
        from config.database import get_database
        db_raw = get_database()
        
        query = """
        UPDATE job_postings 
        SET embedding = %s::vector 
        WHERE job_id = %s
        """
        
        db_raw.execute(query, (embedding_str, job_id))
        logger.debug(f"Stored embedding for job {job_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store embedding for job {job_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_user_embedding(user_id: int, db: Session) -> Optional[List[float]]:
    """
    Retrieve stored user profile embedding from database.
    
    Args:
        user_id: User ID
        db: SQLAlchemy database session
        
    Returns:
        3072-dimensional embedding vector or None if not found
    """
    try:
        from models.orm.user import User
        from config.database import get_database
        
        user = db.query(User).filter(User.uid == user_id).first()
        if not user or not user.description_id:
            return None
        
        db_raw = get_database()
        query = """
        SELECT embedding 
        FROM description 
        WHERE desc_id = %s AND embedding IS NOT NULL
        """
        
        result = db_raw.fetch_one(query, (user.description_id,))
        if not result or not result.get('embedding'):
            return None
        
        # Parse vector string to list
        embedding_str = result['embedding']
        if isinstance(embedding_str, str):
            # Remove brackets and split
            embedding_str = embedding_str.strip('[]')
            embedding = [float(x.strip()) for x in embedding_str.split(',')]
            return embedding
        
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve embedding for user {user_id}: {e}")
        return None


def store_user_embedding(user_id: int, embedding: List[float], db: Session) -> bool:
    """
    Store user profile embedding in PostgreSQL using raw SQL (pgvector support).
    
    Args:
        user_id: User ID
        embedding: 3072-dimensional embedding vector
        db: SQLAlchemy database session
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from models.orm.user import User
        
        user = db.query(User).filter(User.uid == user_id).first()
        if not user or not user.description_id:
            logger.error(f"User {user_id} or description not found")
            return False
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        # Use raw SQL to update embedding
        from config.database import get_database
        db_raw = get_database()
        
        query = """
        UPDATE description 
        SET embedding = %s::vector 
        WHERE desc_id = %s
        """
        
        db_raw.execute(query, (embedding_str, user.description_id))
        logger.debug(f"Stored embedding for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to store embedding for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return False


def update_user_embedding_if_needed(user_id: int, db: Session) -> bool:
    """
    Generate and store user embedding if it doesn't exist or profile has changed.
    This should be called after profile updates.
    
    Args:
        user_id: User ID
        db: SQLAlchemy database session
        
    Returns:
        True if embedding was generated/stored, False otherwise
    """
    try:
        # Generate embedding
        embedding = generate_user_profile_embedding(user_id, db)
        if not embedding:
            return False
        
        # Store embedding
        return store_user_embedding(user_id, embedding, db)
    except Exception as e:
        logger.error(f"Failed to update embedding for user {user_id}: {e}")
        return False