"""Post validators"""
from utils.errors import ValidationError

def validate_create_post(data: dict) -> dict:
    """Validate post creation data"""
    errors = []
    
    content = data.get('content', '').strip()
    
    if not content:
        errors.append('Content cannot be empty')
    elif len(content) > 5000:
        errors.append('Content cannot exceed 5000 characters')
    
    if errors:
        raise ValidationError('Validation failed', errors)
    
    return {'content': content}

def validate_update_post(data: dict) -> dict:
    """Validate post update data"""
    return validate_create_post(data)
