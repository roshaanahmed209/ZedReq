"""Post Service - Using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, joinedload

from models.orm import Post, Like, User, Description
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PostService:
    """Post business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_post(
        self, 
        user_id: int, 
        content: str, 
        media_url: str = None, 
        media_type: str = None
    ) -> dict:
        """Create a new post"""
        try:
            post = Post(
                uid=user_id,
                post_desc=content,
                media_url=media_url,
                media_type=media_type,
                likes=0,
                comments=0,
                is_deleted=False
            )
            
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            
            logger.info(f"Post created: {post.post_id} by user {user_id}")
            return {
                'id': post.post_id,
                'post_id': post.post_id,
                'user_id': post.uid,
                'uid': post.uid,
                'content': post.post_desc,
                'post_desc': post.post_desc,
                'media_url': post.media_url,
                'media_type': post.media_type,
                'likes': post.likes,
                'comments': post.comments,
                'created_at': post.created_at.isoformat() if post.created_at else None
            }
        except Exception as e:
            logger.error(f"Create post error: {e}")
            raise
    
    def get_post(self, post_id: int, user_id: int = None) -> Optional[Dict[str, Any]]:
        """Get a specific post by ID with user info"""
        post = (
            self.db.query(Post)
            .join(User, Post.uid == User.uid)
            .outerjoin(Description, User.description_id == Description.desc_id)
            .filter(
                and_(
                    Post.post_id == post_id,
                    Post.is_deleted == False
                )
            )
            .first()
        )
        
        if not post:
            return None
        
        # Check if user has liked
        is_liked = False
        if user_id:
            is_liked = self._has_liked(post_id, user_id)
        
        return {
            'id': post.post_id,
            'post_id': post.post_id,
            'user_id': post.uid,
            'uid': post.uid,
            'content': post.post_desc,
            'post_desc': post.post_desc,
            'media_url': post.media_url,
            'media_type': post.media_type,
            'likes': post.likes,
            'comments': post.comments,
            'created_at': post.created_at.isoformat() if post.created_at else None,
            'username': post.user.username if post.user else None,
            'name': post.user.name if post.user else None,
            'profile_pic': post.user.description_id and (
                self.db.query(Description)
                .filter(Description.desc_id == post.user.description_id)
                .first()
            ) and (
                self.db.query(Description)
                .filter(Description.desc_id == post.user.description_id)
                .first()
            ).profile_pic if post.user else None,
            'is_liked': is_liked
        }
    
    def get_posts(self, user_id: int = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all posts for feed"""
        try:
            posts = (
                self.db.query(Post)
                .join(User, Post.uid == User.uid)
                .outerjoin(Description, User.description_id == Description.desc_id)
                .filter(Post.is_deleted == False)
                .order_by(desc(Post.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )
            
            result = []
            for post in posts:
                # Check if current user has liked
                is_liked = False
                if user_id:
                    is_liked = self._has_liked(post.post_id, user_id)
                
                # Get profile pic
                profile_pic = None
                if post.user and post.user.description_id:
                    desc = (
                        self.db.query(Description)
                        .filter(Description.desc_id == post.user.description_id)
                        .first()
                    )
                    if desc:
                        profile_pic = desc.profile_pic
                
                result.append({
                    'id': post.post_id,
                    'post_id': post.post_id,
                    'user_id': post.uid,
                    'uid': post.uid,
                    'content': post.post_desc,
                    'post_desc': post.post_desc,
                    'created_at': post.created_at.isoformat() if post.created_at else None,
                    'username': post.user.username if post.user else None,
                    'full_name': post.user.name if post.user else None,
                    'name': post.user.name if post.user else None,
                    'profile_pic': profile_pic,
                    'like_count': post.likes,
                    'likes': post.likes,
                    'comment_count': post.comments,
                    'comments': post.comments,
                    'is_liked': is_liked
                })
            return result
        except Exception as e:
            logger.error(f"Get posts error: {e}")
            raise
    
    def get_posts_by_user(self, target_user_id: int, current_user_id: int = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all posts by a specific user"""
        posts, _ = self.get_posts_by_user_paginated(target_user_id, current_user_id, limit, offset)
        return posts
    
    def get_posts_by_user_paginated(self, target_user_id: int, current_user_id: int = None, limit: int = 20, offset: int = 0) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated posts by a specific user with total count"""
        try:
            # Get total count first
            total = (
                self.db.query(Post)
                .filter(
                    and_(
                        Post.uid == target_user_id,
                        Post.is_deleted == False
                    )
                )
                .count()
            )
            
            # Get paginated posts
            posts = (
                self.db.query(Post)
                .options(joinedload(Post.user))
                .join(User, Post.uid == User.uid)
                .outerjoin(Description, User.description_id == Description.desc_id)
                .filter(
                    and_(
                        Post.uid == target_user_id,
                        Post.is_deleted == False
                    )
                )
                .order_by(desc(Post.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )
            
            result = []
            for post in posts:
                try:
                    # Validate post has required data
                    if not post:
                        logger.warning(f"Empty post object encountered")
                        continue
                    
                    # Check if current user has liked
                    is_liked = False
                    if current_user_id:
                        try:
                            is_liked = self._has_liked(post.post_id, current_user_id)
                        except Exception as e:
                            logger.warning(f"Error checking like status for post {post.post_id}: {e}")
                    
                    # Get user info safely
                    username = None
                    full_name = None
                    name = None
                    profile_pic = None
                    
                    if post.user:
                        username = getattr(post.user, 'username', None)
                        full_name = getattr(post.user, 'name', None)
                        name = getattr(post.user, 'name', None)
                        
                        # Get profile pic
                        if hasattr(post.user, 'description_id') and post.user.description_id:
                            try:
                                description = (
                                    self.db.query(Description)
                                    .filter(Description.desc_id == post.user.description_id)
                                    .first()
                                )
                                if description:
                                    profile_pic = getattr(description, 'profile_pic', None)
                            except Exception as e:
                                logger.warning(f"Error getting description for post {post.post_id}: {e}")
                    else:
                        logger.warning(f"Post {post.post_id} has no associated user (uid={post.uid})")
                    
                    # Format created_at safely
                    created_at_str = None
                    if post.created_at:
                        try:
                            if hasattr(post.created_at, 'isoformat'):
                                created_at_str = post.created_at.isoformat()
                            else:
                                # If it's already a string, use it as is
                                created_at_str = str(post.created_at)
                        except Exception as e:
                            logger.warning(f"Error formatting created_at for post {post.post_id}: {e}")
                            created_at_str = str(post.created_at) if post.created_at else None
                    
                    result.append({
                        'id': post.post_id,
                        'post_id': post.post_id,
                        'user_id': post.uid,
                        'uid': post.uid,
                        'content': post.post_desc or '',
                        'post_desc': post.post_desc or '',
                        'media_url': getattr(post, 'media_url', None),
                        'media_type': getattr(post, 'media_type', None),
                        'created_at': created_at_str,
                        'username': username,
                        'full_name': full_name,
                        'name': name,
                        'profile_pic': profile_pic,
                        'like_count': getattr(post, 'likes', 0) or 0,
                        'likes': getattr(post, 'likes', 0) or 0,
                        'comment_count': getattr(post, 'comments', 0) or 0,
                        'comments': getattr(post, 'comments', 0) or 0,
                        'is_liked': is_liked
                    })
                except Exception as e:
                    logger.error(f"Error processing post {getattr(post, 'post_id', 'unknown')}: {e}", exc_info=True)
                    # Skip this post but continue with others
                    continue
            
            return result, total
        except Exception as e:
            logger.error(f"Get posts by user error: {e}", exc_info=True)
            raise
    
    def get_featured_posts_by_user_paginated(self, target_user_id: int, current_user_id: int = None, limit: int = 10, offset: int = 0) -> tuple[List[Dict[str, Any]], int]:
        """Get paginated featured posts (posts with media) by a specific user with total count"""
        try:
            # Get total count first
            total = (
                self.db.query(Post)
                .filter(
                    and_(
                        Post.uid == target_user_id,
                        Post.is_deleted == False,
                        Post.media_url.isnot(None),
                        Post.media_url != ''
                    )
                )
                .count()
            )
            
            # Get paginated posts
            posts = (
                self.db.query(Post)
                .options(joinedload(Post.user))
                .join(User, Post.uid == User.uid)
                .outerjoin(Description, User.description_id == Description.desc_id)
                .filter(
                    and_(
                        Post.uid == target_user_id,
                        Post.is_deleted == False,
                        Post.media_url.isnot(None),
                        Post.media_url != ''
                    )
                )
                .order_by(desc(Post.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )
            
            result = []
            for post in posts:
                try:
                    # Check if current user has liked
                    is_liked = False
                    if current_user_id:
                        is_liked = self._has_liked(post.post_id, current_user_id)
                    
                    # Get user info
                    username = post.user.username if post.user else None
                    full_name = post.user.name if post.user else None
                    name = post.user.name if post.user else None
                    profile_pic = None
                    
                    if post.user and post.user.description_id:
                        desc = (
                            self.db.query(Description)
                            .filter(Description.desc_id == post.user.description_id)
                            .first()
                        )
                        if desc:
                            profile_pic = desc.profile_pic
                    
                    created_at_str = post.created_at.isoformat() if post.created_at else None
                    
                    result.append({
                        'id': post.post_id,
                        'post_id': post.post_id,
                        'user_id': post.uid,
                        'uid': post.uid,
                        'content': post.post_desc or '',
                        'post_desc': post.post_desc or '',
                        'media_url': post.media_url,
                        'media_type': post.media_type,
                        'created_at': created_at_str,
                        'username': username,
                        'full_name': full_name,
                        'name': name,
                        'profile_pic': profile_pic,
                        'like_count': post.likes or 0,
                        'likes': post.likes or 0,
                        'comment_count': post.comments or 0,
                        'comments': post.comments or 0,
                        'is_liked': is_liked
                    })
                except Exception as e:
                    logger.error(f"Error processing featured post {getattr(post, 'post_id', 'unknown')}: {e}", exc_info=True)
                    continue
            
            return result, total
        except Exception as e:
            logger.error(f"Get featured posts by user error: {e}", exc_info=True)
            raise
    
    def get_featured_posts_by_user(self, target_user_id: int, current_user_id: int = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get featured posts (posts with media) by a specific user"""
        posts, _ = self.get_featured_posts_by_user_paginated(target_user_id, current_user_id, limit, 0)
        return posts
    
    def toggle_like(self, post_id: int, user_id: int) -> dict:
        """Toggle like on a post"""
        try:
            # Verify post exists
            post = self.db.query(Post).filter(Post.post_id == post_id).first()
            if not post:
                raise NotFoundError('Post')
            
            # Check if already liked
            existing_like = (
                self.db.query(Like)
                .filter(
                    and_(
                        Like.post_id == post_id,
                        Like.uid == user_id
                    )
                )
                .first()
            )
            
            if existing_like:
                # Unlike
                self.db.delete(existing_like)
                post.likes = max(0, post.likes - 1)
                is_liked = False
            else:
                # Like
                new_like = Like(post_id=post_id, uid=user_id)
                self.db.add(new_like)
                post.likes = post.likes + 1
                is_liked = True
            
            self.db.commit()
            
            logger.info(f"Post {post_id} {'liked' if is_liked else 'unliked'} by user {user_id}")
            
            return {
                'like_count': post.likes,
                'likes': post.likes,
                'is_liked': is_liked
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Toggle like error: {e}")
            raise
    
    def get_likers(self, post_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get users who liked a post with pagination"""
        likers = (
            self.db.query(Like)
            .join(User, Like.uid == User.uid)
            .filter(Like.post_id == post_id)
            .order_by(desc(Like.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )
        
        return [
            {
                'uid': like.user.uid,
                'username': like.user.username,
                'name': like.user.name
            }
            for like in likers
        ]
    
    def update_post(self, post_id: int, user_id: int, content: str) -> dict:
        """Update a post"""
        try:
            post = (
                self.db.query(Post)
                .filter(
                    and_(
                        Post.post_id == post_id,
                        Post.is_deleted == False
                    )
                )
                .first()
            )
            
            if not post:
                raise NotFoundError('Post')
            
            if post.uid != user_id:
                raise AuthorizationError('You can only update your own posts')
            
            post.post_desc = content
            self.db.commit()
            self.db.refresh(post)
            
            logger.info(f"Post {post_id} updated by user {user_id}")
            return {
                'id': post.post_id,
                'post_id': post.post_id,
                'content': post.post_desc,
                'post_desc': post.post_desc,
                'updated_at': post.updated_at.isoformat() if post.updated_at else None
            }
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Update post error: {e}")
            raise
    
    def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete a post (soft delete)"""
        try:
            post = (
                self.db.query(Post)
                .filter(
                    and_(
                        Post.post_id == post_id,
                        Post.is_deleted == False
                    )
                )
                .first()
            )
            
            if not post:
                raise NotFoundError('Post')
            
            if post.uid != user_id:
                raise AuthorizationError('You can only delete your own posts')
            
            post.is_deleted = True
            self.db.commit()
            
            logger.info(f"Post {post_id} deleted by user {user_id}")
            return True
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Delete post error: {e}")
            raise
    
    def _has_liked(self, post_id: int, user_id: int) -> bool:
        """Check if user has liked a post"""
        like = (
            self.db.query(Like)
            .filter(
                and_(
                    Like.post_id == post_id,
                    Like.uid == user_id
                )
            )
            .first()
        )
        return like is not None