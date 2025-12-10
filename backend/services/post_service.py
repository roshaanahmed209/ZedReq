"""Post service"""
from ..models.post import Post
from ..models.like import Like
from ..utils.errors import NotFoundError, AuthorizationError
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class PostService:
    """Post business logic"""
    
    def __init__(self, db):
        self.post_model = Post(db)
        self.like_model = Like(db)
    
    def create_post(self, user_id: int, content: str) -> dict:
        """Create a new post"""
        try:
            post = self.post_model.create(user_id, content)
            logger.info(f"Post created: {post['id']} by user {user_id}")
            return post
        except Exception as e:
            logger.error(f"Create post error: {e}")
            raise
    
    def get_posts(self, user_id: int = None, limit: int = 20, offset: int = 0) -> list:
        """Get all posts"""
        try:
            posts = self.post_model.find_all(user_id, limit, offset)
            return [{
                'id': post['id'],
                'user_id': post['user_id'],
                'content': post['content'],
                'created_at': post['created_at'],
                'username': post['username'],
                'full_name': post['full_name'],
                'avatar': post['avatar'],
                'like_count': post['like_count'],
                'is_liked': post['is_liked'] > 0
            } for post in posts]
        except Exception as e:
            logger.error(f"Get posts error: {e}")
            raise
    
    def toggle_like(self, post_id: int, user_id: int) -> dict:
        """Toggle like on a post"""
        try:
            # Verify post exists
            post = self.post_model.find_by_id(post_id)
            if not post:
                raise NotFoundError('Post')
            
            is_liked = self.like_model.toggle(post_id, user_id)
            like_count = self.like_model.get_count(post_id)
            
            logger.info(f"Post {post_id} {'liked' if is_liked else 'unliked'} by user {user_id}")
            
            return {
                'like_count': like_count,
                'is_liked': is_liked
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Toggle like error: {e}")
            raise
    
    def update_post(self, post_id: int, user_id: int, content: str) -> dict:
        """Update a post"""
        try:
            post = self.post_model.find_by_id(post_id)
            if not post:
                raise NotFoundError('Post')
            
            if post['user_id'] != user_id:
                raise AuthorizationError('You can only update your own posts')
            
            updated_post = self.post_model.update(post_id, content)
            logger.info(f"Post {post_id} updated by user {user_id}")
            return updated_post
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Update post error: {e}")
            raise
    
    def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete a post"""
        try:
            post = self.post_model.find_by_id(post_id)
            if not post:
                raise NotFoundError('Post')
            
            if post['user_id'] != user_id:
                raise AuthorizationError('You can only delete your own posts')
            
            self.post_model.delete(post_id)
            logger.info(f"Post {post_id} deleted by user {user_id}")
            return True
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Delete post error: {e}")
            raise
