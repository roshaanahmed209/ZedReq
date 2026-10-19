"""Two-Factor Authentication Schemas"""
from pydantic import BaseModel, Field


class TwoFactorSetupResponse(BaseModel):
    """2FA setup response with QR code"""
    secret: str
    qr_code: str
    manual_entry_key: str
    provisioning_uri: str


class TwoFactorVerifySetup(BaseModel):
    """Verify 2FA setup code"""
    code: str = Field(..., min_length=6, max_length=6, description="6-digit TOTP code")


class TwoFactorVerify(BaseModel):
    """Verify 2FA code during login"""
    code: str = Field(..., min_length=6, max_length=8, description="6-digit TOTP code or 8-character backup code")
    temp_token: str = Field(..., description="Temporary token from login response")


class TwoFactorBackupCodesResponse(BaseModel):
    """Backup codes response"""
    backup_codes: list[str]
    message: str


class TwoFactorStatusResponse(BaseModel):
    """2FA status response"""
    enabled: bool
    verified: bool
    has_backup_codes: bool
