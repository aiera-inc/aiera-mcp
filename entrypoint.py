#!/usr/bin/env python
import os
from aiera_mcp import server


def transport():
    """
    Determine the transport type for the MCP server.
    Defaults to 'streamable-http' if not set in environment variables.
    """
    mcp_transport_str = os.environ.get("MCP_TRANSPORT", "streamable-http")

    # These are currently the only supported transports
    supported_transports = {
        "stdio": "stdio",
        "sse": "sse",
        "streamable-http": "streamable-http",
    }

    return supported_transports.get(mcp_transport_str, "streamable-http")


if __name__ == "__main__":
    server.run(transport=transport())