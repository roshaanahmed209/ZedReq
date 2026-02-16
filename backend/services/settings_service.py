"""Settings Service - User settings management"""
import json
import requests
import io
import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from urllib.parse import urlparse

from models.orm import User, Description, UsersContext, Payment
from services.auth_service import hash_password, verify_password, validate_password_strength, validate_email
from services.profile_service import ProfileService
from utils.api_security import sanitize_text_for_storage, validate_url_safe
from utils.errors import NotFoundError, ValidationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SettingsService:
    """Settings business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.profile_service = ProfileService(db)
    
    def _validate_resume_url(self, resume_url: str) -> bool:
        """
        Validate resume URL for security (SSRF protection)
        
        Args:
            resume_url: URL to validate
            
        Returns:
            True if URL is safe, False otherwise
        """
        try:
            # Validate URL format and scheme
            parsed = urlparse(resume_url)
            
            # Only allow http and https schemes
            if parsed.scheme not in ['http', 'https']:
                logger.warning(f"Invalid URL scheme: {parsed.scheme}")
                return False
            
            # Block private/internal IP addresses (SSRF protection)
            hostname = parsed.hostname
            if not hostname:
                return False
            
            # Block localhost and private IP ranges
            blocked_hosts = [
                'localhost', '127.0.0.1', '0.0.0.0', '::1',
                '169.254.169.254',  # AWS metadata service
                'metadata.google.internal',  # GCP metadata
            ]
            
            if hostname.lower() in blocked_hosts:
                logger.warning(f"Blocked internal hostname: {hostname}")
                return False
            
            # Block private IP ranges
            if hostname.startswith('10.') or hostname.startswith('192.168.') or hostname.startswith('172.'):
                # More thorough check needed, but basic protection
                if re.match(r'^(10\.|192\.168\.|172\.(1[6-9]|2[0-9]|3[01])\.)', hostname):
                    logger.warning(f"Blocked private IP: {hostname}")
                    return False
            
            # Only allow Cloudinary URLs or whitelisted domains
            allowed_domains = [
                'cloudinary.com',
                'res.cloudinary.com',
                'api.cloudinary.com'
            ]
            
            # Allow Cloudinary URLs
            if any(domain in hostname for domain in allowed_domains):
                return True
            
            # For other domains, could add additional validation
            # For now, allow any valid https URL (can be restricted further)
            return True
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def _extract_resume_text(self, resume_url: str) -> Optional[str]:
        """
        Extract text content from resume file (PDF, Word, or TXT)
        
        Args:
            resume_url: Cloudinary URL or file URL
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            # Validate URL for security (SSRF protection)
            if not self._validate_resume_url(resume_url):
                logger.warning(f"Invalid or unsafe resume URL: {resume_url}")
                return None
            
            # Validate URL format
            try:
                validate_url_safe(resume_url, allowed_schemes=['http', 'https'])
            except ValueError as e:
                logger.warning(f"URL validation failed: {e}")
                return None
            
            # Download file from URL with size limit
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
            response = requests.get(resume_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > MAX_FILE_SIZE:
                logger.warning(f"File too large: {content_length} bytes")
                return None
            
            # Read file content with size limit
            file_content = b''
            for chunk in response.iter_content(chunk_size=8192):
                file_content += chunk
                if len(file_content) > MAX_FILE_SIZE:
                    logger.warning(f"File size exceeded limit during download")
                    return None
            
            file_extension = resume_url.lower().split('.')[-1].split('?')[0]  # Remove query params
            
            # Extract text based on file type
            if file_extension == 'pdf':
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                    text_content = []
                    for page in pdf_reader.pages:
                        text_content.append(page.extract_text())
                    return '\n'.join(text_content)
                except ImportError:
                    try:
                        import pdfplumber
                        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                            text_content = []
                            for page in pdf.pages:
                                text_content.append(page.extract_text())
                        return '\n'.join(text_content)
                    except ImportError:
                        logger.warning("No PDF extraction library available. Install PyPDF2 or pdfplumber.")
                        return None
                except Exception as e:
                    logger.error(f"PDF extraction error: {e}")
                    return None
            
            elif file_extension in ['docx', 'doc']:
                try:
                    if file_extension == 'docx':
                        from docx import Document
                        doc = Document(io.BytesIO(file_content))
                        return '\n'.join([para.text for para in doc.paragraphs])
                    else:
                        # .doc files need conversion or special handling
                        logger.warning("DOC files require additional conversion. Please use DOCX format.")
                        return None
                except ImportError:
                    logger.warning("python-docx not available. Install it to extract Word documents.")
                    return None
                except Exception as e:
                    logger.error(f"Word extraction error: {e}")
                    return None
            
            elif file_extension == 'txt':
                try:
                    return file_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return file_content.decode('latin-1')
                    except Exception as e:
                        logger.error(f"TXT decoding error: {e}")
                        return None
            
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return None
                
        except Exception as e:
            logger.error(f"Resume extraction error: {e}")
            return None
    
    def _update_runtime_context(self, user_id: int, content: str) -> bool:
        """
        Append content to users_context.runtime_context JSONB
        
        Args:
            user_id: User ID
            content: Content string to add (will be sanitized)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sanitize content before storing
            sanitized_content = sanitize_text_for_storage(content, max_length=5000)
            
            # Get or create users_context record
            users_context = (
                self.db.query(UsersContext)
                .filter(UsersContext.user_id == user_id)
                .first()
            )
            
            new_item = [{"content": sanitized_content}]
            
            if users_context:
                # Update existing record - append to runtime_context
                if users_context.runtime_context:
                    # Append to existing array using PostgreSQL JSONB concatenation
                    # SQLAlchemy doesn't have native support for JSONB || operator, so use text()
                    from sqlalchemy import text
                    self.db.execute(
                        text("""
                            UPDATE users_context 
                            SET runtime_context = runtime_context || :new_item::jsonb,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE user_id = :user_id
                        """),
                        {"new_item": json.dumps(new_item), "user_id": user_id}
                    )
                else:
                    # Initialize with new array
                    users_context.runtime_context = new_item
            else:
                # Create new record
                users_context = UsersContext(
                    user_id=user_id,
                    runtime_context=new_item
                )
                self.db.add(users_context)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update runtime_context for user_id={user_id}: {e}")
            return False
    
    def update_profile(
        self, 
        user_id: int, 
        profile_pic: Optional[str] = None,
        cover_pic: Optional[str] = None,
        resume: Optional[str] = None,
        interests: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update user profile settings"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            update_data = {}
            
            # Get or create description
            description = None
            if user.description_id:
                description = (
                    self.db.query(Description)
                    .filter(Description.desc_id == user.description_id)
                    .first()
                )
            
            if not description:
                description = Description()
                self.db.add(description)
                self.db.flush()
                user.description_id = description.desc_id
            
            # Update profile picture (validate URL)
            if profile_pic:
                try:
                    validated_url = validate_url_safe(profile_pic, allowed_schemes=['http', 'https'])
                    description.profile_pic = validated_url
                    update_data['profile_pic'] = validated_url
                except ValueError as e:
                    logger.warning(f"Invalid profile_pic URL: {e}")
                    raise ValidationError(f"Invalid profile picture URL: {str(e)}")
            
            # Update cover picture (validate URL)
            if cover_pic:
                try:
                    validated_url = validate_url_safe(cover_pic, allowed_schemes=['http', 'https'])
                    description.cover_pic = validated_url
                    update_data['cover_pic'] = validated_url
                except ValueError as e:
                    logger.warning(f"Invalid cover_pic URL: {e}")
                    raise ValidationError(f"Invalid cover picture URL: {str(e)}")
            
            # Update resume (validate URL and extract text content)
            if resume:
                # Validate resume URL
                try:
                    validated_resume_url = validate_url_safe(resume, allowed_schemes=['http', 'https'])
                except ValueError as e:
                    logger.warning(f"Invalid resume URL: {e}")
                    raise ValidationError(f"Invalid resume URL: {str(e)}")
                
                resume_text = self._extract_resume_text(validated_resume_url)
                if resume_text:
                    # Sanitize extracted text (limit to 50KB for storage)
                    sanitized_resume = sanitize_text_for_storage(resume_text, max_length=50000)
                    description.resume = sanitized_resume
                    update_data['resume'] = sanitized_resume
                    # Also add to runtime_context for Zed Agent (limit length)
                    self._update_runtime_context(
                        user_id, 
                        f"User uploaded resume. Extracted content: {sanitized_resume[:500]}..."
                    )
                else:
                    logger.warning(f"Failed to extract text from resume for user {user_id}")
                    raise ValidationError("Failed to extract text from resume file. Please ensure the file is a valid PDF, Word, or TXT file.")
            
            # Update location (sanitize input)
            if location:
                sanitized_location = sanitize_text_for_storage(location, max_length=150)
                description.location = sanitized_location
                update_data['location'] = sanitized_location
            
            # Update interests (sanitize and add to runtime_context)
            if interests:
                sanitized_interests = sanitize_text_for_storage(interests, max_length=1000)
                interests_content = f"User updated interests: {sanitized_interests}"
                self._update_runtime_context(user_id, interests_content)
            
            self.db.commit()
            self.db.refresh(user)
            self.db.refresh(description)
            
            logger.info(f"Profile updated for user {user_id}")
            
            # Return updated profile
            return self.profile_service.get_user_profile(user_id)
            
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update profile error: {e}", exc_info=True)
            raise
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Verify current password
            if not verify_password(current_password, user.password_hash):
                raise ValidationError('Current password is incorrect')
            
            # Validate new password
            is_valid, error_msg = validate_password_strength(new_password)
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Hash and update password
            new_password_hash = hash_password(new_password)
            user.password_hash = new_password_hash
            
            self.db.commit()
            logger.info(f"Password changed for user {user_id}")
            return True
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Change password error: {e}", exc_info=True)
            raise
    
    def update_email(self, user_id: int, new_email: str) -> Dict[str, Any]:
        """Update user email"""
        try:
            # Validate email format
            if not validate_email(new_email):
                raise ValidationError('Invalid email format')
            
            # Check if email already exists
            existing_user = (
                self.db.query(User)
                .filter(User.user_email == new_email.lower())
                .filter(User.uid != user_id)
                .first()
            )
            if existing_user:
                raise ValidationError('Email already exists')
            
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            user.user_email = new_email.lower()
            user.email_verified = False  # Require re-verification
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Email updated for user {user_id}")
            
            return {
                'id': user.uid,
                'email': user.user_email,
                'email_verified': user.email_verified
            }
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update email error: {e}", exc_info=True)
            raise
    
    def toggle_two_factor(self, user_id: int, enabled: bool) -> bool:
        """Toggle two-factor authentication"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            user.two_factor_enabled = enabled
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"2FA {'enabled' if enabled else 'disabled'} for user {user_id}")
            return enabled
            
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Toggle 2FA error: {e}", exc_info=True)
            raise
    
    def get_subscription_info(self, user_id: int) -> Dict[str, Any]:
        """Get user subscription information"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Query payment table using ORM
            if user.pay_id:
                payment = (
                    self.db.query(Payment)
                    .filter(Payment.pay_id == user.pay_id)
                    .first()
                )
                
                if payment:
                    return {
                        'plan': payment.subscription_plan or 'free',
                        'status': payment.subscription_status or 'inactive',
                        'subscription_start': payment.subscription_start.isoformat() if payment.subscription_start else None,
                        'subscription_end': payment.subscription_end.isoformat() if payment.subscription_end else None
                    }
            
            # Default to free plan
            return {
                'plan': 'free',
                'status': 'inactive',
                'subscription_start': None,
                'subscription_end': None
            }
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Get subscription info error: {e}", exc_info=True)
            raise
    
    def update_subscription(self, user_id: int, plan: str) -> Dict[str, Any]:
        """Update user subscription plan"""
        try:
            if plan not in ['free', 'pro', 'premium']:
                raise ValidationError('Invalid subscription plan')
            
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Query or create payment record using ORM
            if user.pay_id:
                payment = (
                    self.db.query(Payment)
                    .filter(Payment.pay_id == user.pay_id)
                    .first()
                )
            else:
                payment = (
                    self.db.query(Payment)
                    .filter(Payment.uid == user_id)
                    .first()
                )
            
            subscription_status = 'inactive' if plan == 'free' else 'active'
            
            if payment:
                # Update existing payment record
                payment.subscription_plan = plan
                payment.subscription_status = subscription_status
            else:
                # Create new payment record
                payment = Payment(
                    uid=user_id,
                    subscription_plan=plan,
                    subscription_status=subscription_status
                )
                self.db.add(payment)
                self.db.flush()  # Get the pay_id
                user.pay_id = payment.pay_id
            
            self.db.commit()
            
            logger.info(f"Subscription updated to {plan} for user {user_id}")
            
            return self.get_subscription_info(user_id)
            
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Update subscription error: {e}", exc_info=True)
            raise
    
    def delete_account(self, user_id: int) -> bool:
        """Delete user account (cascade deletes handled by DB)"""
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Delete user (cascade will handle related records)
            self.db.delete(user)
            self.db.commit()
            
            logger.info(f"Account deleted for user {user_id}")
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Delete account error: {e}", exc_info=True)
            raise
