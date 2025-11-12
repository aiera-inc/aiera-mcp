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

    # Return the structured response directly - no transformation needed
    # since FindThirdBridgeEventsResponse model now matches the actual API format
    return FindThirdBridgeEventsResponse.model_validate(raw_response)


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

    # Build detailed event using new API field names
    event_details = ThirdBridgeEventDetails(
        event_id=event_data.get("event_id", ""),
        content_type=event_data.get("content_type", ""),
        call_date=event_data.get("call_date", ""),
        title=event_data.get("title", ""),
        language=event_data.get("language", ""),
        agenda=event_data.get("agenda"),  # This should be Optional[str] in ThirdBridgeEventDetails
        insights=event_data.get("insights"),  # This should be Optional[str] in ThirdBridgeEventDetails
        citation_block=event_data.get("citation_block"),
        transcript=event_data.get("transcript")
    )

    # Build citation using citation_block from new API format
    citations = []
    citation_block = event_data.get("citation_block")
    if citation_block and citation_block.get("url"):
        # Parse the call_date for timestamp
        timestamp = None
        try:
            if event_data.get("call_date"):
                timestamp = datetime.fromisoformat(event_data["call_date"].replace("Z", "+00:00"))
            else:
                timestamp = datetime.now()
        except (ValueError, AttributeError):
            timestamp = datetime.now()

        citations.append(CitationInfo(
            title=f"Third Bridge: {citation_block.get('title', event_data.get('title', ''))}",
            url=citation_block.get("url"),
            timestamp=timestamp
        ))

    return GetThirdBridgeEventResponse(
        event=event_details,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


# Legacy registration functions removed - all tools now registered via registry
