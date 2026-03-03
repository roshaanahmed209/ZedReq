"""Recommendation Service - User recommendation operations using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, text
from sqlalchemy.sql import text as sql_text

from models.orm import UserRecommendation, JobPosting
from models.orm.user import User
from models.orm.description import Description
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger
from utils.job_embeddings import (
    generate_user_profile_embedding,
    get_user_embedding,
    store_user_embedding,
    update_user_embedding_if_needed
)
from services.user_preferences_service import UserPreferencesService
from services.recommendation_cache_service import RecommendationCacheService
from config.database import get_database

logger = setup_logger(__name__)


class RecommendationService:
    """Recommendation business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_recommendations(self, user_id: int, include_recommender_info: bool = True) -> List[Dict[str, Any]]:
        """Get all visible recommendations for a user"""
        recommendations = (
            self.db.query(UserRecommendation)
            .filter(
                UserRecommendation.user_id == user_id,
                UserRecommendation.is_visible == True
            )
            .order_by(desc(UserRecommendation.created_at))
            .all()
        )
        
        return [rec.to_dict(include_recommender_info=include_recommender_info) for rec in recommendations]
    
    def get_user_recommendations_paginated(
        self, 
        user_id: int, 
        include_recommender_info: bool = True,
        limit: int = 50, 
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated visible recommendations for a user"""
        # Get total count
        total = (
            self.db.query(UserRecommendation)
            .filter(
                UserRecommendation.user_id == user_id,
                UserRecommendation.is_visible == True
            )
            .count()
        )
        
        # Get paginated results
        recommendations = (
            self.db.query(UserRecommendation)
            .filter(
                UserRecommendation.user_id == user_id,
                UserRecommendation.is_visible == True
            )
            .order_by(desc(UserRecommendation.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [rec.to_dict(include_recommender_info=include_recommender_info) for rec in recommendations], total
    
    def get_recommendation(self, recommendation_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific recommendation by ID"""
        recommendation = (
            self.db.query(UserRecommendation)
            .filter(UserRecommendation.id == recommendation_id)
            .first()
        )
        
        if not recommendation:
            return None
        
        return recommendation.to_dict(include_recommender_info=True)
    
    def create_recommendation(
        self, 
        user_id: int, 
        recommender_id: int, 
        recommendation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new recommendation"""
        if user_id == recommender_id:
            raise ValueError("Cannot recommend yourself")
        
        try:
            recommendation = UserRecommendation(
                user_id=user_id,
                recommender_id=recommender_id,
                relationship_type=recommendation_data.get('relationship') or recommendation_data.get('relationship_type'),
                recommendation_text=recommendation_data['recommendation_text'],
                is_visible=recommendation_data.get('is_visible', True)
            )
            
            self.db.add(recommendation)
            self.db.commit()
            self.db.refresh(recommendation)
            
            logger.info(f"Recommendation created: {recommendation.id} for user {user_id} by {recommender_id}")
            return recommendation.to_dict(include_recommender_info=True)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Create recommendation error: {e}", exc_info=True)
            raise
    
    def update_recommendation(
        self, 
        recommendation_id: int, 
        user_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a recommendation (only by the user being recommended)"""
        recommendation = (
            self.db.query(UserRecommendation)
            .filter(UserRecommendation.id == recommendation_id)
            .first()
        )
        
        if not recommendation:
            raise NotFoundError('Recommendation')
        
        if recommendation.user_id != user_id:
            raise AuthorizationError("You don't have permission to update this recommendation")
        
        try:
            if 'is_visible' in update_data:
                recommendation.is_visible = update_data['is_visible']
            
            self.db.commit()
            self.db.refresh(recommendation)
            
            logger.info(f"Recommendation updated: {recommendation_id}")
            return recommendation.to_dict(include_recommender_info=True)
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update recommendation error: {e}", exc_info=True)
            raise
    
    def delete_recommendation(self, recommendation_id: int, user_id: int) -> None:
        """Delete a recommendation (only by the user being recommended)"""
        recommendation = (
            self.db.query(UserRecommendation)
            .filter(UserRecommendation.id == recommendation_id)
            .first()
        )
        
        if not recommendation:
            raise NotFoundError('Recommendation')
        
        if recommendation.user_id != user_id:
            raise AuthorizationError("You don't have permission to delete this recommendation")
        
        try:
            self.db.delete(recommendation)
            self.db.commit()
            logger.info(f"Recommendation deleted: {recommendation_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete recommendation error: {e}", exc_info=True)
            raise
    
    # ========================================================================
    # Job Recommendation Operations
    # ========================================================================
    
    def get_recommendations(
        self, 
        user_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get personalized job recommendations for a user.
        
        Checks cache first, then generates recommendations if cache is invalid/missing.
        
        Location-based priority system:
        1. First level: Jobs in user's city
        2. Second level: Jobs in user's country (if not enough from city)
        3. Remote jobs: Skill-based recommendations
        
        Uses vector embeddings, skill overlap, salary matching, and recency
        to generate composite scores and return top N recommendations.
        
        Args:
            user_id: User ID
            limit: Maximum number of recommendations to return (default: 10)
            
        Returns:
            List of job recommendations with scores
        """
        try:
            # Step 0: Check cache first
            cache_service = RecommendationCacheService(self.db)
            cached_recommendations = cache_service.get_cached_recommendations(user_id)
            
            if cached_recommendations is not None:
                # Return cached results (limit if needed)
                logger.debug(f"Returning cached recommendations for user {user_id}")
                return cached_recommendations[:limit]
            
            # Cache miss or invalid - generate recommendations
            logger.debug(f"Cache miss for user {user_id}, generating recommendations")
            
            # Step 1: Get user location (city and country)
            user_location = self._get_user_location(user_id)
            user_city = user_location.get('city')
            user_country = user_location.get('country')
            
            # Step 2: Get or generate user profile embedding
            user_embedding = get_user_embedding(user_id, self.db)
            if not user_embedding:
                # Embedding doesn't exist, generate and store it
                logger.info(f"Generating embedding for user {user_id} (first time)")
                user_embedding = generate_user_profile_embedding(user_id, self.db)
                if user_embedding:
                    store_user_embedding(user_id, user_embedding, self.db)
                else:
                    logger.warning(f"Could not generate embedding for user {user_id}, returning empty recommendations")
                    return []
            
            # Step 3: Get user preferences for filtering
            prefs_service = UserPreferencesService(self.db)
            preferences = prefs_service.get_user_preferences(user_id)
            
            # Step 4: Get user skills for overlap calculation
            user_skills = self._get_user_skills(user_id)
            
            # Step 5: Collect recommendations with location-based priority
            all_candidate_jobs = []
            job_ids_seen = set()
            
            # Level 1: Jobs in user's city (if city is available)
            if user_city:
                city_jobs = self._vector_similarity_search(
                    user_embedding,
                    preferences,
                    location_filter={'city': user_city},
                    candidate_limit=limit * 2,  # Get more to ensure we have enough after filtering
                    exclude_remote=True  # Exclude remote jobs for location-based search
                )
                for job_data in city_jobs:
                    if job_data['job_id'] not in job_ids_seen:
                        job_data['location_priority'] = 1  # City level
                        all_candidate_jobs.append(job_data)
                        job_ids_seen.add(job_data['job_id'])
            
            # Level 2: Jobs in user's country (if country is available and we need more)
            if user_country and len(all_candidate_jobs) < limit:
                country_jobs = self._vector_similarity_search(
                    user_embedding,
                    preferences,
                    location_filter={'country': user_country, 'exclude_city': user_city},
                    candidate_limit=(limit - len(all_candidate_jobs)) * 2,
                    exclude_remote=True
                )
                for job_data in country_jobs:
                    if job_data['job_id'] not in job_ids_seen:
                        job_data['location_priority'] = 2  # Country level
                        all_candidate_jobs.append(job_data)
                        job_ids_seen.add(job_data['job_id'])
            
            # Remote jobs: Skill-based recommendations
            # Always include remote jobs, even if user has location (for more options)
            remote_limit = max(limit - len(all_candidate_jobs), limit // 2)  # Get at least half limit for remote
            remote_jobs = self._get_remote_job_recommendations(
                user_embedding,
                user_skills,
                preferences,
                candidate_limit=remote_limit
            )
            for job_data in remote_jobs:
                if job_data['job_id'] not in job_ids_seen:
                    job_data['location_priority'] = 3  # Remote level
                    all_candidate_jobs.append(job_data)
                    job_ids_seen.add(job_data['job_id'])
            
            # If no location-based jobs found, try getting any jobs with embeddings (fallback)
            if not all_candidate_jobs:
                logger.info(f"No location-based or remote jobs found for user {user_id}, trying fallback: any jobs with embeddings")
                # Fallback: Get any jobs with embeddings, regardless of location
                fallback_jobs = self._vector_similarity_search(
                    user_embedding,
                    preferences,
                    location_filter=None,
                    candidate_limit=limit * 2,
                    exclude_remote=False
                )
                for job_data in fallback_jobs:
                    if job_data['job_id'] not in job_ids_seen:
                        job_data['location_priority'] = 4  # Fallback level
                        all_candidate_jobs.append(job_data)
                        job_ids_seen.add(job_data['job_id'])
            
            if not all_candidate_jobs:
                logger.warning(
                    f"No candidate jobs found for user {user_id}. "
                    f"This might indicate: no jobs in database, no jobs with embeddings, or vector search issue."
                )
                return []
            
            # Step 6: Calculate composite scores for each candidate
            scored_jobs = []
            for job_data in all_candidate_jobs:
                job_id = job_data['job_id']
                similarity_score = job_data['similarity']
                location_priority = job_data.get('location_priority', 3)
                
                # Get full job details
                job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
                if not job or job.status != 'active':
                    continue
                
                # Calculate individual scores
                skill_score = self._calculate_skill_overlap(job, user_skills)
                salary_score = self._calculate_salary_match(job, preferences)
                recency_score = self._calculate_recency_score(job)
                
                # Location bonus: Higher priority for city/country matches
                location_bonus = 0.0
                if location_priority == 1:  # City match
                    location_bonus = 0.15
                elif location_priority == 2:  # Country match
                    location_bonus = 0.10
                
                # Calculate composite score with location bonus
                composite_score = self._calculate_composite_score(
                    similarity_score,
                    skill_score,
                    salary_score,
                    recency_score
                ) + location_bonus
                
                # Cap at 1.0
                composite_score = min(1.0, composite_score)
                
                # Build recommendation response
                job_dict = job.to_dict(include_relations=True)
                job_dict.update({
                    'similarity_score': round(similarity_score, 4),
                    'skill_match_score': round(skill_score, 4),
                    'salary_match_score': round(salary_score, 4),
                    'recency_score': round(recency_score, 4),
                    'composite_score': round(composite_score, 4),
                    'location_priority': location_priority
                })
                
                scored_jobs.append({
                    'job': job_dict,
                    'composite_score': composite_score,
                    'location_priority': location_priority
                })
            
            # Step 7: Sort by location priority first, then composite score
            scored_jobs.sort(key=lambda x: (x['location_priority'], -x['composite_score']))
            top_jobs = scored_jobs[:limit]
            
            # Format final response
            recommendations = []
            for item in top_jobs:
                job_dict = item['job']
                recommendations.append({
                    'job_id': job_dict['job_id'],
                    'poster_id': job_dict['poster_id'],
                    'title': job_dict['title'],
                    'description': job_dict['description'],
                    'company_name': job_dict.get('company_name'),
                    'location': job_dict.get('location'),
                    'job_type': job_dict.get('job_type'),
                    'is_remote': job_dict.get('is_remote', False),
                    'experience_level': job_dict.get('experience_level'),
                    'skills_required': job_dict.get('skills_required'),
                    'salary_min': job_dict.get('salary_min'),
                    'salary_max': job_dict.get('salary_max'),
                    'status': job_dict.get('status', 'active'),
                    'created_at': job_dict.get('created_at'),
                    'updated_at': job_dict.get('updated_at'),
                    'poster_username': None,  # Can be enriched if needed
                    'poster_name': None,  # Can be enriched if needed
                    'application_count': job_dict.get('application_count'),
                    'is_saved': None,  # Can be enriched if needed
                    'has_applied': None,  # Can be enriched if needed
                    'similarity_score': job_dict['similarity_score'],
                    'skill_match_score': job_dict['skill_match_score'],
                    'salary_match_score': job_dict['salary_match_score'],
                    'recency_score': job_dict['recency_score'],
                    'composite_score': job_dict['composite_score']
                })
            
            logger.info(f"Generated {len(recommendations)} job recommendations for user {user_id} (City: {user_city}, Country: {user_country})")
            
            # Step 8: Store in cache for future requests (only if we have recommendations)
            # Don't cache empty results to allow retry on next request
            if recommendations:
                cache_service.store_recommendations(user_id, recommendations)
            else:
                # Log why no recommendations were found for debugging
                logger.warning(
                    f"No recommendations generated for user {user_id}. "
                    f"Location: city={user_city}, country={user_country}. "
                    f"Candidates found: {len(all_candidate_jobs)}. "
                    f"User embedding exists: {user_embedding is not None}"
                )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating job recommendations for user {user_id}: {e}", exc_info=True)
            return []
    
    def _parse_location(self, location_str: str) -> Dict[str, Optional[str]]:
        """
        Parse location string to extract city and country.
        
        Expected formats:
        - "City, State" (e.g., "San Francisco, CA")
        - "City, Country" (e.g., "London, UK")
        - "City" (only city)
        - "Remote" or "Hybrid"
        
        Args:
            location_str: Location string from database
            
        Returns:
            Dictionary with 'city' and 'country' keys
        """
        if not location_str:
            return {'city': None, 'country': None}
        
        location_str = location_str.strip()
        
        # Handle special cases
        if location_str.lower() in ['remote', 'hybrid']:
            return {'city': None, 'country': None}
        
        # Split by comma
        parts = [p.strip() for p in location_str.split(',')]
        
        if len(parts) == 1:
            # Only city provided
            return {'city': parts[0], 'country': None}
        elif len(parts) >= 2:
            # City and state/country
            city = parts[0]
            state_or_country = parts[1]
            
            # Common US state abbreviations (2 letters)
            us_states = {'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
                        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'}
            
            if state_or_country.upper() in us_states:
                # It's a US state, we'll use the state as country identifier for US
                return {'city': city, 'country': 'USA'}
            else:
                # Likely a country
                return {'city': city, 'country': state_or_country}
        
        return {'city': None, 'country': None}
    
    def _get_user_location(self, user_id: int) -> Dict[str, Optional[str]]:
        """
        Get user's location (city and country) from description table.
        Uses stored city/country columns if available, otherwise parses from location.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with 'city' and 'country' keys
        """
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user or not user.description_id:
                return {'city': None, 'country': None}
            
            description = self.db.query(Description).filter(Description.desc_id == user.description_id).first()
            if not description:
                return {'city': None, 'country': None}
            
            # Use stored city/country if available
            if description.city or description.country:
                return {
                    'city': description.city,
                    'country': description.country
                }
            
            # Fallback to parsing location string
            if description.location:
                parsed = self._parse_location(description.location)
                # Update description with parsed values (async, non-blocking)
                try:
                    description.city = parsed['city']
                    description.country = parsed['country']
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                return parsed
            
            return {'city': None, 'country': None}
            
        except Exception as e:
            logger.error(f"Error getting user location: {e}", exc_info=True)
            return {'city': None, 'country': None}
    
    def _vector_similarity_search(
        self,
        user_embedding: List[float],
        preferences: Dict[str, Any],
        location_filter: Optional[Dict[str, Any]] = None,
        candidate_limit: int = 50,
        exclude_remote: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using pgvector.
        
        Args:
            user_embedding: User profile embedding vector (3072 dimensions)
            preferences: User job preferences for filtering
            location_filter: Optional dict with 'city' and/or 'country' for location filtering
            candidate_limit: Maximum number of candidates to return
            exclude_remote: If True, exclude remote jobs from results
            
        Returns:
            List of candidate jobs with similarity scores
        """
        try:
            # Convert embedding to PostgreSQL vector format
            embedding_str = '[' + ','.join(map(str, user_embedding)) + ']'
            
            # Build WHERE clause for hard filters
            where_conditions = ["status = 'active'"]
            params = []
            
            # Location filter (city or country) - use dedicated columns for better performance
            if location_filter:
                if location_filter.get('city'):
                    # Use city column for exact match (faster than ILIKE on location)
                    where_conditions.append("city = %s")
                    params.append(location_filter['city'])
                elif location_filter.get('country'):
                    # Exclude city if specified
                    if location_filter.get('exclude_city'):
                        where_conditions.append("country = %s AND (city IS NULL OR city != %s)")
                        params.append(location_filter['country'])
                        params.append(location_filter['exclude_city'])
                    else:
                        where_conditions.append("country = %s")
                        params.append(location_filter['country'])
            
            # Remote preference filter
            if exclude_remote:
                where_conditions.append("is_remote = FALSE")
            elif preferences.get('preferred_remote') is not None:
                where_conditions.append("is_remote = %s")
                params.append(preferences['preferred_remote'])
            
            # Experience level filter
            if preferences.get('experience_level'):
                where_conditions.append("experience_level = %s")
                params.append(preferences['experience_level'])
            
            # Job type filter
            if preferences.get('preferred_job_type'):
                where_conditions.append("job_type = %s")
                params.append(preferences['preferred_job_type'])
            
            where_clause = " AND ".join(where_conditions)
            
            # Build query using pgvector cosine distance operator (<=>)
            # 1 - (embedding <=> user_embedding) gives similarity (0 to 1)
            # NOTE: %s placeholders are positional, so params order must match
            # SQL order: embedding (SELECT), ...where_params... (WHERE), embedding (ORDER BY), limit
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
            
            # Build final params in the correct order matching %s positions:
            # 1st %s = embedding (in SELECT), then WHERE params, then embedding (ORDER BY), then LIMIT
            final_params = [embedding_str] + params + [embedding_str, candidate_limit]
            
            # Execute query using raw database connection
            db_raw = get_database()
            results = db_raw.fetch_all(query, tuple(final_params))
            
            candidates = []
            for row in results:
                candidates.append({
                    'job_id': row['job_id'],
                    'similarity': float(row['similarity'])
                })
            
            logger.debug(f"Vector search returned {len(candidates)} candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}", exc_info=True)
            return []
    
    def _get_remote_job_recommendations(
        self,
        user_embedding: List[float],
        user_skills: set,
        preferences: Dict[str, Any],
        candidate_limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get remote job recommendations based primarily on skills.
        
        Args:
            user_embedding: User profile embedding vector
            user_skills: Set of user skills
            preferences: User job preferences
            candidate_limit: Maximum number of candidates to return
            
        Returns:
            List of remote job candidates with similarity scores
        """
        try:
            # Get remote jobs using vector search
            remote_prefs = preferences.copy()
            remote_prefs['preferred_remote'] = True
            
            remote_jobs = self._vector_similarity_search(
                user_embedding,
                remote_prefs,
                candidate_limit=candidate_limit * 2,  # Get more to filter by skills
                exclude_remote=False
            )
            
            if not remote_jobs:
                return []
            
            # Score remote jobs primarily by skill overlap
            scored_remote_jobs = []
            for job_data in remote_jobs:
                job_id = job_data['job_id']
                job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
                
                if not job or not job.is_remote or job.status != 'active':
                    continue
                
                # Calculate skill overlap (primary factor for remote jobs)
                skill_score = self._calculate_skill_overlap(job, user_skills)
                
                # For remote jobs, prioritize skill match over semantic similarity
                # Weight: 60% skills, 40% semantic similarity
                weighted_score = (0.6 * skill_score) + (0.4 * job_data['similarity'])
                
                scored_remote_jobs.append({
                    'job_id': job_id,
                    'similarity': weighted_score,  # Use weighted score as similarity
                    'skill_score': skill_score
                })
            
            # Sort by weighted score (skill-focused)
            scored_remote_jobs.sort(key=lambda x: x['similarity'], reverse=True)
            
            return scored_remote_jobs[:candidate_limit]
            
        except Exception as e:
            logger.error(f"Error getting remote job recommendations: {e}", exc_info=True)
            return []
    
    def _get_user_skills(self, user_id: int) -> set:
        """Extract user skills as a set for comparison"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user or not user.description_id:
                return set()
            
            description = self.db.query(Description).filter(Description.desc_id == user.description_id).first()
            if not description or not description.skills:
                return set()
            
            # Parse skills (assuming comma-separated or space-separated)
            skills_text = description.skills.lower()
            # Split by comma or space, clean and normalize
            skills = [s.strip() for s in skills_text.replace(',', ' ').split()]
            return set(skills)
            
        except Exception as e:
            logger.error(f"Error getting user skills: {e}", exc_info=True)
            return set()
    
    def _calculate_skill_overlap(self, job: JobPosting, user_skills: set) -> float:
        """
        Calculate Jaccard similarity between job skills and user skills.
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not job.skills_required or not user_skills:
            return 0.0
        
        try:
            # Parse job skills
            job_skills_text = job.skills_required.lower()
            job_skills = set([s.strip() for s in job_skills_text.replace(',', ' ').split()])
            
            if not job_skills:
                return 0.0
            
            # Calculate Jaccard similarity: |A ∩ B| / |A ∪ B|
            intersection = user_skills.intersection(job_skills)
            union = user_skills.union(job_skills)
            
            if not union:
                return 0.0
            
            jaccard = len(intersection) / len(union)
            return min(1.0, max(0.0, jaccard))
            
        except Exception as e:
            logger.error(f"Error calculating skill overlap: {e}", exc_info=True)
            return 0.0
    
    def _calculate_salary_match(
        self, 
        job: JobPosting, 
        preferences: Dict[str, Any]
    ) -> float:
        """
        Calculate how well job salary matches user expectations.
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not preferences.get('salary_expectation_min') and not preferences.get('salary_expectation_max'):
            # No salary preference, return neutral score
            return 0.5
        
        user_min = preferences.get('salary_expectation_min', 0)
        user_max = preferences.get('salary_expectation_max', float('inf'))
        
        if not job.salary_min and not job.salary_max:
            # Job has no salary info, return neutral score
            return 0.5
        
        job_min = job.salary_min or 0
        job_max = job.salary_max or float('inf')
        
        try:
            # Calculate overlap between user range and job range
            overlap_min = max(user_min, job_min)
            overlap_max = min(user_max, job_max) if user_max != float('inf') else job_max
            
            if overlap_min > overlap_max:
                # No overlap - calculate penalty based on distance
                if user_max < job_min:
                    # Job pays more than user expects - this is good, but not perfect match
                    gap = job_min - user_max
                    # Normalize: smaller gap = higher score
                    # Assuming max gap of 50000 for normalization
                    return max(0.0, 1.0 - (gap / 50000))
                else:
                    # Job pays less than user expects - this is bad
                    gap = user_min - job_max
                    return max(0.0, 0.5 - (gap / 100000))
            
            # Calculate overlap ratio
            user_range = user_max - user_min if user_max != float('inf') else (user_min * 2)
            job_range = job_max - job_min if job_max != float('inf') else (job_min * 2)
            
            overlap_range = overlap_max - overlap_min
            avg_range = (user_range + job_range) / 2
            
            if avg_range == 0:
                return 1.0
            
            match_ratio = overlap_range / avg_range
            return min(1.0, max(0.0, match_ratio))
            
        except Exception as e:
            logger.error(f"Error calculating salary match: {e}", exc_info=True)
            return 0.5
    
    def _calculate_recency_score(self, job: JobPosting) -> float:
        """
        Calculate recency score based on job age.
        
        Scoring:
        - 0-7 days: 1.0
        - 8-30 days: 0.8
        - 31-90 days: 0.6
        - 91-180 days: 0.4
        - 181+ days: 0.2
        
        Returns:
            Score between 0.0 and 1.0
        """
        if not job.created_at:
            return 0.2
        
        try:
            now = datetime.now()
            if isinstance(job.created_at, str):
                job_date = datetime.fromisoformat(job.created_at.replace('Z', '+00:00'))
            else:
                job_date = job.created_at
            
            # Handle timezone-aware datetime
            if job_date.tzinfo is not None:
                now = datetime.now(job_date.tzinfo)
            
            age_days = (now - job_date).days
            
            if age_days <= 7:
                return 1.0
            elif age_days <= 30:
                return 0.8
            elif age_days <= 90:
                return 0.6
            elif age_days <= 180:
                return 0.4
            else:
                return 0.2
                
        except Exception as e:
            logger.error(f"Error calculating recency score: {e}", exc_info=True)
            return 0.2
    
    def _calculate_composite_score(
        self,
        similarity_score: float,
        skill_score: float,
        salary_score: float,
        recency_score: float
    ) -> float:
        """
        Calculate weighted composite score.
        
        Weights:
        - Semantic Similarity: 40%
        - Skill Overlap: 30%
        - Salary Match: 20%
        - Job Recency: 10%
        
        Returns:
            Composite score between 0.0 and 1.0
        """
        composite = (
            0.40 * similarity_score +
            0.30 * skill_score +
            0.20 * salary_score +
            0.10 * recency_score
        )
        return min(1.0, max(0.0, composite))