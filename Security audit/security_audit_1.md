# ZedReq Security Audit — Report #1

**Date:** 2026-04-09  
**Scope:** All FastAPI backend routes, authentication layer, middleware, and configuration  
**Auditor:** Internal security review  

---

## Executive Summary

A full review of ZedReq's API surface, authentication flow, middleware, and configuration was conducted. **17 security gaps** were identified across four severity levels.

The two most critical issues require immediate attention before any production deployment:

1. **Google/Firebase ID tokens are accepted without cryptographic signature verification.** Any attacker can craft a fake token containing a victim's email address and receive a fully valid ZedReq session — a complete authentication bypass.
2. **Passwords are hashed with plain SHA-256**, which a modern GPU can attack at billions of hashes per second. A database breach would result in near-total password exposure.

Beyond these, the login endpoint has no brute-force protection, system metrics are publicly exposed without authentication, and JWT tokens cannot be revoked on logout — all HIGH severity gaps that compound the risk.

---

## Severity Overview

| Severity | Count |
|----------|-------|
| 🔴 Critical | 2 |
| 🟠 High | 4 |
| 🟡 Medium | 7 |
| 🟢 Low | 4 |
| **Total** | **17** |

---

## Gap List

---

### 🔴 CRITICAL — GAP-01: Firebase/Google JWT accepted without signature verification

**File:** `backend/services/auth_service.py` — `verify_google_token()`, ~line 447  
**Endpoint:** `POST /api/auth/google`

The Firebase ID token is decoded by splitting the JWT on `.` and base64-decoding the payload. The cryptographic signature (third segment) is **never validated** against Firebase's public keys. The code comment reads: *"Decode the JWT token (without verification for simplicity)"*.

**Impact:** Full account takeover. An attacker crafts a fake JWT with `"email": "victim@example.com"` in the payload, signs it with any garbage bytes, and receives a valid ZedReq access + refresh token for the victim's account.

**Fix:** Use the Firebase Admin SDK:
```python
from firebase_admin import auth as firebase_auth
decoded = firebase_auth.verify_id_token(id_token)  # validates RS256 signature
google_email = decoded["email"]
```

---

### 🔴 CRITICAL — GAP-02: Passwords hashed with SHA-256, not a memory-hard algorithm

**File:** `backend/services/auth_service.py` — `hash_password()`, ~line 24  

New user registrations store passwords as `sha256$<salt>$<hex>`. SHA-256 is a general-purpose hash function computing at ~10 billion hashes/second on a consumer GPU. This makes offline brute-force attacks trivially fast after any database breach.

**Impact:** Near-complete password exposure in the event of a DB leak.

**Fix:** Switch to `bcrypt` (cost factor 12) or `argon2id` via `passlib`. The existing `verify_password()` already handles legacy `pbkdf2` and `scrypt` formats, so migration is non-breaking.

---

### 🟠 HIGH — GAP-03: No rate limiting on login endpoint — unlimited brute force

**File:** `backend/routers/auth.py` — `login()`, ~line 56  
**Endpoint:** `POST /api/auth/login`

The login route has no rate limit. All existing rate-limit dependencies (`write_rate_limit`, `sensitive_rate_limit`) require a valid JWT first and cannot protect unauthenticated endpoints.

**Impact:** Unlimited password-guessing attacks against any known username.

**Fix:** Add an IP-keyed sliding-window rate limiter (e.g. 10 attempts per IP per 5 minutes) applied before credential validation. Same fix needed for `POST /api/auth/register` and `POST /api/auth/refresh`.

---

### 🟠 HIGH — GAP-04: Monitoring endpoints publicly accessible without authentication

**File:** `backend/routers/monitoring.py`  
**Endpoints:** `GET /api/monitoring/health`, `GET /api/monitoring/metrics`, `GET /api/monitoring/stats`

