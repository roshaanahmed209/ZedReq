"""User Service - Using SQLAlchemy ORM"""
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, func, case
from sqlalchemy.orm import Session

from models.orm import User, Description
from utils.errors import NotFoundError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class UserService:
    """User business logic using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> dict:
        """Get user by ID"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            return {
                'id': user.uid,
                'uid': user.uid,
                'username': user.username or '',
                'full_name': user.name or '',
                'name': user.name or '',
                'email': user.user_email or '',
                'user_email': user.user_email or '',
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Get user error: {e}")
            raise
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile with description info"""
        user = (
            self.db.query(User)
            .filter(User.uid == user_id)
            .first()
        )
        
        if not user:
            return None
        
        result = user.to_dict()
        
        # Get description if available
        if user.description_id:
            description = (
                self.db.query(Description)
                .filter(Description.desc_id == user.description_id)
                .first()
            )
            if description:
                result.update({
                    'profile_pic': description.profile_pic,
                    'short_desc': description.short_desc,
                    'about': description.about,
                    'skills': description.skills,
                    'current_status': description.current_status
                })
        
        return result
    
    def update_user(self, user_id: int, update_data: dict) -> dict:
        """Update user profile"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Update fields
            if 'full_name' in update_data:
                user.name = update_data['full_name']
            if 'username' in update_data:
                user.username = update_data['username']
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"User {user_id} updated")
            
            return {
                'id': user.uid,
                'uid': user.uid,
                'username': user.username or '',
                'full_name': user.name or '',
                'name': user.name or '',
                'email': user.user_email or '',
                'user_email': user.user_email or ''
            }
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Update user error: {e}")
            raise
    
    def search_users(self, query: str, exclude_user_id: int = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search users by username or name"""
        try:
            if not query or not query.strip():
                return []
            
            search_pattern = f"%{query.strip()}%"
            users = (
                self.db.query(User)
                .filter(
                    or_(
                        func.lower(User.username).like(func.lower(search_pattern)),
                        func.lower(User.name).like(func.lower(search_pattern))
                    )
                )
                .order_by(
                    # Prioritize exact matches, then username matches, then name matches
                    case(
                        (func.lower(User.username) == func.lower(query.strip()), 0),
                        (func.lower(User.username).like(func.lower(f"{query.strip()}%")), 1),
                        else_=2
                    )
                )
                .limit(limit)
                .all()
            )
            
            # Filter out excluded user and format
            result = []
            for user in users:
                if exclude_user_id and user.uid == exclude_user_id:
                    continue
                result.append({
                    'id': user.uid,
                    'uid': user.uid,
                    'username': user.username or '',
                    'full_name': user.name or '',
                    'name': user.name or '',
                    'email': user.user_email or '',
                    'user_email': user.user_email or ''
                })
            
            return result
        except Exception as e:
            logger.error(f"Search users error: {e}")
            raise
