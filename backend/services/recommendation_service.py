"""Recommendation Service - User recommendation operations using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.orm import UserRecommendation
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

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
