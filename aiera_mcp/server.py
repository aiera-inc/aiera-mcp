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
    EmbeddedResource,
    TextResourceContents,
    Resource,
    ReadResourceResult,
    CallToolResult,
)
from aiera_mcp.tools.transcrippets.tools import get_transcrippet_template

# Setup logging
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
            tool_kwargs = {
                "name": tool_name,
                "description": tool_config["description"],
                "inputSchema": tool_config["input_schema"],
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

            tool = Tool(**tool_kwargs)

            # Add OpenAI-compatible metadata for transcrippet tools with UI
            if tool_name in ["find_transcrippets", "create_transcrippet"]:
                tool.annotations = {
                    "openai/outputTemplate": "ui://widget/transcrippet.html",
                    "openai/resultCanProduceWidget": True,
                    "openai/resultType": "structuredContent",
                }

            tools.append(tool)
        return tools

    @server.list_resources()
    async def list_resources() -> List[Resource]:
        """Register UI templates for OpenAI MCP compatibility."""
        return [
            Resource(
                uri="ui://widget/transcrippet.html",
                name="Transcrippet Viewer",
                mimeType="text/html+mcp",
                description="Interactive transcrippet player widget",
            )
        ]

    @server.read_resource()
    async def read_resource(uri: str) -> ReadResourceResult:
        """Serve UI templates for OpenAI MCP compatibility."""
        logger.info(f"Resource requested: {uri}")

        if uri == "ui://widget/transcrippet.html":

            template_html = get_transcrippet_template()
            return ReadResourceResult(
                contents=[
                    TextResourceContents(
                        uri=uri, mimeType="text/html+mcp", text=template_html
                    )
                ]
            )

        logger.error(f"Unknown resource URI: {uri}")
        raise ValueError(f"Unknown resource: {uri}")

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> CallToolResult:
        """Handle tool calls with support for both Claude MCP and OpenAI MCP formats."""
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
            import json

            result_text = (
                json.dumps(result_dict, indent=2)
                if not isinstance(result_dict, str)
                else result_dict
            )

            # Build the content list starting with the JSON response
            content_list: List[TextContent | EmbeddedResource] = [
                TextContent(type="text", text=result_text)
            ]

            # Add embedded UI resources for transcrippet tools (Claude MCP format)
            if name in ["find_transcrippets", "create_transcrippet"]:
                try:
                    from . import get_api_key
                    from .tools.transcrippets.tools import generate_transcrippet_ui_html

                    api_key = get_api_key()
                    if api_key:
                        # Extract transcrippets from response
                        transcrippets = []
                        if name == "find_transcrippets" and result_dict.get("response"):
                            transcrippets = result_dict["response"]
                        elif name == "create_transcrippet" and result_dict.get(
                            "response"
                        ):
                            transcrippets = [result_dict["response"]]

                        # Create embedded resources for Claude MCP
                        for transcrippet in transcrippets:
                            if transcrippet.get("transcrippet_guid"):
                                guid = transcrippet["transcrippet_guid"]
                                html_content = generate_transcrippet_ui_html(
                                    api_key, guid
                                )

                                # Create a unique URI for each transcrippet UI
                                uri = f"ui://transcrippet/{guid}"

                                embedded_resource = EmbeddedResource(
                                    type="resource",
                                    resource=TextResourceContents(
                                        uri=uri,
                                        mimeType="text/html+mcp",
                                        text=html_content,
                                    ),
                                )
                                content_list.append(embedded_resource)
                                logger.debug(
                                    f"Added embedded UI for transcrippet {guid}"
                                )
                except Exception as e:
                    logger.warning(f"Failed to add UI resources: {str(e)}")
                    # Continue without UI resources rather than failing

            logger.info(f"Tool {name} completed successfully")

            # Return CallToolResult with both content (for humans/Claude) and structuredContent (for OpenAI/machines)
            # This supports both Claude MCP (uses content with embedded resources) and OpenAI MCP (uses structuredContent)
            return CallToolResult(
                content=content_list, structuredContent=result_dict, isError=False
            )

        except Exception as e:
            logger.error(f"Tool {name} failed: {str(e)}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                isError=True,
            )

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
