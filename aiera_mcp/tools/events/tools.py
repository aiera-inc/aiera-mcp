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

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)
    params["include_transcripts"] = "false"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )

    # Return the structured response that matches the actual API format
    # Parse individual events to match new model structure
    if "response" in raw_response and "data" in raw_response["response"]:
        events_data = []
        for event_data in raw_response["response"]["data"]:
            # Parse event date
            event_date = datetime.now()
            if event_data.get("event_date"):
                try:
                    event_date = datetime.fromisoformat(event_data["event_date"].replace("Z", "+00:00"))
                except:
                    pass

            # Extract equity info in the format expected by EquityInfo model
            equity_info = None
            if "equity" in event_data:
                equity_data = event_data["equity"]
                if isinstance(equity_data, dict):
                    equity_info = {
                        "equity_id": equity_data.get("equity_id"),
                        "company_id": equity_data.get("company_id"),
                        "name": equity_data.get("name"),
                        "bloomberg_ticker": equity_data.get("bloomberg_ticker"),
                        "sector_id": equity_data.get("sector_id"),
                        "subsector_id": equity_data.get("subsector_id"),
                        "primary_equity": equity_data.get("primary_equity")
                    }

            # Create new event structure matching the actual response
            parsed_event = {
                "event_id": event_data.get("event_id"),
                "title": event_data.get("title", ""),
                "event_type": event_data.get("event_type", ""),
                "event_date": event_date,
                "equity": equity_info,
                "event_category": event_data.get("event_category"),
                "expected_language": event_data.get("expected_language"),
                "grouping": event_data.get("grouping"),
                "summary": event_data.get("summary"),
                "citation_information": event_data.get("citation_information")
            }
            events_data.append(parsed_event)

        raw_response["response"]["data"] = events_data

    return FindEventsResponse.model_validate(raw_response)


async def get_event(args: GetEventArgs) -> GetEventResponse:
    """Retrieve an event, including the summary, transcript, and other metadata. Optionally, you filter the transcripts by section ('presentation' or 'q_and_a')."""
    logger.info("tool called: get_event")

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
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )

    # Extract event data from the nested response structure
    if "response" in raw_response and "event" in raw_response["response"]:
        event_data = raw_response["response"]["event"]
    else:
        raise ValueError(f"Event not found: {args.event_id}")

    # Parse event date
    event_date = datetime.now()
    if event_data.get("event_date"):
        try:
            event_date = datetime.fromisoformat(event_data["event_date"].replace("Z", "+00:00"))
        except:
            pass

    # Extract equity info in the format expected by EquityInfo model
    equity_info = None
    if "equity" in event_data:
        equity_data = event_data["equity"]
        if isinstance(equity_data, dict):
            equity_info = {
                "equity_id": equity_data.get("equity_id"),
                "company_id": equity_data.get("company_id"),
                "name": equity_data.get("name"),
                "bloomberg_ticker": equity_data.get("bloomberg_ticker"),
                "sector_id": equity_data.get("sector_id"),
                "subsector_id": equity_data.get("subsector_id"),
                "primary_equity": equity_data.get("primary_equity")
            }

    # Create event details structure
    event_details_data = {
        "event_id": event_data.get("event_id"),
        "title": event_data.get("title", ""),
        "event_type": event_data.get("event_type", ""),
        "event_date": event_date,
        "equity": equity_info,
        "event_category": event_data.get("event_category"),
        "expected_language": event_data.get("expected_language"),
        "grouping": event_data.get("grouping"),
        "summary": event_data.get("summary"),
        "citation_information": event_data.get("citation_information"),
        "description": event_data.get("description"),
        "transcript_preview": event_data.get("transcript_preview"),
        "audio_url": event_data.get("audio_url")
    }

    event_details = EventDetails.model_validate(event_details_data)

    return GetEventResponse(
        event=event_details,
        instructions=raw_response.get("instructions", [])
    )


async def get_upcoming_events(args: GetUpcomingEventsArgs) -> GetUpcomingEventsResponse:
    """Retrieve confirmed and estimated upcoming events, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector."""
    logger.info("tool called: get_upcoming_events")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/estimated-and-upcoming-events",
        api_key=api_key,
        params=params,
    )

    # Parse the response structure for upcoming events (has estimates and actuals)
    def parse_event_list(event_list):
        """Parse a list of events to match the new model structure."""
        parsed_events = []
        for event_data in event_list:
            # Parse event date
            event_date = datetime.now()
            if event_data.get("event_date"):
                try:
                    event_date = datetime.fromisoformat(event_data["event_date"].replace("Z", "+00:00"))
                except:
                    pass

            # Extract equity info in the format expected by EquityInfo model
            equity_info = None
            if "equity" in event_data:
                equity_data = event_data["equity"]
                if isinstance(equity_data, dict):
                    equity_info = {
                        "equity_id": equity_data.get("equity_id"),
                        "company_id": equity_data.get("company_id"),
                        "name": equity_data.get("name"),
                        "bloomberg_ticker": equity_data.get("bloomberg_ticker"),
                        "sector_id": equity_data.get("sector_id"),
                        "subsector_id": equity_data.get("subsector_id"),
                        "primary_equity": equity_data.get("primary_equity")
                    }

            # Create new event structure matching the actual response
            parsed_event = {
                "event_id": event_data.get("event_id"),
                "title": event_data.get("title", ""),
                "event_type": event_data.get("event_type", ""),
                "event_date": event_date,
                "equity": equity_info,
                "event_category": event_data.get("event_category"),
                "expected_language": event_data.get("expected_language"),
                "grouping": event_data.get("grouping"),
                "summary": event_data.get("summary"),
                "citation_information": event_data.get("citation_information")
            }
            parsed_events.append(parsed_event)
        return parsed_events

    # Process the estimates and actuals lists
    if "response" in raw_response:
        response_data = raw_response["response"]
        if "estimates" in response_data:
            response_data["estimates"] = parse_event_list(response_data["estimates"])
        if "actuals" in response_data:
            response_data["actuals"] = parse_event_list(response_data["actuals"])

    return GetUpcomingEventsResponse.model_validate(raw_response)


# Legacy registration functions removed - all tools now registered via registry