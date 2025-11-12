#!/usr/bin/env python3

"""Aiera MCP Tools package."""

import logging

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
    "get_all_tool_names",
    "get_categories",
    "get_tools_by_category",
    "get_tools_by_read_only",
    "get_destructive_tools",
    "TOOL_REGISTRY",
]

# Note: Tool registration is now handled directly in server.py
# using the standard MCP server approach for better schema control
