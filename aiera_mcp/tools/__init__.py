#!/usr/bin/env python3

"""Aiera MCP Tools package."""

import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP

from .registry import (
    TOOL_REGISTRY,
    get_all_tool_names,
    validate_tool_names,
    suggest_similar_tools,
    get_categories,
    get_tools_by_category,
    get_tools_by_read_only,
    get_destructive_tools,
)

# Setup logging
logger = logging.getLogger(__name__)

__all__ = [
    "register_tools",
    "get_all_tool_names",
    "get_categories",
    "get_tools_by_category",
    "get_tools_by_read_only",
    "get_destructive_tools",
    "TOOL_REGISTRY"
]


def register_tools(
    mcp_server: FastMCP,
    include_tools: Optional[List[str]] = None,
    exclude_tools: Optional[List[str]] = None
) -> None:
    """Register Aiera tools with FastMCP server using centralized registry.

    Args:
        mcp_server: FastMCP server instance to register tools with
        include_tools: Optional list of tool names to include. If provided, only these tools will be registered.
        exclude_tools: Optional list of tool names to exclude. If provided, all tools except these will be registered.

    Raises:
        ValueError: If invalid tool names are provided or if both include and exclude are specified.

    Examples:
        # Register all tools (default behavior)
        register_tools(mcp)

        # Register only specific tools
        register_tools(mcp, include_tools=['find_events', 'get_event'])

        # Register all except specific tools
        register_tools(mcp, exclude_tools=['delete_transcrippet'])
    """
    # Validate parameters
    if include_tools is not None and exclude_tools is not None:
        raise ValueError("Cannot specify both include_tools and exclude_tools. Please use only one.")

    # Determine which tools to register
    tools_to_register = TOOL_REGISTRY.copy()

    if include_tools is not None:
        # Validate include_tools
        valid_tools, invalid_tools = validate_tool_names(include_tools)
        if invalid_tools:
            error_msg = f"Invalid tool names in include_tools: {invalid_tools}\n"
            error_msg += "Available tools: " + ", ".join(sorted(get_all_tool_names()))

            # Add suggestions for invalid tools
            suggestions = []
            for invalid_tool in invalid_tools:
                similar = suggest_similar_tools(invalid_tool)
                if similar:
                    suggestions.append(f"{invalid_tool} -> {similar}")
            if suggestions:
                error_msg += "\nDid you mean: " + "; ".join(suggestions)

            raise ValueError(error_msg)

        # Filter to only include specified tools
        tools_to_register = {name: config for name, config in TOOL_REGISTRY.items() if name in valid_tools}
        logger.info(f"Registering {len(tools_to_register)} tools: {sorted(tools_to_register.keys())}")

    elif exclude_tools is not None:
        # Validate exclude_tools
        valid_tools, invalid_tools = validate_tool_names(exclude_tools)
        if invalid_tools:
            error_msg = f"Invalid tool names in exclude_tools: {invalid_tools}\n"
            error_msg += "Available tools: " + ", ".join(sorted(get_all_tool_names()))

            # Add suggestions for invalid tools
            suggestions = []
            for invalid_tool in invalid_tools:
                similar = suggest_similar_tools(invalid_tool)
                if similar:
                    suggestions.append(f"{invalid_tool} -> {similar}")
            if suggestions:
                error_msg += "\nDid you mean: " + "; ".join(suggestions)

            raise ValueError(error_msg)

        # Filter to exclude specified tools
        tools_to_register = {name: config for name, config in TOOL_REGISTRY.items() if name not in valid_tools}
        logger.info(f"Registering {len(tools_to_register)} tools (excluded {len(valid_tools)}): {sorted(tools_to_register.keys())}")

    else:
        # Register all tools (default behavior)
        logger.info(f"Registering all {len(tools_to_register)} available tools")

    # Register the selected tools
    for tool_name, tool_config in tools_to_register.items():
        # Create a closure that captures the current tool configuration
        def create_tool_wrapper(config):
            async def tool_wrapper(args: Dict[str, Any]) -> Dict[str, Any]:
                # Parse arguments using the Pydantic model from registry
                parsed_args = config['args_model'](**args)
                # Call the actual function with parsed arguments
                return await config['function'](parsed_args)
            return tool_wrapper

        # Register the tool with FastMCP
        mcp_server.tool(
            name=tool_name,
            description=tool_config['description']
        )(create_tool_wrapper(tool_config))

        logger.debug(f"Registered tool: {tool_name}")