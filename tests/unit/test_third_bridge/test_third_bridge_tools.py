#!/usr/bin/env python3

"""Unit tests for third_bridge tools."""

import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock

from aiera_mcp.tools.third_bridge.tools import find_third_bridge_events, get_third_bridge_event
from aiera_mcp.tools.third_bridge.models import (
    FindThirdBridgeEventsArgs, GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse, GetThirdBridgeEventResponse,
    ThirdBridgeEventItem, ThirdBridgeEventDetails
)


@pytest.mark.unit
class TestFindThirdBridgeEvents:
    """Test the find_third_bridge_events tool."""

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_success(self, mock_http_dependencies, third_bridge_api_responses):
        """Test successful Third Bridge events search."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = third_bridge_api_responses["find_third_bridge_events_success"]

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US"
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        assert isinstance(result, FindThirdBridgeEventsResponse)
        assert len(result.events) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 50

        # Check first event
        first_event = result.events[0]
        assert isinstance(first_event, ThirdBridgeEventItem)
        assert first_event.event_id == "tb789"
        assert first_event.title == "Apple Supply Chain Analysis"
        assert first_event.company_name == "Apple Inc"
        assert first_event.expert_name == "Jane Smith"
        assert first_event.expert_title == "Former Apple Supply Chain Director"
        assert isinstance(first_event.event_date, datetime)

        # Check API call was made correctly
        mock_http_dependencies['mock_make_request'].assert_called_once()
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-third-bridge"

        # Check parameters were passed correctly
        params = call_args[1]['params']
        assert params['start_date'] == "2023-10-01"
        assert params['end_date'] == "2023-10-31"
        assert params['bloomberg_ticker'] == "AAPL:US"
        assert params['include_transcripts'] == "false"

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_empty_results(self, mock_http_dependencies):
        """Test find_third_bridge_events with empty results."""
        # Setup
        empty_response = {
            "response": {"data": [], "total": 0},
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        assert isinstance(result, FindThirdBridgeEventsResponse)
        assert len(result.events) == 0
        assert result.total == 0
        assert len(result.citation_information) == 0

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_pagination(self, mock_http_dependencies, third_bridge_api_responses):
        """Test find_third_bridge_events with pagination parameters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = third_bridge_api_responses["find_third_bridge_events_success"]

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            page=2,
            page_size=25
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        assert result.page == 2
        assert result.page_size == 25

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"  # Should be serialized as string
        assert params['page_size'] == "25"

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_with_filters(self, mock_http_dependencies, third_bridge_api_responses):
        """Test find_third_bridge_events with various filters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = third_bridge_api_responses["find_third_bridge_events_success"]

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US,MSFT:US",
            watchlist_id=123,
            sector_id=456,
            subsector_id=789
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['bloomberg_ticker'] == "AAPL:US,MSFT:US"
        assert params['watchlist_id'] == "123"
        assert params['sector_id'] == "456"
        assert params['subsector_id'] == "789"

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_date_parsing(self, mock_http_dependencies):
        """Test find_third_bridge_events handles date parsing correctly."""
        # Setup with various date formats
        response_with_dates = {
            "response": {
                "data": [
                    {
                        "id": "tb123",
                        "title": "Test Event",
                        "company_name": "Test Company",
                        "event_date": "2023-10-20T14:00:00Z",  # ISO format with Z
                        "expert_name": "Test Expert",
                        "expert_title": "Test Title"
                    }
                ],
                "total": 1
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_dates

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify date was parsed correctly
        assert len(result.events) == 1
        event = result.events[0]
        assert isinstance(event.event_date, datetime)
        assert event.event_date.year == 2023
        assert event.event_date.month == 10
        assert event.event_date.day == 20

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_citations(self, mock_http_dependencies, third_bridge_api_responses):
        """Test that find_third_bridge_events generates proper citations."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = third_bridge_api_responses["find_third_bridge_events_success"]

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify citations were created
        assert len(result.citation_information) == 1
        citation = result.citation_information[0]
        assert citation.title.startswith("Third Bridge:")
        assert "Apple Supply Chain Analysis" in citation.title
        assert citation.url == "https://thirdbridge.com/event/tb789"
        assert citation.timestamp is not None


