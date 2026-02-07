"""
Recommendation Service
Provides job recommendations using vector similarity search and multi-factor ranking
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from utils.job_embeddings import generate_user_profile_embedding
from services.user_preferences_service import UserPreferencesService
from models.orm.job_posting import JobPosting
from models.orm.description import Description
from config.database import get_database

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating job recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.preferences_service = UserPreferencesService(db)
    
    def get_recommendations(
        self, 
        user_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get job recommendations for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended jobs with scores
        """
        try:
            # Get user preferences
            preferences = self.preferences_service.get_user_preferences(user_id)
            
            # Generate user profile embedding
            user_embedding = generate_user_profile_embedding(user_id, self.db)
            if not user_embedding:
                logger.warning(f"Failed to generate user embedding for user {user_id}")
                return []
            
            # Perform vector similarity search with hard filters
            candidates = self._vector_similarity_search(
                user_embedding=user_embedding,
                preferences=preferences,
                candidate_limit=50  # Get more candidates for ranking
            )
            
            if not candidates:
                logger.info(f"No candidates found for user {user_id}")
                return []
            
            # Calculate composite scores and rank
            scored_jobs = []
            for candidate in candidates:
                job = self.db.query(JobPosting).filter(
                    JobPosting.job_id == candidate['job_id']
                ).first()
                
                if not job:
                    continue
                
                # Get user skills for skill overlap calculation
                user_skills = self._get_user_skills(user_id)
                
                # Calculate composite score
                composite_score = self._calculate_composite_score(
                    job=job,
                    user_embedding=user_embedding,
                    user_preferences=preferences,
                    similarity_score=candidate['similarity'],
                    user_skills=user_skills
                )
                
                scored_jobs.append({
                    'job': job,
                    'similarity_score': candidate['similarity'],
                    'composite_score': composite_score,
                    'user_skills': user_skills
                })
            
            # Sort by composite score (descending)
            scored_jobs.sort(key=lambda x: x['composite_score'], reverse=True)
            
            # Return top N jobs with full details
            recommendations = []
            for item in scored_jobs[:limit]:
                job = item['job']
                job_dict = job.to_dict()
                
                # Calculate individual scores for response
                skill_score = self._calculate_skill_overlap(
                    job.skills_required or '',
                    item['user_skills']
                )
                salary_score = self._calculate_salary_match(
                    job.salary_min,
                    job.salary_max,
                    preferences.get('salary_expectation_min'),
                    preferences.get('salary_expectation_max')
                )
                recency_score = self._calculate_recency_score(job.created_at)
                
                recommendations.append({
                    **job_dict,
                    'similarity_score': round(item['similarity_score'], 4),
                    'skill_match_score': round(skill_score, 4),
                    'salary_match_score': round(salary_score, 4),
                    'recency_score': round(recency_score, 4),
                    'composite_score': round(item['composite_score'], 4)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to get recommendations for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _vector_similarity_search(
        self,
        user_embedding: List[float],
        preferences: Dict[str, Any],
        candidate_limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search with hard filters.
        
        Args:
            user_embedding: User profile embedding vector
            preferences: User preferences dictionary
            candidate_limit: Maximum number of candidates to return
            
        Returns:
            List of candidate jobs with similarity scores
        """
        db_raw = get_database()
        
        # Convert embedding to PostgreSQL vector format
        embedding_str = '[' + ','.join(map(str, user_embedding)) + ']'
        
        # Build WHERE clause for hard filters
        where_conditions = ["status = 'active'"]
        params = []
        
        # Location filter (if preference set)
        if preferences.get('preferred_location'):
            where_conditions.append("location ILIKE %s")
            params.append(f"%{preferences['preferred_location']}%")
        
        # Remote filter (if preference set)
        if preferences.get('preferred_remote') is not None:
            where_conditions.append("is_remote = %s")
            params.append(preferences['preferred_remote'])
        
        # Experience level filter (if preference set)
        if preferences.get('experience_level'):
            where_conditions.append("experience_level = %s")
            params.append(preferences['experience_level'])
        
        where_clause = " AND ".join(where_conditions)
        
        # Vector similarity search query
        # Using cosine distance (<=>) - lower is more similar
        # We convert to similarity score: 1 - distance
        query = f"""
        SELECT 
            job_id,
            1 - (embedding <=> %s::vector) as similarity
        FROM job_postings
        WHERE {where_clause}
          AND embedding IS NOT NULL
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """
        
        # Add embedding to params (used twice - once in WHERE, once in ORDER BY)
        params = [embedding_str] + params + [embedding_str, candidate_limit]
        
        try:
            results = db_raw.fetch_all(query, tuple(params))
            return results
        except Exception as e:
            logger.error(f"Vector similarity search failed: {e}")
            return []
    
    def _calculate_composite_score(
        self,
        job: JobPosting,
        user_embedding: List[float],
        user_preferences: Dict[str, Any],
        similarity_score: float,
        user_skills: str
    ) -> float:
        """
        Calculate composite recommendation score.
        
        Weights:
        - Semantic similarity: 40%
        - Skill overlap: 30%
        - Salary match: 20%
        - Job recency: 10%
        
        Args:
            job: JobPosting object
            user_embedding: User profile embedding (not used directly, but kept for consistency)
            user_preferences: User preferences dictionary
            similarity_score: Semantic similarity score from vector search
            user_skills: User skills string (comma-separated)
            
        Returns:
            Composite score (0.0 to 1.0)
        """
        # Calculate individual scores
        semantic_score = max(0.0, min(1.0, similarity_score))  # Normalize to [0, 1]
        skill_score = self._calculate_skill_overlap(
            job.skills_required or '',
            user_skills
        )
        salary_score = self._calculate_salary_match(
            job.salary_min,
            job.salary_max,
            user_preferences.get('salary_expectation_min'),
            user_preferences.get('salary_expectation_max')
        )
        recency_score = self._calculate_recency_score(job.created_at)
        
        # Weighted combination
        composite = (
            0.40 * semantic_score +
            0.30 * skill_score +
            0.20 * salary_score +
            0.10 * recency_score
        )
        
        return composite
    
    def _calculate_skill_overlap(
        self,
        job_skills: str,
        user_skills: str
    ) -> float:
        """
        Calculate skill overlap using Jaccard similarity.
        
        Args:
            job_skills: Comma-separated job skills
            user_skills: Comma-separated user skills
            
        Returns:
            Skill overlap score (0.0 to 1.0)
        """
        if not job_skills or not user_skills:
            return 0.0
        
        # Normalize and split skills
        job_skill_set = set(s.strip().lower() for s in job_skills.split(',') if s.strip())
        user_skill_set = set(s.strip().lower() for s in user_skills.split(',') if s.strip())
        
        if not job_skill_set:
            return 0.0
        
        # Jaccard similarity: intersection / union
        intersection = len(job_skill_set & user_skill_set)
        union = len(job_skill_set | user_skill_set)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _calculate_salary_match(
        self,
        job_min: Optional[int],
        job_max: Optional[int],
        user_min: Optional[int],
        user_max: Optional[int]
    ) -> float:
        """
        Calculate salary match score.
        
        Args:
            job_min: Job minimum salary
            job_max: Job maximum salary
            user_min: User minimum salary expectation
            user_max: User maximum salary expectation
            
        Returns:
            Salary match score (0.0 to 1.0)
        """
        # If no salary info, return neutral score
        if not job_min and not job_max:
            return 0.5
        
        if not user_min and not user_max:
            return 0.5
        
        # Calculate job salary range midpoint
        if job_min and job_max:
            job_mid = (job_min + job_max) / 2
        elif job_min:
            job_mid = job_min * 1.2  # Assume 20% range
        elif job_max:
            job_mid = job_max * 0.8
        else:
            return 0.5
        
        # Calculate user salary range
        if user_min and user_max:
            user_mid = (user_min + user_max) / 2
            user_range = user_max - user_min
        elif user_min:
            user_mid = user_min * 1.2
            user_range = user_min * 0.4  # Assume 40% range
        elif user_max:
            user_mid = user_max * 0.8
            user_range = user_max * 0.4
        else:
            return 0.5
        
        # Check if job salary is within user range
        if user_min and user_max:
            if job_mid >= user_min and job_mid <= user_max:
                return 1.0
            elif job_mid < user_min:
                # Below range - penalize based on distance
                diff = user_min - job_mid
                penalty = min(1.0, diff / user_range)
                return max(0.0, 0.5 - penalty * 0.5)
            else:
                # Above range - slight bonus
                return 0.8
        
        # If only one bound, use midpoint comparison
        diff_ratio = abs(job_mid - user_mid) / max(job_mid, user_mid)
        return max(0.0, 1.0 - diff_ratio)
    
    def _calculate_recency_score(self, created_at: Optional[datetime]) -> float:
        """
        Calculate recency score (newer jobs get higher scores).
        
        Args:
            created_at: Job creation timestamp
            
        Returns:
            Recency score (0.0 to 1.0)
        """
        if not created_at:
            return 0.5
        
        # Calculate days since creation
        days_old = (datetime.now() - created_at).days
        
        # Score decays over time
        # Fresh (0-7 days): 1.0
        # Recent (8-30 days): 0.8
        # Moderate (31-90 days): 0.6
        # Older (91+ days): 0.4
        if days_old <= 7:
            return 1.0
        elif days_old <= 30:
            return 0.8
        elif days_old <= 90:
            return 0.6
        else:
            return 0.4
    
    def _get_user_skills(self, user_id: int) -> str:
        """
        Get user skills from description table.
        
        Args:
            user_id: User ID
            
        Returns:
            Comma-separated skills string
        """
        try:
            from models.orm.user import User
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user or not user.description_id:
                return ""
            
            description = self.db.query(Description).filter(
                Description.desc_id == user.description_id
            ).first()
            
            if description and description.skills:
                return description.skills
            
            return ""
        except Exception as e:
            logger.warning(f"Failed to get user skills for user {user_id}: {e}")
            return ""
