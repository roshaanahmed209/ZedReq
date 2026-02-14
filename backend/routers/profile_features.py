"""Profile Features Router - Experience, Education, Projects, Recommendations, Interests"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import logging

from dependencies.auth import get_current_user
from dependencies.rate_limit import profile_rate_limit, write_rate_limit, analytics_rate_limit
from config.database_orm import get_db
from services.experience_service import ExperienceService
from services.education_service import EducationService
from services.project_service import ProjectService
from services.recommendation_service import RecommendationService
from services.interest_service import InterestService
from services.profile_analytics_service import ProfileAnalyticsService
from utils.api_security import sanitize_text_for_storage, validate_url_safe
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


def get_experience_service(db: Session = Depends(get_db)) -> ExperienceService:
    return ExperienceService(db)


def get_education_service(db: Session = Depends(get_db)) -> EducationService:
    return EducationService(db)


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    return RecommendationService(db)


def get_interest_service(db: Session = Depends(get_db)) -> InterestService:
    return InterestService(db)


def get_analytics_service(db: Session = Depends(get_db)) -> ProfileAnalyticsService:
    return ProfileAnalyticsService(db)


# ============================================================================
# Experience Endpoints
# ============================================================================

class ExperienceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=150)
    company: str = Field(..., min_length=1, max_length=150)
    location: Optional[str] = Field(None, max_length=150)
    start_date: Optional[str] = None  # ISO date string
    end_date: Optional[str] = None  # ISO date string
    is_current: bool = False
    description: Optional[str] = None
    employment_type: Optional[str] = Field(None, max_length=50)
    
    @validator('title', 'company', 'location', 'employment_type')
    def sanitize_text_fields(cls, v):
        """Sanitize text fields to prevent XSS"""
        if v is None:
            return v
        return sanitize_text_for_storage(str(v), max_length=150)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Sanitize description field"""
        if v is None:
            return v
        return sanitize_text_for_storage(str(v), max_length=5000)


class ExperienceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    company: Optional[str] = Field(None, min_length=1, max_length=150)
    location: Optional[str] = Field(None, max_length=150)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    employment_type: Optional[str] = Field(None, max_length=50)


@router.get("/experience/{user_id}")
async def get_user_experiences(
    user_id: int,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    service: ExperienceService = Depends(get_experience_service)
):
    """Get all experiences for a user with pagination"""
    try:
        experiences, total = service.get_user_experiences_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return {
            "experiences": experiences,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting user experiences: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve experiences"
        )


@router.post("/experience", status_code=status.HTTP_201_CREATED)
async def create_experience(
    experience_data: ExperienceCreate,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    service: ExperienceService = Depends(get_experience_service)
):
    """Create a new experience"""
    try:
        data = experience_data.dict()
        # Validate and parse dates
        if data.get('start_date'):
            try:
                data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)"
                )
        if data.get('end_date'):
            try:
                data['end_date'] = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)"
                )
        
        # Validate date logic
        if data.get('start_date') and data.get('end_date') and not data.get('is_current'):
            if data['end_date'] < data['start_date']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end_date cannot be before start_date"
                )
        
        experience = service.create_experience(current_user["id"], data)
        return experience
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating experience: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create experience"
        )


@router.put("/experience/{experience_id}")
async def update_experience(
    experience_id: int,
    experience_data: ExperienceUpdate,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    service: ExperienceService = Depends(get_experience_service)
):
    """Update an experience"""
    try:
        data = {k: v for k, v in experience_data.dict().items() if v is not None}
        if 'start_date' in data:
            try:
                data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)"
                )
        if 'end_date' in data:
            try:
                data['end_date'] = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)"
                )
        
        experience = service.update_experience(experience_id, current_user["id"], data)
        return experience
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating experience: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update experience"
        )


@router.delete("/experience/{experience_id}")
async def delete_experience(
    experience_id: int,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    service: ExperienceService = Depends(get_experience_service)
):
    """Delete an experience"""
    try:
        service.delete_experience(experience_id, current_user["id"])
        return {"message": "Experience deleted successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experience not found"
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error deleting experience: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete experience"
        )


