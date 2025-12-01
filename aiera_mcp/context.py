#!/usr/bin/env python3
"""Context provider infrastructure for request customization.

This module provides a plugin system for injecting deployment-specific context
(headers, metadata, error handling) into API requests without modifying tool code.

Example:
    # In aiera-public-mcp server.py:
    from aiera_mcp import set_request_context_provider, set_error_handler
    from .mcp_context import create_request_context, create_oauth_error_handler

    # Configure context injection at startup
    set_request_context_provider(create_request_context)
    set_error_handler(create_oauth_error_handler)

    # Now all tools will automatically include OAuth context in requests
"""

import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Global context provider - returns headers and metadata for current request
_request_context_provider: Optional[Callable[[], Dict[str, Any]]] = None

# Global error handler - creates appropriate exceptions for API errors
_error_handler: Optional[Callable[[int, str, str], Exception]] = None


def set_request_context_provider(provider: Callable[[], Dict[str, Any]]) -> None:
    """Configure a function that provides request context (headers, metadata).

    The provider function should return a dictionary with the following structure:
    {
        "headers": {
            "X-Custom-Header": "value",
            ...
        },
        "log_metadata": {
            "user_id": "12345",
            "stage": "prod",
            ...
        }
    }

    Args:
        provider: A callable that returns a context dictionary

    Example:
        def my_context_provider():
            return {
                "headers": {
                    "X-MCP-Origin": "remote_mcp_prod",
                    "X-User-ID": get_current_user_id(),
                },
                "log_metadata": {
                    "user_id": get_current_user_id(),
                    "stage": "prod",
                }
            }

        set_request_context_provider(my_context_provider)
    """
    global _request_context_provider
    _request_context_provider = provider
    logger.info("Request context provider configured")


def get_request_context() -> Dict[str, Any]:
    """Get current request context from configured provider.

    Returns:
        Dictionary with 'headers' and 'log_metadata' keys, or empty dict if no provider

    Example:
        context = get_request_context()
        headers = context.get("headers", {})
        metadata = context.get("log_metadata", {})
    """
    if _request_context_provider:
        try:
            context = _request_context_provider()
            logger.debug(
                f"Retrieved context with {len(context.get('headers', {}))} headers"
            )
            return context
        except Exception as e:
            logger.warning(f"Context provider failed: {e}", exc_info=True)
            # Return empty context on failure to avoid breaking requests
            return {}

    # No provider configured - return empty context
    return {}


def clear_request_context_provider() -> None:
    """Clear the configured context provider (mainly for testing)."""
    global _request_context_provider
    _request_context_provider = None
    logger.info("Request context provider cleared")


def set_error_handler(handler: Callable[[int, str, str], Exception]) -> None:
    """Configure custom error handler for API failures.

    The error handler receives the HTTP status code, endpoint, and response text,
    and should return an appropriate Exception to raise.

    Args:
        handler: A callable that takes (status_code, endpoint, response_text) and returns Exception

    Example:
        def my_error_handler(status_code: int, endpoint: str, response_text: str) -> Exception:
            if status_code == 401:
                return OAuthAuthenticationError("Please re-authenticate")
            else:
                return Exception(f"API error {status_code}: {response_text}")

        set_error_handler(my_error_handler)
    """
    global _error_handler
    _error_handler = handler
    logger.info("Custom error handler configured")


def handle_api_error(status_code: int, endpoint: str, response_text: str) -> Exception:
    """Handle API error using custom handler if configured.

    Args:
        status_code: HTTP status code from API response
        endpoint: API endpoint that was called
        response_text: Response body text

    Returns:
        Exception to raise (either custom or default)

    Example:
        exception = handle_api_error(401, "/events", "Unauthorized")
        raise exception
    """
    if _error_handler:
        try:
            error = _error_handler(status_code, endpoint, response_text)
            logger.debug(f"Custom error handler created {type(error).__name__}")
            return error
        except Exception as e:
            logger.warning(f"Error handler failed: {e}", exc_info=True)
            # Fall through to default handler

    # Default error handling
    if status_code in [401, 403]:
        return Exception(
            f"Aiera API authentication failed (HTTP {status_code}). "
            f"The API key may be invalid or expired."
        )
    elif status_code == 404:
        return Exception(
            f"Aiera API endpoint not found: {endpoint}. "
            f"This might indicate an incorrect endpoint or missing API access."
        )
    elif status_code == 504:
        return Exception(
            f"API request timed out (504). "
            f"The API endpoint may be experiencing heavy load. Please retry in a moment."
        )
    else:
        return Exception(f"API request failed: {status_code} - {response_text}")


def clear_error_handler() -> None:
    """Clear the configured error handler (mainly for testing)."""
    global _error_handler
    _error_handler = None
    logger.info("Error handler cleared")
