"""Post service"""
from models.post import Post
from models.like import Like
from utils.errors import NotFoundError, AuthorizationError
from utils.logger import setup_logger

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
            logger.info(f"Post created: {post['post_id']} by user {user_id}")
            return {'id': post['post_id']}
        except Exception as e:
            logger.error(f"Create post error: {e}")
            raise
    
    def get_posts(self, user_id: int = None, limit: int = 20, offset: int = 0) -> list:
        """Get all posts for feed"""
        try:
            posts = self.post_model.get_feed(limit, offset)
            result = []
            for post in posts:
                # Check if current user has liked
                is_liked = False
                if user_id:
                    is_liked = self.like_model.has_liked(post['post_id'], user_id)
                
                result.append({
                    'id': post['post_id'],
                    'user_id': post['uid'],
                    'content': post['post_desc'],
                    'created_at': str(post['created_at']),
                    'username': post.get('username', ''),
                    'full_name': post.get('name', ''),
                    'like_count': post.get('likes', 0),
                    'comment_count': post.get('comments', 0),
                    'is_liked': is_liked
                })
            return result
        except Exception as e:
            logger.error(f"Get posts error: {e}")
            raise
    
    def toggle_like(self, post_id: int, user_id: int) -> dict:
        """Toggle like on a post"""
        try:
            # Verify post exists
            post = self.post_model.get_by_id(post_id)
            if not post:
                raise NotFoundError('Post')
            
            is_liked = self.like_model.toggle(post_id, user_id)
            
            # Update post like count
            if is_liked:
                self.post_model.increment_likes(post_id)
            else:
                self.post_model.decrement_likes(post_id)
            
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
            post = self.post_model.get_by_id(post_id)
            if not post:
                raise NotFoundError('Post')
            
            if post['uid'] != user_id:
                raise AuthorizationError('You can only update your own posts')
            
            updated_post = self.post_model.update(post_id, user_id, content)
            logger.info(f"Post {post_id} updated by user {user_id}")
            return {
                'id': updated_post['post_id'],
                'content': updated_post['post_desc']
            }
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Update post error: {e}")
            raise
    
    def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete a post (soft delete)"""
        try:
            post = self.post_model.get_by_id(post_id)
            if not post:
                raise NotFoundError('Post')
            
            if post['uid'] != user_id:
                raise AuthorizationError('You can only delete your own posts')
            
            self.post_model.soft_delete(post_id, user_id)
            logger.info(f"Post {post_id} deleted by user {user_id}")
            return True
        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(f"Delete post error: {e}")
            raise
