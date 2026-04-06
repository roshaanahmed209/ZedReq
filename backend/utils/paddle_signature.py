"""Verify Paddle Billing webhook `Paddle-Signature` header (HMAC-SHA256)."""
from __future__ import annotations

import hashlib
import hmac
import time
from typing import Optional


def _parse_signature_header(header: str) -> tuple[Optional[int], Optional[str]]:
    if not header:
        return None, None
    ts = None
    sig = None
    for part in header.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k, v = k.strip(), v.strip()
        if k == "ts":
            try:
                ts = int(v)
            except ValueError:
                ts = None
        elif k == "h1":
            sig = v
    return ts, sig


def verify_paddle_signature(
    raw_body: bytes,
    paddle_signature_header: Optional[str],
    secret: str,
    max_age_seconds: int = 3600,
) -> bool:
    """
    Returns True if the signature matches Paddle's algorithm:
    HMAC_SHA256(secret, f"{ts}:{raw_body.decode('utf-8')}") compared to h1.

    raw_body must be the exact bytes received (no re-encoding).
    """
    if not secret or not paddle_signature_header or raw_body is None:
        return False
    ts, h1 = _parse_signature_header(paddle_signature_header)
    if ts is None or not h1:
        return False
    now = int(time.time())
    if abs(now - ts) > max_age_seconds:
        return False
    try:
        body_text = raw_body.decode("utf-8")
    except UnicodeDecodeError:
        return False
    signed_payload = f"{ts}:{body_text}".encode("utf-8")
    expected = hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()
    try:
        return hmac.compare_digest(expected, h1)
    except TypeError:
        return False
