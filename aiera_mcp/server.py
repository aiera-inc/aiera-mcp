#!/usr/bin/env python3

import os
import httpx
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, List, Set
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP

# Setup logging
logger = logging.getLogger(__name__)

# Import API key provider functions from package
try:
    from . import get_api_key
except ImportError:
    # Fallback for standalone usage
    def get_api_key() -> Optional[str]:
        return os.getenv("AIERA_API_KEY")

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


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage application lifecycle with HTTP client."""
    # Always create client in lifespan to ensure proper FastMCP initialization
    # Even in Lambda, FastMCP requires the full lifespan cycle to initialize its task groups

    # In Lambda, we can use a shared client for efficiency
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("MCP_LAMBDA_MODE"):
        # For Lambda, yield the global client but still go through full lifespan
        client = get_lambda_http_client()
        yield {"http_client": client}
        # Don't close the global client on shutdown in Lambda

    else:
        # For non-Lambda environments, use context-managed client
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=30.0),
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        ) as client:
            yield {"http_client": client}


# Initialize FastMCP server
mcp = FastMCP(
    name="Aiera",
    stateless_http=True,
    json_response=True,
    lifespan=app_lifespan,
)

# Base configuration
DEFAULT_PAGE_SIZE = 50
DEFAULT_MAX_PAGE_SIZE = 100


@mcp.resource(uri="aiera://api/docs")
def get_api_documentation() -> str:
    """Provide overview documentation for the Aiera API."""
    return f"""
    # Aiera Financial Data API

    This MCP server provides access to Aiera's comprehensive financial data API for institutional finance professionals.

    ## Tool Categories

    **Events & Transcripts**: Find and retrieve corporate events (earnings calls, conferences, meetings) with full transcripts and metadata.

    **SEC Filings**: Search and retrieve SEC filings (10-K, 10-Q, 8-K, etc.) with summaries and full content.

    **Company Data**: Access equity information, sector classifications, index constituents, and watchlists.

    **Company Documents**: Find investor relations documents, press releases, and regulatory filings published by companies.

    **Expert Insights**: Access Third Bridge expert interview events and insights.

    **Transcrippets™**: Create, find, and manage curated transcript segments for key insights and memorable quotes.

    ## Key Features

    - **Comprehensive Coverage**: Access to events, filings, documents, and expert insights across all major markets
    - **Rich Metadata**: Detailed summaries, speaker information, and structured data for all content
    - **Flexible Filtering**: Search by date ranges, tickers, sectors, indices, watchlists, and custom criteria
    - **Pagination Support**: Handle large result sets efficiently with pagination
    - **Citation Ready**: All responses include citation information for professional use

    ## Authentication & Usage

    - Requires `AIERA_API_KEY` environment variable
    - All dates use Eastern Time (ET)
    - Current date: **{datetime.now().strftime("%Y-%m-%d")}**
    - Bloomberg tickers use format "TICKER:COUNTRY" (e.g., "AAPL:US")
    - Multiple values in comma-separated lists (no spaces)

    ## Tool Parameters

    Each tool provides detailed parameter descriptions and validation through its input schema. Common patterns include:

    - **Date ranges**: ISO format (YYYY-MM-DD) with start_date and end_date
    - **Entity filtering**: Filter by tickers, watchlists, indices, sectors, or subsectors
    - **Pagination**: Page number and page size parameters where applicable
    - **Content filtering**: Categories, keywords, form types for targeted searches

    Use tool argument schemas for complete parameter documentation and validation.
    """


def register_aiera_tools(
    mcp_server: FastMCP,
    api_key_provider: Optional[Callable[[], Optional[str]]] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> None:
    """Register Aiera tools with a FastMCP server instance with optional filtering.

    Args:
        mcp_server: FastMCP server instance to register tools with
        api_key_provider: Optional function that returns API key for OAuth systems
        include: Optional list of tool names to include (if specified, only these tools will be registered)
        exclude: Optional list of tool names to exclude (these tools will not be registered)

    Examples:
        # Basic usage with environment variable - registers all tools
        register_aiera_tools(mcp)

        # With OAuth provider - registers all tools
        from aiera_public_mcp.auth import get_current_api_key
        register_aiera_tools(mcp, get_current_api_key)

        # Register only event-related tools
        register_aiera_tools(mcp, include=["find_events", "get_event", "get_upcoming_events"])

        # Register all tools except Third Bridge
        register_aiera_tools(mcp, exclude=["find_third_bridge_events", "get_third_bridge_event"])

        # Combine OAuth with selective registration
        register_aiera_tools(mcp, get_current_api_key, include=["find_events", "find_filings"])
    """
    # Configure API key provider if provided
    if api_key_provider:
        from . import set_api_key_provider
        set_api_key_provider(api_key_provider)

    # Register all tools using the new modular structure
    from .tools import register_tools
    register_tools(mcp_server)


def run(transport: str = "stdio"):
    """Run the MCP server (for standalone usage)."""
    # Register all tools when running standalone
    register_aiera_tools(mcp)

    # Literal type fix for transport parameter
    from typing import Literal
    valid_transports = ["stdio", "sse", "streamable-http"]
    if transport not in valid_transports:
        raise ValueError(f"Invalid transport: {transport}. Must be one of {valid_transports}")

    # Cast to the expected literal type
    transport_literal: Literal["stdio", "sse", "streamable-http"] = transport  # type: ignore
    mcp.run(transport=transport_literal)