"""Settings Service - User settings management"""
import json
import requests
import io
import re
import time
import os
from typing import Dict, Any, Optional
from functools import wraps
from sqlalchemy.orm import Session
from sqlalchemy import text
from urllib.parse import urlparse, unquote
from contextlib import contextmanager
from fastapi import UploadFile

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from models.orm import User, Description, UsersContext, Payment
from models.orm.subscription_plan import SubscriptionPlan
from models.orm.user_subscription import UserSubscription
from services.auth_service import hash_password, verify_password, validate_password_strength, validate_email
from services.profile_service import ProfileService
from utils.api_security import sanitize_text_for_storage, validate_url_safe, validate_request_timeout
from utils.errors import NotFoundError, ValidationError
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Configuration constants
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # seconds
REQUEST_TIMEOUT = 30  # seconds
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def retry_on_failure(max_retries: int = MAX_RETRIES, delay: float = RETRY_DELAY):
    """Decorator for retrying operations on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, ConnectionError, TimeoutError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {wait_time}s: {str(e)}"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All retries exhausted for {func.__name__}: {str(e)}")
                        raise
                except Exception as e:
                    # Don't retry on non-network errors
                    raise
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


@contextmanager
def db_transaction(db: Session):
    """Context manager for database transactions with proper error handling"""
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed, rolled back: {e}", exc_info=True)
        raise


class SettingsService:
    """Settings business logic with enhanced security and scalability"""
    
    def __init__(self, db: Session):
        self.db = db
        self.profile_service = ProfileService(db)
        self._session = requests.Session()
        # Configure session with timeouts and retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=2,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)
        
        # Initialize Cloudinary
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET')
        )
    
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
    
    def _cloudinary_signed_raw_url(self, resume_url: str) -> Optional[str]:
        """
        Signed delivery URL for Cloudinary raw files when anonymous GET returns 401
        (e.g. authenticated/restricted delivery).
        """
        parsed = urlparse(resume_url)
        host = (parsed.hostname or "").lower()
        if "res.cloudinary.com" not in host and "cloudinary.com" not in host:
            return None
        if not os.environ.get("CLOUDINARY_API_SECRET"):
            return None
        match = re.search(r"/raw/upload/(?:v\d+/)?([^?]+)", resume_url)
        if not match:
            return None
        public_id = unquote(match.group(1).rstrip("/"))
        if not public_id:
            return None
        candidates = [public_id]
        base, dot, ext = public_id.rpartition(".")
        if dot and ext.lower() in ("pdf", "doc", "docx", "txt") and base:
            candidates.append(base)
        for pid in candidates:
            try:
                signed, _ = cloudinary.utils.cloudinary_url(
                    pid,
                    resource_type="raw",
                    sign_url=True,
                    secure=True,
                )
                if signed:
                    return signed
            except Exception as e:
                logger.debug(f"Signed URL attempt failed for public_id={pid!r}: {e}")
        logger.warning("Could not build signed Cloudinary URL for resume")
        return None
    
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
            
            # Download file from URL with size limit and timeout
            timeout = validate_request_timeout(REQUEST_TIMEOUT, default=30.0)
            response = self._session.get(
                resume_url,
                timeout=timeout,
                stream=True,
                allow_redirects=True,
                verify=True,  # SSL verification enabled
            )
            if response.status_code == 401 and "cloudinary" in resume_url.lower():
                signed = self._cloudinary_signed_raw_url(resume_url)
                if signed:
                    logger.info("Retrying resume download with signed Cloudinary URL")
                    response = self._session.get(
                        signed,
                        timeout=timeout,
                        stream=True,
                        allow_redirects=True,
                        verify=True,
                    )
            response.raise_for_status()
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length:
                try:
                    size = int(content_length)
                    if size > MAX_FILE_SIZE:
                        logger.warning(f"File too large: {size} bytes (max: {MAX_FILE_SIZE})")
                        return None
                except (ValueError, TypeError):
                    logger.warning(f"Invalid content-length header: {content_length}")
            
            # Read file content with size limit and timeout protection
            file_content = b''
            chunk_size = 8192  # 8KB chunks
            start_time = time.time()
            
            try:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    # Check timeout
                    if time.time() - start_time > timeout:
                        logger.warning(f"Download timeout after {timeout}s")
                        return None
                    
                    if chunk:  # Filter out keep-alive chunks
                        file_content += chunk
                        if len(file_content) > MAX_FILE_SIZE:
                            logger.warning(f"File size exceeded limit during download: {len(file_content)} bytes")
                            return None
            except requests.Timeout:
                logger.warning(f"Request timeout while downloading resume")
                return None
            except requests.RequestException as e:
                logger.error(f"Request error while downloading resume: {e}")
                return None
            
            # Determine file extension from URL or Content-Type header
            file_extension = None
            
            # Try to get from URL first
            url_parts = resume_url.lower().split('.')
            if len(url_parts) > 1:
                potential_ext = url_parts[-1].split('?')[0].split('/')[0]  # Remove query params and path
                if potential_ext in ['pdf', 'doc', 'docx', 'txt']:
                    file_extension = potential_ext
            
            # Fallback to Content-Type header if URL doesn't have extension
            if not file_extension:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type:
                    file_extension = 'pdf'
                elif 'msword' in content_type or 'wordprocessingml' in content_type:
                    file_extension = 'docx' if 'wordprocessingml' in content_type else 'doc'
                elif 'text/plain' in content_type:
                    file_extension = 'txt'
                else:
                    # Try to detect from file content (magic bytes)
                    if file_content.startswith(b'%PDF'):
                        file_extension = 'pdf'
                    elif file_content.startswith(b'PK') and b'word/' in file_content[:2000]:
                        file_extension = 'docx'
                    elif file_content.startswith(b'\xd0\xcf\x11\xe0'):  # OLE2 format (old .doc)
                        file_extension = 'doc'
                    else:
                        logger.warning(f"Could not determine file type from URL or Content-Type. URL: {resume_url}, Content-Type: {content_type}")
                        return None
            
            logger.debug(f"Detected file extension: {file_extension} for URL: {resume_url}")
            
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
                    logger.error(f"PDF extraction error: {e}", exc_info=True)
                    # Try pdfplumber as fallback if PyPDF2 failed
                    try:
                        import pdfplumber
                        logger.info("Trying pdfplumber as fallback for PDF extraction")
                        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                            text_content = []
                            for page in pdf.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    text_content.append(page_text)
                        if text_content:
                            result = '\n'.join(text_content)
                            logger.info(f"Successfully extracted {len(result)} characters using pdfplumber")
                            return result
                        else:
                            logger.warning("pdfplumber extracted no text from PDF")
                            return None
                    except ImportError:
                        logger.error("pdfplumber not available as fallback")
                        return None
                    except Exception as e2:
                        logger.error(f"pdfplumber fallback also failed: {e2}", exc_info=True)
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
    
    async def upload_resume_file(self, resume_file: UploadFile, user_id: int) -> str:
        """
        Upload resume file to Cloudinary and extract text immediately.
        
        Args:
            resume_file: Uploaded file from FastAPI
            user_id: User ID for logging
            
        Returns:
            Cloudinary URL of uploaded file
            
        Raises:
            ValidationError: If file is invalid or extraction fails
        """
        try:
            # Validate file
            if not resume_file.filename:
                raise ValidationError("No file provided")
            
            # Check file size
            file_content = await resume_file.read()
            if len(file_content) > MAX_FILE_SIZE:
                raise ValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024)}MB")
            
            # Validate file type
            file_extension = resume_file.filename.lower().split('.')[-1] if '.' in resume_file.filename else ''
            if file_extension not in ['pdf', 'doc', 'docx', 'txt']:
                raise ValidationError("Invalid file type. Only PDF, DOC, DOCX, and TXT files are supported.")
            
            # Upload to Cloudinary using file content
            logger.info(f"Uploading resume file for user {user_id}: {resume_file.filename}")
            
            # Create a BytesIO object for Cloudinary
            file_io = io.BytesIO(file_content)
            file_io.name = resume_file.filename  # Cloudinary may use this
            
            upload_result = cloudinary.uploader.upload(
                file_io,
                resource_type='raw',
                folder='resumes',
                public_id=f"user_{user_id}_{int(time.time())}",
                overwrite=False,
                access_mode='public',
            )
            
            resume_url = upload_result.get('secure_url')
            if not resume_url:
                raise ValidationError("Failed to upload resume to Cloudinary")
            
            logger.info(f"Resume uploaded successfully: {resume_url}")
            
            # Extract text immediately from the file content we already have
            resume_text = self._extract_text_from_bytes(file_content, file_extension)
            
            if not resume_text:
                # If extraction failed, try downloading from Cloudinary URL
                logger.warning(f"Direct extraction failed, trying to download from Cloudinary URL")
                resume_text = self._extract_resume_text(resume_url)
            
            if resume_text:
                # Sanitize and store text
                sanitized_resume = sanitize_text_for_storage(resume_text, max_length=50000)
                
                # Ensure Description row exists (same as update_profile) so resume text persists
                user = self.db.query(User).filter(User.uid == user_id).first()
                if not user:
                    raise ValidationError("User not found")
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
                    self.db.flush()
                description.resume = sanitized_resume
                self.db.commit()
                logger.info(f"Resume text extracted and stored for user {user_id} ({len(sanitized_resume)} chars)")
                
                # Update runtime context
                self._update_runtime_context(
                    user_id,
                    f"User uploaded resume. Extracted content: {sanitized_resume[:500]}..."
                )
                
                # Update user embedding and invalidate recommendation cache
                # This ensures recommendations are regenerated with the new resume content
                try:
                    from utils.job_embeddings import update_user_embedding_if_needed
                    update_user_embedding_if_needed(user_id, self.db)
                    
                    # Invalidate recommendation cache and increment profile version
                    from services.recommendation_cache_service import RecommendationCacheService
                    cache_service = RecommendationCacheService(self.db)
                    cache_service.increment_profile_version(user_id)
                    logger.info(f"Updated user embedding and invalidated cache for user {user_id} after resume upload")
                except Exception as e:
                    logger.warning(f"Failed to update embedding/cache for user {user_id} after resume upload: {e}")
                    # Don't fail resume upload if embedding/cache update fails
            else:
                logger.warning(f"Could not extract text from resume for user {user_id}")
                raise ValidationError("Failed to extract text from resume file. Please ensure the file is a valid PDF, Word, or TXT file.")
            
            return resume_url
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error uploading resume file: {e}", exc_info=True)
            raise ValidationError(f"Failed to upload resume: {str(e)}")
    
    def _extract_text_from_bytes(self, file_content: bytes, file_extension: str) -> Optional[str]:
        """
        Extract text from file bytes directly (without downloading from URL).
        
        Args:
            file_content: File content as bytes
            file_extension: File extension (pdf, docx, doc, txt)
            
        Returns:
            Extracted text or None
        """
        try:
            if file_extension == 'pdf':
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                    text_content = []
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                    if text_content:
                        return '\n'.join(text_content)
                except ImportError:
                    try:
                        import pdfplumber
                        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                            text_content = []
                            for page in pdf.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    text_content.append(page_text)
                        if text_content:
                            return '\n'.join(text_content)
                    except ImportError:
                        logger.warning("No PDF extraction library available")
                        return None
                except Exception as e:
                    logger.error(f"PDF extraction error: {e}", exc_info=True)
                    return None
            
            elif file_extension == 'docx':
                try:
                    from docx import Document
                    doc = Document(io.BytesIO(file_content))
                    return '\n'.join([para.text for para in doc.paragraphs])
                except ImportError:
                    logger.warning("python-docx not available")
                    return None
                except Exception as e:
                    logger.error(f"Word extraction error: {e}", exc_info=True)
                    return None
            
            elif file_extension == 'doc':
                logger.warning("DOC files require additional conversion. Please use DOCX format.")
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
            
            return None
            
        except Exception as e:
            logger.error(f"Text extraction error: {e}", exc_info=True)
            return None
    
    async def upload_image_file(self, image_file: UploadFile, file_type: str = 'image') -> str:
        """
        Upload image file to Cloudinary.
        
        Args:
            image_file: Uploaded file from FastAPI
            file_type: Type of image ('profile_pic' or 'cover_pic')
            
        Returns:
            Cloudinary URL of uploaded image
            
        Raises:
            ValidationError: If file is invalid
        """
        try:
            # Validate file
            if not image_file.filename:
                raise ValidationError("No file provided")
            
            # Check file size (5MB for images)
            file_content = await image_file.read()
            max_image_size = 5 * 1024 * 1024  # 5MB
            if len(file_content) > max_image_size:
                raise ValidationError(f"Image too large. Maximum size is {max_image_size / (1024*1024)}MB")
            
            # Validate file type (some browsers omit content_type; allow common image extensions)
            ct = (image_file.content_type or "").strip().lower()
            ext = os.path.splitext(image_file.filename or "")[1].lower().lstrip(".")
            image_exts = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "svg", "heic", "heif", "avif"}
            if not ct.startswith("image/") and ext not in image_exts:
                raise ValidationError("Invalid file type. Only image files are supported.")
            
            # Upload to Cloudinary using file content
            logger.info(f"Uploading {file_type}: {image_file.filename}")
            
            # Create a BytesIO object for Cloudinary
            file_io = io.BytesIO(file_content)
            file_io.name = image_file.filename  # Cloudinary may use this
            
            upload_result = cloudinary.uploader.upload(
                file_io,
                resource_type='image',
                folder=file_type,
                overwrite=False
            )
            
            image_url = upload_result.get('secure_url')
            if not image_url:
                raise ValidationError(f"Failed to upload {file_type} to Cloudinary")
            
            logger.info(f"{file_type} uploaded successfully: {image_url}")
            return image_url
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error uploading {file_type}: {e}", exc_info=True)
            raise ValidationError(f"Failed to upload {file_type}: {str(e)}")
    
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
                    # Merge arrays in Python to avoid SQL parameter binding issues
                    existing_context = users_context.runtime_context
                    if isinstance(existing_context, list):
                        users_context.runtime_context = existing_context + new_item
                    else:
                        # If it's not a list, convert it
                        users_context.runtime_context = [existing_context] + new_item if existing_context else new_item
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
        name: Optional[str] = None,
        profile_pic: Optional[str] = None,
        cover_pic: Optional[str] = None,
        resume: Optional[str] = None,
        interests: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update user profile settings with transaction management
        
        Args:
            user_id: User ID
            name: User's full name
            profile_pic: Profile picture URL
            cover_pic: Cover picture URL
            resume: Resume file URL
            interests: User interests
            location: User location
            
        Returns:
            Updated user profile dictionary
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If validation fails
        """
        # Use transaction context manager for atomicity
        with db_transaction(self.db):
            # Optimize query: use get() if possible, or select only needed columns
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            update_data = {}
            
            # Update name if provided (check for both None and empty string)
            if name is not None and str(name).strip():
                sanitized_name = sanitize_text_for_storage(str(name), max_length=100)
                trimmed_name = sanitized_name.strip()
                if trimmed_name:
                    user.name = trimmed_name
                    update_data['name'] = trimmed_name
                    logger.info(f"Updating name for user {user_id} to: {trimmed_name}")
                else:
                    raise ValidationError("Name cannot be empty")
            
            # Get or create description (optimized query)
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
                self.db.flush()  # Get the ID without committing
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
                
                # Check if resume text is already stored (e.g., from upload_resume_file)
                # If text already exists, skip extraction to avoid re-downloading from Cloudinary
                if description.resume and len(description.resume.strip()) > 0:
                    logger.info(f"Resume text already exists for user {user_id}, skipping extraction")
                    # Resume text is already stored, no need to extract again
                    update_data['resume'] = description.resume
                else:
                    # Extract text from resume URL
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
            
            # Track if recommendation-relevant fields changed
            recommendation_changed = False
            
            # Update location (sanitize input and parse city/country)
            if location:
                sanitized_location = sanitize_text_for_storage(location, max_length=150)
                description.location = sanitized_location
                update_data['location'] = sanitized_location
                recommendation_changed = True
                
                # Parse and store city/country
                from services.recommendation_service import RecommendationService
                rec_service = RecommendationService(self.db)
                parsed_location = rec_service._parse_location(sanitized_location)
                description.city = parsed_location.get('city')
                description.country = parsed_location.get('country')
            
            # Resume changes also affect recommendations
            if resume:
                recommendation_changed = True
            
            # Update interests (sanitize and add to runtime_context)
            if interests:
                sanitized_interests = sanitize_text_for_storage(interests, max_length=1000)
                interests_content = f"User updated interests: {sanitized_interests}"
                self._update_runtime_context(user_id, interests_content)
            
            # Flush changes to ensure they're persisted
            self.db.flush()
            
            # Log the name update for debugging
            if 'name' in update_data:
                logger.info(f"Name update flushed for user {user_id}: {update_data['name']}")
            
            # Update user embedding and invalidate cache if recommendation-relevant fields changed
            if recommendation_changed:
                try:
                    from utils.job_embeddings import update_user_embedding_if_needed
                    update_user_embedding_if_needed(user_id, self.db)
                    
                    # Invalidate recommendation cache and increment profile version
                    from services.recommendation_cache_service import RecommendationCacheService
                    cache_service = RecommendationCacheService(self.db)
                    cache_service.increment_profile_version(user_id)
                except Exception as e:
                    logger.warning(f"Failed to update embedding/cache for user {user_id}: {e}")
                    # Don't fail profile update if embedding/cache update fails
            
            # Transaction commits automatically via context manager
            logger.info(f"Profile updated for user {user_id}, name={user.name}")
            
            # Return updated profile (query will use fresh data after commit)
            return self.profile_service.get_user_profile(user_id)
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password with enhanced security
        
        Args:
            user_id: User ID
            current_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If password validation fails
        """
        with db_transaction(self.db):
            # Optimize: select only needed columns
            user = self.db.query(User.uid, User.password_hash).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Verify current password (constant-time comparison)
            if not verify_password(current_password, user.password_hash):
                # Log failed attempt (for security monitoring)
                logger.warning(f"Failed password change attempt for user {user_id}")
                raise ValidationError('Current password is incorrect')
            
            # Validate new password strength
            is_valid, error_msg = validate_password_strength(new_password)
            if not is_valid:
                raise ValidationError(error_msg)
            
            # Hash and update password (get full user object for update)
            full_user = self.db.query(User).filter(User.uid == user_id).first()
            new_password_hash = hash_password(new_password)
            full_user.password_hash = new_password_hash
            
            # Transaction commits automatically via context manager
            logger.info(f"Password changed successfully for user {user_id}")
            return True
    
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
        """
        Toggle two-factor authentication
        Note: For enabling, use the 2FA setup endpoints. This only disables.
        """
        if enabled:
            # Enabling should be done through 2FA setup flow
            raise ValidationError("To enable 2FA, please use the 2FA setup endpoint to generate a secret and QR code")
        
        # Disable 2FA
        from services.two_factor_service import TwoFactorService
        two_factor_service = TwoFactorService(self.db)
        two_factor_service.disable_2fa(user_id)
        
        logger.info(f"2FA disabled for user {user_id}")
        return False
    
    def get_subscription_info(self, user_id: int) -> Dict[str, Any]:
        """
        Get user subscription information.
        Reads from user_subscriptions (authoritative) with fallback to payment.
        """
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # 1. Check user_subscriptions (authoritative source for quotas)
            user_sub = (
                self.db.query(UserSubscription)
                .filter(UserSubscription.user_id == user_id, UserSubscription.status == 'active')
                .first()
            )
            if user_sub and user_sub.plan:
                return {
                    'plan': str(user_sub.plan.plan_name),
                    'status': str(user_sub.status or 'inactive'),
                    'subscription_start': user_sub.started_at.isoformat() if user_sub.started_at else None,
                    'subscription_end': user_sub.expires_at.isoformat() if user_sub.expires_at else None
                }
            
            # 2. Fallback to payment table (for users not yet migrated)
            if user.pay_id:
                payment = (
                    self.db.query(Payment)
                    .filter(Payment.pay_id == user.pay_id)
                    .first()
                )
                if payment and payment.subscription_plan:
                    return {
                        'plan': str(payment.subscription_plan),
                        'status': str(payment.subscription_status) if payment.subscription_status else 'inactive',
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

    def requires_plan_selection(self, user_id: int) -> bool:
        """
        True until the user has a persisted plan signal (active subscription and/or payment row with a plan).
        """
        try:
            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                return True
            active_sub = (
                self.db.query(UserSubscription)
                .filter(UserSubscription.user_id == user_id, UserSubscription.status == 'active')
                .first()
            )
            if active_sub:
                return False
            if user.pay_id:
                payment = self.db.query(Payment).filter(Payment.pay_id == user.pay_id).first()
                if payment and payment.subscription_plan and str(payment.subscription_plan).strip():
                    return False
            payment_orphan = self.db.query(Payment).filter(Payment.uid == user_id).first()
            if payment_orphan and payment_orphan.subscription_plan and str(payment_orphan.subscription_plan).strip():
                return False
            return True
        except Exception as e:
            logger.error(f"requires_plan_selection error: {e}", exc_info=True)
            return True

    def get_subscription_info_with_flags(self, user_id: int) -> Dict[str, Any]:
        """Subscription dict plus requires_plan_selection for API responses."""
        info = self.get_subscription_info(user_id)
        info['requires_plan_selection'] = self.requires_plan_selection(user_id)
        user = self.db.query(User).filter(User.uid == user_id).first()
        if user:
            if user.pay_id:
                pay = self.db.query(Payment).filter(Payment.pay_id == user.pay_id).first()
            else:
                pay = self.db.query(Payment).filter(Payment.uid == user_id).first()
            if pay:
                info['paddle_subscription_id'] = pay.paddle_subscription_id
        return info

    def update_subscription(
        self,
        user_id: int,
        plan: str,
        billing_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update user subscription plan (payment-first flow).
        
        Write order (payment is source of truth):
        1. Look up plan_id from subscription_plans.
        2. UPSERT payment FIRST (plan, billing subscription status).
        3. UPSERT user_subscriptions (entitlement; always active for self-serve tiers).
        4. SET payment.subscription_id FK link.
        
        Free tier: payment.subscription_status stays inactive (no paid sub);
        user_subscriptions.status is active so quota/API reads match the chosen plan.
        
        Enterprise plan cannot be self-assigned — admin only.
        """
        try:
            if plan not in ['free', 'pro', 'premium']:
                raise ValidationError('Invalid subscription plan. Enterprise is admin-only.')

            if plan in ('pro', 'premium'):
                raise ValidationError(
                    'Paid plans are managed through Paddle. Use checkout to subscribe, or '
                    'POST /api/user/subscription/change-plan if you already have an active subscription.'
                )

            user = self.db.query(User).filter(User.uid == user_id).first()
            if not user:
                raise NotFoundError('User')
            
            # Billing row: inactive for free (no recurring payment), active for paid tiers
            payment_subscription_status = 'inactive' if plan == 'free' else 'active'
            # Entitlement row: active whenever user has a self-serve plan (used by get_user_plan)
            user_sub_status = 'active'
            
            # 1. Look up plan_id from subscription_plans
            plan_obj = self.db.query(SubscriptionPlan).filter_by(plan_name=plan, is_active=True).first()
            if not plan_obj:
                raise ValidationError(f"Plan '{plan}' not found. Ensure plans are seeded.")
            
            # 2. UPSERT payment FIRST (source of truth)
            if user.pay_id:
                payment = self.db.query(Payment).filter(Payment.pay_id == user.pay_id).first()
            else:
                payment = self.db.query(Payment).filter(Payment.uid == user_id).first()
            
            if payment:
                payment.subscription_plan = plan
                payment.subscription_status = payment_subscription_status
            else:
                payment = Payment(
                    uid=user_id,
                    subscription_plan=plan,
                    subscription_status=payment_subscription_status,
                )
                self.db.add(payment)
                self.db.flush()
                user.pay_id = payment.pay_id

            be = (billing_email or "").strip()
            if be:
                payment.billing_email = be[:150]
            
            # 3. UPSERT user_subscriptions (synced from payment, used for quota reads)
            user_sub = self.db.query(UserSubscription).filter_by(user_id=user_id).first()
            if user_sub:
                user_sub.plan_id = plan_obj.plan_id
                user_sub.status = user_sub_status
                user_sub.assigned_by = 'self'
            else:
                from datetime import datetime, timezone
                user_sub = UserSubscription(
                    user_id=user_id,
                    plan_id=plan_obj.plan_id,
                    status=user_sub_status,
                    assigned_by='self',
                    started_at=datetime.now(timezone.utc),
                )
                self.db.add(user_sub)
                self.db.flush()  # Get subscription_id
            
            # 4. SET payment.subscription_id FK link
            payment.subscription_id = user_sub.subscription_id
            
            self.db.commit()
            
            logger.info(f"Subscription updated to {plan} for user {user_id} (subscription_id={user_sub.subscription_id})")
            
            return self.get_subscription_info_with_flags(user_id)

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