All three endpoints require zero authentication. `/api/monitoring/metrics` returns real-time CPU percentage, memory used/total/available, disk used/total/free, and CPU core count.

**Impact:** Attackers gain detailed server resource information useful for timing attacks, capacity fingerprinting, and identifying hosting provider limits.

**Fix:** Add `current_user: dict = Depends(get_current_user)` to each route, or restrict the entire router to an internal/admin key.

---

### 🟠 HIGH — GAP-05: JWT revocation not implemented — logout is cosmetic

**File:** `backend/routers/auth.py` — `logout()`, ~line 210  

Logout only schedules a background context refresh. The issued tokens (access token: configurable TTL, refresh token: multi-day TTL) remain cryptographically valid for their full lifetime after logout.

**Impact:** A user who logs out after suspecting account compromise is still fully exposed via the stolen token.

**Fix:** Generate a `jti` (JWT ID) claim on every issued token. On logout, add the `jti` to a denylist (Redis TTL set or DB table). Check the denylist in `verify_token()`.

---

### 🟠 HIGH — GAP-06: Register and refresh endpoints have no rate limiting

**File:** `backend/routers/auth.py`  
**Endpoints:** `POST /api/auth/register`, `POST /api/auth/refresh`

No throttle exists on account creation (allows account spam, username/email enumeration at scale, resource exhaustion) or token refresh (allows a stolen refresh token to be kept alive indefinitely with no alarm).

**Fix:** Apply IP-based rate limiting as described in GAP-03. For refresh specifically, also consider binding refresh tokens to a device fingerprint or IP range.

---

### 🟡 MEDIUM — GAP-07: 2FA backup codes readable and 2FA disableable without password re-check

**File:** `backend/routers/user.py`  
**Endpoints:** `GET /api/user/2fa/backup-codes`, `DELETE /api/user/2fa`

Both actions require only a valid access token. If an access token is stolen (XSS, compromised device, network intercept), an attacker can immediately read backup codes and permanently disable 2FA — eliminating the second factor entirely.

**Fix:** Require current-password verification in the request body for both endpoints before proceeding.

---

### 🟡 MEDIUM — GAP-08: Profile description update accepts raw unvalidated dictionary

**File:** `backend/routers/user.py` — `update_profile_description()`, ~line 631  
**Endpoint:** `PUT /api/user/profile/description`

The request body type is `Dict[str, Any]` — no Pydantic schema. The raw dict is passed directly to `ProfileService.update_profile()`. A user can submit arbitrary field names, potentially including server-controlled fields (`email_verified`, `role`, `two_factor_enabled`, etc.), relying solely on the service layer to reject them.

**Fix:** Define an explicit `ProfileDescriptionUpdate` Pydantic model with an allowlist of updatable fields (`short_desc`, `about`, `skills`, `certificates`, `current_status`, etc.).

---

### 🟡 MEDIUM — GAP-09: Rate limiters are in-memory and not distributed

**File:** `backend/dependencies/rate_limit.py` and multiple routers  

All `RateLimiter` instances are Python `defaultdict` objects held in process memory. In a multi-worker deployment (Gunicorn, multiple Uvicorn workers), each worker maintains its own independent counter — the effective limit is `requests_per_minute × worker_count`. Limits also reset on every restart or deploy.

**Fix:** Replace the in-memory store with a Redis-backed sliding window counter. Libraries like `fastapi-limiter` provide a drop-in solution.

---

### 🟡 MEDIUM — GAP-10: Paddle webhook replay window is 1 hour

**File:** `backend/config/settings.py` line 112  
**Setting:** `PADDLE_WEBHOOK_MAX_AGE_SECONDS = 3600`

Paddle recommends validating that the `ts` claim in the `Paddle-Signature` header is within ~5 seconds of the current time. A 1-hour window allows a captured webhook (e.g. `subscription.activated`) to be replayed up to 3600 times within the window.

**Fix:** Change the default to `30` seconds. This matches Paddle's documented best practice.

