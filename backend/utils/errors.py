"""Custom exception classes"""

class AppError(Exception):
    """Base application error"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str = "Validation failed", errors: list = None):
        super().__init__(message, 400)
        self.errors = errors or []

class AuthenticationError(AppError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)

class AuthorizationError(AppError):
    """Authorization error"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, 403)

class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", 404)

class ConflictError(AppError):
    """Resource conflict error"""
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409)


class GoogleSignInNoAccountError(AppError):
    """Google sign-in (login intent): no ZedReq user for that email."""
    def __init__(
        self,
        message: str = (
            "No ZedReq account is registered for this Google email. "
            "Please create an account first (use Sign up)."
        ),
    ):
        super().__init__(message, 404)
