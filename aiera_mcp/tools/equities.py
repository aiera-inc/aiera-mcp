#!/usr/bin/env python3

"""Equity and company metadata tools for Aiera MCP."""

import logging
from typing import Any, Dict

from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .params import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    EmptyArgs,
    SearchArgs
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_equities(args: FindEquitiesArgs) -> Dict[str, Any]:
    """Retrieve equities, filtered by various identifiers, such as ticker, ISIN, or RIC; or by search."""
    logger.info("tool called: find_equities")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_company_metadata"] = "true"

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-equities",
        api_key=api_key,
        params=params,
    )


async def get_sectors_and_subsectors(args: SearchArgs) -> Dict[str, Any]:
    """Retrieve a list of all sectors and subsectors."""
    logger.info("tool called: get_sectors_and_subsectors")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-sectors-and-subsectors",
        api_key=api_key,
        params=params,
    )


async def get_equity_summaries(args: GetEquitySummariesArgs) -> Dict[str, Any]:
    """Retrieve detailed summary information about one or more equities, filtered by ticker(s)."""
    logger.info("tool called: get_equity_summaries")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["lookback"] = "90"

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/equity-summaries",
        api_key=api_key,
        params=params,
    )


async def get_available_indexes(args: EmptyArgs) -> Dict[str, Any]:
    """Retrieve the list of available indexes."""
    logger.info("tool called: get_available_indexes")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-indexes",
        api_key=api_key,
        params=params,
    )


async def get_index_constituents(args: GetIndexConstituentsArgs) -> Dict[str, Any]:
    """Retrieve the list of all equities within an index."""
    logger.info("tool called: get_index_constituents")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/index-constituents/{args.index}",
        api_key=api_key,
        params=params,
    )


async def get_available_watchlists(args: EmptyArgs) -> Dict[str, Any]:
    """Retrieve the list of available watchlists."""
    logger.info("tool called: get_available_watchlists")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-watchlists",
        api_key=api_key,
        params=params,
    )


async def get_watchlist_constituents(args: GetWatchlistConstituentsArgs) -> Dict[str, Any]:
    """Retrieve the list of all equities within a watchlist."""
    logger.info("tool called: get_watchlist_constituents")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/watchlist-constituents/{args.watchlist_id}",
        api_key=api_key,
        params=params,
    )


# Legacy registration functions removed - all tools now registered via registry
