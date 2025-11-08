#!/usr/bin/env python3

"""Event tools for Aiera MCP."""

import logging
from datetime import datetime

from .models import (
    FindEventsArgs, GetEventArgs, GetUpcomingEventsArgs,
    FindEventsResponse, GetEventResponse, GetUpcomingEventsResponse,
    EventItem, EventDetails, EventType
)
from ..common.models import CitationInfo
from ..base import get_http_client, get_api_key_from_context, make_aiera_request

# Setup logging
logger = logging.getLogger(__name__)


async def find_events(args: FindEventsArgs) -> FindEventsResponse:
    """Find events, filtered by a date range, and (optionally) ticker(s), watchlist, index, sector, or subsector; or event type(s)."""
    logger.info("tool called: find_events")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "false"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        events_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        events_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(events_data))

    events = []
    citations = []

    for event_data in events_data:
        # Extract event information
        # Try different field names for event ID
        event_id = event_data.get("event_id") or event_data.get("id") or ""
        event_item = EventItem(
            event_id=str(event_id),
            title=event_data.get("title", ""),
            event_type=EventType(event_data.get("event_type", "earnings")),
            event_date=datetime.fromisoformat(event_data.get("event_date").replace("Z", "+00:00")) if event_data.get("event_date") else datetime.now(),
            company_name=event_data.get("company_name"),
            ticker=event_data.get("ticker"),
            event_status=event_data.get("status")
        )
        events.append(event_item)

        # Add citation if we have URL information
        if event_data.get("url"):
            citations.append(CitationInfo(
                title=event_data.get("title"),
                url=event_data.get("url"),
                timestamp=event_item.event_date
            ))

    return FindEventsResponse(
        events=events,
        total=total_count,
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_event(args: GetEventArgs) -> GetEventResponse:
    """Retrieve an event, including the summary, transcript, and other metadata. Optionally, you filter the transcripts by section ('presentation' or 'q_and_a')."""
    logger.info("tool called: get_event")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "true"

    # Handle special field mapping: event_id -> event_ids
    if 'event_id' in params:
        params['event_ids'] = str(params.pop('event_id'))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        events_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        events_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(events_data))

    if not events_data:
        raise ValueError(f"Event not found: {args.event_id}")

    event_data = events_data[0]  # Get the first (and should be only) event

    # Build detailed event
    # Try different field names for event ID
    event_id = event_data.get("event_id") or event_data.get("id") or ""
    event_details = EventDetails(
        event_id=str(event_id),
        title=event_data.get("title", ""),
        event_type=EventType(event_data.get("event_type", "earnings")),
        event_date=datetime.fromisoformat(event_data.get("event_date").replace("Z", "+00:00")) if event_data.get("event_date") else datetime.now(),
        company_name=event_data.get("company_name"),
        ticker=event_data.get("ticker"),
        event_status=event_data.get("status"),
        description=event_data.get("description"),
        transcript_preview=event_data.get("transcript_preview"),
        audio_url=event_data.get("audio_url")
    )

    # Build citation
    citations = []
    if event_data.get("url"):
        citations.append(CitationInfo(
            title=event_data.get("title"),
            url=event_data.get("url"),
            timestamp=event_details.event_date
        ))

    return GetEventResponse(
        event=event_details,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_upcoming_events(args: GetUpcomingEventsArgs) -> GetUpcomingEventsResponse:
    """Retrieve confirmed and estimated upcoming events, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector."""
    logger.info("tool called: get_upcoming_events")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/estimated-and-upcoming-events",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        events_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        events_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(events_data))

    events = []
    citations = []

    for event_data in events_data:
        # Extract event information
        # Try different field names for event ID
        event_id = event_data.get("event_id") or event_data.get("id") or ""
        event_item = EventItem(
            event_id=str(event_id),
            title=event_data.get("title", ""),
            event_type=EventType(event_data.get("event_type", "earnings")),
            event_date=datetime.fromisoformat(event_data.get("event_date").replace("Z", "+00:00")) if event_data.get("event_date") else datetime.now(),
            company_name=event_data.get("company_name"),
            ticker=event_data.get("ticker"),
            event_status=event_data.get("status", "upcoming")
        )
        events.append(event_item)

        # Add citation if we have URL information
        if event_data.get("url"):
            citations.append(CitationInfo(
                title=event_data.get("title"),
                url=event_data.get("url"),
                timestamp=event_item.event_date
            ))

    return GetUpcomingEventsResponse(
        events=events,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


# Legacy registration functions removed - all tools now registered via registry