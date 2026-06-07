from pydantic import ValidationError
from functools import wraps

def validate_tool_call(model, max_retries=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                validated_data = model(**kwargs)
                return func(*args, **validated_data.dict())
            except ValidationError as e:
                return {"error": "Schema validation failed", "details": str(e)}
        return wrapper
    return decorator