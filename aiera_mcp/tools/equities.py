#!/usr/bin/env python3

"""Equity and company metadata tools for Aiera MCP."""

import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .utils import correct_bloomberg_ticker

# Setup logging
logger = logging.getLogger(__name__)

# Default pagination settings
DEFAULT_PAGE_SIZE = 50


async def find_equities(
    bloomberg_ticker: Optional[str] = None,
    isin: Optional[str] = None,
    ric: Optional[str] = None,
    ticker: Optional[str] = None,
    permid: Optional[str] = None,
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve equities, filtered by various identifiers, such as ticker, ISIN, or RIC; or by search."""
    logger.info("tool called: find_equities")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "include_company_metadata": "true",
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if isin:
        params["isin"] = isin

    if ric:
        params["ric"] = ric

    if ticker:
        params["ticker"] = ticker

    if permid:
        params["permid"] = permid

    if search:
        params["search"] = search

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-equities",
        api_key=api_key,
        params=params,
    )


async def get_sectors_and_subsectors() -> Dict[str, Any]:
    """Retrieve a list of all sectors and subsectors."""
    logger.info("tool called: get_sectors_and_subsectors")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-sectors-and-subsectors",
        api_key=api_key,
        params={},
    )


async def get_equity_summaries(bloomberg_ticker: str) -> Dict[str, Any]:
    """Retrieve detailed summary information about one or more equities, filtered by ticker(s)."""
    logger.info("tool called: get_equity_summaries")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "bloomberg_ticker": correct_bloomberg_ticker(bloomberg_ticker),
        "lookback": "90",
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/equity-summaries",
        api_key=api_key,
        params=params,
    )


async def get_available_indexes() -> Dict[str, Any]:
    """Retrieve the list of available indexes."""
    logger.info("tool called: get_available_indexes")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-indexes",
        api_key=api_key,
        params={},
    )


async def get_index_constituents(
    index: str,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve the list of all equities within an index."""
    logger.info("tool called: get_index_constituents")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {}

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/index-constituents/{index}",
        api_key=api_key,
        params=params,
    )


async def get_available_watchlists() -> Dict[str, Any]:
    """Retrieve the list of available watchlists."""
    logger.info("tool called: get_available_watchlists")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-watchlists",
        api_key=api_key,
        params={},
    )


async def get_watchlist_constituents(
    watchlist_id: str,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve the list of all equities within a watchlist."""
    logger.info("tool called: get_watchlist_constituents")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {}

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/watchlist-constituents/{watchlist_id}",
        api_key=api_key,
        params=params,
    )


def register_equities_tools(mcp_server: FastMCP) -> None:
    """Register equity and company metadata tools with FastMCP server."""

    @mcp_server.tool(
        name="find_equities",
        description="Finds companies/equities using search filters like company name, ticker, sector, and more.",
        annotations={
            "title": "Find Equities",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def find_equities_tool(
        bloomberg_ticker: Optional[str] = None,
        isin: Optional[str] = None,
        ric: Optional[str] = None,
        ticker: Optional[str] = None,
        permid: Optional[str] = None,
        search: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        return await find_equities(bloomberg_ticker, isin, ric, ticker, permid, search, page, page_size)

    @mcp_server.tool(
        name="get_sectors_and_subsectors",
        description="Returns the list of available sectors and their subsectors for filtering.",
        annotations={
            "title": "Get Sectors and Subsectors",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_sectors_and_subsectors_tool() -> Dict[str, Any]:
        return await get_sectors_and_subsectors()

    @mcp_server.tool(
        name="get_equity_summaries",
        description="Returns summary statistics for equities.",
        annotations={
            "title": "Get Equity Summaries",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_equity_summaries_tool(bloomberg_ticker: str) -> Dict[str, Any]:
        return await get_equity_summaries(bloomberg_ticker)

    @mcp_server.tool(
        name="get_available_indexes",
        description="Returns the list of available stock indexes.",
        annotations={
            "title": "Get Available Indexes",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_available_indexes_tool() -> Dict[str, Any]:
        return await get_available_indexes()

    @mcp_server.tool(
        name="get_index_constituents",
        description="Returns the constituents of a stock index.",
        annotations={
            "title": "Get Index Constituents",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_index_constituents_tool(
        index: str,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        return await get_index_constituents(index, page, page_size)

    @mcp_server.tool(
        name="get_available_watchlists",
        description="Returns the list of available watchlists.",
        annotations={
            "title": "Get Available Watchlists",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_available_watchlists_tool() -> Dict[str, Any]:
        return await get_available_watchlists()

    @mcp_server.tool(
        name="get_watchlist_constituents",
        description="Returns the constituents of a watchlist.",
        annotations={
            "title": "Get Watchlist Constituents",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_watchlist_constituents_tool(
        watchlist_id: str,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        return await get_watchlist_constituents(watchlist_id, page, page_size)