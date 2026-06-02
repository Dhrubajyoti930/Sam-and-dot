"""
Resilient Gemini API wrapper with retry logic and error handling.
"""
import time
import logging
import json
from functools import wraps

logger = logging.getLogger(__name__)

def gemini_call_resilient(max_retries=3, backoff_factor=2):
    """Decorator for resilient Gemini API calls."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    err_str = str(e).upper()
                    # Only retry on transient errors
                    if any(x in err_str for x in ["429", "500", "503", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "QUOTA"]):
                        if attempt < max_retries - 1:
                            wait_time = backoff_factor ** attempt
                            logger.warning(
                                f"Attempt {attempt + 1}/{max_retries} failed: {e}. "
                                f"Retrying in {wait_time}s..."
                            )
                            time.sleep(wait_time)
                            continue

                    logger.error(f"Call failed: {e}")
                    raise e
            raise last_error
        return wrapper
    return decorator

def validate_gemini_response(response, expected_type='text') -> str:
    """Validate Gemini response before processing."""
    try:
        if not response:
            raise ValueError("Empty response from Gemini")

        if expected_type == 'text':
            if hasattr(response, 'text'):
                return response.text
            elif isinstance(response, str):
                return response
            else:
                raise ValueError(f"Unexpected response type: {type(response)}")

        elif expected_type == 'json':
            text = response.text if hasattr(response, 'text') else str(response)
            # Basic cleanup if it's markdown-wrapped
            if isinstance(text, str):
                text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(text)

    except Exception as e:
        logger.error(f"Invalid Gemini response: {e}")
        raise ValueError(f"Could not validate Gemini response: {e}")
