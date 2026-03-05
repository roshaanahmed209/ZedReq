"""User validators"""
from utils.errors import ValidationError

def validate_user_search(query: str) -> str:
    """Validate user search query"""
    if not query or not isinstance(query, str):
        return ''
    return query.strip()

def validate_user_update(data: dict) -> dict:
    """Validate user update data"""
    errors = []
    allowed_fields = ['full_name', 'headline', 'bio', 'avatar']
    update_data = {}
    
    for key, value in data.items():
        if key in allowed_fields and value is not None:
            if isinstance(value, str):
                update_data[key] = value.strip()
                
                # Field-specific validations
                if key == 'full_name' and len(update_data[key]) > 100:
                    errors.append('Full name cannot exceed 100 characters')
                elif key == 'headline' and len(update_data[key]) > 200:
                    errors.append('Headline cannot exceed 200 characters')
                elif key == 'bio' and len(update_data[key]) > 1000:
                    errors.append('Bio cannot exceed 1000 characters')
            else:
                update_data[key] = value
    
    if errors:
        raise ValidationError('Validation failed', errors)
    
    return update_data
