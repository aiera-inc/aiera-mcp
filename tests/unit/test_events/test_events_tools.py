#!/usr/bin/env python3

"""Unit tests for events tools."""

import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock

from aiera_mcp.tools.events.tools import find_events, get_event, get_upcoming_events
from aiera_mcp.tools.events.models import (
    FindEventsArgs, GetEventArgs, GetUpcomingEventsArgs,
    FindEventsResponse, GetEventResponse, GetUpcomingEventsResponse,
    EventItem, EventDetails, EventType
)


@pytest.mark.unit
class TestFindEvents:
    """Test the find_events tool."""

    @pytest.mark.asyncio
    async def test_find_events_success(self, mock_http_dependencies, events_api_responses):
        """Test successful events search."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["find_events_success"]

        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            event_type="earnings"
        )

        # Execute
        result = await find_events(args)

        # Verify
        assert isinstance(result, FindEventsResponse)
        assert len(result.events) == 2
        assert result.total == 2
        assert result.page == 1
        assert result.page_size == 50

        # Check first event
        first_event = result.events[0]
        assert isinstance(first_event, EventItem)
        assert first_event.event_id == "event123"
        assert first_event.title == "Apple Inc Q4 2023 Earnings Call"
        assert first_event.event_type == EventType.EARNINGS
        assert first_event.company_name == "Apple Inc"
        assert first_event.ticker == "AAPL"

        # Check API call was made correctly
        mock_http_dependencies['mock_make_request'].assert_called_once()
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-events"

        # Check parameters were passed correctly
        params = call_args[1]['params']
        assert params['start_date'] == "2023-10-01"
        assert params['end_date'] == "2023-10-31"
        assert params['bloomberg_ticker'] == "AAPL:US"
        assert params['event_type'] == "earnings"

    @pytest.mark.asyncio
    async def test_find_events_empty_results(self, mock_http_dependencies):
        """Test find_events with empty results."""
        # Setup
        empty_response = {
            "response": {"data": [], "total": 0},
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_events(args)

        # Verify
        assert isinstance(result, FindEventsResponse)
        assert len(result.events) == 0
        assert result.total == 0
        assert len(result.citation_information) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("event_type", ["earnings", "presentation", "shareholder_meeting"])
    async def test_find_events_different_types(self, mock_http_dependencies, events_api_responses, event_type):
        """Test find_events with different event types."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["find_events_success"]

        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            event_type=event_type
        )

        # Execute
        result = await find_events(args)

        # Verify
        assert isinstance(result, FindEventsResponse)
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['params']['event_type'] == event_type

    @pytest.mark.asyncio
    async def test_find_events_pagination(self, mock_http_dependencies, events_api_responses):
        """Test find_events with pagination parameters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["find_events_success"]

        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            page=2,
            page_size=25
        )

        # Execute
        result = await find_events(args)

        # Verify
        assert result.page == 2
        assert result.page_size == 25

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"  # Should be serialized as string
        assert params['page_size'] == "25"

    @pytest.mark.asyncio
    async def test_find_events_with_filters(self, mock_http_dependencies, events_api_responses):
        """Test find_events with various filters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["find_events_success"]

        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US,MSFT:US",
            watchlist_id=123,
            sector_id=456,
            subsector_id=789
        )

        # Execute
        result = await find_events(args)

        # Verify
        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['bloomberg_ticker'] == "AAPL:US,MSFT:US"
        assert params['watchlist_id'] == "123"
        assert params['sector_id'] == "456"
        assert params['subsector_id'] == "789"


