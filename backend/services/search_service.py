"""Search Service - LinkedIn-style comprehensive search across users, jobs, and posts"""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, and_

from services.user_service import UserService
from services.job_service import JobService
from services.post_service import PostService
from models.orm import Post, User, Description
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SearchService:
    """Comprehensive search service for users, jobs, and posts"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.job_service = JobService(db)
        self.post_service = PostService(db)
    
    def search_all(
        self,
        query: str,
        current_user_id: int = None,
        limit_per_type: int = 10,
        search_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search across users, jobs, and posts (LinkedIn-style)
        
        Args:
            query: Search query string
            current_user_id: Current user ID (to exclude from results)
            limit_per_type: Number of results per type
            search_types: List of types to search ['users', 'jobs', 'posts'] or None for all
        
        Returns:
            Dictionary with users, jobs, posts, and metadata
        """
        if not query or not query.strip():
            return {
                'users': [],
                'jobs': [],
                'posts': [],
                'total_results': 0,
                'query': query
            }
        
        search_types = search_types or ['users', 'jobs', 'posts']
        query = query.strip()
        
        results = {
            'users': [],
            'jobs': [],
            'posts': [],
            'query': query
        }
        
        # Search users
        if 'users' in search_types:
            try:
                users = self.user_service.search_users(
                    query=query,
                    exclude_user_id=current_user_id,
                    limit=limit_per_type
                )
                results['users'] = users
            except Exception as e:
                logger.error(f"Error searching users: {e}")
                results['users'] = []
        
        # Search jobs
        if 'jobs' in search_types:
            try:
                jobs = self.job_service.search_jobs(
                    user_id=current_user_id,
                    query=query,
                    limit=limit_per_type,
                    offset=0
                )
                results['jobs'] = jobs
            except Exception as e:
                logger.error(f"Error searching jobs: {e}")
                results['jobs'] = []
        
        # Search posts
        if 'posts' in search_types:
            try:
                posts = self._search_posts(
                    query=query,
                    current_user_id=current_user_id,
                    limit=limit_per_type
                )
                results['posts'] = posts
            except Exception as e:
                logger.error(f"Error searching posts: {e}")
                results['posts'] = []
        
        # Calculate total results
        results['total_results'] = (
            len(results['users']) +
            len(results['jobs']) +
            len(results['posts'])
        )
        
        return results
    
    def _search_posts(
        self,
        query: str,
        current_user_id: int = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search posts by content
        
        Args:
            query: Search query
            current_user_id: Current user ID (for like status)
            limit: Maximum number of results
        
        Returns:
            List of post dictionaries
        """
        if not query or not query.strip():
            return []
        
        search_pattern = f"%{query.strip()}%"
        
        # Search posts by content
        posts = (
            self.db.query(Post)
            .join(User, Post.uid == User.uid)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(
                and_(
                    Post.not_deleted(),
                    Post.post_desc.ilike(search_pattern)
                )
            )
            .order_by(desc(Post.created_at))
            .limit(limit)
            .all()
        )
        
        # Format results
        result = []
        for post in posts:
            # Check if user has liked
            is_liked = False
            if current_user_id:
                is_liked = self.post_service._has_liked(post.post_id, current_user_id)
            
            # Get profile pic
            profile_pic = None
            if post.user and post.user.description_id:
                description = (
                    self.db.query(Description)
                    .filter(Description.desc_id == post.user.description_id)
                    .first()
                )
                if description:
                    profile_pic = description.profile_pic
            
            result.append({
                'id': post.post_id,
                'post_id': post.post_id,
                'user_id': post.uid,
                'uid': post.uid,
                'content': post.post_desc or '',
                'post_desc': post.post_desc or '',
                'media_url': post.media_url,
                'media_type': post.media_type,
                'created_at': post.created_at.isoformat() if post.created_at else None,
                'username': post.user.username if post.user else None,
                'full_name': post.user.name if post.user else None,
                'name': post.user.name if post.user else None,
                'profile_pic': profile_pic,
                'like_count': post.likes or 0,
                'likes': post.likes or 0,
                'comment_count': post.comments or 0,
                'comments': post.comments or 0,
                'is_liked': is_liked
            })
        
        return result