# ============================================================================
# Education Endpoints
# ============================================================================

class EducationCreate(BaseModel):
    school: str = Field(..., min_length=1, max_length=200)
    degree: Optional[str] = Field(None, max_length=150)
    field_of_study: Optional[str] = Field(None, max_length=150)
    start_year: Optional[int] = Field(None, ge=1900, le=2100)
    end_year: Optional[int] = Field(None, ge=1900, le=2100)
    grade: Optional[str] = Field(None, max_length=50)
    activities: Optional[str] = None
    description: Optional[str] = None
    
    @validator('school', 'degree', 'field_of_study', 'grade')
    def sanitize_text_fields(cls, v):
        """Sanitize text fields"""
        if v is None:
            return v
        return sanitize_text_for_storage(str(v), max_length=200)
    
    @validator('activities', 'description')
    def sanitize_description_fields(cls, v):
        """Sanitize description fields"""
        if v is None:
            return v
        return sanitize_text_for_storage(str(v), max_length=5000)
    
    @validator('end_year')
    def validate_year_range(cls, v, values):
        """Validate that end_year is after start_year"""
        if v and 'start_year' in values and values['start_year']:
            if v < values['start_year']:
                raise ValueError("end_year cannot be before start_year")
        return v


class EducationUpdate(BaseModel):
    school: Optional[str] = Field(None, min_length=1, max_length=200)
    degree: Optional[str] = Field(None, max_length=150)
    field_of_study: Optional[str] = Field(None, max_length=150)
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    grade: Optional[str] = Field(None, max_length=50)
    activities: Optional[str] = None
    description: Optional[str] = None


@router.get("/education/{user_id}")
async def get_user_educations(
    user_id: int,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    service: EducationService = Depends(get_education_service)
):
    """Get all educations for a user with pagination"""
    try:
        educations, total = service.get_user_educations_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return {
            "educations": educations,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting user educations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve educations"
        )


@router.post("/education", status_code=status.HTTP_201_CREATED)
async def create_education(
    education_data: EducationCreate,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    service: EducationService = Depends(get_education_service)
):
    """Create a new education"""
    try:
        education = service.create_education(current_user["id"], education_data.dict())
        return education
    except Exception as e:
        logger.error(f"Error creating education: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create education"
        )


@router.put("/education/{education_id}")
async def update_education(
    education_id: int,
    education_data: EducationUpdate,
    current_user: dict = Depends(get_current_user),
    service: EducationService = Depends(get_education_service)
):
    """Update an education"""
    data = {k: v for k, v in education_data.dict().items() if v is not None}
    education = service.update_education(education_id, current_user["id"], data)
    return education


@router.delete("/education/{education_id}")
async def delete_education(
    education_id: int,
    current_user: dict = Depends(get_current_user),
    service: EducationService = Depends(get_education_service)
):
    """Delete an education"""
    service.delete_education(education_id, current_user["id"])
    return {"message": "Education deleted successfully"}


# ============================================================================
# Project Endpoints
# ============================================================================

class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    associated_with: Optional[str] = Field(None, max_length=200)
    technologies: Optional[List[str]] = []
    
    @validator('title', 'associated_with')
    def sanitize_text_fields(cls, v):
        """Sanitize text fields"""
        if v is None:
            return v
        return sanitize_text_for_storage(str(v), max_length=200)
    
    @validator('description')
    def sanitize_description(cls, v):
        """Sanitize description field"""
        if v is None:
            return v
        return sanitize_text_for_storage(str(v), max_length=5000)
    
    @validator('url')
    def validate_url(cls, v):
        """Validate and sanitize URL"""
        if v is None or v == "":
            return v
        try:
            return validate_url_safe(v)
        except ValueError as e:
            raise ValueError(f"Invalid URL: {str(e)}")


class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    associated_with: Optional[str] = Field(None, max_length=200)
    technologies: Optional[List[str]] = None


