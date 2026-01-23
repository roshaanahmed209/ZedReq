"""Job Service - Business logic for job portal using SQLAlchemy ORM"""
from typing import Optional, List, Dict, Any
from sqlalchemy import or_, and_, desc
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
        job = JobPosting(
            poster_id=poster_id,
            title=job_data['title'],
            description=job_data['description'],
            company_name=job_data.get('company_name'),
            location=job_data.get('location'),
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
        return job
    
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
        jobs = (
            self.db.query(JobPosting)
            .filter(JobPosting.status == 'active')
            .order_by(desc(JobPosting.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return self._enrich_jobs(jobs, user_id)
    
    def get_my_posted_jobs(
        self, 
        poster_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get jobs posted by current user"""
        jobs = (
            self.db.query(JobPosting)
            .filter(JobPosting.poster_id == poster_id)
            .order_by(desc(JobPosting.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [
            {**job.to_dict(include_relations=True)}
            for job in jobs
        ]
    
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
                    JobPosting.skills_required.ilike(search_pattern)
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
        
        return self._enrich_jobs(jobs, user_id)
    
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
        
        # Update fields
        for key, value in job_data.items():
            if value is not None and hasattr(job, key):
                setattr(job, key, value)
        
        self.db.commit()
        self.db.refresh(job)
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
            self.db.query(JobPosting)
            .filter(JobPosting.status == 'active')
            .count()
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
            
            # Get user info
            user = db_raw.fetch_one(
                '''SELECT u.username, u.name, u.user_email, d.profile_pic, d.skills, d.short_desc
                   FROM users u
                   LEFT JOIN description d ON u.description_id = d.desc_id
                   WHERE u.uid = %s''',
                (app.applicant_id,)
            )
            
            if user:
                data.update({
                    'applicant_username': user['username'],
                    'applicant_name': user['name'],
                    'applicant_email': user['user_email'],
                    'profile_pic': user.get('profile_pic'),
                    'skills': user.get('skills'),
                    'short_desc': user.get('short_desc')
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
            return {'is_saved': False, 'message': 'Job unsaved'}
        else:
            # Save
            saved = JobSaved(job_id=job_id, user_id=user_id)
            self.db.add(saved)
            self.db.commit()
            return {'is_saved': True, 'message': 'Job saved'}
    
    def get_saved_jobs(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's saved jobs"""
        saved_jobs = (
            self.db.query(JobSaved)
            .join(JobPosting)
            .filter(JobSaved.user_id == user_id)
            .order_by(desc(JobSaved.saved_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        results = []
        for saved in saved_jobs:
            job = saved.job
            data = job.to_dict()
            data['saved_at'] = saved.saved_at.isoformat() if saved.saved_at else None
            data['is_saved'] = True
            data['has_applied'] = self._has_applied(job.job_id, user_id)
            
            # Get poster info
            from config.database import get_database
            db_raw = get_database()
            poster = db_raw.fetch_one(
                'SELECT username, name FROM users WHERE uid = %s',
                (job.poster_id,)
            )
            data['poster_username'] = poster['username'] if poster else None
            data['poster_name'] = poster['name'] if poster else None
            
            results.append(data)
        
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
        """Enrich job data with poster info and user-specific flags"""
        from config.database import get_database
        db_raw = get_database()
        
        results = []
        for job in jobs:
            data = job.to_dict()
            
            # Get poster info
            poster = db_raw.fetch_one(
                'SELECT username, name FROM users WHERE uid = %s',
                (job.poster_id,)
            )
            data['poster_username'] = poster['username'] if poster else None
            data['poster_name'] = poster['name'] if poster else None
            
            if user_id:
                data['is_saved'] = self._is_job_saved(job.job_id, user_id)
                data['has_applied'] = self._has_applied(job.job_id, user_id)
            
            results.append(data)
        
        return results