@pytest.mark.unit
class TestGetEvent:
    """Test the get_event tool."""

    @pytest.mark.asyncio
    async def test_get_event_success(self, mock_http_dependencies, events_api_responses):
        """Test successful event retrieval."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["get_event_success"]

        args = GetEventArgs(event_id="event123")

        # Execute
        result = await get_event(args)

        # Verify
        assert isinstance(result, GetEventResponse)
        assert isinstance(result.event, EventDetails)
        assert result.event.event_id == "event123"
        assert result.event.title == "Apple Inc Q4 2023 Earnings Call"
        assert result.event.description == "Apple Inc quarterly earnings call for Q4 2023"
        assert result.event.transcript_preview is not None
        assert result.event.audio_url == "https://example.com/audio/event123.mp3"

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-events"

        # Check field mapping (event_id -> event_ids)
        params = call_args[1]['params']
        assert 'event_ids' in params
        assert params['event_ids'] == "event123"
        assert 'event_id' not in params
        assert params['include_transcripts'] == "true"

    @pytest.mark.asyncio
    async def test_get_event_with_transcript_section(self, mock_http_dependencies, events_api_responses):
        """Test get_event with transcript section filter."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["get_event_success"]

        args = GetEventArgs(event_id="event123", transcript_section="q_and_a")

        # Execute
        result = await get_event(args)

        # Verify
        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['transcript_section'] == "q_and_a"

    @pytest.mark.asyncio
    async def test_get_event_not_found(self, mock_http_dependencies):
        """Test get_event when event is not found."""
        # Setup - empty response
        mock_http_dependencies['mock_make_request'].return_value = {
            "response": {"data": []},
            "instructions": []
        }

        args = GetEventArgs(event_id="nonexistent")

        # Execute & Verify
        with pytest.raises(ValueError, match="Event not found: nonexistent"):
            await get_event(args)

    @pytest.mark.asyncio
    async def test_get_event_date_parsing(self, mock_http_dependencies):
        """Test get_event handles date parsing correctly."""
        # Setup with various date formats
        response_with_dates = {
            "response": {
                "data": [
                    {
                        "id": "event123",
                        "title": "Test Event",
                        "event_type": "earnings",
                        "event_date": "2023-10-26T21:00:00Z",  # ISO format with Z
                        "company_name": "Test Company",
                        "ticker": "TEST",
                        "event_status": "confirmed"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_dates

        args = GetEventArgs(event_id="event123")

        # Execute
        result = await get_event(args)

        # Verify date was parsed correctly
        assert isinstance(result.event.event_date, datetime)
        assert result.event.event_date.year == 2023
        assert result.event.event_date.month == 10
        assert result.event.event_date.day == 26


@pytest.mark.unit
class TestGetUpcomingEvents:
    """Test the get_upcoming_events tool."""

    @pytest.mark.asyncio
    async def test_get_upcoming_events_success(self, mock_http_dependencies, events_api_responses):
        """Test successful upcoming events retrieval."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["find_events_success"]

        args = GetUpcomingEventsArgs(
            start_date="2023-11-01",
            end_date="2023-11-30",
            bloomberg_ticker="AAPL:US"
        )

        # Execute
        result = await get_upcoming_events(args)

        # Verify
        assert isinstance(result, GetUpcomingEventsResponse)
        assert len(result.events) == 2
        assert all(isinstance(event, EventItem) for event in result.events)

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-events"

        params = call_args[1]['params']
        assert params['upcoming_only'] == "true"
        assert params['start_date'] == "2023-11-01"
        assert params['end_date'] == "2023-11-30"
        assert params['bloomberg_ticker'] == "AAPL:US"

    @pytest.mark.asyncio
    async def test_get_upcoming_events_citations(self, mock_http_dependencies, events_api_responses):
        """Test that upcoming events generates proper citations."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = events_api_responses["find_events_success"]

        args = GetUpcomingEventsArgs(start_date="2023-11-01", end_date="2023-11-30")

        # Execute
        result = await get_upcoming_events(args)

        # Verify citations were created
        assert len(result.citation_information) == 2
        first_citation = result.citation_information[0]
        assert first_citation.title.startswith("Upcoming:")
        assert "Apple Inc" in first_citation.title
        assert first_citation.source == "Aiera"
        assert first_citation.timestamp is not None


@pytest.mark.unit
class TestEventsToolsErrorHandling:
    """Test error handling for events tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response
        mock_http_dependencies['mock_make_request'].return_value = {"invalid": "response"}

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_events(args)

        # Verify - should handle gracefully with empty results
        assert isinstance(result, FindEventsResponse)
        assert len(result.events) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_handle_missing_date_fields(self, mock_http_dependencies):
        """Test handling of events with missing or invalid date fields."""
        # Setup - response with missing/invalid dates
        response_with_bad_dates = {
            "response": {
                "data": [
                    {
                        "id": "event123",
                        "title": "Test Event",
                        "event_type": "earnings",
                        "event_date": "invalid-date",  # Invalid date
                        "company_name": "Test Company"
                    },
                    {
                        "id": "event456",
                        "title": "Test Event 2",
                        "event_type": "earnings",
                        # Missing event_date
                        "company_name": "Test Company 2"
                    }
                ],
                "total": 2
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_bad_dates

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_events(args)

        # Verify - should still process events with fallback dates
        assert len(result.events) == 2
        for event in result.events:
            assert isinstance(event.event_date, datetime)  # Should have fallback date

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, TimeoutError, ValueError])
    async def test_network_errors_propagate(self, mock_http_dependencies, exception_type):
        """Test that network errors are properly propagated."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies['mock_make_request'].side_effect = exception_type("Test error")

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_events(args)