@router.get("/projects/{user_id}")
async def get_user_projects(
    user_id: int,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    service: ProjectService = Depends(get_project_service)
):
    """Get all projects for a user with pagination"""
    try:
        projects, total = service.get_user_projects_paginated(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return {
            "projects": projects,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting user projects: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve projects"
        )


@router.post("/projects", status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(write_rate_limit),  # write_rate_limit includes get_current_user
    service: ProjectService = Depends(get_project_service)
):
    """Create a new project"""
    try:
        data = project_data.dict()
        # Validate and parse dates
        if data.get('start_date'):
            try:
                data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format (YYYY-MM-DD)"
                )
        if data.get('end_date'):
            try:
                data['end_date'] = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')).date()
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format (YYYY-MM-DD)"
                )
        
        # Validate date logic
        if data.get('start_date') and data.get('end_date'):
            if data['end_date'] < data['start_date']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="end_date cannot be before start_date"
                )
        
        # Validate technologies list
        if data.get('technologies'):
            if not isinstance(data['technologies'], list):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="technologies must be a list"
                )
            if len(data['technologies']) > 50:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Maximum 50 technologies allowed"
                )
            # Sanitize each technology
            data['technologies'] = [sanitize_text_for_storage(str(t), max_length=100) for t in data['technologies']]
        
        project = service.create_project(current_user["id"], data)
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )


@router.put("/projects/{project_id}")
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Update a project"""
    from datetime import datetime
    
    data = {k: v for k, v in project_data.dict().items() if v is not None}
    if 'start_date' in data:
        data['start_date'] = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00')).date()
    if 'end_date' in data:
        data['end_date'] = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00')).date()
    
    project = service.update_project(project_id, current_user["id"], data)
    return project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    """Delete a project"""
    service.delete_project(project_id, current_user["id"])
    return {"message": "Project deleted successfully"}


# ============================================================================
# Recommendation Endpoints
# ============================================================================

class RecommendationCreate(BaseModel):
    user_id: int
    relationship: Optional[str] = Field(None, max_length=100)
    recommendation_text: str = Field(..., min_length=1)
    is_visible: bool = True


class RecommendationUpdate(BaseModel):
    is_visible: Optional[bool] = None


@router.get("/recommendations/{user_id}")
async def get_user_recommendations(
    user_id: int,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Get all visible recommendations for a user with pagination"""
    try:
        recommendations, total = service.get_user_recommendations_paginated(
            user_id=user_id,
            include_recommender_info=True,
            limit=limit,
            offset=offset
        )
        return {
            "recommendations": recommendations,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting user recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recommendations"
        )


