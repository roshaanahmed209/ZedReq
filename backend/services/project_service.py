"""Project Service - User project operations using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.orm import UserProject
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ProjectService:
    """Project business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_projects(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all projects for a user"""
        projects = (
            self.db.query(UserProject)
            .filter(UserProject.user_id == user_id)
            .order_by(desc(UserProject.end_date), desc(UserProject.start_date))
            .all()
        )
        
        return [proj.to_dict() for proj in projects]
    
    def get_user_projects_paginated(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated projects for a user"""
        # Get total count
        total = (
            self.db.query(UserProject)
            .filter(UserProject.user_id == user_id)
            .count()
        )
        
        # Get paginated results
        projects = (
            self.db.query(UserProject)
            .filter(UserProject.user_id == user_id)
            .order_by(desc(UserProject.end_date), desc(UserProject.start_date))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [proj.to_dict() for proj in projects], total
    
    def get_project(self, project_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get a specific project by ID"""
        project = (
            self.db.query(UserProject)
            .filter(UserProject.id == project_id)
            .first()
        )
        
        if not project:
            return None
        
        if user_id and project.user_id != user_id:
            raise AuthorizationError("You don't have permission to access this project")
        
        return project.to_dict()
    
    def create_project(self, user_id: int, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        try:
            project = UserProject(
                user_id=user_id,
                title=project_data['title'],
                description=project_data.get('description'),
                url=project_data.get('url'),
                start_date=project_data.get('start_date'),
                end_date=project_data.get('end_date'),
                associated_with=project_data.get('associated_with'),
                technologies=project_data.get('technologies', [])
            )
            
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
            
            logger.info(f"Project created: {project.id} for user {user_id}")
            return project.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Create project error: {e}", exc_info=True)
            raise
    
    def update_project(
        self, 
        project_id: int, 
        user_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a project"""
        project = (
            self.db.query(UserProject)
            .filter(UserProject.id == project_id)
            .first()
        )
        
        if not project:
            raise NotFoundError('Project')
        
        if project.user_id != user_id:
            raise AuthorizationError("You don't have permission to update this project")
        
        try:
            if 'title' in update_data:
                project.title = update_data['title']
            if 'description' in update_data:
                project.description = update_data['description']
            if 'url' in update_data:
                project.url = update_data['url']
            if 'start_date' in update_data:
                project.start_date = update_data['start_date']
            if 'end_date' in update_data:
                project.end_date = update_data['end_date']
            if 'associated_with' in update_data:
                project.associated_with = update_data['associated_with']
            if 'technologies' in update_data:
                project.technologies = update_data['technologies']
            
            self.db.commit()
            self.db.refresh(project)
            
            logger.info(f"Project updated: {project_id}")
            return project.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update project error: {e}", exc_info=True)
            raise
    
    def delete_project(self, project_id: int, user_id: int) -> None:
        """Delete a project"""
        project = (
            self.db.query(UserProject)
            .filter(UserProject.id == project_id)
            .first()
        )
        
        if not project:
            raise NotFoundError('Project')
        
        if project.user_id != user_id:
            raise AuthorizationError("You don't have permission to delete this project")
        
        try:
            self.db.delete(project)
            self.db.commit()
            logger.info(f"Project deleted: {project_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete project error: {e}", exc_info=True)
            raise
