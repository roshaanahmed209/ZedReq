"""Post validators"""
from utils.errors import ValidationError

def validate_create_post(data: dict) -> dict:
    """Validate post creation data"""
    errors = []
    
    content = data.get('content', '').strip()
    media_url = data.get('media_url')
    media_type = data.get('media_type')
    
    # Post must have content OR media
    if not content and not media_url:
        errors.append('Post must have content or media')
    elif content and len(content) > 5000:
        errors.append('Content cannot exceed 5000 characters')
    
    # Validate media_type if media_url is provided
    if media_url and media_type not in [None, 'image', 'video']:
        errors.append("media_type must be 'image' or 'video'")
    
    if errors:
        raise ValidationError('Validation failed', errors)
    
    return {
        'content': content,
        'media_url': media_url,
        'media_type': media_type
    }

def validate_update_post(data: dict) -> dict:
    """Validate post update data"""
    return validate_create_post(data)
