#!/usr/bin/env python3

"""Event tools for Aiera MCP."""

import logging

from .models import (
    FindEventsArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindEventsResponse,
    GetEventResponse,
    GetUpcomingEventsResponse,
    EventItem,
    EventType,
)
from ..common.models import CitationInfo
from ..base import get_http_client, make_aiera_request
from ... import get_api_key

# Setup logging
logger = logging.getLogger(__name__)


async def find_events(args: FindEventsArgs) -> FindEventsResponse:
    """Find events, filtered by a date range, and (optionally) ticker(s), watchlist, index, sector, or subsector; or event type(s)."""
    logger.info("tool called: find_events")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "false"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )

    # Pydantic validators will automatically parse datetime strings and nested objects
    return FindEventsResponse.model_validate(raw_response)


async def get_event(args: GetEventArgs) -> GetEventResponse:
    """Retrieve an event, including the summary, transcript, and other metadata. Optionally, you filter the transcripts by section ('presentation' or 'q_and_a')."""
    logger.info("tool called: get_event")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "true"

    # Handle special field mapping: event_id -> event_ids
    if "event_id" in params:
        params["event_ids"] = str(params.pop("event_id"))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )

    # Pydantic validators will automatically parse datetime strings and nested objects
    return GetEventResponse.model_validate(raw_response)


async def get_upcoming_events(args: GetUpcomingEventsArgs) -> GetUpcomingEventsResponse:
    """Retrieve confirmed and estimated upcoming events, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector."""
    logger.info("tool called: get_upcoming_events")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/estimated-and-upcoming-events",
        api_key=api_key,
        params=params,
    )

    # Pydantic validators will automatically parse datetime strings and nested objects
    return GetUpcomingEventsResponse.model_validate(raw_response)


# Legacy registration functions removed - all tools now registered via registry
