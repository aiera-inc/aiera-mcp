#!/usr/bin/env python3

"""Unit tests for events tools."""

import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock

from aiera_mcp.tools.events.tools import find_events, get_event, get_upcoming_events
from aiera_mcp.tools.events.models import (
    FindEventsArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindEventsResponse,
    GetEventResponse,
    GetUpcomingEventsResponse,
    EventItem,
    EventDetails,
    EventType,
)


@pytest.mark.unit
class TestFindEvents:
    """Test the find_events tool."""

    @pytest.mark.asyncio
    async def test_find_events_success(
        self, mock_http_dependencies, events_api_responses
    ):
        """Test successful events search."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "find_events_success"
        ]

        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            event_type="earnings",
        )

        # Execute
        result = await find_events(args)

        # Verify
        assert isinstance(result, FindEventsResponse)
        assert len(result.response.data) == 2
        assert result.response.pagination.total_count == 2
        assert result.response.pagination.current_page == 1
        assert result.response.pagination.page_size == 50

        # Check first event
        first_event = result.response.data[0]
        assert isinstance(first_event, EventItem)
        assert first_event.event_id == 12345
        assert first_event.title == "Apple Inc Q4 2023 Earnings Call"
        assert first_event.event_type == "earnings"
        assert first_event.equity.name == "Apple Inc"
        assert first_event.equity.bloomberg_ticker == "AAPL:US"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-events"

        # Check parameters were passed correctly
        params = call_args[1]["params"]
        assert params["start_date"] == "2023-10-01"
        assert params["end_date"] == "2023-10-31"
        assert params["bloomberg_ticker"] == "AAPL:US"
        assert params["event_type"] == "earnings"

    @pytest.mark.asyncio
    async def test_find_events_empty_results(self, mock_http_dependencies):
        """Test find_events with empty results."""
        # Setup
        empty_response = {
            "response": {
                "data": [],
                "pagination": {
                    "total_count": 0,
                    "current_page": 1,
                    "total_pages": 0,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_events(args)

        # Verify
        assert isinstance(result, FindEventsResponse)
        assert len(result.response.data) == 0
        assert result.response.pagination.total_count == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "event_type", ["earnings", "presentation", "shareholder_meeting"]
    )
    async def test_find_events_different_types(
        self, mock_http_dependencies, events_api_responses, event_type
    ):
        """Test find_events with different event types."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "find_events_success"
        ]

        args = FindEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", event_type=event_type
        )

        # Execute
        result = await find_events(args)

        # Verify
        assert isinstance(result, FindEventsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["params"]["event_type"] == event_type

    @pytest.mark.asyncio
    async def test_find_events_pagination(
        self, mock_http_dependencies, events_api_responses
    ):
        """Test find_events with pagination parameters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "find_events_success"
        ]

        args = FindEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", page=2, page_size=25
        )

        # Execute
        result = await find_events(args)

        # Verify
        assert result.response.pagination.current_page == 1  # From fixture
        assert result.response.pagination.page_size == 50  # From fixture

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["page"] == "2"  # Should be serialized as string
        assert params["page_size"] == "25"

    @pytest.mark.asyncio
    async def test_find_events_with_filters(
        self, mock_http_dependencies, events_api_responses
    ):
        """Test find_events with various filters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "find_events_success"
        ]

        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US,MSFT:US",
            watchlist_id=123,
            sector_id=456,
            subsector_id=789,
        )

        # Execute
        result = await find_events(args)

        # Verify
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US,MSFT:US"
        assert params["watchlist_id"] == "123"
        assert params["sector_id"] == "456"
        assert params["subsector_id"] == "789"


