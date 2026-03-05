"""Education Service - User education operations using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.orm import UserEducation
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class EducationService:
    """Education business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_educations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all educations for a user"""
        educations = (
            self.db.query(UserEducation)
            .filter(UserEducation.user_id == user_id)
            .order_by(desc(UserEducation.end_year), desc(UserEducation.start_year))
            .all()
        )
        
        return [edu.to_dict() for edu in educations]
    
    def get_user_educations_paginated(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated educations for a user"""
        # Get total count
        total = (
            self.db.query(UserEducation)
            .filter(UserEducation.user_id == user_id)
            .count()
        )
        
        # Get paginated results
        educations = (
            self.db.query(UserEducation)
            .filter(UserEducation.user_id == user_id)
            .order_by(desc(UserEducation.end_year), desc(UserEducation.start_year))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [edu.to_dict() for edu in educations], total
    
    def get_education(self, education_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get a specific education by ID"""
        education = (
            self.db.query(UserEducation)
            .filter(UserEducation.id == education_id)
            .first()
        )
        
        if not education:
            return None
        
        if user_id and education.user_id != user_id:
            raise AuthorizationError("You don't have permission to access this education")
        
        return education.to_dict()
    
    def create_education(self, user_id: int, education_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new education"""
        try:
            education = UserEducation(
                user_id=user_id,
                school=education_data['school'],
                degree=education_data.get('degree'),
                field_of_study=education_data.get('field_of_study'),
                start_year=education_data.get('start_year'),
                end_year=education_data.get('end_year'),
                grade=education_data.get('grade'),
                activities=education_data.get('activities'),
                description=education_data.get('description')
            )
            
            self.db.add(education)
            self.db.commit()
            self.db.refresh(education)
            
            logger.info(f"Education created: {education.id} for user {user_id}")
            return education.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Create education error: {e}", exc_info=True)
            raise
    
    def update_education(
        self, 
        education_id: int, 
        user_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an education"""
        education = (
            self.db.query(UserEducation)
            .filter(UserEducation.id == education_id)
            .first()
        )
        
        if not education:
            raise NotFoundError('Education')
        
        if education.user_id != user_id:
            raise AuthorizationError("You don't have permission to update this education")
        
        try:
            if 'school' in update_data:
                education.school = update_data['school']
            if 'degree' in update_data:
                education.degree = update_data['degree']
            if 'field_of_study' in update_data:
                education.field_of_study = update_data['field_of_study']
            if 'start_year' in update_data:
                education.start_year = update_data['start_year']
            if 'end_year' in update_data:
                education.end_year = update_data['end_year']
            if 'grade' in update_data:
                education.grade = update_data['grade']
            if 'activities' in update_data:
                education.activities = update_data['activities']
            if 'description' in update_data:
                education.description = update_data['description']
            
            self.db.commit()
            self.db.refresh(education)
            
            logger.info(f"Education updated: {education_id}")
            return education.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update education error: {e}", exc_info=True)
            raise
    
    def delete_education(self, education_id: int, user_id: int) -> None:
        """Delete an education"""
        education = (
            self.db.query(UserEducation)
            .filter(UserEducation.id == education_id)
            .first()
        )
        
        if not education:
            raise NotFoundError('Education')
        
        if education.user_id != user_id:
            raise AuthorizationError("You don't have permission to delete this education")
        
        try:
            self.db.delete(education)
            self.db.commit()
            logger.info(f"Education deleted: {education_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete education error: {e}", exc_info=True)
            raise
