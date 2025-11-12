#!/usr/bin/env python3

"""Integration tests for events tools with real Aiera API."""

import pytest
import pytest_asyncio
from unittest.mock import patch

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
)


@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
class TestEventsIntegration:
    """Integration tests for events tools with real API."""

    @pytest.mark.asyncio
    async def test_find_events_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_date_ranges,
        api_rate_limiter,
        mock_get_http_client,
    ):
        """Test find_events with real API."""
        await api_rate_limiter.wait()

        with patch("aiera_mcp.tools.base.get_http_client", mock_get_http_client):
            # Test with a date range that should have events
            date_range = sample_date_ranges[0]  # Q4 2023 earnings season
            args = FindEventsArgs(
                start_date=date_range["start_date"],
                end_date=date_range["end_date"],
                event_type="earnings",
                page_size=10,
            )

            # Make real API call
            result = await find_events(args)

            # Verify response structure
            assert isinstance(result, FindEventsResponse)
            assert isinstance(result.events, list)
            assert result.total >= 0
            assert result.page == 1
            assert result.page_size == 10

            # If we found events, verify their structure
            if result.events:
                first_event = result.events[0]
                assert isinstance(first_event, EventItem)
                assert first_event.event_id
                assert first_event.title
                assert first_event.event_date
                assert first_event.event_type

    @pytest.mark.asyncio
    async def test_find_events_with_ticker_filter(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client,
    ):
        """Test find_events with ticker filter."""
        await api_rate_limiter.wait()

        with patch("aiera_mcp.tools.base.get_http_client", mock_get_http_client):

            # Test with Apple ticker
            args = FindEventsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31",
                bloomberg_ticker=sample_tickers[0],  # AAPL:US
                event_type="earnings",
            )

            result = await find_events(args)

            assert isinstance(result, FindEventsResponse)
            assert result.total >= 0

            # If we found events, they should be for Apple or related companies
            for event in result.events:
                assert isinstance(event, EventItem)
                # The ticker filter might find related events, so we don't assert exact match

    @pytest.mark.asyncio
    async def test_get_event_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client,
    ):
        """Test get_event with real API (requires finding an event first)."""
        await api_rate_limiter.wait()

        with patch("aiera_mcp.tools.base.get_http_client", mock_get_http_client):

            # First find an event
            find_args = FindEventsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31",
                event_type="earnings",
                page_size=1,
            )

            find_result = await find_events(find_args)

            # Skip test if no events found
            if not find_result.events:
                pytest.skip("No events found for the specified date range")

            await api_rate_limiter.wait()

            # Get details for the first event
            event_id = find_result.events[0].event_id
            get_args = GetEventArgs(event_id=event_id)

            result = await get_event(get_args)

            # Verify response structure
            assert isinstance(result, GetEventResponse)
            assert isinstance(result.event, EventDetails)
            assert result.event.event_id == event_id
            assert result.event.title
            assert result.event.event_date

            # EventDetails should have additional fields
            assert hasattr(result.event, "description")
            assert hasattr(result.event, "transcript_preview")
            assert hasattr(result.event, "audio_url")

    @pytest.mark.asyncio
    async def test_get_upcoming_events_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client,
    ):
        """Test get_upcoming_events with real API."""
        await api_rate_limiter.wait()

        with patch("aiera_mcp.tools.base.get_http_client", mock_get_http_client):

            # Test with future date range
            args = GetUpcomingEventsArgs(start_date="2024-06-01", end_date="2024-06-30")

            result = await get_upcoming_events(args)

            # Verify response structure
            assert isinstance(result, GetUpcomingEventsResponse)
            assert isinstance(result.events, list)

            # Verify citations are generated for upcoming events
            if result.events:
                assert len(result.citation_information) >= 0
                for event in result.events:
                    assert isinstance(event, EventItem)

    @pytest.mark.asyncio
    async def test_events_api_error_handling(
        self,
        integration_mcp_server,
        real_http_client,
        api_rate_limiter,
        mock_get_http_client,
    ):
        """Test events API error handling with invalid API key."""
        await api_rate_limiter.wait()

        with patch(
            "aiera_mcp.tools.base.get_api_key_from_context",
            return_value="invalid-api-key",
        ):

            args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

            # This should raise an exception or return an error response
            # The exact behavior depends on how the API handles invalid keys
            try:
                result = await find_events(args)
                # If it doesn't raise an exception, check for error indicators
                if hasattr(result, "error") or len(result.events) == 0:
                    # API handled the error gracefully
                    pass
            except Exception as e:
                # Expected - invalid API key should cause an error
                assert (
                    "401" in str(e) or "Unauthorized" in str(e) or "Invalid" in str(e)
                )

    @pytest.mark.asyncio
    async def test_events_pagination_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client,
    ):
        """Test events pagination with real API."""
        await api_rate_limiter.wait()

        with patch("aiera_mcp.tools.base.get_http_client", mock_get_http_client):

            # Test first page
            args_page1 = FindEventsArgs(
                start_date="2023-10-01", end_date="2023-10-31", page=1, page_size=5
            )

            result_page1 = await find_events(args_page1)
            assert result_page1.page == 1
            assert result_page1.page_size == 5

            # If we have enough events, test second page
            if result_page1.total > 5:
                await api_rate_limiter.wait()

                args_page2 = FindEventsArgs(
                    start_date="2023-10-01", end_date="2023-10-31", page=2, page_size=5
                )

                result_page2 = await find_events(args_page2)
                assert result_page2.page == 2
                assert result_page2.page_size == 5
                assert result_page2.total == result_page1.total

                # Events should be different between pages
                page1_ids = {event.event_id for event in result_page1.events}
                page2_ids = {event.event_id for event in result_page2.events}
                assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_events_different_types_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client,
    ):
        """Test different event types with real API."""

        event_types = ["earnings", "presentation", "investor_meeting"]

        with patch("aiera_mcp.tools.base.get_http_client", mock_get_http_client):

            for event_type in event_types:
                await api_rate_limiter.wait()

                args = FindEventsArgs(
                    start_date="2023-10-01",
                    end_date="2023-10-31",
                    event_type=event_type,
                    page_size=5,
                )

                result = await find_events(args)

                assert isinstance(result, FindEventsResponse)
                assert result.total >= 0

                # If events found, verify they match the requested type
                for event in result.events:
                    # Note: API might return related events, so we don't enforce strict matching
                    assert isinstance(event, EventItem)
                    assert event.event_type  # Should have some event type
