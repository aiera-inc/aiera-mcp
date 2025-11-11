#!/usr/bin/env python3

"""Third Bridge event tools for Aiera MCP."""

import logging
from typing import Any, Dict
from datetime import datetime

from .models import (
    FindThirdBridgeEventsArgs,
    GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse,
    GetThirdBridgeEventResponse,
    ThirdBridgeEventItem,
    ThirdBridgeEventDetails
)
from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from ..common.models import CitationInfo

# Setup logging
logger = logging.getLogger(__name__)


async def find_third_bridge_events(args: FindThirdBridgeEventsArgs) -> FindThirdBridgeEventsResponse:
    """Find expert insight events from Third Bridge, filtering by a date range and (optionally) by ticker, index, watchlist, sector, or subsector."""
    logger.info("tool called: find_third_bridge_events")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "false"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
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
        # Parse event date safely
        event_date = None
        try:
            if event_data.get("event_date"):
                event_date = datetime.fromisoformat(event_data["event_date"].replace("Z", "+00:00"))
            else:
                event_date = datetime.now()
        except (ValueError, AttributeError):
            event_date = datetime.now()

        event_item = ThirdBridgeEventItem(
            event_id=str(event_data.get("id", "")),
            title=event_data.get("title", ""),
            company_name=event_data.get("company_name"),
            event_date=event_date,
            expert_name=event_data.get("expert_name"),
            expert_title=event_data.get("expert_title")
        )
        events.append(event_item)

        # Add citation if we have URL information
        if event_data.get("url"):
            citations.append(CitationInfo(
                title=f"Third Bridge: {event_data.get('title', '')}",
                url=event_data.get("url"),
                timestamp=event_date
            ))

    return FindThirdBridgeEventsResponse(
        events=events,
        total=total_count,
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_third_bridge_event(args: GetThirdBridgeEventArgs) -> GetThirdBridgeEventResponse:
    """Retrieve an expert insight events from Third Bridge, including agenda, insights, transcript, and other metadata."""
    logger.info("tool called: get_third_bridge_event")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "true"

    # Handle special field mapping: event_id -> event_ids
    if 'event_id' in params:
        params['event_ids'] = str(params.pop('event_id'))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
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
        raise ValueError(f"Third Bridge event not found: {args.event_id}")

    event_data = events_data[0]  # Get the first (and should be only) event

    # Parse event date safely
    event_date = None
    try:
        if event_data.get("event_date"):
            event_date = datetime.fromisoformat(event_data["event_date"].replace("Z", "+00:00"))
        else:
            event_date = datetime.now()
    except (ValueError, AttributeError):
        event_date = datetime.now()

    # Build detailed event
    event_details = ThirdBridgeEventDetails(
        event_id=str(event_data.get("id", "")),
        title=event_data.get("title", ""),
        company_name=event_data.get("company_name"),
        event_date=event_date,
        expert_name=event_data.get("expert_name"),
        expert_title=event_data.get("expert_title"),
        agenda=event_data.get("agenda"),
        insights=event_data.get("insights"),
        transcript=event_data.get("transcript")
    )

    # Build citation
    citations = []
    if event_data.get("url"):
        citations.append(CitationInfo(
            title=f"Third Bridge: {event_data.get('title', '')}",
            url=event_data.get("url"),
            timestamp=event_date
        ))

    return GetThirdBridgeEventResponse(
        event=event_details,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


# Legacy registration functions removed - all tools now registered via registry