@pytest.mark.unit
class TestGetThirdBridgeEvent:
    """Test the get_third_bridge_event tool."""

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_success(self, mock_http_dependencies):
        """Test successful Third Bridge event retrieval."""
        # Setup
        response_with_details = {
            "response": {
                "data": [
                    {
                        "id": "tb789",
                        "title": "Apple Supply Chain Analysis",
                        "company_name": "Apple Inc",
                        "event_date": "2023-10-20T14:00:00Z",
                        "expert_name": "Jane Smith",
                        "expert_title": "Former Apple Supply Chain Director",
                        "agenda": "Discussion of Apple's supply chain resilience and challenges",
                        "insights": "Key insights on Apple's supply chain management strategies",
                        "transcript": "Full transcript of the expert discussion...",
                        "url": "https://thirdbridge.com/event/tb789"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_details

        args = GetThirdBridgeEventArgs(event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify
        assert isinstance(result, GetThirdBridgeEventResponse)
        assert isinstance(result.event, ThirdBridgeEventDetails)
        assert result.event.event_id == "tb789"
        assert result.event.title == "Apple Supply Chain Analysis"
        assert result.event.company_name == "Apple Inc"
        assert result.event.expert_name == "Jane Smith"
        assert result.event.expert_title == "Former Apple Supply Chain Director"
        assert result.event.agenda is not None
        assert result.event.insights is not None
        assert result.event.transcript is not None

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-third-bridge"

        # Check field mapping (event_id -> event_ids)
        params = call_args[1]['params']
        assert 'event_ids' in params
        assert params['event_ids'] == "tb789"
        assert 'event_id' not in params
        assert params['include_transcripts'] == "true"

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_not_found(self, mock_http_dependencies):
        """Test get_third_bridge_event when event is not found."""
        # Setup - empty response
        mock_http_dependencies['mock_make_request'].return_value = {
            "response": {"data": []},
            "instructions": []
        }

        args = GetThirdBridgeEventArgs(event_id="nonexistent")

        # Execute & Verify
        with pytest.raises(ValueError, match="Third Bridge event not found: nonexistent"):
            await get_third_bridge_event(args)

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_date_parsing(self, mock_http_dependencies):
        """Test get_third_bridge_event handles date parsing correctly."""
        # Setup with missing event_date
        response_without_date = {
            "response": {
                "data": [
                    {
                        "id": "tb789",
                        "title": "Test Event",
                        "company_name": "Test Company",
                        # Missing event_date
                        "expert_name": "Test Expert",
                        "expert_title": "Test Title"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_without_date

        args = GetThirdBridgeEventArgs(event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify - should have fallback date
        assert isinstance(result.event.event_date, datetime)

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_invalid_date(self, mock_http_dependencies):
        """Test get_third_bridge_event handles invalid dates correctly."""
        # Setup with invalid event_date
        response_with_bad_date = {
            "response": {
                "data": [
                    {
                        "id": "tb789",
                        "title": "Test Event",
                        "company_name": "Test Company",
                        "event_date": "invalid-date",  # Invalid date
                        "expert_name": "Test Expert",
                        "expert_title": "Test Title"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_bad_date

        args = GetThirdBridgeEventArgs(event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify - should have fallback date
        assert isinstance(result.event.event_date, datetime)

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_citation(self, mock_http_dependencies):
        """Test that get_third_bridge_event generates proper citation."""
        # Setup
        response_with_url = {
            "response": {
                "data": [
                    {
                        "id": "tb789",
                        "title": "Apple Supply Chain Analysis",
                        "company_name": "Apple Inc",
                        "event_date": "2023-10-20T14:00:00Z",
                        "expert_name": "Jane Smith",
                        "expert_title": "Former Apple Supply Chain Director",
                        "url": "https://thirdbridge.com/event/tb789"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_url

        args = GetThirdBridgeEventArgs(event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify citation was created
        assert len(result.citation_information) == 1
        citation = result.citation_information[0]
        assert citation.title.startswith("Third Bridge:")
        assert "Apple Supply Chain Analysis" in citation.title
        assert citation.url == "https://thirdbridge.com/event/tb789"
        assert citation.timestamp is not None


@pytest.mark.unit
class TestThirdBridgeToolsErrorHandling:
    """Test error handling for third_bridge tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response
        mock_http_dependencies['mock_make_request'].return_value = {"invalid": "response"}

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should handle gracefully with empty results
        assert isinstance(result, FindThirdBridgeEventsResponse)
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
                        "id": "tb123",
                        "title": "Test Event",
                        "company_name": "Test Company",
                        "event_date": "invalid-date",  # Invalid date
                        "expert_name": "Test Expert"
                    },
                    {
                        "id": "tb456",
                        "title": "Test Event 2",
                        "company_name": "Test Company 2",
                        # Missing event_date
                        "expert_name": "Test Expert 2"
                    }
                ],
                "total": 2
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_bad_dates

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should still process events with fallback dates
        assert len(result.events) == 2
        for event in result.events:
            assert isinstance(event.event_date, datetime)  # Should have fallback date

    @pytest.mark.asyncio
    async def test_handle_missing_expert_info(self, mock_http_dependencies):
        """Test handling of events with missing expert information."""
        # Setup - response with missing expert fields
        response_with_missing_expert = {
            "response": {
                "data": [
                    {
                        "id": "tb123",
                        "title": "Test Event",
                        "company_name": "Test Company",
                        "event_date": "2023-10-20T14:00:00Z"
                        # Missing expert_name and expert_title
                    }
                ],
                "total": 1
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_missing_expert

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should handle missing expert info gracefully
        assert len(result.events) == 1
        event = result.events[0]
        assert event.expert_name is None
        assert event.expert_title is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, TimeoutError, ValueError])
    async def test_network_errors_propagate(self, mock_http_dependencies, exception_type):
        """Test that network errors are properly propagated."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies['mock_make_request'].side_effect = exception_type("Test error")

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_third_bridge_events(args)

    @pytest.mark.asyncio
    async def test_bloomberg_ticker_handling(self, mock_http_dependencies, third_bridge_api_responses):
        """Test Bloomberg ticker format handling."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = third_bridge_api_responses["find_third_bridge_events_success"]

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL"  # Test ticker without :US suffix
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should still work and pass ticker through
        assert isinstance(result, FindThirdBridgeEventsResponse)
        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        # The ticker should be passed as provided (validation handled by utils if implemented)
        assert 'bloomberg_ticker' in params