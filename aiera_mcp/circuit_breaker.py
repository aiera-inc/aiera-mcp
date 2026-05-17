#!/usr/bin/env python3
"""Circuit breaker for Aiera API calls.

Implements the circuit breaker pattern to prevent cascade failures when the
backend API is down or experiencing issues. The breaker "opens" after repeated
failures, failing fast instead of overwhelming the backend with doomed requests.

Circuit States:
- CLOSED: Normal operation, requests go through
- OPEN: Too many failures, requests fail immediately
- HALF_OPEN: Testing if backend has recovered
"""

import logging
from typing import Any, Callable, Optional
from pybreaker import CircuitBreaker, CircuitBreakerError

logger = logging.getLogger(__name__)

# Global circuit breaker instance for the Aiera API
# Opens after 5 consecutive failures, stays open for 60 seconds
_aiera_api_breaker: Optional[CircuitBreaker] = None


def get_aiera_api_breaker() -> CircuitBreaker:
    """Get or create the global Aiera API circuit breaker.

    Circuit breaker configuration:
    - fail_max=5: Opens after 5 consecutive failures
    - timeout_duration=60: Stays open for 60 seconds before trying again
    - name="aiera_api": Identifier for logging and monitoring

    Returns:
        Circuit breaker instance
    """
    global _aiera_api_breaker
    if _aiera_api_breaker is None:
        _aiera_api_breaker = CircuitBreaker(
            fail_max=5,
            timeout_duration=60,
            name="aiera_api",
            # Custom exception handler to log state changes
            listeners=[CircuitBreakerListener()],
        )
    return _aiera_api_breaker


class CircuitBreakerListener:
    """Listener for circuit breaker state changes."""

    def state_change(self, breaker: CircuitBreaker, old_state, new_state):
        """Called when circuit breaker changes state."""
        logger.warning(
            f"Circuit breaker '{breaker.name}' state changed: {old_state} -> {new_state}. "
            f"Failure count: {breaker.fail_counter}/{breaker.fail_max}"
        )

    def before_call(self, breaker: CircuitBreaker, func: Callable, *args, **kwargs):
        """Called before executing the protected function."""
        if breaker.current_state == "open":
            logger.debug(f"Circuit breaker '{breaker.name}' is OPEN - failing fast")

    def success(self, breaker: CircuitBreaker):
        """Called after successful execution."""
        if breaker.fail_counter > 0:
            logger.info(
                f"Circuit breaker '{breaker.name}' success - "
                f"resetting failure count from {breaker.fail_counter}"
            )

    def failure(self, breaker: CircuitBreaker, exception: Exception):
        """Called after failed execution."""
        logger.warning(
            f"Circuit breaker '{breaker.name}' failure ({breaker.fail_counter}/{breaker.fail_max}): "
            f"{type(exception).__name__}: {exception}"
        )


def is_circuit_breaker_error(exception: Exception) -> bool:
    """Check if an exception is a circuit breaker error.

    Args:
        exception: Exception to check

    Returns:
        True if exception is CircuitBreakerError
    """
    return isinstance(exception, CircuitBreakerError)


def get_circuit_breaker_state() -> dict[str, Any]:
    """Get current circuit breaker state for health checks.

    Returns:
        Dictionary with breaker state information
    """
    breaker = get_aiera_api_breaker()
    return {
        "state": breaker.current_state,  # "closed", "open", or "half_open"
        "failure_count": breaker.fail_counter,
        "fail_max": breaker.fail_max,
        "timeout_duration": breaker.timeout_duration,
    }


__all__ = [
    "get_aiera_api_breaker",
    "is_circuit_breaker_error",
    "get_circuit_breaker_state",
    "CircuitBreakerError",
]
