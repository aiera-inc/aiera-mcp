#!/usr/bin/env python3

import asyncio
import json
import httpx
import logging
from typing import Any, Dict, Optional, Callable, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Setup logging
logger = logging.getLogger(__name__)

# Import settings and API key provider functions from package
from .config import get_settings


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


# Strong references to background tasks to prevent garbage collection
_background_tasks: set = set()


async def _send_tool_log(
    tool_name: str,
    parameters: Optional[Dict[str, Any]],
    response: Optional[Dict[str, Any]],
    is_error: bool = False,
) -> None:
    """Fire-and-forget: send tool invocation log to the collect-mcp-log endpoint.

    All exceptions are swallowed so this never affects tool execution.
    """
    try:
        from . import get_api_key
        from .tools.base import DEFAULT_HEADERS, get_http_client

        logger.info(
            "MCP tool log: starting for tool=%s is_error=%s", tool_name, is_error
        )

        api_key = get_api_key()
        if not api_key:
            logger.warning("MCP tool log: skipping, no API key available")
            return

        client = await get_http_client(None)
        settings = get_settings()
        url = f"{settings.aiera_base_url}/chat-support/collect-mcp-log"

        headers = DEFAULT_HEADERS.copy()
        headers["X-API-Key"] = api_key

        body: Dict[str, Any] = {"tool": tool_name}
        if parameters is not None:
            body["parameters"] = parameters
        if response is not None:
            body["response"] = response
        if is_error:
            body["is_error"] = True

        logger.info("MCP tool log: sending POST to %s for tool=%s", url, tool_name)
        resp = await client.post(url, json=body, headers=headers, timeout=5.0)
        logger.info(
            "MCP tool log: completed for tool=%s status=%s",
            tool_name,
            resp.status_code,
        )
    except Exception:
        # Swallow all errors – logging should never break tool execution
        logger.warning("MCP tool log: failed for tool=%s", tool_name, exc_info=True)


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

    ## Grammar Templates (Response Formatting)

    Before producing any response that uses Aiera data, you MUST call the `get_grammar_template` tool to retrieve formatting instructions. These templates define how you should structure, format, and present your responses — including tone, style, and common language patterns.

    - **At the start of each session**, call `get_grammar_template` with `template_type='general'` to get baseline formatting rules.
    - Follow the instructions returned in the template when composing your response.

    ## Tool Categories

    **Research**: Find, retrieve, and search within sell-side research content (analyst reports, research notes, market analysis, etc.)

    **Events & Transcripts**: Find, retrieve, and search within corporate events (earnings calls, conferences, M&A announcements, etc.).

    **SEC Filings**: Find, retrieve, and search within SEC filings (10-K, 10-Q, 8-K, etc.).

    **Company Documents**: Find and retrieve company publications (press releases, regulatory filings, announcements, etc.).

    **Expert Insights**: Find and retrieve Third Bridge expert interview events and insights.

    **Company Data**: Access company financials and KPIs, sector classifications, index constituents, and watchlists.

    **Utility**: Grammar templates for response formatting guidance.

    ## Key Features

    - **Comprehensive Coverage**: Access to events, filings, documents, and expert insights across all major markets.
    - **Rich Metadata**: Detailed summaries, speaker information, and structured data for all content.
    - **Flexible Filtering**: Search by date ranges, tickers, sectors, indices, watchlists, and custom criteria.
    - **Pagination Support**: Handle large result sets efficiently with pagination.
    - **Citation Ready**: All responses include citation information for professional use.

    ## Authentication & Usage

    - Requires `AIERA_API_KEY` environment variable.
    - Bloomberg tickers use format "TICKER:COUNTRY" (e.g., "AAPL:US").
    - Multiple values in comma-separated lists (no spaces).

    ## Tool Parameters

    Each tool provides detailed parameter descriptions and validation through its input schema. Common patterns include:

    - **Date ranges**: ISO format (YYYY-MM-DD) with start_date and end_date.
    - **Entity filtering**: Filter by tickers, watchlists, indices, sectors, or subsectors.
    - **Pagination**: Page number and page size parameters where applicable.
    - **Content filtering**: Categories, keywords, form types for targeted searches.

    Use tool argument schemas for complete parameter documentation and validation.

    **Be aware:** certain tools (get_event, get_filing, get_document) may return large text fields. Ensure your client can handle large responses.
    If you need to fetch multiple documents, it is recommended to favor the search tools, or use tools that return summaries.
    """


def register_aiera_tools(
    api_key_provider: Optional[Callable[[], Optional[str]]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Register Aiera tools and return the tool registry.

    Args:
        api_key_provider: Optional function that returns API key for OAuth systems

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


async def run_server():
    """Run the MCP server using stdio transport."""
    # Get the tool registry
    tool_registry = register_aiera_tools()

    logger.info(f"Registered {len(tool_registry)} tools")

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """Return list of available tools with proper schemas."""
        tools = []
        for tool_name, tool_config in tool_registry.items():
            tools.append(
                Tool(
                    name=tool_name,
                    title=tool_config.get("display_name"),
                    description=tool_config["description"],
                    inputSchema=tool_config["input_schema"],
                )
            )
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> List[TextContent]:
        """Handle tool calls."""
        logger.info(f"Tool called: {name}")
        logger.debug(f"Arguments: {arguments}")

        # Find the tool in registry
        if name not in tool_registry:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")

        tool_config = tool_registry[name]

        try:
            # Parse arguments using the Pydantic model
            parsed_args = tool_config["args_model"](**arguments)
            logger.debug(f"Arguments parsed successfully for {name}")

            # Call the tool function
            result = await tool_config["function"](parsed_args)

            # Convert result to dict if needed
            if hasattr(result, "model_dump"):
                result_dict = result.model_dump()
            else:
                result_dict = result

            # Return as TextContent
            result_text = (
                json.dumps(result_dict, indent=2)
                if not isinstance(result_dict, str)
                else result_dict
            )

            # Fire-and-forget: log tool invocation
            task = asyncio.create_task(_send_tool_log(name, arguments, result_dict))
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)

            logger.info(f"Tool {name} completed successfully")
            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            logger.error(f"Tool {name} failed: {str(e)}")
            # Fire-and-forget: log failed tool invocation
            task = asyncio.create_task(
                _send_tool_log(name, arguments, {"error": str(e)}, is_error=True)
            )
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    # Start stdio-based MCP server
    logger.info("🚀 Aiera MCP Server ready!")
    logger.info("📡 Transport: stdio (JSON-RPC over stdin/stdout)")
    logger.info(f"🔧 Tools enabled: {len(tool_registry)}")

    options = server.create_initialization_options()
    async with stdio_server() as (reader, writer):
        logger.info("✅ stdio server started - ready for MCP client connections")
        await server.run(reader, writer, options, raise_exceptions=True)


def run(transport: str = "stdio"):
    """Run the MCP server (for standalone usage)."""
    if transport != "stdio":
        raise ValueError("Only stdio transport is currently supported")

    import asyncio

    asyncio.run(run_server())
