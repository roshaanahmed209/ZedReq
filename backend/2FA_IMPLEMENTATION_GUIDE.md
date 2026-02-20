# Two-Factor Authentication (2FA) Implementation Guide

## Overview

This document explains how the complete 2FA (Two-Factor Authentication) system works in ZedRec, using TOTP (Time-based One-Time Password) with authenticator apps like Google Authenticator, Authy, or Microsoft Authenticator.

## Architecture

### Components

1. **Database Schema** (`users` table):
   - `two_factor_enabled` (BOOLEAN) - Whether 2FA is enabled
   - `two_factor_secret` (TEXT) - Encrypted TOTP secret
   - `two_factor_backup_codes` (TEXT) - Encrypted JSON array of backup codes
   - `two_factor_verified` (BOOLEAN) - Whether 2FA setup is complete

2. **Backend Services**:
   - `TwoFactorService` - Handles TOTP generation, QR codes, verification
   - `AuthService` - Modified login flow to check 2FA

3. **API Endpoints**:
   - Setup endpoints (generate secret, verify setup)
   - Verification endpoints (login verification)
   - Management endpoints (backup codes, disable)

4. **Frontend**:
   - Settings page - 2FA setup and management
   - Login page - 2FA verification during login

## How It Works

### 1. 2FA Setup Flow

```
User clicks "Enable 2FA" in Settings
    ↓
POST /api/user/2fa/setup
    ↓
Backend generates TOTP secret
    ↓
Backend generates QR code
    ↓
Frontend displays QR code
    ↓
User scans QR code with authenticator app
    ↓
User enters 6-digit code from app
    ↓
POST /api/user/2fa/verify-setup
    ↓
Backend verifies code
    ↓
Backend generates backup codes
    ↓
2FA enabled and verified
```

### 2. Login Flow with 2FA

```
User enters username/password
    ↓
POST /api/auth/login
    ↓
Backend verifies password
    ↓
Backend checks two_factor_enabled
    ↓
If 2FA enabled:
    - Returns temp_token (5-minute validity)
    - Returns requires_2fa: true
    ↓
Frontend shows 2FA code input
    ↓
User enters 6-digit code from app
    ↓
POST /api/auth/2fa/verify
    ↓
Backend verifies TOTP code
    ↓
If valid:
    - Returns full access_token and refresh_token
    - Login complete
```

### 3. Backup Codes

- Generated during 2FA setup
- 10 codes, 8 characters each
- Each code can only be used once
- Can be regenerated (invalidates old codes)
- Stored encrypted in database

## Security Features

### 1. Encryption
- **Secret Storage**: TOTP secrets are encrypted using Fernet (symmetric encryption)
- **Backup Codes**: Stored encrypted in database
- **Encryption Key**: Set via `2FA_ENCRYPTION_KEY` environment variable

### 2. Token Security
- **Temporary Tokens**: Short-lived (5 minutes) for 2FA verification
- **JWT-based**: Uses same JWT system as regular authentication
- **Type Validation**: Tokens have type field to prevent misuse

### 3. Code Verification
- **Time Window**: Allows 1 time step (30 seconds) before/after for clock drift
- **Backup Code Support**: Can use backup codes if authenticator unavailable
- **Rate Limiting**: Sensitive operations rate-limited (5 requests/minute)

### 4. Input Validation
- **Code Format**: 6 digits for TOTP, 8 characters for backup codes
- **Length Validation**: Enforced at multiple layers
- **Sanitization**: All inputs sanitized

## API Endpoints

### Setup Endpoints

#### `POST /api/user/2fa/setup`
Generate 2FA secret and QR code.

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "manual_entry_key": "JBSWY3DPEHPK3PXP",
  "provisioning_uri": "otpauth://totp/..."
}
```

#### `POST /api/user/2fa/verify-setup`
Verify setup code and complete 2FA enablement.

**Request:**
```json
{
  "code": "123456"
}
```

**Response:**
```json
{
  "message": "2FA enabled successfully",
  "backup_codes": ["ABC12345", "DEF67890", ...]
}
```

### Verification Endpoints

#### `POST /api/auth/2fa/verify`
Verify 2FA code during login.

**Request:**
```json
{
  "temp_token": "eyJ...",
  "code": "123456"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}
