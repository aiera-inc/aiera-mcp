#!/usr/bin/env python
"""
MCP Server Entrypoint

This script starts the Aiera MCP server with the specified transport.

Transport Types:
- stdio (default): Communication via stdin/stdout (recommended for local use)
- sse: Server-Sent Events (HTTP-based streaming)
- streamable-http: HTTP with streaming support

Set transport via environment variable:
    MCP_TRANSPORT=stdio python entrypoint.py    # Default
    MCP_TRANSPORT=sse python entrypoint.py
"""
import os
from aiera_mcp import server

# Default transport - stdio is recommended for local development
DEFAULT_TRANSPORT = "stdio"


def transport():
    """
    Determine the transport type for the MCP server.

    Returns:
        str: Transport type ('stdio', 'sse', or 'streamable-http')

    Environment:
        MCP_TRANSPORT: Override default transport (default: 'stdio')
    """
    mcp_transport_str = os.environ.get("MCP_TRANSPORT", DEFAULT_TRANSPORT)

    # Supported transports
    supported_transports = {
        "stdio": "stdio",
        "sse": "sse",
        "streamable-http": "streamable-http",
    }

    # Return requested transport or fall back to default
    return supported_transports.get(mcp_transport_str, DEFAULT_TRANSPORT)


if __name__ == "__main__":
    server.run(transport=transport())
