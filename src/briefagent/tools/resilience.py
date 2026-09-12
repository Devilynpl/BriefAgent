import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, Optional, Tuple, Type

logger = logging.getLogger("briefagent.resilience")


class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is OPEN due to repeated failures."""
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 10.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count: int = 0
        self.last_failure_time: Optional[float] = None
        self.state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"CircuitBreaker transitioned to OPEN (failures: {self.failure_count})")

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if self.last_failure_time and (time.time() - self.last_failure_time > self.recovery_timeout):
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return False


def with_retry_and_circuit_breaker(
    max_retries: int = 2,
    base_delay: float = 1.0,
    backoff_factor: float = 3.0,
    circuit_breaker: Optional[CircuitBreaker] = None,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Exponential Backoff with Circuit Breaker decorator for async tool methods.
    Retries max 2 times with delay 1s -> 3s on 429/5xx or network errors.
    Returns (result, duration_ms, retry_count, recovered_error)
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Dict[str, Any]:
            cb = circuit_breaker or getattr(func, "_cb", None)
            if cb and not cb.can_execute():
                raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            retry_count = 0
            start_time = time.time()
            recovered_from_error = False

            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    duration_ms = (time.time() - start_time) * 1000.0
                    if cb:
                        cb.record_success()
                    return {
                        "success": True,
                        "data": result,
                        "error": None,
                        "duration_ms": duration_ms,
                        "retry_count": retry_count,
                        "recovered": recovered_from_error,
                    }
                except retryable_exceptions as ex:
                    retry_count = attempt + 1
                    recovered_from_error = True
                    if cb:
                        cb.record_failure()
                    if attempt < max_retries:
                        delay = base_delay * (backoff_factor ** attempt)
                        logger.warning(
                            f"Tool {func.__name__} failed with {type(ex).__name__}: {ex}. "
                            f"Retrying in {delay}s (attempt {attempt + 1}/{max_retries})..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        duration_ms = (time.time() - start_time) * 1000.0
                        return {
                            "success": False,
                            "data": None,
                            "error": f"{type(ex).__name__}: {str(ex)}",
                            "duration_ms": duration_ms,
                            "retry_count": retry_count,
                            "recovered": False,
                        }
            duration_ms = (time.time() - start_time) * 1000.0
            return {
                "success": False,
                "data": None,
                "error": "Max retries exceeded",
                "duration_ms": duration_ms,
                "retry_count": retry_count,
                "recovered": False,
            }

        return wrapper
    return decorator
