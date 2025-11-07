#!/usr/bin/env python3

"""Event-related tools for Aiera MCP."""

import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .utils import correct_bloomberg_ticker, correct_event_type

# Setup logging
logger = logging.getLogger(__name__)

# Default pagination settings
DEFAULT_PAGE_SIZE = 50


async def find_events(
    start_date: str,
    end_date: str,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
    event_type: Optional[str] = "earnings",
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Find events, filtered by a date range, and (optionally) ticker(s), watchlist, index, sector, or subsector; or event type(s)."""
    logger.info("tool called: find_events")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "include_transcripts": False,
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

    if event_type:
        params["event_type"] = correct_event_type(event_type)

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )


async def get_event(
    event_id: str,
    transcript_section: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve an event, including the summary, transcript, and other metadata. Optionally, you filter the transcripts by section ('presentation' or 'q_and_a')."""
    logger.info("tool called: get_event")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "event_ids": str(event_id),
        "include_transcripts": True,
    }

    if transcript_section:
        params["transcript_section"] = transcript_section

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )


async def get_upcoming_events(
    start_date,
    end_date,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve confirmed and estimated upcoming events, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector."""
    logger.info("tool called: get_upcoming_events")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "start_date": start_date,
        "end_date": end_date,
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

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/estimated-and-upcoming-events",
        api_key=api_key,
        params=params,
    )


def register_events_tools(mcp_server: FastMCP) -> None:
    """Register event-related tools with FastMCP server."""

    @mcp_server.tool(
        name="find_events",
        description="Finds company events using search filters including date, event type, company, sectors, and more.",
        annotations={
            "title": "Find Events",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def find_events_tool(
        start_date: str,
        end_date: str,
        bloomberg_ticker: Optional[str] = None,
        watchlist_id: Optional[int] = None,
        index_id: Optional[int] = None,
        sector_id: Optional[int] = None,
        subsector_id: Optional[int] = None,
        event_type: Optional[str] = "earnings",
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        return await find_events(start_date, end_date, bloomberg_ticker, watchlist_id, index_id, sector_id, subsector_id, event_type, page, page_size)

    @mcp_server.tool(
        name="get_event",
        description="Returns the details of an event given its identifier.",
        annotations={
            "title": "Get Event",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_event_tool(
        event_id: str,
        transcript_section: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await get_event(event_id, transcript_section)

    @mcp_server.tool(
        name="get_upcoming_events",
        description="Returns upcoming events of a specific type that match provided filters.",
        annotations={
            "title": "Get Upcoming Events",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_upcoming_events_tool(
        start_date,
        end_date,
        bloomberg_ticker: Optional[str] = None,
        watchlist_id: Optional[int] = None,
        index_id: Optional[int] = None,
        sector_id: Optional[int] = None,
        subsector_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        return await get_upcoming_events(start_date, end_date, bloomberg_ticker, watchlist_id, index_id, sector_id, subsector_id)