```

### Management Endpoints

#### `GET /api/user/2fa/status`
Get 2FA status for current user.

**Response:**
```json
{
  "enabled": true,
  "verified": true,
  "has_backup_codes": true
}
```

#### `GET /api/user/2fa/backup-codes`
Get backup codes (decrypted).

**Response:**
```json
{
  "backup_codes": ["ABC12345", "DEF67890", ...],
  "message": "Store these codes in a safe place..."
}
```

#### `POST /api/user/2fa/regenerate-backup-codes`
Regenerate backup codes (invalidates old ones).

**Response:**
```json
{
  "backup_codes": ["NEW12345", "NEW67890", ...],
  "message": "New backup codes generated..."
}
```

#### `DELETE /api/user/2fa`
Disable 2FA for current user.

**Response:**
```json
{
  "message": "2FA disabled successfully"
}
```

## Database Migration

Run the migration script to add 2FA columns:

```bash
python backend/db/migrations/add_2fa_columns.py
```

Or manually:

```sql
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS two_factor_secret TEXT,
ADD COLUMN IF NOT EXISTS two_factor_backup_codes TEXT,
ADD COLUMN IF NOT EXISTS two_factor_verified BOOLEAN DEFAULT FALSE;
```

## Environment Variables

Add to `.env`:

```bash
# 2FA Configuration
2FA_ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
2FA_ISSUER_NAME=ZedRec  # Optional, defaults to "ZedRec"
```

## Installation

Install required packages:

```bash
pip install pyotp qrcode[pil] cryptography
```

Or add to `requirements.txt` (already added):
```
pyotp>=2.9.0
qrcode[pil]>=7.4.2
cryptography>=41.0.0
```

## Usage Examples

### Enabling 2FA

1. User goes to Settings → Security
2. Clicks "Enable 2FA"
3. Scans QR code with authenticator app
4. Enters 6-digit code to verify
5. Saves backup codes

### Logging In with 2FA

1. User enters username/password
2. If 2FA enabled, sees 2FA code input
3. Opens authenticator app
4. Enters 6-digit code
5. Login completes

### Using Backup Codes

If user loses access to authenticator app:
1. During login, enter backup code instead of TOTP code
2. Code is validated and removed (single-use)
3. User should regenerate codes after use

## Security Best Practices

1. **Encryption Key**: Store `2FA_ENCRYPTION_KEY` securely, never commit to git
2. **Backup Codes**: Users should store backup codes securely (password manager)
3. **Rate Limiting**: All 2FA endpoints are rate-limited
4. **Token Expiry**: Temporary tokens expire in 5 minutes
5. **Code Validation**: TOTP codes validated with time window for clock drift
6. **Single-Use Backup Codes**: Backup codes removed after use

## Troubleshooting

### QR Code Not Scanning
- Use manual entry key instead
- Ensure authenticator app supports TOTP
- Check QR code is fully visible

### Code Not Working
- Check device time is synchronized
- Try code from next 30-second window
- Verify 2FA is properly enabled

### Lost Authenticator Access
- Use backup codes to login
- Regenerate backup codes after login
- Disable and re-enable 2FA if no backup codes

## Testing

### Manual Testing

1. **Setup Flow**:
   - Enable 2FA
   - Scan QR code
   - Verify with code
   - Check backup codes generated

2. **Login Flow**:
   - Login with 2FA enabled
   - Enter TOTP code
   - Verify login succeeds

3. **Backup Codes**:
   - Use backup code during login
   - Verify code is removed after use
   - Regenerate codes

### Test Cases

- ✅ 2FA setup with valid code
- ✅ 2FA setup with invalid code
- ✅ Login with 2FA enabled
- ✅ Login with invalid 2FA code
- ✅ Login with backup code
- ✅ Backup code single-use enforcement
- ✅ Disable 2FA
- ✅ Regenerate backup codes

## Future Enhancements

- [ ] SMS-based 2FA (alternative to TOTP)
- [ ] Email-based 2FA codes
- [ ] Recovery email for 2FA reset
- [ ] 2FA device management (multiple devices)
- [ ] Remember device option (30-day bypass)
- [ ] 2FA activity log
