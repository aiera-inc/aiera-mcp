#!/usr/bin/env python3

"""Base functionality for Aiera MCP tools."""

import os
import httpx
import logging
import contextvars
from typing import Any, Dict, Optional
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Base configuration
AIERA_BASE_URL = "https://premium.aiera.com/api"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Aiera-MCP/1.0.0",
    "X-MCP-Origin": "local_mcp"
}

# Citation prompt for UI clients
CITATION_PROMPT = """IMPORTANT: when referencing this data in your response, ALWAYS include inline citations by using the information found in the `citation_information` block, along with an incrementing counter. Render these citations as markdown (padded with a leading space for readability), like this: [[1]](url "title")

Where possible, include inline citations for every fact, figure, or quote that was sourced, directly or indirectly, from a transcript by using transcript-level citations (as opposed to event-level citations).

If multiple citations are relevant, include them all. You can reference the same citation multiple times if needed.

However, if the user has requested a response as JSON, you do NOT need to include any citations."""

# Global HTTP client for Lambda environment with proper configuration
_lambda_http_client: Optional[httpx.AsyncClient] = None


async def cleanup_lambda_http_client():
    """Cleanup the global HTTP client."""
    global _lambda_http_client
    if _lambda_http_client is not None:
        await _lambda_http_client.aclose()
        _lambda_http_client = None


def get_lambda_http_client() -> httpx.AsyncClient:
    """Get or create a shared HTTP client for Lambda environment."""
    global _lambda_http_client
    if _lambda_http_client is None:
        # Configure client with connection pooling and timeouts
        _lambda_http_client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=30.0),
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    return _lambda_http_client


async def get_http_client(ctx) -> httpx.AsyncClient:
    """Get HTTP client from context."""
    # Try to get client from lifespan context first
    try:
        if hasattr(ctx, "request_context") and hasattr(ctx.request_context, "lifespan_context"):
            client = ctx.request_context.lifespan_context.get("http_client")
            if client:
                return client
    except (KeyError, AttributeError) as e:
        logger.debug(f"Could not get client from lifespan context: {e}")

    # Fall back to global client for Lambda or when lifespan context is not available
    return get_lambda_http_client()


async def get_api_key_from_context(ctx) -> str:
    """Extract API key from authenticated context with enhanced OAuth integration."""
    # Log context ID to verify isolation between concurrent requests
    context_id = id(contextvars.copy_context())
    logger.debug(f"Context ID: {context_id}")

    # Check if API key is already stored in context variable
    try:
        from .. import get_api_key
        api_key = get_api_key()
    except ImportError:
        # Fallback for standalone usage
        def get_api_key() -> Optional[str]:
            return os.getenv("AIERA_API_KEY")
        api_key = get_api_key()

    # If API key already set (e.g., from query parameter or OAuth), use it
    if api_key:
        logger.info(f"API key already set, using {api_key[:8]}...")
        return api_key

    # If no API key yet, try OAuth authentication
    try:
        # Try to import and use OAuth authentication
        try:
            from ..auth import validate_auth_context, get_current_api_key
            await validate_auth_context(ctx)
            api_key = get_current_api_key()

            if not api_key:
                # This is the critical issue - if OAuth succeeds but no API key found,
                # we should NOT fall back to environment variables
                logger.error("OAuth authentication succeeded but no API key found in user claims")
                raise ValueError("No API key found in authenticated user claims")

        except ImportError:
            # OAuth not available, fall back to environment variable
            logger.debug("OAuth authentication not available, using environment variable")
            api_key = os.getenv("AIERA_API_KEY")

    except Exception as e:
        logger.error(f"Auth validation failed: {str(e)}")

        # Special handling for Lambda environment with direct API key
        # This should only be used as absolute last resort
        if os.getenv("AWS_LAMBDA_FUNCTION_NAME") and os.getenv("AIERA_API_KEY"):
            logger.warning("Using Lambda environment API key as emergency fallback")
            logger.warning("This should only happen during Lambda cold starts or system issues")

            api_key = os.getenv("AIERA_API_KEY")

        else:
            # Re-raise the original error
            raise

    if not api_key:
        raise ValueError("Failed to retrieve API key after all authentication attempts")

    return api_key


async def make_aiera_request(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    api_key: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    additional_instructions: Optional[str] = None,
    return_type: str = "json",
) -> Dict[str, Any]:
    """Make a request to the Aiera API with enhanced error handling and logging.

    Args:
        client: HTTP client instance
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        api_key: API key (required)
        params: Query parameters
        data: Request body data
        additional_instructions: Additional instructions for response formatting
        return_type: Response format type

    Returns:
        JSON response data with instructions
    """
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-Key"] = api_key

    # Log API key info for debugging (without exposing the full key)
    logger.info(
        f"API request: {endpoint}\n"
        f"API key preview: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}\n"
        f"Params: {params}\n"
    )

    url = f"{AIERA_BASE_URL}{endpoint}"

    try:
        response = await client.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=60.0,
        )

    except httpx.RequestError as e:
        logger.error(f"Request URL was: {url}")
        logger.error(f"Request headers were: {headers}")
        if params:
            logger.error(f"Request params were: {params}")

        raise Exception(f"Network error calling Aiera API: {str(e)}")

    if response.status_code != 200:
        logger.error(f"API error: {response.status_code} - {response.text}")
        logger.error(f"Request URL: {url}")
        logger.error(f"Request headers were: {headers}")
        if params:
            logger.error(f"Request params: {params}")

        # Check if this looks like an auth error
        if response.status_code in [401, 403]:
            raise Exception(
                f"Aiera API authentication failed (HTTP {response.status_code}). The API key may be invalid or expired."
            )
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

    if return_type == "json":
        response_data = response.json()
    else:
        response_data = response.text

    # Prepare instructions for response formatting
    instructions = [
        "This data is provided for institutional finance professionals. Responses should be composed of accurate, concise, and well-structured financial insights.",
        CITATION_PROMPT,
    ]

    if additional_instructions:
        instructions.append(additional_instructions)

    return {
        "instructions": instructions,
        "response": response_data,
    }