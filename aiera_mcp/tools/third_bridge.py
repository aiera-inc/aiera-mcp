#!/usr/bin/env python3

"""Third Bridge event tools for Aiera MCP."""

import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .utils import correct_bloomberg_ticker

# Setup logging
logger = logging.getLogger(__name__)

# Default pagination settings
DEFAULT_PAGE_SIZE = 50


async def find_third_bridge_events(
    start_date: str,
    end_date: str,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Find expert insight events from Third Bridge, filtering by a date range and (optionally) by ticker, index, watchlist, sector, or subsector."""
    logger.info("tool called: find_third_bridge_events")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "include_transcripts": "false",
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if watchlist_id:
        params["watchlist_id"] = str(watchlist_id)

    if index_id:
        params["index_id"] = str(index_id)

    if sector_id:
        params["sector_id"] = str(sector_id)

    if subsector_id:
        params["subsector_id"] = str(subsector_id)

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
        api_key=api_key,
        params=params,
    )


async def get_third_bridge_event(event_id: str) -> Dict[str, Any]:
    """Retrieve an expert insight events from Third Bridge, including agenda, insights, transcript, and other metadata."""
    logger.info("tool called: get_third_bridge_event")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "event_ids": str(event_id),
        "include_transcripts": "true",
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
        api_key=api_key,
        params=params,
    )


def register_third_bridge_tools(mcp_server: FastMCP) -> None:
    """Register Third Bridge event tools with FastMCP server."""

    @mcp_server.tool(
        name="find_third_bridge_events",
        description="Finds Third Bridge events using search filters.",
        annotations={
            "title": "Find Third Bridge Events",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def find_third_bridge_events_tool(
        start_date: str,
        end_date: str,
        bloomberg_ticker: Optional[str] = None,
        watchlist_id: Optional[int] = None,
        index_id: Optional[int] = None,
        sector_id: Optional[int] = None,
        subsector_id: Optional[int] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        return await find_third_bridge_events(start_date, end_date, bloomberg_ticker, watchlist_id, index_id, sector_id, subsector_id, page, page_size)

    @mcp_server.tool(
        name="get_third_bridge_event",
        description="Returns the details of a Third Bridge event given its identifier.",
        annotations={
            "title": "Get Third Bridge Event",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_third_bridge_event_tool(event_id: str) -> Dict[str, Any]:
        return await get_third_bridge_event(event_id)