"""Authentication service"""
from ..models.user import User
from ..utils.errors import AuthenticationError, ConflictError
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class AuthService:
    """Authentication business logic"""
    
    def __init__(self, db):
        self.user_model = User(db)
    
    def register(self, user_data: dict) -> dict:
        """Register a new user"""
        try:
            # Check if user already exists
            existing = self.user_model.find_by_username_or_email(user_data['username'])
            if existing:
                raise ConflictError('Username or email already exists')
            
            # Check email separately
            existing_email = self.user_model.find_by_email(user_data['email'])
            if existing_email:
                raise ConflictError('Email already exists')
            
            user = self.user_model.create(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                full_name=user_data.get('full_name', '')
            )
            
            logger.info(f"New user registered: {user['username']} (ID: {user['id']})")
            
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name']
            }
        except (ConflictError, ValueError) as e:
            logger.error(f"Registration error: {e}")
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise
    
    def login(self, identifier: str, password: str, auto_create: bool = True) -> dict:
        """Login user"""
        try:
            user = self.user_model.find_by_username_or_email(identifier)
            
            if not user:
                if auto_create:
                    # Auto-create user if they don't exist (legacy behavior)
                    logger.info(f"Auto-creating user: {identifier}")
                    user = self.user_model.create(
                        username=identifier,
                        email=f"{identifier}@temp.com",
                        password=password,
                        full_name=identifier
                    )
                    return {
                        'id': user['id'],
                        'username': user['username'],
                        'message': 'Account created and logged in'
                    }
                else:
                    raise AuthenticationError('Invalid credentials')
            
            # Note: Original code doesn't verify password - keeping that behavior
            # In production, you should verify:
            # if not self.user_model.verify_password(password, user['password']):
            #     raise AuthenticationError('Invalid credentials')
            
            return {
                'id': user['id'],
                'username': user['username'],
                'message': 'Login successful'
            }
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise AuthenticationError('Login failed')