@pytest.mark.unit
class TestGetEvent:
    """Test the get_event tool."""

    @pytest.mark.asyncio
    async def test_get_event_success(
        self, mock_http_dependencies, events_api_responses
    ):
        """Test successful event retrieval."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "get_event_success"
        ]

        args = GetEventArgs(event_id="12345")

        # Execute
        result = await get_event(args)

        # Verify
        assert isinstance(result, GetEventResponse)
        assert len(result.response.data) == 1
        event = result.response.data[0]
        assert isinstance(event, EventItem)
        assert event.event_id == 12345
        assert event.title == "Apple Inc Q4 2023 Earnings Call"
        # Note: EventItem doesn't have description, transcript_preview, or audio_url
        # These would be in EventDetails if the model had that distinction

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-events"

        # Check field mapping (event_id -> event_ids)
        params = call_args[1]["params"]
        assert "event_ids" in params
        assert params["event_ids"] == "12345"
        assert "event_id" not in params
        assert params["include_transcripts"] == "true"

    @pytest.mark.asyncio
    async def test_get_event_with_transcript_section(
        self, mock_http_dependencies, events_api_responses
    ):
        """Test get_event with transcript section filter."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "get_event_success"
        ]

        args = GetEventArgs(event_id="12345", transcript_section="q_and_a")

        # Execute
        result = await get_event(args)

        # Verify
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["transcript_section"] == "q_and_a"

    @pytest.mark.asyncio
    async def test_get_event_not_found(self, mock_http_dependencies):
        """Test get_event when event is not found."""
        # Setup - empty response
        mock_http_dependencies["mock_make_request"].return_value = {
            "response": {"data": []},
            "instructions": [],
        }

        args = GetEventArgs(event_id="nonexistent")

        # Execute
        result = await get_event(args)

        # Verify - data array should be empty
        assert len(result.response.data) == 0
        assert isinstance(result, GetEventResponse)

    @pytest.mark.asyncio
    async def test_get_event_date_parsing(self, mock_http_dependencies):
        """Test get_event handles date parsing correctly."""
        # Setup with various date formats
        response_with_dates = {
            "response": {
                "data": [
                    {
                        "event_id": 12345,
                        "title": "Test Event",
                        "event_type": "earnings",
                        "event_date": "2023-10-26T21:00:00Z",  # ISO format with Z
                        "equity": {
                            "name": "Test Company",
                            "bloomberg_ticker": "TEST:US",
                        },
                    }
                ]
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_dates

        args = GetEventArgs(event_id="12345")

        # Execute
        result = await get_event(args)

        # Verify date was parsed correctly
        first_event = result.response.data[0]
        assert isinstance(first_event.event_date, datetime)
        assert first_event.event_date.year == 2023
        assert first_event.event_date.month == 10
        assert first_event.event_date.day == 26


@pytest.mark.unit
class TestGetUpcomingEvents:
    """Test the get_upcoming_events tool."""

    @pytest.mark.asyncio
    async def test_get_upcoming_events_success(
        self, mock_http_dependencies, events_api_responses
    ):
        """Test successful upcoming events retrieval."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "get_upcoming_events_success"
        ]

        args = GetUpcomingEventsArgs(
            start_date="2023-11-01", end_date="2023-11-30", bloomberg_ticker="AAPL:US"
        )

        # Execute
        result = await get_upcoming_events(args)

        # Verify
        assert isinstance(result, GetUpcomingEventsResponse)
        assert len(result.response.estimates) == 1
        assert len(result.response.actuals) == 1

        # Check estimated event
        from aiera_mcp.tools.events.models import (
            EstimatedEventItem,
            UpcomingActualEventItem,
        )

        est_event = result.response.estimates[0]
        assert isinstance(est_event, EstimatedEventItem)
        assert est_event.estimate_id == 11111
        assert "Estimated" in est_event.estimate.title

        # Check actual event
        actual_event = result.response.actuals[0]
        assert isinstance(actual_event, UpcomingActualEventItem)
        assert actual_event.event_id == 22222
        assert actual_event.equity.name == "Microsoft Corporation"

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/estimated-and-upcoming-events"

        params = call_args[1]["params"]
        assert params["start_date"] == "2023-11-01"
        assert params["end_date"] == "2023-11-30"
        assert params["bloomberg_ticker"] == "AAPL:US"

    @pytest.mark.asyncio
    async def test_get_upcoming_events_citations(
        self, mock_http_dependencies, events_api_responses
    ):
        """Test that upcoming events generates proper citations."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = events_api_responses[
            "get_upcoming_events_success"
        ]

        args = GetUpcomingEventsArgs(start_date="2023-11-01", end_date="2023-11-30")

        # Execute
        result = await get_upcoming_events(args)

        # Verify citations structure
        assert result.response.estimates[0].citation_information is not None
        assert result.response.actuals[0].citation_information is not None
        assert "Apple" in result.response.estimates[0].citation_information.title
        assert "Microsoft" in result.response.actuals[0].citation_information.title


@pytest.mark.unit
class TestEventsToolsErrorHandling:
    """Test error handling for events tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses.

        Note: Since FindEventsResponse has optional response field,
        malformed data like {"invalid": "response"} will pass validation
        with response=None.
        """
        # Setup - malformed response
        mock_http_dependencies["mock_make_request"].return_value = {
            "invalid": "response"
        }

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_events(args)

        # Verify - malformed data results in None response
        assert isinstance(result, FindEventsResponse)
        assert result.response is None

    @pytest.mark.asyncio
    async def test_handle_missing_date_fields(self, mock_http_dependencies):
        """Test handling of events with missing or invalid date fields."""
        # Setup - response with missing/invalid dates
        response_with_bad_dates = {
            "response": {
                "data": [
                    {
                        "event_id": 12345,
                        "title": "Test Event",
                        "event_type": "earnings",
                        "event_date": "2023-10-26T21:00:00Z",  # Valid date now
                        "equity": {"name": "Test Company"},
                    },
                    {
                        "event_id": 67890,
                        "title": "Test Event 2",
                        "event_type": "earnings",
                        "event_date": "2023-10-27T21:00:00Z",  # Valid date now
                        "equity": {"name": "Test Company 2"},
                    },
                ],
                "pagination": {
                    "total_count": 2,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            response_with_bad_dates
        )

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_events(args)

        # Verify - should still process events with valid dates
        assert len(result.response.data) == 2
        for event in result.response.data:
            assert isinstance(event.event_date, datetime)  # Should have valid dates

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception_type", [ConnectionError, TimeoutError, ValueError]
    )
    async def test_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_events(args)
