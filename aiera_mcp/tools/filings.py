#!/usr/bin/env python3

"""SEC filing tools for Aiera MCP."""

import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .utils import correct_bloomberg_ticker

# Setup logging
logger = logging.getLogger(__name__)

# Default pagination settings
DEFAULT_PAGE_SIZE = 50


async def find_filings(
    start_date: str,
    end_date: str,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
    form_number: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """Find SEC filings, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector; and (optionally) by a form number."""
    logger.info("tool called: find_filings")

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

    if form_number:
        params["form_number"] = form_number

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )


async def get_filing(filing_id: str) -> Dict[str, Any]:
    """Retrieve an SEC filing, including a summary and other metadata."""
    logger.info("tool called: get_filing")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "filing_ids": str(filing_id),
        "include_content": True,
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )


def register_filings_tools(mcp_server: FastMCP) -> None:
    """Register SEC filing tools with FastMCP server."""

    @mcp_server.tool(
        name="find_filings",
        description="Finds SEC filings using search filters including company, date, form type, and more.",
        annotations={
            "title": "Find Filings",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def find_filings_tool(
        start_date: str,
        end_date: str,
        bloomberg_ticker: Optional[str] = None,
        watchlist_id: Optional[int] = None,
        index_id: Optional[int] = None,
        sector_id: Optional[int] = None,
        subsector_id: Optional[int] = None,
        form_number: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE
    ) -> Dict[str, Any]:
        return await find_filings(start_date, end_date, bloomberg_ticker, watchlist_id, index_id, sector_id, subsector_id, form_number, page, page_size)

    @mcp_server.tool(
        name="get_filing",
        description="Returns the details of a filing given its identifier.",
        annotations={
            "title": "Get Filing",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_filing_tool(filing_id: str) -> Dict[str, Any]:
        return await get_filing(filing_id)