"""Helpers for creating main ZedReq app users from the backoffice (not backoffice admins)."""
import re
import secrets
import string
from werkzeug.security import generate_password_hash

# Must match backend/utils/auth.py in the main ZedReq app
PASSWORD_HASH_METHOD = "pbkdf2:sha256:600000"

RESERVED_USERNAMES = frozenset(
    {"admin", "root", "system", "api", "null", "undefined"}
)
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def hash_main_app_password(password: str) -> str:
    return generate_password_hash(password, method=PASSWORD_HASH_METHOD)


def validate_main_app_email(email: str) -> bool:
    return bool(email and _EMAIL_RE.match(email) and len(email) <= 150)


def generate_random_password(length: int = 16) -> str:
    """Random password satisfying main app rules: 8+, upper, lower, digit."""
    length = max(8, min(length, 128))
    upper = secrets.choice(string.ascii_uppercase)
    lower = secrets.choice(string.ascii_lowercase)
    digit = secrets.choice(string.digits)
    alphabet = string.ascii_letters + string.digits
    rest = "".join(secrets.choice(alphabet) for _ in range(length - 3))
    chars = list(upper + lower + digit + rest)
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def _int_to_base36(n: int) -> str:
    if n == 0:
        return "0"
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = ""
    while n > 0:
        result = chars[n % 36] + result
        n //= 36
    return result


def hash_user_id(user_id: int) -> str | None:
    if not user_id or not isinstance(user_id, int):
        return None
    encoded = _int_to_base36(user_id)
    hash_value = (user_id * 7919) % 46656
    hash_part = _int_to_base36(hash_value).zfill(3)
    return f"{hash_part}{encoded}"[:8]


def generate_profile_path(user_id: int, username: str) -> str | None:
    """Same path format as main app utils/profile_url.generate_profile_path."""
    if not user_id or not username:
        return None
    hashed_id = hash_user_id(user_id)
    if not hashed_id:
        return None
    sanitized = username.lower().replace(" ", "-")
    sanitized = "".join(c for c in sanitized if c.isalnum() or c in ("-", "_"))
    sanitized = sanitized.strip("-").strip("_")
    if not sanitized:
        return None
    return f"/profile/{sanitized}-{hashed_id}"


def sanitize_username_base(local_part: str) -> str:
    s = local_part.lower()
    s = re.sub(r"[^a-zA-Z0-9_-]", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        return "user"
    if not s[0].isalpha():
        s = "u_" + s
    return s[:50]


def is_valid_username_shape(username: str) -> bool:
    if len(username) < 3 or len(username) > 50:
        return False
    if username.lower() in RESERVED_USERNAMES:
        return False
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", username))
