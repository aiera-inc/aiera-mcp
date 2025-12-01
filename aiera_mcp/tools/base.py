#!/usr/bin/env python3

"""Base functionality for Aiera MCP tools."""

import httpx
import logging
from typing import Any, Dict, Optional
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)

# Import settings
from ..config import get_settings

# Default headers configuration
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Aiera-MCP/1.0.0",
    "X-MCP-Origin": "local_mcp",
}


# Backward compatibility - expose AIERA_BASE_URL as a module-level variable
# This will be dynamically resolved from settings
def _get_base_url() -> str:
    """Get the base URL from settings."""
    return get_settings().aiera_base_url


# For backward compatibility, keep AIERA_BASE_URL as a module constant
# but it will be resolved at import time
AIERA_BASE_URL = get_settings().aiera_base_url

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
        # Get settings for HTTP client configuration
        settings = get_settings()
        # Configure client with connection pooling and timeouts
        _lambda_http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=settings.http_max_keepalive_connections,
                max_connections=settings.http_max_connections,
                keepalive_expiry=settings.http_keepalive_expiry,
            ),
            timeout=httpx.Timeout(settings.http_timeout),
            follow_redirects=True,
        )

    return _lambda_http_client


async def get_http_client(ctx) -> httpx.AsyncClient:
    """Get HTTP client from context."""
    # Try to get client from lifespan context first
    try:
        if hasattr(ctx, "request_context") and hasattr(
            ctx.request_context, "lifespan_context"
        ):
            client = ctx.request_context.lifespan_context.get("http_client")
            if client:
                return client
    except (KeyError, AttributeError) as e:
        logger.debug(f"Could not get client from lifespan context: {e}")

    # Fall back to global client for Lambda or when lifespan context is not available
    return get_lambda_http_client()


async def get_api_key_from_context(ctx) -> str:
    """Extract API key using configured provider.

    This function is now a simple wrapper around get_api_key() for backward compatibility.
    The actual authentication logic is handled by the configured provider (e.g., OAuth).

    Args:
        ctx: Context parameter (kept for backward compatibility but not used)

    Returns:
        API key string

    Raises:
        ValueError: If no API key is available
    """
    from .. import get_api_key

    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "No API key available. Please configure an API key provider or set AIERA_API_KEY environment variable."
        )

    logger.debug(f"Retrieved API key (length: {len(api_key)})")
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
    # headers["X-MCP-Origin"] = f"remote_mcp_{config.STAGE}"

    # Log API request info for debugging
    logger.info(
        f"API request: {endpoint}\n" f"API key: Present\n" f"Params: {params}\n"
    )

    # Get base URL from settings dynamically
    settings = get_settings()
    url = f"{settings.aiera_base_url}{endpoint}"

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

    if response.status_code not in [200, 201]:
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
        # For 504 Gateway Timeout, provide a more informative message
        elif response.status_code == 504:
            raise Exception(
                f"API request timed out (504). The API endpoint may be experiencing heavy load. Please retry in a moment."
            )
        else:
            raise Exception(
                f"API request failed: {response.status_code} - {response.text}"
            )

    if return_type == "json":
        response_data = response.json()
    else:
        response_data = response.text

    # Prepare instructions for response formatting
    instructions = [
        f"""This data is provided for institutional finance professionals. Responses should be composed of accurate, concise,
and well-structured financial insights.
The current date is **{datetime.now().strftime("%Y-%m-%d")}**, and the current time is **{datetime.now().strftime("%I:%M %p")}**.
Relative dates and times (e.g., "last 3 months" or "next 3 months" or "later today") should be calculated based on this date.
All dates and times are in eastern time (ET) unless specifically stated otherwise.

## Usage Hints:
- Questions about guidance will always require the transcript from at least one earnings event, and often will require multiple earnings transcripts from the last year in order to provide sufficient context.
- Answers to guidance questions should focus on management commentary, and avoid analyst commentary unless specifically asked for.

Some endpoints may require specific permissions based on a subscription plan. If access is denied, the user should talk to their Aiera representative about gaining access.
""",
        CITATION_PROMPT,
    ]

    if additional_instructions:
        instructions.append(additional_instructions)

    return {
        "instructions": instructions,
        "response": response_data,
    }
