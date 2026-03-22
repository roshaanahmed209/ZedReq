"""Authentication Service with JWT using ORM"""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import hashlib
import hmac
import secrets
import re
import requests
import json
import base64
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from models.orm import User
from services.user_service import UserService
from config.settings import settings
from utils.logger import setup_logger
from utils.errors import GoogleSignInNoAccountError

logger = setup_logger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    # Generate a random salt
    salt = secrets.token_hex(16)
    # Hash password with salt
    password_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    # Store as salt$hash format
    return f"sha256${salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    Supports:
    - sha256 (new passwords)
    - pbkdf2:sha256 (existing Werkzeug passwords, for backward compatibility)
    """
    if not hashed_password:
        return False
    
    try:
        # Check if it's our new SHA-256 format: sha256$salt$hash
        if hashed_password.startswith('sha256$'):
            parts = hashed_password.split('$')
            if len(parts) == 3:
                _, salt, stored_hash = parts
                computed_hash = hashlib.sha256((salt + plain_password).encode('utf-8')).hexdigest()
                return hmac.compare_digest(computed_hash, stored_hash)
        
        # Werkzeug pbkdf2 format: pbkdf2:sha256:iterations$salt$hash
        if hashed_password.startswith('pbkdf2:'):
            method_part, rest = hashed_password.split('$', 1)
            salt, hash_value = rest.rsplit('$', 1)
            
            # Parse iterations from method (pbkdf2:sha256:iterations)
            parts = method_part.split(':')
            iterations = int(parts[2]) if len(parts) >= 3 else 260000
            
            # Compute and compare hash
            computed = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), iterations)
            return hmac.compare_digest(computed.hex(), hash_value)
        
        # Werkzeug scrypt format: scrypt:n:r:p$salt$hash
        if hashed_password.startswith('scrypt:'):
            method_part, salt, hash_value = hashed_password.split('$')
            parts = method_part.split(':')
            n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
            computed = hashlib.scrypt(plain_password.encode('utf-8'), salt=salt.encode('utf-8'), n=n, r=r, p=p)
            return hmac.compare_digest(computed.hex(), hash_value)
        
        return False
    except Exception as e:
        print(f"Password verification error: {e}")
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password meets requirements: 8-25 chars, at least one uppercase"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 25:
        return False, "Password must not exceed 25 characters"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, ""


class AuthService:
    """Authentication business logic with JWT using ORM"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    def _create_access_token(self, user_id: str, username: str) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": user_id,
            "username": username,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def _create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def _create_tokens(self, user: dict) -> dict:
        """Create both access and refresh tokens"""
        user_id = str(user.get("id") or user.get("uid"))
        username = user.get("username", "")
        access_token = self._create_access_token(user_id, username)
        refresh_token = self._create_refresh_token(user_id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.get("id") or user.get("uid"),
                "username": user.get("username", ""),
                "email": user.get("email") or user.get("user_email", ""),
                "name": user.get("name", ""),
                "profile_pic": user.get("profile_pic"),
                "bio": user.get("bio"),
                "job_title": user.get("job_title"),
                "company": user.get("company"),
                "created_at": user.get("created_at")
            }
        }
    
    def register(self, user_data: dict) -> dict:
        """Register a new user and return tokens"""
        username = user_data.get('username', '').strip()
        email = user_data.get('email', '').strip()
        password = user_data.get('password', '')
        full_name = user_data.get('full_name', '').strip() or username
        
        # Validate username
        is_valid, error_msg = validate_username(username)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Validate email
        if not validate_email(email):
            raise ValueError('Please provide a valid email address')
        
        # Validate password
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check if username already exists using ORM
        existing_user = (
            self.db.query(User)
            .filter(func.lower(User.username) == func.lower(username))
            .first()
        )
        if existing_user:
            raise ValueError('Username already exists')
        
        # Check if email already exists using ORM
        existing_email = (
            self.db.query(User)
            .filter(func.lower(User.user_email) == func.lower(email))
            .first()
        )
        if existing_email:
            raise ValueError('Email already exists')
        
        # Hash password and create user using ORM
        password_hash = hash_password(password)
        user = User(
            username=username,
            user_email=email,
            password_hash=password_hash,
            name=full_name,
            email_verified=False
        )
        
        self.db.add(user)
        self.db.flush()  # Flush to get the user ID
        
        # Generate profile path (not full URL) after user is created (so we have the user ID)
        # Store only the path part so it works in any environment
        from utils.profile_url import generate_profile_path
        profile_path = generate_profile_path(user.uid, username)
        if profile_path:
            user.profile_url = profile_path
        
        self.db.commit()
        self.db.refresh(user)
        
        # Format user for token creation
        user_dict = {
            "id": user.uid,
            "uid": user.uid,
            "username": user.username,
            "email": user.user_email,
            "user_email": user.user_email,
            "name": user.name,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        # Return tokens
        return self._create_tokens(user_dict)
    
    def _create_temp_token(self, user_id: str) -> str:
        """Create temporary token for 2FA verification (short-lived)"""
        expire = datetime.utcnow() + timedelta(minutes=5)  # 5 minutes validity
        payload = {
            "sub": user_id,
            "type": "2fa_temp",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    def login(self, identifier: str, password: str) -> dict:
        """Login user and return tokens (or temp token if 2FA enabled)"""
        if not identifier or not password:
            raise ValueError('Username/email and password are required')
        
        # Find user by username or email using ORM
        user = (
            self.db.query(User)
            .filter(
                or_(
                    func.lower(User.username) == func.lower(identifier.strip()),
                    func.lower(User.user_email) == func.lower(identifier.strip())
                )
            )
            .first()
        )
        
        if not user:
            raise ValueError('Invalid username or password')
        
        # Verify password
        if not verify_password(password, user.password_hash):
            raise ValueError('Invalid username or password')
        
        # Check if 2FA is enabled and verified
        if user.two_factor_enabled and user.two_factor_verified:
            # Return temporary token for 2FA verification
            temp_token = self._create_temp_token(str(user.uid))
            return {
                "requires_2fa": True,
                "temp_token": temp_token,
                "message": "Please enter your 2FA code to complete login"
            }
        
        # Update last login using ORM
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Format user for token creation
        user_dict = {
            "id": user.uid,
            "uid": user.uid,
            "username": user.username,
            "email": user.user_email,
            "user_email": user.user_email,
            "name": user.name,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        # Return tokens
        return self._create_tokens(user_dict)
    
    def verify_2fa_and_login(self, temp_token: str, code: str) -> dict:
        """
        Verify 2FA code and complete login
        
        Args:
            temp_token: Temporary token from login
            code: 2FA code (TOTP or backup code)
            
        Returns:
            Full access and refresh tokens
        """
        from services.two_factor_service import TwoFactorService
        
        try:
            # Verify temp token
            payload = jwt.decode(
                temp_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "2fa_temp":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token")
            
            # Get user
            user = (
                self.db.query(User)
                .filter(User.uid == int(user_id))
                .first()
            )
            
            if not user:
                raise ValueError("User not found")
            
            if not user.two_factor_enabled or not user.two_factor_verified:
                raise ValueError("2FA is not enabled for this user")
            
            # Verify 2FA code
            two_factor_service = TwoFactorService(self.db)
            if not two_factor_service.verify_code(int(user_id), code):
                raise ValueError("Invalid 2FA code")
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            
            # Format user for token creation
            user_dict = {
                "id": user.uid,
                "uid": user.uid,
                "username": user.username,
                "email": user.user_email,
                "user_email": user.user_email,
                "name": user.name,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            
            # Return full tokens
            return self._create_tokens(user_dict)
            
        except JWTError as e:
            raise ValueError(f"Invalid or expired token: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token")
            
            # Get user using ORM
            user = self.user_service.get_user_by_id(int(user_id))
            if not user:
                raise ValueError("User not found")
            
            # Create new tokens
            return self._create_tokens(user)
            
        except JWTError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    def verify_token(self, token: str) -> dict:
        """Verify access token and return user info"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            if not user_id:
                raise ValueError("Invalid token")
            
            # Get user using ORM
            user = self.user_service.get_user_by_id(int(user_id))
            if not user:
                raise ValueError("User not found")
            
            return {
                "id": user.get("id") or user.get("uid"),
                "username": user.get("username", ""),
                "email": user.get("email") or user.get("user_email", ""),
                "name": user.get("name", "")
            }
            
        except JWTError as e:
            raise ValueError(f"Invalid token: {str(e)}")
    
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """Get user by ID"""
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return None

        return {
            "id": user.get("id") or user.get("uid"),
            "username": user.get("username", ""),
            "email": user.get("email") or user.get("user_email", ""),
            "name": user.get("name", ""),
            "profile_pic": user.get("profile_pic"),
            "bio": user.get("bio"),
            "job_title": user.get("job_title"),
            "company": user.get("company"),
            "created_at": user.get("created_at")
        }
    
    def verify_google_token(self, id_token: str, intent: str = "signup") -> dict:
        """Verify Firebase ID token. intent 'signup' creates user if missing; 'login' requires existing user."""
        try:
            # Firebase ID tokens are JWTs - decode without verification for now
            # In production, you should verify the signature using Firebase's public keys
            try:
                # Decode the JWT token (without verification for simplicity)
                # The token contains: email, name, picture, sub (user ID), aud (audience/project ID)
                token_parts = id_token.split('.')
                if len(token_parts) != 3:
                    raise ValueError('Invalid token format')
                
                # Decode the payload (second part of JWT)
                # Add padding if needed
                payload = token_parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                
                decoded_payload = base64.urlsafe_b64decode(payload)
                token_data = json.loads(decoded_payload)
                
                # Check token expiration (exp claim is Unix timestamp)
                exp = token_data.get('exp')
                if exp:
                    current_time = datetime.utcnow().timestamp()
                    if current_time > exp:
                        raise ValueError('Firebase token has expired')
                
                # Verify the token is for our Firebase project (if configured)
                if settings.FIREBASE_AUTH_PROJECT_ID:
                    # Firebase tokens have audience (aud) as the project ID
                    # But it might be in format: {project_id} or full client ID
                    token_aud = token_data.get('aud', '')
                    if settings.FIREBASE_AUTH_PROJECT_ID not in str(token_aud):
                        logger.warning(f"Token audience mismatch: {token_aud} vs {settings.FIREBASE_AUTH_PROJECT_ID}")
                        # Don't fail, but log it
                
                # Extract user info from token
                google_email = token_data.get('email')
                google_name = token_data.get('name', '')
                google_picture = token_data.get('picture', '')
                google_sub = token_data.get('sub')  # Firebase user ID
                
                if not google_email:
                    raise ValueError('Email not found in Firebase token')
                    
            except (ValueError, json.JSONDecodeError, Exception) as decode_error:
                logger.error(f"Token decode error: {decode_error}")
                raise ValueError('Invalid Firebase token format')
            
            # Check if user exists by email
            user = (
                self.db.query(User)
                .filter(func.lower(User.user_email) == func.lower(google_email))
                .first()
            )
            
            if user:
                # User exists, update last login and return tokens
                user.last_login = datetime.utcnow()
                if google_picture and not user.profile_url:
                    user.profile_url = google_picture
                self.db.commit()
                self.db.refresh(user)
                
                user_dict = {
                    "id": user.uid,
                    "uid": user.uid,
                    "username": user.username,
                    "email": user.user_email,
                    "user_email": user.user_email,
                    "name": user.name,
                    "profile_pic": user.profile_url or google_picture,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "two_factor_enabled": user.two_factor_enabled or False,
                    "two_factor_verified": user.two_factor_verified or False
                }
                
                return self._create_tokens(user_dict)
            else:
                if intent == "login":
                    raise GoogleSignInNoAccountError()

                # Create new user (signup intent)
                # Generate username from email (before @)
                base_username = google_email.split('@')[0].lower()
                username = base_username
                counter = 1
                
                # Ensure username is unique
                while self.db.query(User).filter(func.lower(User.username) == func.lower(username)).first():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Create user with Google info
                # Generate a random password hash (user won't use it, but required by schema)
                random_password = secrets.token_urlsafe(32)
                password_hash = hash_password(random_password)
                
                new_user = User(
                    username=username,
                    name=google_name or username,
                    user_email=google_email,
                    password_hash=password_hash,
                    email_verified=True,  # Google emails are verified
                    profile_url=google_picture,
                    last_login=datetime.utcnow()
                )
                
                self.db.add(new_user)
                self.db.commit()
                self.db.refresh(new_user)
                
                user_dict = {
                    "id": new_user.uid,
                    "uid": new_user.uid,
                    "username": new_user.username,
                    "email": new_user.user_email,
                    "user_email": new_user.user_email,
                    "name": new_user.name,
                    "profile_pic": new_user.profile_url,
                    "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
                    "two_factor_enabled": False,
                    "two_factor_verified": False
                }
                
                return self._create_tokens(user_dict)
                
        except GoogleSignInNoAccountError:
            raise
        except requests.RequestException as e:
            logger.error(f"Google token verification error: {e}")
            raise ValueError('Failed to verify Google token')
        except Exception as e:
            logger.error(f"Google auth error: {e}", exc_info=True)
            raise ValueError(f'Google authentication failed: {str(e)}')