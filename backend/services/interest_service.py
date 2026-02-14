"""Interest Service - User interest operations using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.orm import UserInterest
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class InterestService:
    """Interest business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_interests(self, user_id: int, interest_type: str = None) -> List[Dict[str, Any]]:
        """Get all interests for a user, optionally filtered by type"""
        query = (
            self.db.query(UserInterest)
            .filter(UserInterest.user_id == user_id)
        )
        
        if interest_type:
            query = query.filter(UserInterest.interest_type == interest_type)
        
        interests = query.order_by(desc(UserInterest.created_at)).all()
        
        return [interest.to_dict() for interest in interests]
    
    def get_user_interests_paginated(
        self, 
        user_id: int, 
        interest_type: Optional[str] = None,
        limit: int = 50, 
        offset: int = 0
    ) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated interests for a user, optionally filtered by type"""
        query = (
            self.db.query(UserInterest)
            .filter(UserInterest.user_id == user_id)
        )
        
        if interest_type:
            query = query.filter(UserInterest.interest_type == interest_type)
        
        # Get total count
        total = query.count()
        
        # Get paginated results
        interests = (
            query
            .order_by(desc(UserInterest.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [interest.to_dict() for interest in interests], total
    
    def get_interest(self, interest_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get a specific interest by ID"""
        interest = (
            self.db.query(UserInterest)
            .filter(UserInterest.id == interest_id)
            .first()
        )
        
        if not interest:
            return None
        
        if user_id and interest.user_id != user_id:
            raise AuthorizationError("You don't have permission to access this interest")
        
        return interest.to_dict()
    
    def create_interest(self, user_id: int, interest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new interest"""
        try:
            interest = UserInterest(
                user_id=user_id,
                interest_type=interest_data['interest_type'],
                name=interest_data['name'],
                url=interest_data.get('url')
            )
            
            self.db.add(interest)
            self.db.commit()
            self.db.refresh(interest)
            
            logger.info(f"Interest created: {interest.id} for user {user_id}")
            return interest.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Create interest error: {e}", exc_info=True)
            raise
    
    def update_interest(
        self, 
        interest_id: int, 
        user_id: int, 
        update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an interest"""
        interest = (
            self.db.query(UserInterest)
            .filter(UserInterest.id == interest_id)
            .first()
        )
        
        if not interest:
            raise NotFoundError('Interest')
        
        if interest.user_id != user_id:
            raise AuthorizationError("You don't have permission to update this interest")
        
        try:
            if 'interest_type' in update_data:
                interest.interest_type = update_data['interest_type']
            if 'name' in update_data:
                interest.name = update_data['name']
            if 'url' in update_data:
                interest.url = update_data['url']
            
            self.db.commit()
            self.db.refresh(interest)
            
            logger.info(f"Interest updated: {interest_id}")
            return interest.to_dict()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update interest error: {e}", exc_info=True)
            raise
    
    def delete_interest(self, interest_id: int, user_id: int) -> None:
        """Delete an interest"""
        interest = (
            self.db.query(UserInterest)
            .filter(UserInterest.id == interest_id)
            .first()
        )
        
        if not interest:
            raise NotFoundError('Interest')
        
        if interest.user_id != user_id:
            raise AuthorizationError("You don't have permission to delete this interest")
        
        try:
            self.db.delete(interest)
            self.db.commit()
            logger.info(f"Interest deleted: {interest_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete interest error: {e}", exc_info=True)
            raise
