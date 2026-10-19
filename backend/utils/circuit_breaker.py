"""
Circuit Breaker Pattern Implementation
Prevents cascading failures when external services are down
"""
import os
import time
import threading
import logging
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests immediately
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Thread-safe circuit breaker implementation"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        half_open_max_calls: int = 3,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker
        
        Args:
            name: Name identifier for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
            half_open_max_calls: Max test calls in half-open state
            expected_exception: Exception type to catch (default: all exceptions)
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self.lock = threading.Lock()
        
        logger.info(
            f"CircuitBreaker '{name}' initialized: "
            f"threshold={failure_threshold}, timeout={timeout}s"
        )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
        
        Returns:
            Result of function call
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception raised by the function
        """
        with self.lock:
            # Check circuit state
            if self.state == CircuitState.OPEN:
                # Check if timeout has passed
                if self.last_failure_time:
                    elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                    if elapsed >= self.timeout:
                        logger.info(f"CircuitBreaker '{self.name}': Moving to HALF_OPEN state")
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0
                        self.success_count = 0
                    else:
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker '{self.name}' is OPEN. "
                            f"Retry after {self.timeout - elapsed:.1f}s"
                        )
                else:
                    raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
            
            elif self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.half_open_max_calls:
                    # Too many test calls, keep circuit open
                    logger.warning(
                        f"CircuitBreaker '{self.name}': Too many half-open calls, "
                        f"keeping circuit OPEN"
                    )
                    self.state = CircuitState.OPEN
                    self.last_failure_time = datetime.now()
                    raise CircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                self.half_open_calls += 1
                
                # If we get enough successes, close the circuit
                if self.success_count >= self.half_open_max_calls:
                    logger.info(f"CircuitBreaker '{self.name}': Moving to CLOSED state")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.half_open_calls = 0
            
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                # Failure in half-open state, open circuit immediately
                logger.warning(f"CircuitBreaker '{self.name}': Failure in HALF_OPEN, moving to OPEN")
                self.state = CircuitState.OPEN
                self.half_open_calls = 0
                self.success_count = 0
            
            elif self.state == CircuitState.CLOSED:
                # Check if we've exceeded threshold
                if self.failure_count >= self.failure_threshold:
                    logger.warning(
                        f"CircuitBreaker '{self.name}': {self.failure_count} failures, "
                        f"moving to OPEN state"
                    )
                    self.state = CircuitState.OPEN
    
    def reset(self):
        """Manually reset circuit breaker to CLOSED state"""
        with self.lock:
            logger.info(f"CircuitBreaker '{self.name}': Manually reset to CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
            self.last_failure_time = None
    
    def get_state(self) -> CircuitState:
        """Get current circuit state"""
        with self.lock:
            return self.state


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


class CircuitBreakerManager:
    """Singleton manager for circuit breakers"""
    
    _instance = None
    _lock = threading.Lock()
    _breakers: dict = {}
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def get_breaker(
        self,
        name: str,
        failure_threshold: Optional[int] = None,
        timeout: Optional[float] = None,
        half_open_max_calls: Optional[int] = None
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker
        
        Args:
            name: Unique name for the breaker
            failure_threshold: Failures before opening (from env if not provided)
            timeout: Seconds before attempting to close (from env if not provided)
            half_open_max_calls: Test calls in half-open state (from env if not provided)
        
        Returns:
            CircuitBreaker instance
        """
        if name not in self._breakers:
            # Get defaults from environment
            if failure_threshold is None:
                failure_threshold = int(os.environ.get('CIRCUIT_BREAKER_FAILURE_THRESHOLD', 5))
            if timeout is None:
                timeout = float(os.environ.get('CIRCUIT_BREAKER_TIMEOUT', 60.0))
            if half_open_max_calls is None:
                half_open_max_calls = int(os.environ.get('CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS', 3))
            
            with self._lock:
                if name not in self._breakers:
                    self._breakers[name] = CircuitBreaker(
                        name=name,
                        failure_threshold=failure_threshold,
                        timeout=timeout,
                        half_open_max_calls=half_open_max_calls
                    )
        
        return self._breakers[name]


# Convenience functions
def get_circuit_breaker(name: str, **kwargs) -> CircuitBreaker:
    """Get a circuit breaker by name"""
    manager = CircuitBreakerManager.get_instance()
    return manager.get_breaker(name, **kwargs)


def circuit_breaker(name: str, **breaker_kwargs):
    """
    Decorator for circuit breaker protection
    
    Usage:
        @circuit_breaker('openai_api')
        def api_call():
            # API call code
            pass
    """
    def decorator(func: Callable) -> Callable:
        breaker = get_circuit_breaker(name, **breaker_kwargs)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return breaker.call(func, *args, **kwargs)
        
        return wrapper
    return decorator
