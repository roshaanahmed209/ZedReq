"""
Two-Factor Authentication Service
TOTP-based 2FA implementation using pyotp
"""
import json
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
import os

try:
    import pyotp
    import qrcode
    from io import BytesIO
    import base64 as b64
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    pyotp = None
    qrcode = None

from models.orm import User
from utils.errors import NotFoundError, ValidationError
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TwoFactorService:
    """Service for managing two-factor authentication"""
    
    def __init__(self, db: Session):
        self.db = db
        self._encryption_key = self._get_encryption_key()
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for 2FA secrets"""
        key = os.environ.get('2FA_ENCRYPTION_KEY')
        if not key:
            # Generate a key if not set (for development)
            # In production, this should be set in environment variables
            logger.warning("2FA_ENCRYPTION_KEY not set. Generating temporary key. Set this in production!")
            key = Fernet.generate_key().decode()
        else:
            # If key is provided as string, ensure it's valid
            try:
                Fernet(key.encode() if isinstance(key, str) else key)
                return key.encode() if isinstance(key, str) else key
            except Exception:
                logger.error("Invalid 2FA_ENCRYPTION_KEY format. Generating new key.")
                key = Fernet.generate_key().decode()
        
        return key.encode() if isinstance(key, str) else key
    
    def _encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            f = Fernet(self._encryption_key)
            encrypted = f.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise ValidationError("Failed to encrypt data")
    
    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            f = Fernet(self._encryption_key)
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = f.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise ValidationError("Failed to decrypt data")
    
    def generate_secret(self, user_id: int) -> Dict[str, Any]:
        """
        Generate TOTP secret for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with secret, QR code, and setup URL
        """
        if not PYOTP_AVAILABLE:
            raise ValidationError("2FA libraries not installed. Install pyotp and qrcode[pil]")
        
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError('User')
        
        # Generate a new secret
        secret = pyotp.random_base32()
        
        # Create TOTP object
        totp = pyotp.TOTP(secret)
        
        # Generate provisioning URI
        issuer = os.environ.get('2FA_ISSUER_NAME', 'ZedRec')
        account_name = f"{user.username} ({user.user_email})"
        provisioning_uri = totp.provisioning_uri(
            name=account_name,
            issuer_name=issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Convert to base64 for frontend
        qr_code_base64 = b64.b64encode(buffer.getvalue()).decode()
        qr_code_data_url = f"data:image/png;base64,{qr_code_base64}"
        
        # Store secret temporarily (not verified yet)
        encrypted_secret = self._encrypt(secret)
        user.two_factor_secret = encrypted_secret
        user.two_factor_verified = False  # Not verified until user confirms
        self.db.commit()
        
        logger.info(f"Generated 2FA secret for user {user_id}")
        
        return {
            'secret': secret,  # Return plain secret for QR code generation (one-time)
            'qr_code': qr_code_data_url,
            'provisioning_uri': provisioning_uri,
            'manual_entry_key': secret  # For manual entry
        }
    
    def verify_setup_code(self, user_id: int, code: str) -> bool:
        """
        Verify 2FA setup code and complete setup
        
        Args:
            user_id: User ID
            code: 6-digit TOTP code from authenticator app
            
        Returns:
            True if verification successful
        """
        if not PYOTP_AVAILABLE:
            raise ValidationError("2FA libraries not installed")
        
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError('User')
        
        if not user.two_factor_secret:
            raise ValidationError("2FA secret not found. Please generate a new secret.")
        
        # Decrypt secret
        try:
            decrypted_secret = self._decrypt(user.two_factor_secret)
        except Exception as e:
            logger.error(f"Failed to decrypt 2FA secret for user {user_id}: {e}")
            raise ValidationError("Invalid 2FA secret. Please generate a new one.")
        
        # Verify code
        totp = pyotp.TOTP(decrypted_secret)
        if not totp.verify(code, valid_window=1):  # Allow 1 time step window
            logger.warning(f"Invalid 2FA setup code for user {user_id}")
            return False
        
        # Generate backup codes
        backup_codes = self._generate_backup_codes()
        encrypted_backup_codes = self._encrypt(json.dumps(backup_codes))
        
        # Complete setup
        user.two_factor_enabled = True
        user.two_factor_verified = True
        user.two_factor_backup_codes = encrypted_backup_codes
        self.db.commit()
        
        logger.info(f"2FA setup completed for user {user_id}")
        
        return True
    
    def _generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for account recovery"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_urlsafe(6).upper().replace('-', '').replace('_', '')[:8]
            codes.append(code)
        return codes
    
    def verify_code(self, user_id: int, code: str, allow_backup: bool = True) -> bool:
        """
        Verify 2FA code during login
        
        Args:
            user_id: User ID
            code: 6-digit TOTP code or backup code
            allow_backup: Whether to allow backup codes
            
        Returns:
            True if verification successful
        """
        if not PYOTP_AVAILABLE:
            raise ValidationError("2FA libraries not installed")
        
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError('User')
        
        if not user.two_factor_enabled or not user.two_factor_verified:
            raise ValidationError("2FA is not enabled for this user")
        
        if not user.two_factor_secret:
            raise ValidationError("2FA secret not found")
        
        # Check if it's a backup code
        if allow_backup and user.two_factor_backup_codes:
            try:
                decrypted_backup_codes = self._decrypt(user.two_factor_backup_codes)
                backup_codes = json.loads(decrypted_backup_codes)
                
                if code in backup_codes:
                    # Remove used backup code
                    backup_codes.remove(code)
                    if backup_codes:
                        encrypted_backup_codes = self._encrypt(json.dumps(backup_codes))
                        user.two_factor_backup_codes = encrypted_backup_codes
                    else:
                        user.two_factor_backup_codes = None
                    self.db.commit()
                    logger.info(f"Backup code used for user {user_id}")
                    return True
            except Exception as e:
                logger.warning(f"Error checking backup codes: {e}")
        
        # Verify TOTP code
        try:
            decrypted_secret = self._decrypt(user.two_factor_secret)
        except Exception as e:
            logger.error(f"Failed to decrypt 2FA secret: {e}")
            return False
        
        totp = pyotp.TOTP(decrypted_secret)
        # Allow 1 time step window (30 seconds before/after) for clock drift
        is_valid = totp.verify(code, valid_window=1)
        
        if is_valid:
            logger.info(f"2FA code verified for user {user_id}")
        else:
            logger.warning(f"Invalid 2FA code for user {user_id}")
        
        return is_valid
    
    def get_backup_codes(self, user_id: int) -> List[str]:
        """
        Get backup codes for user (decrypted)
        
        Args:
            user_id: User ID
            
        Returns:
            List of backup codes
        """
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError('User')
        
        if not user.two_factor_backup_codes:
            return []
        
        try:
            decrypted = self._decrypt(user.two_factor_backup_codes)
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt backup codes: {e}")
            return []
    
    def regenerate_backup_codes(self, user_id: int) -> List[str]:
        """
        Regenerate backup codes for user
        
        Args:
            user_id: User ID
            
        Returns:
            List of new backup codes
        """
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError('User')
        
        if not user.two_factor_enabled:
            raise ValidationError("2FA is not enabled")
        
        backup_codes = self._generate_backup_codes()
        encrypted_backup_codes = self._encrypt(json.dumps(backup_codes))
        
        user.two_factor_backup_codes = encrypted_backup_codes
        self.db.commit()
        
        logger.info(f"Backup codes regenerated for user {user_id}")
        
        return backup_codes
    
    def disable_2fa(self, user_id: int) -> bool:
        """
        Disable 2FA for user
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        user = self.db.query(User).filter(User.uid == user_id).first()
        if not user:
            raise NotFoundError('User')
        
        user.two_factor_enabled = False
        user.two_factor_verified = False
        user.two_factor_secret = None
        user.two_factor_backup_codes = None
        self.db.commit()
        
        logger.info(f"2FA disabled for user {user_id}")
        
        return True