---

### 🟡 MEDIUM — GAP-11: CSP contains `unsafe-inline` and `unsafe-eval`

**File:** `backend/middleware/security_headers.py`, ~line 153  

The `Content-Security-Policy` header includes `'unsafe-inline'` in `script-src` and `style-src`, and `'unsafe-eval'` in `script-src`. These directives largely defeat the XSS protections that CSP is designed to provide.

**Fix:** Migrate to nonce-based CSP (`'nonce-{random-per-request}'`) for inline scripts. Audit and eliminate `eval()` usage in the frontend to allow removing `unsafe-eval`.

---

### 🟡 MEDIUM — GAP-12: No HTTP Strict-Transport-Security (HSTS) header

**File:** `backend/middleware/security_headers.py`  

The security headers middleware sets X-Frame-Options, X-Content-Type-Options, and others, but omits `Strict-Transport-Security`. Without HSTS, browsers may silently downgrade the first request to HTTP, enabling MITM and cookie-theft attacks.

**Fix:** Add to the middleware:
```python
response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
```

---

### 🟡 MEDIUM — GAP-13: `expose_headers: ["*"]` leaks all response headers to browsers

**File:** `backend/main.py` — CORS configuration, line 329  

`expose_headers=["*"]` instructs the browser to expose every response header to cross-origin JavaScript. Internal headers such as rate-limit counters, internal tracing IDs, and server version details become readable by any frontend.

**Fix:** Replace with an explicit allowlist:
```python
expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Retry-After"]
```

---

### 🟢 LOW — GAP-14: Internal error details surfaced in Google auth failure response

**File:** `backend/services/auth_service.py` ~line 579  

The final catch block raises `ValueError(f'Google authentication failed: {str(e)}')`, embedding the raw Python exception message in the HTTP 401 response body. DB errors, connection strings, or library internals can leak.

**Fix:** Raise a static `ValueError("Google authentication failed")` without embedding `str(e)`.

---

### 🟢 LOW — GAP-15: Password maximum length capped at 25 characters

**File:** `backend/services/auth_service.py` — `validate_password_strength()`, ~line 84  

A 25-character hard cap narrows the brute-force keyspace and signals to sophisticated attackers that passwords are not properly hashed (bcrypt naturally handles up to 72 characters).

**Fix:** After switching to bcrypt (GAP-02), raise the cap to 72 characters.

---

### 🟢 LOW — GAP-16: Username and email enumerable via distinct registration errors

**File:** `backend/services/auth_service.py` — `register()`, ~lines 189–199  

Registration returns `"Username already exists"` or `"Email already exists"` as separate, distinct error messages, allowing an attacker to enumerate the entire user base by username and email without authenticating.

**Fix:** Return a single generic message: `"An account with this username or email already exists"`.

---

### 🟢 LOW — GAP-17: `server_origins` variable defined but never used

**File:** `backend/main.py` line 334  

```python
server_origins = cors_origins + ["http://localhost:5000", "http://localhost:5173"]
```

This variable is assigned but referenced nowhere in the file. It was likely intended for the CORS exception handlers but was never wired in.

**Fix:** Remove the dead variable or complete the intended logic.

---

## Recommended Fix Priority

| Priority | Gaps | Action |
|----------|------|--------|
| Immediate (pre-launch blocker) | GAP-01, GAP-02 | Firebase token verification; replace SHA-256 with bcrypt |
| This sprint | GAP-03, GAP-04, GAP-05, GAP-06 | Login rate limiting; auth monitoring endpoints; JWT revocation |
| Next sprint | GAP-07, GAP-08, GAP-09, GAP-10, GAP-11, GAP-12, GAP-13 | 2FA hardening; schema validation; Redis rate limiting; CSP/HSTS |
| Backlog | GAP-14, GAP-15, GAP-16, GAP-17 | Error leakage; password length; enum protection; dead code |

---

*End of Report #1*
