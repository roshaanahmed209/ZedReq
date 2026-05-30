"""Job Service - Business logic for job portal using SQLAlchemy ORM"""
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, and_, desc, func
from sqlalchemy.orm import Session, joinedload

# Import all ORM models - User must be imported first
from models.orm import User, JobPosting, JobApplication, JobSaved


class JobService:
    """Service class for job portal operations using SQLAlchemy ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Job Posting Operations
    # ========================================================================
    
    def create_job(self, poster_id: int, job_data: dict) -> JobPosting:
        """Create a new job posting"""
        # Parse location to extract city and country
        location = job_data.get('location')
        city, country = self._parse_location(location) if location else (None, None)
        
        job = JobPosting(
            poster_id=poster_id,
            title=job_data['title'],
            description=job_data['description'],
            company_name=job_data.get('company_name'),
            location=location,
            city=city,
            country=country,
            job_type=job_data.get('job_type', 'full-time'),
            is_remote=job_data.get('is_remote', False),
            experience_level=job_data.get('experience_level'),
            skills_required=job_data.get('skills_required'),
            salary_min=job_data.get('salary_min'),
            salary_max=job_data.get('salary_max'),
            status=job_data.get('status', 'active')
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        # Generate and store job_link
        job_link = f"/job/{job.job_id}"
        job.job_link = job_link
        self.db.commit()
        
        # Generate and store embedding asynchronously (non-blocking)
        try:
            from utils.job_embeddings import generate_job_embedding, store_job_embedding
            embedding = generate_job_embedding(job)
            if embedding:
                store_job_embedding(job.job_id, embedding, self.db)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to generate embedding for job {job.job_id}: {e}")
            # Don't fail job creation if embedding fails

        try:
            from services.job_cache import invalidate_job_lists_for_user, invalidate_job_lists_global
            invalidate_job_lists_for_user(poster_id)
            invalidate_job_lists_global()
        except Exception:
            pass
        
        return job
    
    def _parse_location(self, location_str: str) -> tuple[Optional[str], Optional[str]]:
        """
        Parse location string to extract city and country.
        
        Expected formats:
        - "City, State" (e.g., "San Francisco, CA")
        - "City, Country" (e.g., "London, UK")
        - "City" (only city)
        - "Remote" or "Hybrid"
        
        Args:
            location_str: Location string
            
        Returns:
            Tuple of (city, country)
        """
        if not location_str:
            return (None, None)
        
        location_str = location_str.strip()
        
        # Handle special cases
        if location_str.lower() in ['remote', 'hybrid']:
            return (None, None)
        
        # Split by comma
        parts = [p.strip() for p in location_str.split(',')]
        
        if len(parts) == 1:
            # Only city provided
            return (parts[0], None)
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
                return (city, 'USA')
            else:
                # Likely a country
                return (city, state_or_country)
        
        return (None, None)
    
    def get_job(self, job_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get a job posting with enriched data"""
        job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
        
        if not job:
            return None
        
        # Get poster info via raw query (users table uses old pattern)
        from config.database import get_database
        db_raw = get_database()
        poster = db_raw.fetch_one(
            'SELECT username, name FROM users WHERE uid = %s',
            (job.poster_id,)
        )
        
        result = job.to_dict(include_relations=True)
        result['poster_username'] = poster['username'] if poster else None
        result['poster_name'] = poster['name'] if poster else None
        
        if user_id:
            result['is_saved'] = self._is_job_saved(job_id, user_id)
            result['has_applied'] = self._has_applied(job_id, user_id)
        
        return result
    
    def get_all_jobs(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get all active job postings"""
        from services.job_cache import get_cached_job_list, cache_job_list

        if offset == 0 and user_id:
            cached = get_cached_job_list("all", user_id)
            if cached is not None:
                return cached[:limit]

        jobs = (
            self.db.query(JobPosting)
            .filter(JobPosting.status == 'active')
            .order_by(desc(JobPosting.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

        results = self._enrich_jobs(jobs, user_id)
        if offset == 0 and user_id:
            cache_job_list("all", user_id, results)
        return results
    
    def get_my_posted_jobs(
        self, 
        poster_id: int, 
        limit: int = 50, 
        offset: int = 0,
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get jobs posted by current user with enriched data"""
        jobs = (
            self.db.query(JobPosting)
            .filter(JobPosting.poster_id == poster_id)
            .order_by(desc(JobPosting.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        from services.job_cache import get_cached_job_list, cache_job_list

        uid = user_id or poster_id
        if offset == 0 and uid:
            cached = get_cached_job_list("posted", uid)
            if cached is not None:
                return cached[:limit]

        results = self._enrich_jobs(jobs, user_id)
        if offset == 0 and uid:
            cache_job_list("posted", uid, results)
        return results
    
    def search_jobs(
        self,
        user_id: int = None,
        query: str = None,
        location: str = None,
        job_type: str = None,
        is_remote: bool = None,
        experience_level: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search jobs with filters"""
        q = self.db.query(JobPosting).filter(JobPosting.status == 'active')
        
        if query:
            search_pattern = f'%{query}%'
            q = q.filter(
                or_(
                    JobPosting.title.ilike(search_pattern),
                    JobPosting.description.ilike(search_pattern),
                    JobPosting.skills_required.ilike(search_pattern),
                    JobPosting.company_name.ilike(search_pattern),
                )
            )
        
        if location:
            q = q.filter(JobPosting.location.ilike(f'%{location}%'))
        
        if job_type:
            q = q.filter(JobPosting.job_type == job_type)
        
        if is_remote is not None:
            q = q.filter(JobPosting.is_remote == is_remote)
        
        if experience_level:
            q = q.filter(JobPosting.experience_level == experience_level)
        
        jobs = q.order_by(desc(JobPosting.created_at)).limit(limit).offset(offset).all()
        
        return self._enrich_jobs(jobs, user_id)
    
    def get_remote_jobs(
        self, 
        limit: int = 50, 
        offset: int = 0, 
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get remote job postings"""
        from services.job_cache import get_cached_job_list, cache_job_list

        if offset == 0 and user_id:
            cached = get_cached_job_list("remote", user_id)
            if cached is not None:
                return cached[:limit]

        jobs = (
            self.db.query(JobPosting)
            .filter(
                and_(
                    JobPosting.is_remote == True,
                    JobPosting.status == 'active'
                )
            )
            .order_by(desc(JobPosting.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

        results = self._enrich_jobs(jobs, user_id)
        if offset == 0 and user_id:
            cache_job_list("remote", user_id, results)
        return results
    
    def update_job(
        self, 
        job_id: int, 
        poster_id: int, 
        job_data: dict
    ) -> Optional[JobPosting]:
        """Update a job posting"""
        job = (
            self.db.query(JobPosting)
            .filter(
                and_(
                    JobPosting.job_id == job_id,
                    JobPosting.poster_id == poster_id
                )
            )
            .first()
        )
        
        if not job:
            return None
        
        # Track if content fields changed (these affect embeddings)
        content_fields = {'title', 'description', 'company_name', 'location', 
                         'job_type', 'is_remote', 'experience_level', 'skills_required',
                         'salary_min', 'salary_max'}
        content_changed = any(key in content_fields for key in job_data.keys())
        location_changed = 'location' in job_data
        
        # Update fields
        for key, value in job_data.items():
            if value is not None and hasattr(job, key):
                setattr(job, key, value)
        
        # Parse and update city/country if location changed
        if location_changed and job_data.get('location'):
            city, country = self._parse_location(job_data['location'])
            job.city = city
            job.country = country
        
        self.db.commit()
        self.db.refresh(job)
        
        # Regenerate embedding if content fields changed
        if content_changed:
            try:
                from utils.job_embeddings import generate_job_embedding, store_job_embedding
                embedding = generate_job_embedding(job)
                if embedding:
                    store_job_embedding(job.job_id, embedding, self.db)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to regenerate embedding for job {job.job_id}: {e}")
                # Don't fail job update if embedding fails
        
        return job
    
    def close_job(self, job_id: int, poster_id: int) -> Optional[JobPosting]:
        """Close a job posting"""
        job = (
            self.db.query(JobPosting)
            .filter(
                and_(
                    JobPosting.job_id == job_id,
                    JobPosting.poster_id == poster_id
                )
            )
            .first()
        )
        
        if not job:
            return None
        
        job.status = 'closed'
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def delete_job(self, job_id: int, poster_id: int) -> bool:
        """Delete a job posting"""
        result = (
            self.db.query(JobPosting)
            .filter(
                and_(
                    JobPosting.job_id == job_id,
                    JobPosting.poster_id == poster_id
                )
            )
            .delete()
        )
        
        self.db.commit()
        return result > 0
    
    def get_total_jobs_count(self) -> int:
        """Get total count of active jobs"""
        return (
            self.db.query(func.count(JobPosting.job_id))
            .filter(JobPosting.status == 'active')
            .scalar()
        )
    
    def get_my_posted_jobs_count(self, poster_id: int) -> int:
        """Get total count of jobs posted by user"""
        return (
            self.db.query(func.count(JobPosting.job_id))
            .filter(JobPosting.poster_id == poster_id)
            .scalar()
        )
    
    # ========================================================================
    # Job Application Operations
    # ========================================================================
    
    def apply_to_job(
        self,
        job_id: int,
        applicant_id: int,
        cover_letter: str = None,
        match_score: int = None
    ) -> JobApplication:
        """Apply to a job posting"""
        # Check if job exists and is active
        job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
        
        if not job:
            raise ValueError("Job not found")
        if job.status != 'active':
            raise ValueError("Job is no longer accepting applications")
        if job.poster_id == applicant_id:
            raise ValueError("You cannot apply to your own job posting")
        
        # Check if already applied
        existing = (
            self.db.query(JobApplication)
            .filter(
                and_(
                    JobApplication.job_id == job_id,
                    JobApplication.applicant_id == applicant_id
                )
            )
            .first()
        )
        
        if existing:
            raise ValueError("You have already applied to this job")
        
        # Create application
        application = JobApplication(
            job_id=job_id,
            applicant_id=applicant_id,
            cover_letter=cover_letter,
            match_score=match_score
        )
        
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)

        try:
            from services.job_cache import invalidate_job_lists_for_user
            invalidate_job_lists_for_user(applicant_id)
        except Exception:
            pass

        return application
    
    def get_job_applicants(
        self, 
        job_id: int, 
        poster_id: int, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get applicants for a job (only job poster can see)"""
        # Verify ownership
        job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
        
        if not job or job.poster_id != poster_id:
            raise PermissionError("You don't have permission to view applicants for this job")
        
        applications = (
            self.db.query(JobApplication)
            .filter(JobApplication.job_id == job_id)
            .order_by(desc(JobApplication.applied_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        # Get applicant info
        from config.database import get_database
        db_raw = get_database()
        
        results = []
        for app in applications:
            data = app.to_dict()
            
            # Get user info with resume and profile_url
            user = db_raw.fetch_one(
                '''SELECT u.username, u.name, u.user_email, u.profile_url, 
                          d.profile_pic, d.skills, d.short_desc, d.about, d.resume,
                          d.current_status, d.role, d.company, d.location, d.industry
                   FROM users u
                   LEFT JOIN description d ON u.description_id = d.desc_id
                   WHERE u.uid = %s''',
                (app.applicant_id,)
            )
            
            if user:
                # Generate full profile URL
                from utils.profile_url import get_full_profile_url
                full_profile_url = get_full_profile_url(user.get('profile_url')) if user.get('profile_url') else None
                
                data.update({
                    'applicant_id': app.applicant_id,
                    'applicant_username': user['username'],
                    'applicant_name': user['name'],
                    'applicant_email': user['user_email'],
                    'profile_pic': user.get('profile_pic'),
                    'profile_url': full_profile_url,
                    'skills': user.get('skills'),
                    'short_desc': user.get('short_desc'),
                    'about': user.get('about'),
                    'resume': user.get('resume'),
                    'current_status': user.get('current_status'),
                    'role': user.get('role'),
                    'company': user.get('company'),
                    'location': user.get('location'),
                    'industry': user.get('industry')
                })
            
            results.append(data)
        
        return results
    
    def get_my_applications(
        self, 
        applicant_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get applications submitted by user"""
        applications = (
            self.db.query(JobApplication)
            .join(JobPosting)
            .filter(JobApplication.applicant_id == applicant_id)
            .order_by(desc(JobApplication.applied_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        results = []
        for app in applications:
            data = app.to_dict()
            job = app.job
            data.update({
                'job_title': job.title,
                'company_name': job.company_name,
                'location': job.location,
                'job_type': job.job_type,
                'is_remote': job.is_remote,
                'job_status': job.status
            })
            results.append(data)
        
        return results
    
    def update_application_status(
        self,
        application_id: int,
        status: str,
        poster_id: int
    ) -> Optional[JobApplication]:
        """Update application status (only job poster can do this)"""
        application = (
            self.db.query(JobApplication)
            .join(JobPosting)
            .filter(
                and_(
                    JobApplication.application_id == application_id,
                    JobPosting.poster_id == poster_id
                )
            )
            .first()
        )
        
        if not application:
            return None
        
        application.status = status
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def withdraw_application(self, application_id: int, applicant_id: int) -> bool:
        """Withdraw an application"""
        result = (
            self.db.query(JobApplication)
            .filter(
                and_(
                    JobApplication.application_id == application_id,
                    JobApplication.applicant_id == applicant_id
                )
            )
            .delete()
        )
        
        self.db.commit()
        return result > 0
    
    # ========================================================================
    # Saved Jobs Operations
    # ========================================================================
    
    def toggle_save_job(self, job_id: int, user_id: int) -> Dict[str, Any]:
        """Toggle save/bookmark status for a job"""
        # Check if job exists
        job = self.db.query(JobPosting).filter(JobPosting.job_id == job_id).first()
        if not job:
            raise ValueError("Job not found")
        
        # Check if already saved
        existing = (
            self.db.query(JobSaved)
            .filter(
                and_(
                    JobSaved.job_id == job_id,
                    JobSaved.user_id == user_id
                )
            )
            .first()
        )
        
        if existing:
            # Unsave
            self.db.delete(existing)
            self.db.commit()
            result = {'is_saved': False, 'message': 'Job unsaved'}
        else:
            # Save
            saved = JobSaved(job_id=job_id, user_id=user_id)
            self.db.add(saved)
            self.db.commit()
            result = {'is_saved': True, 'message': 'Job saved'}

        try:
            from services.job_cache import invalidate_job_lists_for_user
            invalidate_job_lists_for_user(user_id)
        except Exception:
            pass

        return result
    
    def get_saved_jobs(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's saved jobs (batched enrichment, no per-row poster queries)."""
        from services.job_cache import get_cached_job_list, cache_job_list

        if offset == 0:
            cached = get_cached_job_list("saved", user_id)
            if cached is not None:
                return cached[:limit]

        saved_rows = (
            self.db.query(JobSaved)
            .join(JobPosting)
            .filter(JobSaved.user_id == user_id)
            .order_by(desc(JobSaved.saved_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

        jobs = [row.job for row in saved_rows]
        saved_at_by_job_id = {
            row.job.job_id: row.saved_at for row in saved_rows
        }

        results = self._enrich_jobs(jobs, user_id)
        for data in results:
            data["is_saved"] = True
            job_id = data.get("job_id")
            saved_at = saved_at_by_job_id.get(job_id)
            if saved_at is not None:
                data["saved_at"] = (
                    saved_at.isoformat() if hasattr(saved_at, "isoformat") else str(saved_at)
                )

        if offset == 0:
            cache_job_list("saved", user_id, results)

        return results
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _is_job_saved(self, job_id: int, user_id: int) -> bool:
        """Check if a job is saved by user"""
        return (
            self.db.query(JobSaved)
            .filter(
                and_(
                    JobSaved.job_id == job_id,
                    JobSaved.user_id == user_id
                )
            )
            .first() is not None
        )
    
    def _has_applied(self, job_id: int, user_id: int) -> bool:
        """Check if user has applied to a job"""
        return (
            self.db.query(JobApplication)
            .filter(
                and_(
                    JobApplication.job_id == job_id,
                    JobApplication.applicant_id == user_id
                )
            )
            .first() is not None
        )
    
    def _enrich_jobs(
        self, 
        jobs: List[JobPosting], 
        user_id: int = None
    ) -> List[Dict[str, Any]]:
        """Enrich job data with poster info, user-specific flags, and counts (optimized with batch queries)"""
        from config.database import get_database
        db_raw = get_database()
        
        if not jobs:
            return []
        
        # Batch query: Get all poster info in a single query
        poster_ids = list(set([job.poster_id for job in jobs]))
        poster_info_map = {}
        
        if poster_ids:
            # Build query with IN clause for all poster IDs
            placeholders = ','.join(['%s'] * len(poster_ids))
            query = f'SELECT uid, username, name FROM users WHERE uid IN ({placeholders})'
            posters = db_raw.fetch_all(query, tuple(poster_ids))
            
            for poster in posters:
                poster_info_map[poster['uid']] = {
                    'username': poster.get('username'),
                    'name': poster.get('name')
                }
        
        # Batch query: Get user-specific flags if user_id provided
        saved_job_ids = set()
        applied_job_ids = set()
        
        if user_id:
            job_ids = [job.job_id for job in jobs]
            
            # Batch query for saved jobs
            saved_jobs = (
                self.db.query(JobSaved.job_id)
                .filter(
                    and_(
                        JobSaved.job_id.in_(job_ids),
                        JobSaved.user_id == user_id
                    )
                )
                .all()
            )
            saved_job_ids = {job_id for (job_id,) in saved_jobs}
            
            # Batch query for applied jobs
            applied_jobs = (
                self.db.query(JobApplication.job_id)
                .filter(
                    and_(
                        JobApplication.job_id.in_(job_ids),
                        JobApplication.applicant_id == user_id
                    )
                )
                .all()
            )
            applied_job_ids = {job_id for (job_id,) in applied_jobs}
        
        # Build results
        results = []
        for job in jobs:
            # Get base job data with relations (application_count, save_count)
            data = job.to_dict(include_relations=True)
            
            # Get poster info from batch query result
            poster_info = poster_info_map.get(job.poster_id, {})
            data['poster_username'] = poster_info.get('username')
            data['poster_name'] = poster_info.get('name')
            
            if user_id:
                data['is_saved'] = job.job_id in saved_job_ids
                data['has_applied'] = job.job_id in applied_job_ids
            
            results.append(data)
        
        return results
