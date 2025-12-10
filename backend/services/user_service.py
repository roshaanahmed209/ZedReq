"""User service"""
from ..models.user import User
from ..utils.errors import NotFoundError
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class UserService:
    """User business logic"""
    
    def __init__(self, db):
        self.user_model = User(db)
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Get user by ID"""
        try:
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundError('User')
            
            return {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'headline': user['headline'],
                'bio': user['bio'],
                'avatar': user['avatar']
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Get user error: {e}")
            raise
    
    def update_user(self, user_id: int, update_data: dict) -> dict:
        """Update user"""
        try:
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundError('User')
            
            updated_user = self.user_model.update(user_id, **update_data)
            logger.info(f"User {user_id} updated")
            
            return {
                'id': updated_user['id'],
                'username': updated_user['username'],
                'full_name': updated_user['full_name'],
                'headline': updated_user['headline'],
                'bio': updated_user['bio'],
                'avatar': updated_user['avatar']
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Update user error: {e}")
            raise
    
    def search_users(self, query: str, exclude_user_id: int = None, limit: int = 10) -> list:
        """Search users"""
        try:
            if not query or not query.strip():
                return []
            
            users = self.user_model.search(query.strip(), exclude_user_id, limit)
            
            return [{
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'headline': user['headline'],
                'avatar': user['avatar']
            } for user in users]
        except Exception as e:
            logger.error(f"Search users error: {e}")
            raise
