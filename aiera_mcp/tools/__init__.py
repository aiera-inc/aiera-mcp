#!/usr/bin/env python3

"""Aiera MCP Tools package."""

from mcp.server.fastmcp import FastMCP

from .events import register_events_tools
from .filings import register_filings_tools
from .equities import register_equities_tools
from .company_docs import register_company_docs_tools
from .third_bridge import register_third_bridge_tools
from .transcrippets import register_transcrippets_tools

__all__ = [
    "register_all_tools",
    "register_events_tools",
    "register_filings_tools",
    "register_equities_tools",
    "register_company_docs_tools",
    "register_third_bridge_tools",
    "register_transcrippets_tools"
]


def register_all_tools(mcp_server: FastMCP) -> None:
    """Register all Aiera tools with FastMCP server."""
    register_events_tools(mcp_server)
    register_filings_tools(mcp_server)
    register_equities_tools(mcp_server)
    register_company_docs_tools(mcp_server)
    register_third_bridge_tools(mcp_server)
    register_transcrippets_tools(mcp_server)