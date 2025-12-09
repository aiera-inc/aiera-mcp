#!/usr/bin/env python3

import os
import httpx
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, List
from collections.abc import AsyncIterator

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
)

# Setup logging with file handler and reduced stderr verbosity
# File handler: All INFO+ messages for debugging
# stderr handler: Only ERROR+ messages (sent as MCP notifications to inspector)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/tmp/aiera-mcp-server.log"),
    ],
)

# Add stderr handler with ERROR level only to reduce inspector noise
stderr_handler = logging.StreamHandler()
stderr_handler.setLevel(logging.ERROR)
stderr_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
)
logging.getLogger().addHandler(stderr_handler)

# Suppress noisy third-party loggers
logging.getLogger("httpx").setLevel(logging.WARNING)

# Ensure MCP SDK loggers write to file
# The "mcp" logger will inherit root logger's file handler
logging.getLogger("mcp").setLevel(logging.INFO)
logging.getLogger("mcp.server").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# Import settings and API key provider functions from package
from .config import get_settings

try:
    pass
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


# HTTP client management for the standard MCP server
# We'll manage clients directly in the tool functions as needed


# Initialize standard MCP server
server = Server("Aiera")

# Base configuration - these are now loaded from settings
# but kept as module-level constants for backward compatibility
_settings = get_settings()
DEFAULT_PAGE_SIZE = _settings.default_page_size
DEFAULT_MAX_PAGE_SIZE = _settings.default_max_page_size


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

    **Search**: Perform semantic search across transcripts and filings with advanced filtering.

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
    api_key_provider: Optional[Callable[[], Optional[str]]] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Register Aiera tools and return the tool registry.

    Args:
        api_key_provider: Optional function that returns API key for OAuth systems
        include: Optional list of tool names to include (if specified, only these tools will be registered)
        exclude: Optional list of tool names to exclude (these tools will not be registered)

    Returns:
        Dictionary of registered tools
    """
    # Configure API key provider if provided
    if api_key_provider:
        from . import set_api_key_provider

        set_api_key_provider(api_key_provider)

    # Get the tool registry
    from .tools.registry import TOOL_REGISTRY

    return TOOL_REGISTRY


def normalize_empty_schema(schema: dict) -> dict:
    """Ensure empty schemas have clear structure for LLMs.

    When a tool has no parameters, the JSON schema shows empty properties: {},
    which can be ambiguous for LLMs. This function makes the expectations explicit
    by adding constraints and clarifying the description.

    Args:
        schema: The original JSON schema dict

    Returns:
        Normalized schema with explicit constraints for empty parameter sets
    """
    if schema.get("properties") == {}:
        return {
            **schema,
            "description": f"{schema.get('description', '')} This tool requires no parameters.",
            "additionalProperties": False,
            "minProperties": 0,
            "maxProperties": 0,
        }
    return schema


def unwrap_arguments(arguments: dict, tool_name: str) -> dict:
    """Unwrap arguments if they're wrapped in an 'args' key.

    Some MCP clients (notably ChatGPT) may wrap tool arguments in an 'args' field:
        {args: {search: "Tesla", page_size: 5}}
    instead of the expected flat format:
        {search: "Tesla", page_size: 5}

    Without unwrapping, Pydantic would:
    - Accept 'args' as an extra field (silently ignored)
    - Use default values for all actual parameters
    - Appear to "succeed" but with wrong values

    This function detects and unwraps such cases.

    Args:
        arguments: The arguments dict received from the MCP client
        tool_name: Name of the tool being called (for logging)

    Returns:
        Unwrapped arguments dict

    Example:
        >>> unwrap_arguments({"args": {"search": "Tesla"}}, "find_equities")
        {"search": "Tesla"}
    """
    if not isinstance(arguments, dict):
        logger.warning(f"Arguments for {tool_name} is not a dict: {type(arguments)}")
        return arguments

    # Check for wrapped pattern: {args: {...}}
    if "args" in arguments and isinstance(arguments.get("args"), dict):
        # If 'args' is the ONLY key, it's definitely a wrapper
        if len(arguments) == 1:
            logger.info(f"🔧 Unwrapping 'args' wrapper for {tool_name}")
            logger.debug(f"   Before: {arguments}")
            unwrapped = arguments["args"]
            logger.debug(f"   After: {unwrapped}")
            return unwrapped

        # If there are other keys, this is ambiguous - log a warning
        logger.warning(
            f"Ambiguous arguments for {tool_name}: has 'args' key plus others: {list(arguments.keys())}"
        )

    return arguments


async def run_server():
    """Run the MCP server using stdio transport."""
    logger.info("=" * 60)
    logger.info("🚀 Starting Aiera MCP Server initialization...")
    logger.info("=" * 60)

    # Get the tool registry
    tool_registry = register_aiera_tools()

    logger.info(f"✓ Registered {len(tool_registry)} tools")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """Return list of available tools with proper schemas."""
        tools = []
        for tool_name, tool_config in tool_registry.items():
            # Normalize empty schemas for better LLM compatibility
            normalized_schema = normalize_empty_schema(tool_config["input_schema"])

            tool_kwargs = {
                "name": tool_name,
                "description": tool_config["description"],
                "inputSchema": normalized_schema,
            }

            # Add output schema for transcrippet tools
            if tool_name in [
                "find_transcrippets",
                "create_transcrippet",
                "delete_transcrippet",
            ]:
                # Import response models to get their schemas
                if tool_name == "find_transcrippets":
                    from .tools.transcrippets.models import FindTranscrippetsResponse

                    tool_kwargs["outputSchema"] = (
                        FindTranscrippetsResponse.model_json_schema()
                    )
                elif tool_name == "create_transcrippet":
                    from .tools.transcrippets.models import CreateTranscrippetResponse

                    tool_kwargs["outputSchema"] = (
                        CreateTranscrippetResponse.model_json_schema()
                    )
                elif tool_name == "delete_transcrippet":
                    from .tools.transcrippets.models import DeleteTranscrippetResponse

                    tool_kwargs["outputSchema"] = (
                        DeleteTranscrippetResponse.model_json_schema()
                    )

            # Log UI-enabled tools (using embedded UI resources via MCP UI SDK)
            if tool_name in ["find_transcrippets", "create_transcrippet"]:
                logger.info(f"Registered UI tool: {tool_name} (embedded UI)")
                logger.debug(
                    f"  - inputSchema keys: {list(tool_kwargs['inputSchema'].keys())}"
                )
                logger.debug(
                    f"  - outputSchema present: {'outputSchema' in tool_kwargs}"
                )

            tool = Tool(**tool_kwargs)

            tools.append(tool)
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[TextContent]:
        """Handle tool calls with support for both Claude MCP and OpenAI MCP formats."""
        logger.info(f"Tool called: {name}")
        logger.debug(f"Raw arguments: {arguments}")

        # Find the tool in registry
        if name not in tool_registry:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")

        tool_config = tool_registry[name]

        try:
            # Unwrap arguments if ChatGPT wrapped them in an 'args' key
            # This handles cases where ChatGPT sends {args: {search: "Tesla"}}
            # instead of the expected flat format {search: "Tesla"}
            normalized_arguments = unwrap_arguments(arguments, name)

            # Parse arguments using the Pydantic model
            parsed_args = tool_config["args_model"](**normalized_arguments)
            logger.debug(f"Arguments parsed successfully for {name}")

            # Call the tool function
            result = await tool_config["function"](parsed_args)

            # Convert result to dict if needed
            if hasattr(result, "model_dump"):
                result_dict = result.model_dump()
            else:
                result_dict = result

            logger.debug(f"Tool {name} result type: {type(result)}")
            logger.debug(
                f"Tool {name} result_dict keys: {list(result_dict.keys()) if isinstance(result_dict, dict) else 'not a dict'}"
            )

            # Return as TextContent
            import json

            result_text = (
                json.dumps(result_dict, indent=2)
                if not isinstance(result_dict, str)
                else result_dict
            )

            logger.info(f"Tool {name} completed successfully")
            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            logger.error(f"Tool {name} failed: {str(e)}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    # Start stdio-based MCP server
    logger.info("=" * 60)
    logger.info("🚀 Aiera MCP Server initialization complete!")
    logger.info("=" * 60)
    logger.info("📡 Transport: stdio (JSON-RPC over stdin/stdout)")
    logger.info(f"🔧 Tools registered: {len(tool_registry)}")
    logger.info("=" * 60)

    options = server.create_initialization_options()
    async with stdio_server() as (reader, writer):
        logger.info("✅ stdio server started - awaiting MCP client connections...")
        await server.run(reader, writer, options, raise_exceptions=True)


def run(transport: str = "stdio"):
    """Run the MCP server (for standalone usage)."""
    if transport != "stdio":
        raise ValueError("Only stdio transport is currently supported")

    import asyncio

    asyncio.run(run_server())
