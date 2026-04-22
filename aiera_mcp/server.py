#!/usr/bin/env python3

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


def get_instructions() -> str:
    """Provide server-level instructions for the Aiera MCP server."""
    return """Aiera financial data API for institutional finance professionals.

CRITICAL — Before calling any other tools, you MUST:
1. Call `get_core_instructions` to retrieve baseline instructions for tool selection, data interpretation, and response composition.
2. Call `get_grammar_template` with `template_type='general'` to retrieve response formatting rules.

These two calls provide all the guidance needed to use the remaining tools effectively.
"""


# Initialize standard MCP server
server = Server("Aiera", instructions=get_instructions())

# Base configuration - these are now loaded from settings
# but kept as module-level constants for backward compatibility
_settings = get_settings()
DEFAULT_PAGE_SIZE = _settings.default_page_size
DEFAULT_MAX_PAGE_SIZE = _settings.default_max_page_size


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

            logger.info(f"Tool {name} completed successfully")
            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            logger.error(f"Tool {name} failed: {str(e)}")
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