@router.post("/recommendations", status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    recommendation_data: RecommendationCreate,
    current_user: dict = Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Create a new recommendation"""
    recommendation = service.create_recommendation(
        user_id=recommendation_data.user_id,
        recommender_id=current_user["id"],
        recommendation_data=recommendation_data.dict(exclude={'user_id'})
    )
    return recommendation


@router.put("/recommendations/{recommendation_id}")
async def update_recommendation(
    recommendation_id: int,
    recommendation_data: RecommendationUpdate,
    current_user: dict = Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Update a recommendation visibility"""
    data = {k: v for k, v in recommendation_data.dict().items() if v is not None}
    recommendation = service.update_recommendation(recommendation_id, current_user["id"], data)
    return recommendation


@router.delete("/recommendations/{recommendation_id}")
async def delete_recommendation(
    recommendation_id: int,
    current_user: dict = Depends(get_current_user),
    service: RecommendationService = Depends(get_recommendation_service)
):
    """Delete a recommendation"""
    service.delete_recommendation(recommendation_id, current_user["id"])
    return {"message": "Recommendation deleted successfully"}


# ============================================================================
# Interest Endpoints
# ============================================================================

class InterestCreate(BaseModel):
    interest_type: str = Field(..., max_length=50)  # company, group, influencer, school
    name: str = Field(..., min_length=1, max_length=200)
    url: Optional[str] = None
    
    @validator('interest_type')
    def validate_interest_type(cls, v):
        """Validate interest type"""
        allowed_types = ['company', 'group', 'influencer', 'school']
        if v.lower() not in allowed_types:
            raise ValueError(f"interest_type must be one of: {', '.join(allowed_types)}")
        return v.lower()
    
    @validator('name')
    def sanitize_name(cls, v):
        """Sanitize name field"""
        return sanitize_text_for_storage(str(v), max_length=200)
    
    @validator('url')
    def validate_url(cls, v):
        """Validate and sanitize URL"""
        if v is None or v == "":
            return v
        try:
            return validate_url_safe(v)
        except ValueError as e:
            raise ValueError(f"Invalid URL: {str(e)}")


class InterestUpdate(BaseModel):
    interest_type: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = None


@router.get("/interests/{user_id}")
async def get_user_interests(
    user_id: int,
    interest_type: Optional[str] = Query(None, description="Filter by interest type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    current_user: dict = Depends(profile_rate_limit),  # profile_rate_limit includes get_current_user
    service: InterestService = Depends(get_interest_service)
):
    """Get all interests for a user with pagination"""
    try:
        # Validate interest_type if provided
        if interest_type:
            allowed_types = ['company', 'group', 'influencer', 'school']
            if interest_type.lower() not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"interest_type must be one of: {', '.join(allowed_types)}"
                )
        
        interests, total = service.get_user_interests_paginated(
            user_id=user_id,
            interest_type=interest_type.lower() if interest_type else None,
            limit=limit,
            offset=offset
        )
        return {
            "interests": interests,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user interests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interests"
        )


@router.post("/interests", status_code=status.HTTP_201_CREATED)
async def create_interest(
    interest_data: InterestCreate,
    current_user: dict = Depends(get_current_user),
    service: InterestService = Depends(get_interest_service)
):
    """Create a new interest"""
    interest = service.create_interest(current_user["id"], interest_data.dict())
    return interest


@router.put("/interests/{interest_id}")
async def update_interest(
    interest_id: int,
    interest_data: InterestUpdate,
    current_user: dict = Depends(get_current_user),
    service: InterestService = Depends(get_interest_service)
):
    """Update an interest"""
    data = {k: v for k, v in interest_data.dict().items() if v is not None}
    interest = service.update_interest(interest_id, current_user["id"], data)
    return interest


@router.delete("/interests/{interest_id}")
async def delete_interest(
    interest_id: int,
    current_user: dict = Depends(get_current_user),
    service: InterestService = Depends(get_interest_service)
):
    """Delete an interest"""
    service.delete_interest(interest_id, current_user["id"])
    return {"message": "Interest deleted successfully"}


# ============================================================================
# Profile Analytics Endpoints
# ============================================================================

@router.get("/analytics/{user_id}")
async def get_profile_analytics(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: dict = Depends(analytics_rate_limit),  # analytics_rate_limit includes get_current_user
    service: ProfileAnalyticsService = Depends(get_analytics_service)
):
    """Get profile analytics summary (only accessible by profile owner)"""
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own analytics"
        )
    
    try:
        summary = service.get_analytics_summary(user_id, days=days)
        return summary
    except Exception as e:
        logger.error(f"Error getting analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


@router.get("/analytics/{user_id}/views")
async def get_profile_views(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    service: ProfileAnalyticsService = Depends(get_analytics_service)
):
    """Get profile views (only accessible by profile owner)"""
    if current_user["id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own analytics"
        )
    
    views = service.get_profile_views(user_id, days=days, include_viewer_info=True)
    return {"views": views, "total": len(views)}


class TrackViewRequest(BaseModel):
    user_id: int
    source: str = "direct"


@router.post("/analytics/track-view")
async def track_profile_view(
    request: TrackViewRequest,
    current_user: dict = Depends(get_current_user),
    service: ProfileAnalyticsService = Depends(get_analytics_service)
):
    """Track a profile view (called when someone views a profile)"""
    try:
        # Validate source
        allowed_sources = ['direct', 'search', 'feed', 'recommendation', 'other']
        source = request.source.lower() if request.source else 'direct'
        if source not in allowed_sources:
            source = 'other'
        
        viewer_id = current_user.get("id") if current_user else None
        service.track_profile_view(request.user_id, viewer_id=viewer_id, source=source)
        return {"message": "View tracked"}
    except Exception as e:
        logger.error(f"Error tracking profile view: {e}", exc_info=True)
        # Don't fail the request if analytics tracking fails
        return {"message": "View tracking attempted"}
