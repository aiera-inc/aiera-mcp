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
    from ..server import mcp
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
    api_data = raw_response.get("response", {})
    events_data = api_data.get("data", [])

    events = []
    citations = []

    for event_data in events_data:
        # Extract event information
        event_item = EventItem(
            event_id=str(event_data.get("id")),
            title=event_data.get("title", ""),
            event_type=EventType(event_data.get("event_type", "earnings")),
            event_date=datetime.fromisoformat(event_data.get("event_date").replace("Z", "+00:00")) if event_data.get("event_date") else datetime.now(),
            company_name=event_data.get("company_name"),
            company_ticker=event_data.get("ticker"),
            has_transcript=event_data.get("has_transcript", False),
            status=event_data.get("status")
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
        total=api_data.get("total", len(events)),
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_event(args: GetEventArgs) -> GetEventResponse:
    """Retrieve an event, including the summary, transcript, and other metadata. Optionally, you filter the transcripts by section ('presentation' or 'q_and_a')."""
    logger.info("tool called: get_event")

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

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    api_data = raw_response.get("response", {})
    events_data = api_data.get("data", [])

    if not events_data:
        raise ValueError(f"Event not found: {args.event_id}")

    event_data = events_data[0]  # Get the first (and should be only) event

    # Build event summary
    summary = None
    if event_data.get("summary"):
        summary = EventSummary(
            summary=event_data.get("summary"),
            key_topics=event_data.get("key_topics", []),
            speakers=event_data.get("speakers", [])
        )

    # Build transcript
    transcript = None
    if event_data.get("transcript"):
        transcript = EventTranscript(
            transcript_text=event_data.get("transcript", ""),
            sections=event_data.get("transcript_sections", []),
            word_count=len(event_data.get("transcript", "").split()) if event_data.get("transcript") else 0
        )

    # Build detailed event
    event_details = EventDetails(
        event_id=str(event_data.get("id")),
        title=event_data.get("title", ""),
        event_type=EventType(event_data.get("event_type", "earnings")),
        event_date=datetime.fromisoformat(event_data.get("event_date").replace("Z", "+00:00")) if event_data.get("event_date") else datetime.now(),
        company_name=event_data.get("company_name"),
        company_ticker=event_data.get("ticker"),
        has_transcript=bool(transcript),
        status=event_data.get("status"),
        summary=summary,
        transcript=transcript,
        audio_url=event_data.get("audio_url"),
        attachments=event_data.get("attachments", [])
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
    from ..server import mcp
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
    api_data = raw_response.get("response", {})
    events_data = api_data.get("data", [])

    events = []
    citations = []

    for event_data in events_data:
        # Extract event information
        event_item = EventItem(
            event_id=str(event_data.get("id")),
            title=event_data.get("title", ""),
            event_type=EventType(event_data.get("event_type", "earnings")),
            event_date=datetime.fromisoformat(event_data.get("event_date").replace("Z", "+00:00")) if event_data.get("event_date") else datetime.now(),
            company_name=event_data.get("company_name"),
            company_ticker=event_data.get("ticker"),
            has_transcript=event_data.get("has_transcript", False),
            status=event_data.get("status", "upcoming")
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