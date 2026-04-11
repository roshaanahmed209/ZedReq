"""Post Service - Using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload

from models.orm import Post, PostComment, Like, User, Description
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PostService:
    """Post business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db

    def get_comment_counts_by_post_ids(self, post_ids: List[int]) -> Dict[int, int]:
        """Actual comment row counts from post_comment (not the denormalized post.comments column)."""
        if not post_ids:
            return {}
        unique = list(dict.fromkeys(int(x) for x in post_ids))
        rows = (
            self.db.query(PostComment.post_id, func.count(PostComment.comment_id))
            .filter(PostComment.post_id.in_(unique))
            .group_by(PostComment.post_id)
            .all()
        )
        by_id = {int(r[0]): int(r[1]) for r in rows}
        return {pid: by_id.get(pid, 0) for pid in unique}

    def _reconcile_post_comment_count(self, post_id: int) -> int:
        """Set post.comments to match COUNT(post_comment) for this post."""
        n = (
            self.db.query(func.count(PostComment.comment_id))
            .filter(PostComment.post_id == post_id)
            .scalar()
        )
        n = int(n or 0)
        post = self.db.query(Post).filter(Post.post_id == post_id).first()
        if post:
            post.comments = n
            self.db.commit()
        return n
    
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
            
            # Generate and store post_link
            post_link = f"/post/{post.post_id}"
            post.post_link = post_link
            self.db.commit()
            
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
                'post_link': post.post_link,
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
                    Post.not_deleted()
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

        comment_counts = self.get_comment_counts_by_post_ids([post_id])
        actual_comments = comment_counts.get(post_id, 0)
        
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
            'comments': actual_comments,
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
                .filter(Post.not_deleted())
                .order_by(desc(Post.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )

            cc_map = self.get_comment_counts_by_post_ids([p.post_id for p in posts])
            
            result = []
            for post in posts:
                # Check if current user has liked
                is_liked = False
                if user_id:
                    is_liked = self._has_liked(post.post_id, user_id)
                
                # Get profile pic
                profile_pic = None
                if post.user and post.user.description_id:
                    user_description = (
                        self.db.query(Description)
                        .filter(Description.desc_id == post.user.description_id)
                        .first()
                    )
                    if user_description:
                        profile_pic = user_description.profile_pic

                cct = cc_map.get(post.post_id, 0)
                
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
                    'comment_count': cct,
                    'comments': cct,
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
                        Post.not_deleted()
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
                        Post.not_deleted()
                    )
                )
                .order_by(desc(Post.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )

            cc_map = self.get_comment_counts_by_post_ids([p.post_id for p in posts])
            
            result = []
            for post in posts:
                try:
                    # Validate post has required data
                    if not post:
                        logger.warning(f"Empty post object encountered")
                        continue

                    cct = cc_map.get(post.post_id, 0)
                    
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
                        'comment_count': cct,
                        'comments': cct,
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
                        Post.not_deleted(),
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
                        Post.not_deleted(),
                        Post.media_url.isnot(None),
                        Post.media_url != ''
                    )
                )
                .order_by(desc(Post.created_at))
                .limit(limit)
                .offset(offset)
                .all()
            )

            cc_map = self.get_comment_counts_by_post_ids([p.post_id for p in posts])
            
            result = []
            for post in posts:
                try:
                    cct = cc_map.get(post.post_id, 0)
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
                        user_description = (
                            self.db.query(Description)
                            .filter(Description.desc_id == post.user.description_id)
                            .first()
                        )
                        if user_description:
                            profile_pic = user_description.profile_pic
                    
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
                        'comment_count': cct,
                        'comments': cct,
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
                        Post.not_deleted()
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
                        Post.not_deleted()
                    )
                )
                .first()
            )
            
            if not post:
                raise NotFoundError('Post')
            
            if post.uid != user_id:
                raise AuthorizationError('You can only delete your own posts')
            
            self.db.delete(post)
            self.db.commit()
            
            logger.info(f"Post {post_id} hard-deleted by user {user_id}")
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

    def _profile_pic_for_desc_id(self, desc_id: Optional[int]) -> Optional[str]:
        if not desc_id:
            return None
        row = self.db.query(Description).filter(Description.desc_id == desc_id).first()
        return row.profile_pic if row else None

    def _comment_row_to_dict(self, c: PostComment, profile_pic: Optional[str] = None) -> Dict[str, Any]:
        if profile_pic is None and c.user and c.user.description_id:
            profile_pic = self._profile_pic_for_desc_id(c.user.description_id)
        return {
            "id": c.comment_id,
            "comment_id": c.comment_id,
            "user_id": c.uid,
            "body": c.body or "",
            "media_url": getattr(c, "media_url", None),
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "username": c.user.username if c.user else None,
            "full_name": c.user.name if c.user else None,
            "profile_pic": profile_pic,
        }

    def list_comments(
        self, post_id: int, limit: int = 50, offset: int = 0
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List comments for a post (newest first). Raises NotFoundError if post missing or deleted."""
        post = (
            self.db.query(Post)
            .filter(and_(Post.post_id == post_id, Post.not_deleted()))
            .first()
        )
        if not post:
            raise NotFoundError("Post")

        total = (
            self.db.query(func.count(PostComment.comment_id))
            .filter(PostComment.post_id == post_id)
            .scalar()
        ) or 0

        rows = (
            self.db.query(PostComment)
            .options(joinedload(PostComment.user))
            .filter(PostComment.post_id == post_id)
            .order_by(desc(PostComment.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

        desc_ids = list(
            {c.user.description_id for c in rows if c.user and c.user.description_id}
        )
        pic_by_desc: Dict[int, Optional[str]] = {}
        if desc_ids:
            for d in self.db.query(Description).filter(Description.desc_id.in_(desc_ids)).all():
                pic_by_desc[d.desc_id] = d.profile_pic

        out: List[Dict[str, Any]] = []
        for c in rows:
            did = c.user.description_id if c.user else None
            pic = pic_by_desc.get(did) if did else None
            out.append(self._comment_row_to_dict(c, profile_pic=pic))

        return out, int(total)

    def add_comment(
        self,
        post_id: int,
        user_id: int,
        body: str,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add a comment; increments post.comments counter."""
        post = (
            self.db.query(Post)
            .filter(and_(Post.post_id == post_id, Post.not_deleted()))
            .first()
        )
        if not post:
            raise NotFoundError("Post")

        text = (body or "").strip()
        row = PostComment(
            post_id=post_id,
            uid=user_id,
            body=text if text else "",
            media_url=media_url or None,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)

        row = (
            self.db.query(PostComment)
            .options(joinedload(PostComment.user))
            .filter(PostComment.comment_id == row.comment_id)
            .first()
        )
        pic = None
        if row and row.user and row.user.description_id:
            pic = self._profile_pic_for_desc_id(row.user.description_id)

        actual_total = self._reconcile_post_comment_count(post_id)

        logger.info(
            "comment_audit action=create post_id=%s comment_id=%s user_id=%s has_media=%s",
            post_id,
            row.comment_id,
            user_id,
            bool(media_url),
        )
        return {
            "comment": self._comment_row_to_dict(row, profile_pic=pic),
            "comment_count": actual_total,
        }

    def delete_comment(self, post_id: int, comment_id: int, user_id: int) -> Dict[str, Any]:
        """Delete own comment; decrements post.comments."""
        c = (
            self.db.query(PostComment)
            .filter(
                and_(
                    PostComment.comment_id == comment_id,
                    PostComment.post_id == post_id,
                )
            )
            .first()
        )
        if not c:
            raise NotFoundError("Comment")
        if c.uid != user_id:
            raise AuthorizationError("You can only delete your own comments")

        post = self.db.query(Post).filter(Post.post_id == post_id).first()
        self.db.delete(c)
        self.db.commit()

        actual_total = self._reconcile_post_comment_count(post_id) if post else 0

        logger.info(
            "comment_audit action=delete post_id=%s comment_id=%s user_id=%s",
            post_id,
            comment_id,
            user_id,
        )
        return {"comment_count": actual_total}