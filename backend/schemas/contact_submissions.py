"""Pydantic schemas for contact form submissions."""
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional


class ContactSubmitRequest(BaseModel):
    """User-facing request to submit a contact/support message."""
    submission_type: str = Field(..., pattern="^(help|enterprise)$")
    subject: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=5000)
    extra: Optional[Dict[str, Any]] = None
