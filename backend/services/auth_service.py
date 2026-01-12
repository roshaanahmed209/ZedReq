"""Authentication service"""
from models.user import User
from utils.errors import AuthenticationError, ConflictError, ValidationError
from utils.auth import hash_password, verify_password, validate_password_strength, validate_email, validate_username
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AuthService:
    """Authentication business logic"""
    
    def __init__(self, db):
        self.user_model = User(db)
    
    def register(self, user_data: dict) -> dict:
        """
        Register a new user
        
        Args:
            user_data: Dict containing username, email, password, and optionally full_name
        
        Returns:
            Dict with user info (id, username, email, full_name)
        
        Raises:
            ValidationError: If validation fails
            ConflictError: If username or email already exists
        """
        try:
            username = user_data.get('username', '').strip()
            email = user_data.get('email', '').strip()
            password = user_data.get('password', '')
            full_name = user_data.get('full_name', '').strip() or username
            
            # Validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Validate email
            if not validate_email(email):
                raise ValidationError('Please provide a valid email address')
            
            # Validate password
            is_valid, error_msg = validate_password_strength(password)
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Check if username already exists
            if self.user_model.username_exists(username):
                raise ConflictError('Username already exists')
            
            # Check if email already exists
            if self.user_model.email_exists(email):
                raise ConflictError('Email already exists')
            
            # Hash password
            password_hash = hash_password(password)
            
            # Create user
            user = self.user_model.create(
                username=username,
                email=email,
                password_hash=password_hash,
                full_name=full_name
            )
            
            if not user:
                raise Exception('Failed to create user')
            
            logger.info(f"New user registered: {user['username']} (ID: {user['uid']})")
            
            return {
                'id': user['uid'],
                'username': user['username'],
                'email': user['user_email'],
                'full_name': user['name']
            }
            
        except (ConflictError, ValidationError) as e:
            logger.warning(f"Registration error: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise ValidationError('Registration failed. Please try again.')
    
    def login(self, identifier: str, password: str) -> dict:
        """
        Login user with username or email
        
        Args:
            identifier: Username or email
            password: User's password
        
        Returns:
            Dict with user info and success message
        
        Raises:
            AuthenticationError: If credentials are invalid
        """
        try:
            if not identifier or not password:
                raise AuthenticationError('Username/email and password are required')
            
            # Find user by username or email
            user = self.user_model.find_by_username_or_email(identifier.strip())
            
            if not user:
                logger.warning(f"Login attempt for non-existent user: {identifier}")
                raise AuthenticationError('Invalid username or password')
            
            # Verify password
            if not verify_password(password, user['password_hash']):
                logger.warning(f"Invalid password attempt for user: {user['username']}")
                raise AuthenticationError('Invalid username or password')
            
            logger.info(f"User logged in: {user['username']} (ID: {user['uid']})")
            
            return {
                'id': user['uid'],
                'username': user['username'],
                'email': user['user_email'],
                'full_name': user['name'],
                'message': 'Login successful'
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise AuthenticationError('Login failed. Please try again.')
    
    def get_user_by_id(self, user_id: int) -> dict:
        """
        Get user by ID
        
        Args:
            user_id: User's database ID
        
        Returns:
            Dict with user info
        
        Raises:
            AuthenticationError: If user not found
        """
        try:
            user = self.user_model.find_by_uid(user_id)
            
            if not user:
                raise AuthenticationError('User not found')
            
            return {
                'id': user['uid'],
                'username': user['username'],
                'email': user['user_email'],
                'full_name': user['name'],
                'created_at': str(user.get('created_at', ''))
            }
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Get user error: {e}")
            raise AuthenticationError('Failed to get user')
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> dict:
        """
        Change user's password
        
        Args:
            user_id: User's database ID
            current_password: Current password for verification
            new_password: New password to set
        
        Returns:
            Success message dict
        
        Raises:
            AuthenticationError: If current password is wrong
            ValidationError: If new password doesn't meet requirements
        """
        try:
            user = self.user_model.find_by_uid(user_id)
            
            if not user:
                raise AuthenticationError('User not found')
            
            # Verify current password
            if not verify_password(current_password, user['password_hash']):
                raise AuthenticationError('Current password is incorrect')
            
            # Validate new password
            is_valid, error_msg = validate_password_strength(new_password)
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Hash and update new password
            password_hash = hash_password(new_password)
            self.user_model.update_password(user_id, password_hash)
            
            logger.info(f"Password changed for user: {user['username']}")
            
            return {'message': 'Password changed successfully'}
            
        except (AuthenticationError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Change password error: {e}")
            raise AuthenticationError('Failed to change password')
