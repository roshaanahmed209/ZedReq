"""Experience Service - User work experience operations using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import date

from models.orm import UserExperience
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ExperienceService:
    """Experience business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_experiences(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all experiences for a user"""
        experiences = (
            self.db.query(UserExperience)
            .filter(UserExperience.user_id == user_id)
            .order_by(
                desc(UserExperience.is_current),
                desc(UserExperience.end_date),
                desc(UserExperience.start_date)
            )
            .all()
        )
        
        return [exp.to_dict() for exp in experiences]
    
    def get_user_experiences_paginated(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated experiences for a user"""
        # Get total count
        total = (
            self.db.query(UserExperience)
            .filter(UserExperience.user_id == user_id)
            .count()
        )
        
        # Get paginated results
        experiences = (
            self.db.query(UserExperience)
            .filter(UserExperience.user_id == user_id)
            .order_by(
                desc(UserExperience.is_current),
                desc(UserExperience.end_date),
                desc(UserExperience.start_date)
            )
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [exp.to_dict() for exp in experiences], total
    
    def get_experience(self, experience_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get a specific experience by ID"""
        experience = (
            self.db.query(UserExperience)
            .filter(UserExperience.id == experience_id)
            .first()
        )
        
        if not experience:
            return None
        
        # Check authorization if user_id provided
        if user_id and experience.user_id != user_id:
            raise AuthorizationError("You don't have permission to access this experience")
        
        return experience.to_dict()
    
    def create_experience(self, user_id: int, experience_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new experience"""
        try:
            experience = UserExperience(
                user_id=user_id,
                title=experience_data['title'],
                company=experience_data['company'],
                location=experience_data.get('location'),
                start_date=experience_data.get('start_date'),
                end_date=experience_data.get('end_date'),
                is_current=experience_data.get('is_current', False),
                description=experience_data.get('description'),
                employment_type=experience_data.get('employment_type')
            )
            
            self.db.add(experience)
            self.db.commit()
            self.db.refresh(experience)
            
            logger.info(f"Experience created: {experience.id} for user {user_id}")
            return experience.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Create experience error: {e}", exc_info=True)
            raise
    
    def update_experience(
        self, 
        experience_id: int, 
        user_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an experience"""
        experience = (
            self.db.query(UserExperience)
            .filter(UserExperience.id == experience_id)
            .first()
        )
        
        if not experience:
            raise NotFoundError('Experience')
        
        if experience.user_id != user_id:
            raise AuthorizationError("You don't have permission to update this experience")
        
        try:
            if 'title' in update_data:
                experience.title = update_data['title']
            if 'company' in update_data:
                experience.company = update_data['company']
            if 'location' in update_data:
                experience.location = update_data['location']
            if 'start_date' in update_data:
                experience.start_date = update_data['start_date']
            if 'end_date' in update_data:
                experience.end_date = update_data['end_date']
            if 'is_current' in update_data:
                experience.is_current = update_data['is_current']
            if 'description' in update_data:
                experience.description = update_data['description']
            if 'employment_type' in update_data:
                experience.employment_type = update_data['employment_type']
            
            self.db.commit()
            self.db.refresh(experience)
            
            logger.info(f"Experience updated: {experience_id}")
            return experience.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update experience error: {e}", exc_info=True)
            raise
    
    def delete_experience(self, experience_id: int, user_id: int) -> None:
        """Delete an experience"""
        experience = (
            self.db.query(UserExperience)
            .filter(UserExperience.id == experience_id)
            .first()
        )
        
        if not experience:
            raise NotFoundError('Experience')
        
        if experience.user_id != user_id:
            raise AuthorizationError("You don't have permission to delete this experience")
        
        try:
            self.db.delete(experience)
            self.db.commit()
            logger.info(f"Experience deleted: {experience_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete experience error: {e}", exc_info=True)
            raise
