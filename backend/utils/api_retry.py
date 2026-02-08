"""
API Retry Utilities
Retry logic with exponential backoff for API calls
"""
import os
import time
import logging
from typing import Callable, Any, Optional, Type, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class RetryableError(Exception):
    """Base class for retryable errors"""
    pass


class NonRetryableError(Exception):
    """Base class for non-retryable errors"""
    pass


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable
    
    Args:
        error: Exception to check
    
    Returns:
        True if error is retryable, False otherwise
    """
    error_str = str(error).lower()
    error_type = type(error).__name__.lower()
    
    # HTTP status codes that are retryable
    retryable_status_codes = [429, 500, 502, 503, 504]
    
    # Check for status codes in error message
    for code in retryable_status_codes:
        if f"status {code}" in error_str or f"{code}" in error_str:
            return True
    
    # Check for specific error types
    retryable_keywords = [
        'timeout', 'connection', 'network', 'rate limit',
        'too many requests', 'service unavailable', 'bad gateway',
        'gateway timeout', 'internal server error'
    ]
    
    for keyword in retryable_keywords:
        if keyword in error_str:
            return True
    
    # Non-retryable errors
    non_retryable_keywords = [
        'authentication', 'authorization', 'forbidden', 'not found',
        'bad request', 'invalid', 'malformed'
    ]
    
    for keyword in non_retryable_keywords:
        if keyword in error_str:
            return False
    
    # Default: retry on unknown errors (conservative approach)
    return True


def exponential_backoff(
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    multiplier: float = 2.0,
    jitter: bool = True
) -> Callable[[int], float]:
    """
    Generate exponential backoff delay function
    
    Args:
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        multiplier: Multiplier for each retry
        jitter: Add random jitter to prevent thundering herd
    
    Returns:
        Function that takes attempt number and returns delay
    """
    import random
    
    def calculate_delay(attempt: int) -> float:
        delay = min(base_delay * (multiplier ** (attempt - 1)), max_delay)
        
        if jitter:
            # Add up to 25% random jitter
            jitter_amount = delay * 0.25 * random.random()
            delay += jitter_amount
        
        return delay
    
    return calculate_delay


def retry_with_backoff(
    max_retries: Optional[int] = None,
    base_delay: Optional[float] = None,
    max_delay: Optional[float] = None,
    multiplier: Optional[float] = None,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying function calls with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts (from env if not provided)
        base_delay: Base delay in seconds (from env if not provided)
        max_delay: Maximum delay in seconds (from env if not provided)
        multiplier: Exponential backoff multiplier (from env if not provided)
        retryable_exceptions: Tuple of exception types to retry on
        on_retry: Callback function called on each retry (exception, attempt_number)
    
    Usage:
        @retry_with_backoff(max_retries=3)
        def api_call():
            # API call code
            pass
    """
    # Get defaults from environment
    if max_retries is None:
        max_retries = int(os.environ.get('API_MAX_RETRIES', 3))
    if base_delay is None:
        base_delay = float(os.environ.get('API_RETRY_BASE_DELAY', 1.0))
    if max_delay is None:
        max_delay = float(os.environ.get('API_RETRY_MAX_DELAY', 60.0))
    if multiplier is None:
        multiplier = float(os.environ.get('API_RETRY_MULTIPLIER', 2.0))
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay_calculator = exponential_backoff(base_delay, max_delay, multiplier)
            
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except Exception as e:
                    last_exception = e
                    
                    # Check if exception is retryable
                    if retryable_exceptions:
                        if not isinstance(e, retryable_exceptions):
                            logger.debug(f"{func.__name__}: Non-retryable exception {type(e).__name__}: {e}")
                            raise
                    elif not is_retryable_error(e):
                        logger.debug(f"{func.__name__}: Non-retryable error: {e}")
                        raise
                    
                    # Check if we've exhausted retries
                    if attempt >= max_retries:
                        logger.warning(
                            f"{func.__name__}: Max retries ({max_retries}) exceeded. "
                            f"Last error: {type(e).__name__}: {e}"
                        )
                        raise
                    
                    # Calculate delay and wait
                    delay = delay_calculator(attempt)
                    logger.info(
                        f"{func.__name__}: Retry {attempt}/{max_retries} after {delay:.2f}s. "
                        f"Error: {type(e).__name__}: {str(e)[:100]}"
                    )
                    
                    if on_retry:
                        try:
                            on_retry(e, attempt)
                        except Exception as callback_error:
                            logger.warning(f"Error in retry callback: {callback_error}")
                    
                    time.sleep(delay)
            
            # Should never reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__}: Unexpected retry loop exit")
        
        return wrapper
    return decorator


def retry_api_call(
    func: Callable,
    max_retries: Optional[int] = None,
    base_delay: Optional[float] = None,
    **kwargs
) -> Any:
    """
    Retry an API call function with exponential backoff
    
    Args:
        func: Function to retry
        max_retries: Maximum retry attempts
        base_delay: Base delay for backoff
        **kwargs: Additional arguments to pass to func
    
    Returns:
        Result of function call
    
    Usage:
        result = retry_api_call(api_function, max_retries=3, param1=value1)
    """
    if max_retries is None:
        max_retries = int(os.environ.get('API_MAX_RETRIES', 3))
    if base_delay is None:
        base_delay = float(os.environ.get('API_RETRY_BASE_DELAY', 1.0))
    
    last_exception = None
    delay_calculator = exponential_backoff(base_delay)
    
    for attempt in range(1, max_retries + 1):
        try:
            return func(**kwargs)
        except Exception as e:
            last_exception = e
            
            if not is_retryable_error(e):
                logger.debug(f"Non-retryable error in {func.__name__}: {e}")
                raise
            
            if attempt >= max_retries:
                logger.warning(f"{func.__name__}: Max retries exceeded. Error: {e}")
                raise
            
            delay = delay_calculator(attempt)
            logger.info(f"{func.__name__}: Retry {attempt}/{max_retries} after {delay:.2f}s")
            time.sleep(delay)
    
    if last_exception:
        raise last_exception
    raise RuntimeError("Unexpected retry loop exit")
