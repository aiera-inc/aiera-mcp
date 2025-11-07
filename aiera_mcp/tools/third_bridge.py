#!/usr/bin/env python3

"""Third Bridge event tools for Aiera MCP."""

import logging
from typing import Any, Dict

from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .params import FindThirdBridgeEventsArgs, GetThirdBridgeEventArgs

# Setup logging
logger = logging.getLogger(__name__)


async def find_third_bridge_events(args: FindThirdBridgeEventsArgs) -> Dict[str, Any]:
    """Find expert insight events from Third Bridge, filtering by a date range and (optionally) by ticker, index, watchlist, sector, or subsector."""
    logger.info("tool called: find_third_bridge_events")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "false"

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
        api_key=api_key,
        params=params,
    )


async def get_third_bridge_event(args: GetThirdBridgeEventArgs) -> Dict[str, Any]:
    """Retrieve an expert insight events from Third Bridge, including agenda, insights, transcript, and other metadata."""
    logger.info("tool called: get_third_bridge_event")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "true"

    # Handle special field mapping: event_id -> event_ids
    if 'event_id' in params:
        params['event_ids'] = str(params.pop('event_id'))

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
        api_key=api_key,
        params=params,
    )


# Legacy registration functions removed - all tools now registered via registry
