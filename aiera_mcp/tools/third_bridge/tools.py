#!/usr/bin/env python3

"""Third Bridge event tools for Aiera MCP."""

import logging

from .models import (
    FindThirdBridgeEventsArgs,
    GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse,
    GetThirdBridgeEventResponse,
)
from ..base import get_http_client, make_aiera_request
from ... import get_api_key

# Setup logging
logger = logging.getLogger(__name__)


async def find_third_bridge_events(
    args: FindThirdBridgeEventsArgs,
) -> FindThirdBridgeEventsResponse:
    """Find expert insight events from Third Bridge, filtering by a date range and (optionally) by ticker, index, watchlist, sector, or subsector.

    RECOMMENDED: It is highly recommended to include at least one parameter that identifies equity(s), such as bloomberg_ticker, watchlist_id, index_id, sector_id, or subsector_id.
    """
    logger.info("tool called: find_third_bridge_events")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "false"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
        api_key=api_key,
        params=params,
    )

    response = FindThirdBridgeEventsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_third_bridge_event(
    args: GetThirdBridgeEventArgs,
) -> GetThirdBridgeEventResponse:
    """Retrieve an expert insight event from Third Bridge, including agenda, insights, transcript, and other metadata."""
    logger.info("tool called: get_third_bridge_event")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True, by_alias=True)
    params["include_transcripts"] = "true"

    # Handle special field mapping: event_id -> event_ids
    if "event_id" in params:
        params["event_ids"] = str(params.pop("event_id"))

    # Handle special field mapping: aiera_event_id -> aiera_event_ids
    if "aiera_event_id" in params:
        params["aiera_event_ids"] = str(params.pop("aiera_event_id"))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
        api_key=api_key,
        params=params,
    )

    response = GetThirdBridgeEventResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
