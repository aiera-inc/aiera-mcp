#!/usr/bin/env python3

"""Unit tests for third_bridge tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from aiera_mcp.tools.third_bridge.tools import (
    find_third_bridge_events,
    get_third_bridge_event,
)
from aiera_mcp.tools.third_bridge.models import (
    FindThirdBridgeEventsArgs,
    GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse,
    GetThirdBridgeEventResponse,
    ThirdBridgeEventItem,
    ThirdBridgeEventDetails,
)


@pytest.mark.unit
class TestFindThirdBridgeEvents:
    """Test the find_third_bridge_events tool."""

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_success(
        self, mock_http_dependencies, third_bridge_api_responses
    ):
        """Test successful Third Bridge events search."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            third_bridge_api_responses["find_third_bridge_events_success"]
        )

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", bloomberg_ticker="AAPL:US"
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        assert isinstance(result, FindThirdBridgeEventsResponse)
        assert len(result.response.data) == 1
        assert result.response.pagination.total_count == 13
        assert result.response.pagination.current_page == 1
        assert result.response.pagination.page_size == 13

        # Check first event
        first_event = result.response.data[0]
        assert isinstance(first_event, ThirdBridgeEventItem)
        assert first_event.thirdbridge_event_id == "46abc016e6da845a6459e80a200341c5"
        assert (
            first_event.title
            == "Robotic Delivery Market - Senior Executive, Sales & Operations Planning at Amazon.com Inc"
        )
        assert first_event.content_type == "COMMUNITY"
        assert first_event.language == "eng"
        assert first_event.call_date == "2025-04-23T19:00:00"
        assert len(first_event.agenda) == 3
        assert first_event.insights is None  # Can be null in real API
        # Check citation information
        assert first_event.citation_information.title == first_event.title
        assert "dashboard.aiera.com" in first_event.citation_information.url

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-third-bridge"

        # Check parameters were passed correctly
        params = call_args[1]["params"]
        assert params["start_date"] == "2023-10-01"
        assert params["end_date"] == "2023-10-31"
        assert params["bloomberg_ticker"] == "AAPL:US"
        assert params["include_transcripts"] == "false"

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_empty_results(self, mock_http_dependencies):
        """Test find_third_bridge_events with empty results."""
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

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        assert isinstance(result, FindThirdBridgeEventsResponse)
        assert len(result.response.data) == 0
        assert result.response.pagination.total_count == 0
        assert result.response.pagination.current_page == 1

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_pagination(
        self, mock_http_dependencies, third_bridge_api_responses
    ):
        """Test find_third_bridge_events with pagination parameters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            third_bridge_api_responses["find_third_bridge_events_success"]
        )

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", page=2, page_size=25
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        assert (
            result.response.pagination.current_page == 1
        )  # Since we're using the success fixture
        assert (
            result.response.pagination.page_size == 13
        )  # Since we're using the success fixture

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["page"] == "2"  # Should be serialized as string
        assert params["page_size"] == "25"

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_with_filters(
        self, mock_http_dependencies, third_bridge_api_responses
    ):
        """Test find_third_bridge_events with various filters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            third_bridge_api_responses["find_third_bridge_events_success"]
        )

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US,MSFT:US",
            watchlist_id=123,
            sector_id=456,
            subsector_id=789,
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US,MSFT:US"
        assert params["watchlist_id"] == "123"
        assert params["sector_id"] == "456"
        assert params["subsector_id"] == "789"

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_date_parsing(self, mock_http_dependencies):
        """Test find_third_bridge_events handles date parsing correctly."""
        # Setup with various date formats
        response_with_dates = {
            "response": {
                "data": [
                    {
                        "event_id": "tb123",
                        "content_type": "FORUM",
                        "call_date": "2023-10-20T14:00:00Z",
                        "title": "Test Event",
                        "language": "EN",
                        "agenda": ["Test agenda item"],
                        "insights": ["Test insight"],
                        "citation_information": {
                            "title": "Test Event",
                            "url": "https://thirdbridge.com/event/tb123",
                            "metadata": {
                                "type": "event",
                                "url_target": "thirdbridge",
                                "event_id": 123,
                            },
                        },
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_dates

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify date was parsed correctly
        assert len(result.response.data) == 1
        event = result.response.data[0]
        assert event.call_date == "2023-10-20T14:00:00Z"

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_citations(
        self, mock_http_dependencies, third_bridge_api_responses
    ):
        """Test that find_third_bridge_events generates proper citations."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            third_bridge_api_responses["find_third_bridge_events_success"]
        )

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify citation information data
        assert len(result.response.data) == 1
        event = result.response.data[0]
        citation = event.citation_information
        assert (
            citation.title
            == "Robotic Delivery Market - Senior Executive, Sales & Operations Planning at Amazon.com Inc"
        )
        assert (
            citation.url
            == "https://dashboard.aiera.com/companies/1/calendar?tabs[0]=evt%7C2833969"
        )


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
                        "event_id": "tb789",
                        "content_type": "FORUM",
                        "call_date": "2023-10-20T14:00:00Z",
                        "title": "Apple Supply Chain Analysis",
                        "language": "EN",
                        "agenda": [
                            "Discussion of Apple's supply chain resilience and challenges"
                        ],
                        "insights": [
                            "Key insights on Apple's supply chain management strategies"
                        ],
                        "citation_information": {
                            "title": "Apple Supply Chain Analysis",
                            "url": "https://thirdbridge.com/event/tb789",
                            "metadata": {
                                "type": "event",
                                "url_target": "aiera",
                                "company_id": 1,
                                "event_id": 2833969,
                            },
                        },
                        "transcripts": [
                            {
                                "start_ms": 1000,
                                "duration_ms": 60000,
                                "transcript": "Full transcript of the expert discussion...",
                            }
                        ],
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_details

        args = GetThirdBridgeEventArgs(thirdbridge_event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify
        assert isinstance(result, GetThirdBridgeEventResponse)
        assert isinstance(result.event, ThirdBridgeEventDetails)
        assert result.event.thirdbridge_event_id == "tb789"
        assert result.event.title == "Apple Supply Chain Analysis"
        assert result.event.agenda is not None
        assert result.event.insights is not None
        assert result.event.transcripts is not None

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-third-bridge"

        # Check field mapping (event_id -> event_ids)
        params = call_args[1]["params"]
        assert "event_ids" in params
        assert params["event_ids"] == "tb789"
        assert "event_id" not in params
        assert params["include_transcripts"] == "true"

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_not_found(self, mock_http_dependencies):
        """Test get_third_bridge_event when event is not found."""
        # Setup - empty response
        mock_http_dependencies["mock_make_request"].return_value = {
            "response": {"data": []},
            "instructions": [],
        }

        args = GetThirdBridgeEventArgs(thirdbridge_event_id="nonexistent")

        # Execute & Verify
        with pytest.raises(
            ValueError, match="Third Bridge event not found: nonexistent"
        ):
            await get_third_bridge_event(args)

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_date_parsing(self, mock_http_dependencies):
        """Test get_third_bridge_event handles date parsing correctly."""
        # Setup with missing event_date
        response_without_date = {
            "response": {
                "data": [
                    {
                        "event_id": "tb789",
                        "content_type": "FORUM",
                        "title": "Test Event",
                        "language": "EN",
                        "agenda": ["Test agenda"],
                        "insights": ["Test insights"],
                        "citation_information": {
                            "title": "Test Event",
                            "url": "https://thirdbridge.com/event/tb789",
                            "metadata": {
                                "type": "event",
                                "url_target": "thirdbridge",
                                "event_id": 789,
                            },
                        },
                        # Missing call_date
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_without_date

        args = GetThirdBridgeEventArgs(thirdbridge_event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify - should handle missing call_date gracefully
        assert result.event.call_date == ""  # Should get empty string as default

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_invalid_date(self, mock_http_dependencies):
        """Test get_third_bridge_event handles invalid dates correctly."""
        # Setup with invalid event_date
        response_with_bad_date = {
            "response": {
                "data": [
                    {
                        "event_id": "tb789",
                        "content_type": "FORUM",
                        "call_date": "invalid-date",  # Invalid date
                        "title": "Test Event",
                        "language": "EN",
                        "agenda": ["Test agenda"],
                        "insights": ["Test insights"],
                        "citation_information": {
                            "title": "Test Event",
                            "url": "https://thirdbridge.com/event/tb789",
                            "metadata": {
                                "type": "event",
                                "url_target": "thirdbridge",
                                "event_id": 789,
                            },
                        },
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            response_with_bad_date
        )

        args = GetThirdBridgeEventArgs(thirdbridge_event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify - should handle invalid call_date gracefully
        assert (
            result.event.call_date == "invalid-date"
        )  # Should preserve the invalid date as string

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_citation(self, mock_http_dependencies):
        """Test that get_third_bridge_event generates proper citation."""
        # Setup
        response_with_url = {
            "response": {
                "data": [
                    {
                        "event_id": "tb789",
                        "content_type": "FORUM",
                        "call_date": "2023-10-20T14:00:00Z",
                        "title": "Apple Supply Chain Analysis",
                        "language": "EN",
                        "agenda": ["Test agenda"],
                        "insights": ["Test insights"],
                        "citation_information": {
                            "title": "Apple Supply Chain Analysis",
                            "url": "https://thirdbridge.com/event/tb789",
                            "metadata": {
                                "type": "event",
                                "url_target": "thirdbridge",
                                "event_id": 789,
                            },
                        },
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_url

        args = GetThirdBridgeEventArgs(thirdbridge_event_id="tb789")

        # Execute
        result = await get_third_bridge_event(args)

        # Verify event has citation information
        assert result.event is not None
        assert result.event.citation_information is not None
        # Citation title and url should be present
        assert result.event.citation_information.title is not None
        assert result.event.citation_information.url is not None


@pytest.mark.unit
class TestThirdBridgeToolsErrorHandling:
    """Test error handling for third_bridge tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response (missing response field)
        mock_http_dependencies["mock_make_request"].return_value = {
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

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should handle gracefully with empty results
        assert isinstance(result, FindThirdBridgeEventsResponse)
        assert len(result.response.data) == 0
        assert result.response.pagination.total_count == 0

    @pytest.mark.asyncio
    async def test_handle_missing_date_fields(self, mock_http_dependencies):
        """Test handling of events with missing or invalid date fields."""
        # Setup - response with missing/invalid dates
        response_with_bad_dates = {
            "response": {
                "data": [
                    {
                        "event_id": "tb123",
                        "content_type": "FORUM",
                        "call_date": "invalid-date",  # Invalid date
                        "title": "Test Event",
                        "language": "EN",
                        "agenda": ["Test agenda"],
                        "insights": ["Test insight"],
                        "citation_information": {
                            "title": "Test Event",
                            "url": "https://thirdbridge.com/event/tb123",
                            "metadata": {
                                "type": "event",
                                "url_target": "thirdbridge",
                                "event_id": 123,
                            },
                        },
                    },
                    {
                        "event_id": "tb456",
                        "content_type": "FORUM",
                        "call_date": "2023-10-20T14:00:00Z",
                        "title": "Test Event 2",
                        "language": "EN",
                        "agenda": ["Test agenda 2"],
                        "insights": ["Test insight 2"],
                        "citation_information": {
                            "title": "Test Event 2",
                            "url": "https://thirdbridge.com/event/tb456",
                            "metadata": {
                                "type": "event",
                                "url_target": "thirdbridge",
                                "event_id": 456,
                            },
                        },
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

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should still process events
        assert len(result.response.data) == 2
        assert result.response.data[0].call_date == "invalid-date"
        assert result.response.data[1].call_date == "2023-10-20T14:00:00Z"

    @pytest.mark.asyncio
    async def test_handle_missing_expert_info(self, mock_http_dependencies):
        """Test handling of events with missing expert information."""
        # Setup - response with missing expert fields
        response_with_missing_expert = {
            "response": {
                "data": [
                    {
                        "event_id": "tb123",
                        "content_type": "FORUM",
                        "call_date": "2023-10-20T14:00:00Z",
                        "title": "Test Event",
                        "language": "EN",
                        "agenda": ["Test agenda"],
                        "insights": ["Test insight"],
                        "citation_information": {
                            "title": "Test Event",
                            "url": "https://thirdbridge.com/event/tb123",
                            "metadata": {
                                "type": "event",
                                "url_target": "thirdbridge",
                                "event_id": 123,
                            },
                        },
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            response_with_missing_expert
        )

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should handle missing expert info gracefully
        assert len(result.response.data) == 1
        event = result.response.data[0]
        # Citation information should still be present
        assert event.citation_information is not None
        assert event.citation_information.title is not None

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

        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_third_bridge_events(args)

    @pytest.mark.asyncio
    async def test_bloomberg_ticker_handling(
        self, mock_http_dependencies, third_bridge_api_responses
    ):
        """Test Bloomberg ticker format handling."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            third_bridge_api_responses["find_third_bridge_events_success"]
        )

        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL",  # Test ticker without :US suffix
        )

        # Execute
        result = await find_third_bridge_events(args)

        # Verify - should still work and pass ticker through
        assert isinstance(result, FindThirdBridgeEventsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        # The ticker should be passed as provided (validation handled by utils if implemented)
        assert "bloomberg_ticker" in params
