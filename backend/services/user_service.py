"""User service"""
from models.user import User
from utils.errors import NotFoundError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class UserService:
    """User business logic"""
    
    def __init__(self, db):
        self.user_model = User(db)
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Get user by ID"""
        try:
            user = self.user_model.find_by_uid(user_id)
            if not user:
                raise NotFoundError('User')
            
            return {
                'id': user['uid'],
                'username': user.get('username', ''),
                'full_name': user.get('name', ''),
                'email': user.get('user_email', ''),
                'created_at': str(user.get('created_at', ''))
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Get user error: {e}")
            raise
    
    def update_user(self, user_id: int, update_data: dict) -> dict:
        """Update user profile"""
        try:
            user = self.user_model.find_by_uid(user_id)
            if not user:
                raise NotFoundError('User')
            
            # Update profile with provided data
            updated_user = self.user_model.update_profile(
                uid=user_id,
                name=update_data.get('full_name'),
                username=update_data.get('username')
            )
            
            if not updated_user:
                raise Exception('Failed to update user')
            
            logger.info(f"User {user_id} updated")
            
            return {
                'id': updated_user['uid'],
                'username': updated_user.get('username', ''),
                'full_name': updated_user.get('name', ''),
                'email': updated_user.get('user_email', '')
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Update user error: {e}")
            raise
    
    def search_users(self, query: str, exclude_user_id: int = None, limit: int = 10) -> list:
        """Search users by username or name"""
        try:
            if not query or not query.strip():
                return []
            
            users = self.user_model.search_users(query.strip(), limit)
            
            # Filter out the excluded user
            result = []
            for user in users:
                if exclude_user_id and user['uid'] == exclude_user_id:
                    continue
                result.append({
                    'id': user['uid'],
                    'username': user.get('username', ''),
                    'full_name': user.get('name', ''),
                    'email': user.get('user_email', '')
                })
            
            return result
        except Exception as e:
            logger.error(f"Search users error: {e}")
            raise
