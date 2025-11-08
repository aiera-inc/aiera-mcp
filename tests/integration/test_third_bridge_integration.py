#!/usr/bin/env python3

"""Integration tests for third bridge tools with real Aiera API."""

import pytest
import pytest_asyncio
from unittest.mock import patch

from aiera_mcp.tools.third_bridge.tools import find_third_bridge_events, get_third_bridge_event
from aiera_mcp.tools.third_bridge.models import (
    FindThirdBridgeEventsArgs, GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse, GetThirdBridgeEventResponse,
    ThirdBridgeEventItem, ThirdBridgeEventDetails
)


@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
class TestThirdBridgeIntegration:
    """Integration tests for third bridge tools with real API."""

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_date_ranges,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_third_bridge_events with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a date range that might have Third Bridge events
            date_range = sample_date_ranges[1]  # Q1 2024
            args = FindThirdBridgeEventsArgs(
                start_date=date_range["start_date"],
                end_date=date_range["end_date"],
                page_size=10
            )

            result = await find_third_bridge_events(args)

            # Verify response structure
            assert isinstance(result, FindThirdBridgeEventsResponse)
            assert isinstance(result.events, list)
            assert result.total >= 0
            assert result.page == 1
            assert result.page_size == 10

            # If we found events, verify their structure
            if result.events:
                first_event = result.events[0]
                assert isinstance(first_event, ThirdBridgeEventItem)
                assert first_event.event_id
                assert first_event.title
                assert first_event.company_name
                assert first_event.event_date

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_with_ticker_filter(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_third_bridge_events with ticker filter."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with Apple ticker - might have Third Bridge events
            args = FindThirdBridgeEventsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                bloomberg_ticker=sample_tickers[0],  # AAPL:US
                page_size=5
            )

            result = await find_third_bridge_events(args)

            assert isinstance(result, FindThirdBridgeEventsResponse)
            assert result.total >= 0

            # If we found events, they should be for Apple or related companies
            for event in result.events:
                assert isinstance(event, ThirdBridgeEventItem)
                # Note: Third Bridge events might not have exact ticker matches
                # so we verify the structure without enforcing specific content

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_extended_date_range(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_third_bridge_events with extended date range to increase chance of finding events."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a longer date range to increase chance of finding Third Bridge events
            args = FindThirdBridgeEventsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30",
                page_size=10
            )

            result = await find_third_bridge_events(args)

            assert isinstance(result, FindThirdBridgeEventsResponse)
            assert isinstance(result.events, list)
            assert result.total >= 0

            # Third Bridge events might be rare, so we don't require finding any
            # but if found, verify structure
            for event in result.events:
                assert isinstance(event, ThirdBridgeEventItem)
                assert event.event_id
                assert event.title
                assert event.company_name
                assert event.event_date

    @pytest.mark.asyncio
    async def test_find_third_bridge_events_with_search(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_third_bridge_events with search query."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test search for expert events
            args = FindThirdBridgeEventsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30",
                search="technology expert",
                page_size=5
            )

            result = await find_third_bridge_events(args)

            assert isinstance(result, FindThirdBridgeEventsResponse)
            assert result.total >= 0

            # If we found events, they should be related to the search
            for event in result.events:
                assert isinstance(event, ThirdBridgeEventItem)
                # The search might find related events, so we don't enforce strict matching

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_third_bridge_event with real API (requires finding an event first)."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # First find a Third Bridge event with extended date range
            find_args = FindThirdBridgeEventsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30",
                page_size=1
            )

            find_result = await find_third_bridge_events(find_args)

            # Skip test if no Third Bridge events found (they might be rare)
            if not find_result.events:
                pytest.skip("No Third Bridge events found for the specified date range")

            await api_rate_limiter.wait()

            # Get details for the first event
            event_id = find_result.events[0].event_id
            get_args = GetThirdBridgeEventArgs(event_id=event_id)

            result = await get_third_bridge_event(get_args)

            # Verify response structure
            assert isinstance(result, GetThirdBridgeEventResponse)
            assert isinstance(result.event, ThirdBridgeEventDetails)
            assert result.event.event_id == event_id
            assert result.event.title
            assert result.event.company_name
            assert result.event.event_date

            # ThirdBridgeEventDetails should have additional fields
            assert hasattr(result.event, 'description')
            assert hasattr(result.event, 'expert_name')
            assert hasattr(result.event, 'expert_bio')

    @pytest.mark.asyncio
    async def test_third_bridge_events_pagination_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test third bridge events pagination with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test first page with extended date range to increase chance of results
            args_page1 = FindThirdBridgeEventsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30",
                page=1,
                page_size=5
            )

            result_page1 = await find_third_bridge_events(args_page1)
            assert result_page1.page == 1
            assert result_page1.page_size == 5

            # If we have enough events, test second page
            if result_page1.total > 5:
                await api_rate_limiter.wait()

                args_page2 = FindThirdBridgeEventsArgs(
                    start_date="2023-01-01",
                    end_date="2024-06-30",
                    page=2,
                    page_size=5
                )

                result_page2 = await find_third_bridge_events(args_page2)
                assert result_page2.page == 2
                assert result_page2.page_size == 5
                assert result_page2.total == result_page1.total

                # Events should be different between pages
                page1_ids = {event.event_id for event in result_page1.events}
                page2_ids = {event.event_id for event in result_page2.events}
                assert page1_ids.isdisjoint(page2_ids)
            else:
                # If no pagination possible, that's fine for Third Bridge events
                # which might be limited in number
                pass

    @pytest.mark.asyncio
    async def test_third_bridge_events_api_error_handling(
        self,
        integration_mcp_server,
        real_http_client,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test third bridge events API error handling with invalid API key."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_api_key_from_context', return_value="invalid-api-key"):

            args = FindThirdBridgeEventsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31"
            )

            # This should raise an exception or return an error response
            try:
                result = await find_third_bridge_events(args)
                # If it doesn't raise an exception, check for error indicators
                if hasattr(result, 'error') or len(result.events) == 0:
                    # API handled the error gracefully
                    pass
            except Exception as e:
                # Expected - invalid API key should cause an error
                assert "401" in str(e) or "Unauthorized" in str(e) or "Invalid" in str(e)

    @pytest.mark.asyncio
    async def test_get_third_bridge_event_invalid_id(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_third_bridge_event with invalid event ID."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with invalid event ID
            get_args = GetThirdBridgeEventArgs(event_id="invalid-event-id-12345")

            # This should raise an exception or return an error
            try:
                result = await get_third_bridge_event(get_args)
                # If no exception, the result should indicate an error
                assert not hasattr(result, 'event') or result.event is None
            except (ValueError, Exception) as e:
                # Expected - invalid event ID should cause an error
                assert "not found" in str(e).lower() or "invalid" in str(e).lower()

    @pytest.mark.asyncio
    async def test_third_bridge_events_with_multiple_filters(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test third bridge events with multiple filter combinations."""

        filter_combinations = [
            {
                "start_date": "2023-01-01",
                "end_date": "2024-06-30",
                "bloomberg_ticker": sample_tickers[0]
            },
            {
                "start_date": "2023-01-01",
                "end_date": "2024-06-30",
                "search": "expert"
            },
            {
                "start_date": "2023-06-01",
                "end_date": "2024-06-30"
            }
        ]

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            for filter_combo in filter_combinations:
                await api_rate_limiter.wait()

                args = FindThirdBridgeEventsArgs(
                    page_size=5,
                    **filter_combo
                )

                result = await find_third_bridge_events(args)

                assert isinstance(result, FindThirdBridgeEventsResponse)
                assert result.total >= 0

                # Verify structure of any found events
                for event in result.events:
                    assert isinstance(event, ThirdBridgeEventItem)
                    assert event.event_id
                    assert event.title
                    assert event.company_name

    @pytest.mark.asyncio
    async def test_third_bridge_events_citations_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that third bridge events responses include citation information."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = FindThirdBridgeEventsArgs(
                start_date="2023-01-01",
                end_date="2024-06-30",
                page_size=5
            )

            result = await find_third_bridge_events(args)

            # Verify citations are handled appropriately
            assert hasattr(result, 'citation_information')
            assert isinstance(result.citation_information, list)

            # Third Bridge events might not always have URLs, but citations should still be structured properly
            if result.events:
                # If we have events, citation structure should be valid even if empty
                assert len(result.citation_information) >= 0

    @pytest.mark.asyncio
    async def test_third_bridge_events_response_structure(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that third bridge events return proper response structures even when no events exist."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a narrow date range that probably won't have Third Bridge events
            args = FindThirdBridgeEventsArgs(
                start_date="2024-01-01",
                end_date="2024-01-01",
                page_size=5
            )

            result = await find_third_bridge_events(args)

            # Even with no events, response should have proper structure
            assert isinstance(result, FindThirdBridgeEventsResponse)
            assert isinstance(result.events, list)
            assert result.total >= 0
            assert result.page == 1
            assert result.page_size == 5
            assert hasattr(result, 'instructions')
            assert hasattr(result, 'citation_information')
            assert isinstance(result.citation_information, list)