"""Profile Analytics Service - Track profile views and search appearances"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from datetime import datetime, timedelta

from models.orm import ProfileAnalytics
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ProfileAnalyticsService:
    """Profile analytics business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def track_profile_view(
        self, 
        user_id: int, 
        viewer_id: Optional[int] = None, 
        source: str = 'direct'
    ) -> None:
        """Track a profile view"""
        try:
            # Don't track self-views
            if viewer_id and viewer_id == user_id:
                return
            
            analytics = ProfileAnalytics(
                user_id=user_id,
                viewer_id=viewer_id,
                view_type='profile_view',
                source=source,
                viewed_at=datetime.now()
            )
            
            self.db.add(analytics)
            self.db.commit()
            
            logger.debug(f"Profile view tracked: user_id={user_id}, viewer_id={viewer_id}, source={source}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Track profile view error: {e}", exc_info=True)
            # Don't raise - analytics failures shouldn't break the app
    
    def track_search_appearance(
        self, 
        user_id: int, 
        source: str = 'search'
    ) -> None:
        """Track a search appearance (when user appears in search results)"""
        try:
            analytics = ProfileAnalytics(
                user_id=user_id,
                viewer_id=None,
                view_type='search_appearance',
                source=source,
                viewed_at=datetime.now()
            )
            
            self.db.add(analytics)
            self.db.commit()
            
            logger.debug(f"Search appearance tracked: user_id={user_id}, source={source}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Track search appearance error: {e}", exc_info=True)
            # Don't raise - analytics failures shouldn't break the app
    
    def get_profile_views(
        self, 
        user_id: int, 
        days: int = 30,
        include_viewer_info: bool = False
    ) -> List[Dict[str, Any]]:
        """Get profile views for a user within specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        views = (
            self.db.query(ProfileAnalytics)
            .filter(
                and_(
                    ProfileAnalytics.user_id == user_id,
                    ProfileAnalytics.view_type == 'profile_view',
                    ProfileAnalytics.viewed_at >= cutoff_date
                )
            )
            .order_by(desc(ProfileAnalytics.viewed_at))
            .all()
        )
        
        return [view.to_dict(include_viewer_info=include_viewer_info) for view in views]
    
    def get_search_appearances(
        self, 
        user_id: int, 
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get search appearances for a user within specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        appearances = (
            self.db.query(ProfileAnalytics)
            .filter(
                and_(
                    ProfileAnalytics.user_id == user_id,
                    ProfileAnalytics.view_type == 'search_appearance',
                    ProfileAnalytics.viewed_at >= cutoff_date
                )
            )
            .order_by(desc(ProfileAnalytics.viewed_at))
            .all()
        )
        
        return [app.to_dict() for app in appearances]
    
    def get_analytics_summary(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get analytics summary for a user"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get view counts by source
        view_counts = (
            self.db.query(
                ProfileAnalytics.source,
                func.count(ProfileAnalytics.id).label('count')
            )
            .filter(
                and_(
                    ProfileAnalytics.user_id == user_id,
                    ProfileAnalytics.view_type == 'profile_view',
                    ProfileAnalytics.viewed_at >= cutoff_date
                )
            )
            .group_by(ProfileAnalytics.source)
            .all()
        )
        
        # Get total views
        total_views = (
            self.db.query(func.count(ProfileAnalytics.id))
            .filter(
                and_(
                    ProfileAnalytics.user_id == user_id,
                    ProfileAnalytics.view_type == 'profile_view',
                    ProfileAnalytics.viewed_at >= cutoff_date
                )
            )
            .scalar() or 0
        )
        
        # Get total search appearances
        total_appearances = (
            self.db.query(func.count(ProfileAnalytics.id))
            .filter(
                and_(
                    ProfileAnalytics.user_id == user_id,
                    ProfileAnalytics.view_type == 'search_appearance',
                    ProfileAnalytics.viewed_at >= cutoff_date
                )
            )
            .scalar() or 0
        )
        
        return {
            'total_views': total_views,
            'total_search_appearances': total_appearances,
            'views_by_source': {source: count for source, count in view_counts},
            'period_days': days
        }
