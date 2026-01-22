"""Jobs Router - Job Portal CRUD operations using SQLAlchemy ORM"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from dependencies.auth import get_current_user
from config.database_orm import get_db
from services.job_service import JobService
from schemas.job import (
    JobPostingCreate,
    JobPostingUpdate,
    JobPostingResponse,
    JobPostingListResponse,
    JobApplicationCreate,
    JobApplicationUpdate,
    JobApplicationResponse,
    JobApplicationListResponse,
    JobSavedToggleResponse,
    JobType,
    ExperienceLevel
)

router = APIRouter()


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    """Dependency to get JobService with database session"""
    return JobService(db)


# ============================================================================
# Job Posting Endpoints
# ============================================================================

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobPostingCreate,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Create a new job posting"""
    job = service.create_job(
        poster_id=current_user["id"],
        job_data=job_data.model_dump()
    )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job posting"
        )
    
    return {
        **job.to_dict(),
        "message": "Job posted successfully"
    }


@router.get("", response_model=JobPostingListResponse)
async def get_jobs(
    query: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    is_remote: Optional[bool] = Query(None, description="Remote jobs only"),
    experience_level: Optional[str] = Query(None, description="Experience level"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Get all active job postings with optional filters"""
    # If any filter is provided, use search
    if any([query, location, job_type, is_remote is not None, experience_level]):
        jobs = service.search_jobs(
            user_id=current_user["id"],
            query=query,
            location=location,
            job_type=job_type,
            is_remote=is_remote,
            experience_level=experience_level,
            limit=limit,
            offset=offset
        )
    else:
        jobs = service.get_all_jobs(limit, offset, current_user["id"])
    
    total = service.get_total_jobs_count()
    
    return {
        "jobs": jobs,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/remote")
async def get_remote_jobs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Get all remote job postings"""
    jobs = service.get_remote_jobs(limit, offset, current_user["id"])
    
    return {
        "jobs": jobs,
        "total": len(jobs),
        "limit": limit,
        "offset": offset
    }


@router.get("/my-posts")
async def get_my_posted_jobs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Get jobs posted by current user"""
    jobs = service.get_my_posted_jobs(current_user["id"], limit, offset)
    
    return {
        "jobs": jobs,
        "total": len(jobs)
    }


@router.get("/saved")
async def get_saved_jobs(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Get user's saved/bookmarked jobs"""
    jobs = service.get_saved_jobs(current_user["id"], limit, offset)
    
    return {
        "jobs": jobs,
        "total": len(jobs)
    }


@router.get("/applications")
async def get_my_applications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Get current user's job applications"""
    applications = service.get_my_applications(current_user["id"], limit, offset)
    
    return {
        "applications": applications,
        "total": len(applications)
    }


@router.get("/{job_id}")
async def get_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Get a specific job posting by ID"""
    job = service.get_job(job_id, current_user["id"])
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job


@router.put("/{job_id}")
async def update_job(
    job_id: int,
    job_data: JobPostingUpdate,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Update a job posting (only by owner)"""
    # Filter out None values
    update_data = {k: v for k, v in job_data.model_dump().items() if v is not None}
    
    job = service.update_job(job_id, current_user["id"], update_data)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or you don't have permission to update it"
        )
    
    return {
        **job.to_dict(),
        "message": "Job updated successfully"
    }


@router.post("/{job_id}/close")
async def close_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Close a job posting (only by owner)"""
    job = service.close_job(job_id, current_user["id"])
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or you don't have permission to close it"
        )
    
    return {
        **job.to_dict(),
        "message": "Job closed successfully"
    }


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Delete a job posting (only by owner)"""
    result = service.delete_job(job_id, current_user["id"])
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or you don't have permission to delete it"
        )
    
    return {"message": "Job deleted successfully"}


# ============================================================================
# Job Application Endpoints
# ============================================================================

@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: int,
    application_data: JobApplicationCreate,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Apply to a job posting"""
    try:
        application = service.apply_to_job(
            job_id=job_id,
            applicant_id=current_user["id"],
            cover_letter=application_data.cover_letter
        )
        
        return {
            **application.to_dict(),
            "message": "Application submitted successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{job_id}/applicants")
async def get_job_applicants(
    job_id: int,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Get all applicants for a job (only job poster can see)"""
    try:
        applicants = service.get_job_applicants(
            job_id=job_id,
            poster_id=current_user["id"],
            limit=limit,
            offset=offset
        )
        
        return {
            "applicants": applicants,
            "total": len(applicants)
        }
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    status_data: JobApplicationUpdate,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Update application status (only job poster can do this)"""
    application = service.update_application_status(
        application_id=application_id,
        status=status_data.status.value,
        poster_id=current_user["id"]
    )
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or you don't have permission to update it"
        )
    
    return {
        **application.to_dict(),
        "message": f"Application status updated to {status_data.status.value}"
    }


@router.delete("/applications/{application_id}")
async def withdraw_application(
    application_id: int,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Withdraw a job application (only by applicant)"""
    result = service.withdraw_application(application_id, current_user["id"])
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or you don't have permission to withdraw it"
        )
    
    return {"message": "Application withdrawn successfully"}


# ============================================================================
# Saved Jobs Endpoints
# ============================================================================

@router.post("/{job_id}/save", response_model=JobSavedToggleResponse)
async def toggle_save_job(
    job_id: int,
    current_user: dict = Depends(get_current_user),
    service: JobService = Depends(get_job_service)
):
    """Toggle save/bookmark status for a job"""
    try:
        result = service.toggle_save_job(job_id, current_user["id"])
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
