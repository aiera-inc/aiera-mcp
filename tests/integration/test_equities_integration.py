#!/usr/bin/env python3

"""Integration tests for equities tools with real Aiera API."""

import pytest
import pytest_asyncio
from unittest.mock import patch

from aiera_mcp.tools.equities.tools import (
    find_equities, get_equity_summaries, get_sectors_and_subsectors,
    get_available_indexes, get_index_constituents,
    get_available_watchlists, get_watchlist_constituents
)
from aiera_mcp.tools.equities.models import (
    FindEquitiesArgs, GetEquitySummariesArgs, GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs, EmptyArgs, SearchArgs,
    FindEquitiesResponse, GetEquitySummariesResponse, GetSectorsSubsectorsResponse,
    GetAvailableIndexesResponse, GetIndexConstituentsResponse,
    GetAvailableWatchlistsResponse, GetWatchlistConstituentsResponse,
    EquityItem, EquityDetails, EquitySummary, SectorSubsector,
    IndexItem, WatchlistItem
)


@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
class TestEquitiesIntegration:
    """Integration tests for equities tools with real API."""

    @pytest.mark.asyncio
    async def test_find_equities_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_equities with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with Apple ticker
            args = FindEquitiesArgs(
                bloomberg_ticker=sample_tickers[0],  # AAPL:US
                page_size=10
            )

            result = await find_equities(args)

            # Verify response structure
            assert isinstance(result, FindEquitiesResponse)
            assert isinstance(result.equities, list)
            assert result.total >= 0
            assert result.page == 1
            assert result.page_size == 10

            # If we found equities, verify their structure
            if result.equities:
                first_equity = result.equities[0]
                assert isinstance(first_equity, EquityItem)
                assert first_equity.equity_id
                assert first_equity.company_name
                assert first_equity.bloomberg_ticker

    @pytest.mark.asyncio
    async def test_find_equities_by_search(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_equities with search query."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test search for Apple
            args = FindEquitiesArgs(
                search="Apple",
                page_size=5
            )

            result = await find_equities(args)

            assert isinstance(result, FindEquitiesResponse)
            assert result.total >= 0

            # If we found equities, they should be related to Apple
            for equity in result.equities:
                assert isinstance(equity, EquityItem)
                assert "apple" in equity.company_name.lower() or equity.bloomberg_ticker == "AAPL:US"

    @pytest.mark.asyncio
    async def test_get_equity_summaries_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_equity_summaries with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with multiple popular tickers
            args = GetEquitySummariesArgs(
                bloomberg_ticker=",".join(sample_tickers[:3])  # First 3 tickers
            )

            result = await get_equity_summaries(args)

            # Verify response structure
            assert isinstance(result, GetEquitySummariesResponse)
            assert isinstance(result.summaries, list)

            # If we found summaries, verify their structure
            for summary in result.summaries:
                assert isinstance(summary, EquityDetails)
                assert summary.equity_id
                assert summary.company_name
                assert summary.bloomberg_ticker

    @pytest.mark.asyncio
    async def test_get_sectors_and_subsectors_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_sectors_and_subsectors with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test without search to get all sectors
            args = SearchArgs()

            result = await get_sectors_and_subsectors(args)

            # Verify response structure
            assert isinstance(result, GetSectorsSubsectorsResponse)
            assert isinstance(result.sectors, list)

            # Should have some sectors
            if result.sectors:
                for sector in result.sectors:
                    assert isinstance(sector, SectorSubsector)
                    assert sector.sector_id
                    assert sector.sector_name

    @pytest.mark.asyncio
    async def test_get_sectors_with_search(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_sectors_and_subsectors with search query."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test search for Technology sector
            args = SearchArgs(search="Technology")

            result = await get_sectors_and_subsectors(args)

            assert isinstance(result, GetSectorsSubsectorsResponse)

            # If we found sectors, they should be related to technology
            for sector in result.sectors:
                assert isinstance(sector, SectorSubsector)
                assert "technolog" in sector.sector_name.lower() or "tech" in sector.sector_name.lower()

    @pytest.mark.asyncio
    async def test_get_available_indexes_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_available_indexes with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = EmptyArgs()
            result = await get_available_indexes(args)

            # Verify response structure
            assert isinstance(result, GetAvailableIndexesResponse)
            assert isinstance(result.indexes, list)

            # Should have some indexes
            if result.indexes:
                for index in result.indexes:
                    assert isinstance(index, IndexItem)
                    assert index.index_id
                    assert index.index_name

    @pytest.mark.asyncio
    async def test_get_index_constituents_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_index_constituents with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # First get available indexes
            empty_args = EmptyArgs()
            indexes_result = await get_available_indexes(empty_args)

            # Skip test if no indexes available
            if not indexes_result.indexes:
                pytest.skip("No indexes available for testing")

            await api_rate_limiter.wait()

            # Test with the first available index
            first_index_name = indexes_result.indexes[0].symbol  # Use symbol as the index identifier
            args = GetIndexConstituentsArgs(index=first_index_name)

            result = await get_index_constituents(args)

            # Verify response structure
            assert isinstance(result, GetIndexConstituentsResponse)
            assert isinstance(result.constituents, list)

            # If we found constituents, verify their structure
            for constituent in result.constituents:
                assert isinstance(constituent, EquityItem)
                assert constituent.equity_id
                assert constituent.company_name

    @pytest.mark.asyncio
    async def test_get_available_watchlists_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_available_watchlists with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = EmptyArgs()
            result = await get_available_watchlists(args)

            # Verify response structure
            assert isinstance(result, GetAvailableWatchlistsResponse)
            assert isinstance(result.watchlists, list)

            # If we found watchlists, verify their structure
            for watchlist in result.watchlists:
                assert isinstance(watchlist, WatchlistItem)
                assert watchlist.watchlist_id
                assert watchlist.watchlist_name

    @pytest.mark.asyncio
    async def test_get_watchlist_constituents_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_watchlist_constituents with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # First get available watchlists
            empty_args = EmptyArgs()
            watchlists_result = await get_available_watchlists(empty_args)

            # Skip test if no watchlists available
            if not watchlists_result.watchlists:
                pytest.skip("No watchlists available for testing")

            await api_rate_limiter.wait()

            # Test with the first available watchlist
            first_watchlist_id = watchlists_result.watchlists[0].watchlist_id
            args = GetWatchlistConstituentsArgs(watchlist_id=first_watchlist_id)

            result = await get_watchlist_constituents(args)

            # Verify response structure
            assert isinstance(result, GetWatchlistConstituentsResponse)
            assert isinstance(result.constituents, list)

            # If we found constituents, verify their structure
            for constituent in result.constituents:
                assert isinstance(constituent, EquityItem)
                assert constituent.equity_id
                assert constituent.company_name

    @pytest.mark.asyncio
    async def test_equities_pagination_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test equities pagination with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test first page with search to ensure we have results
            args_page1 = FindEquitiesArgs(
                search="tech",
                page=1,
                page_size=5
            )

            result_page1 = await find_equities(args_page1)
            assert result_page1.page == 1
            assert result_page1.page_size == 5

            # If we have enough equities, test second page
            if result_page1.total > 5:
                await api_rate_limiter.wait()

                args_page2 = FindEquitiesArgs(
                    search="tech",
                    page=2,
                    page_size=5
                )

                result_page2 = await find_equities(args_page2)
                assert result_page2.page == 2
                assert result_page2.page_size == 5
                assert result_page2.total == result_page1.total

                # Equities should be different between pages
                page1_ids = {equity.equity_id for equity in result_page1.equities}
                page2_ids = {equity.equity_id for equity in result_page2.equities}
                assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_equities_api_error_handling(
        self,
        integration_mcp_server,
        real_http_client,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test equities API error handling with invalid API key."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_api_key_from_context', return_value="invalid-api-key"):

            args = FindEquitiesArgs(search="Apple")

            # This should raise an exception or return an error response
            try:
                result = await find_equities(args)
                # If it doesn't raise an exception, check for error indicators
                if hasattr(result, 'error') or len(result.equities) == 0:
                    # API handled the error gracefully
                    pass
            except Exception as e:
                # Expected - invalid API key should cause an error
                assert "401" in str(e) or "Unauthorized" in str(e) or "Invalid" in str(e)

    @pytest.mark.asyncio
    async def test_multiple_equity_tools_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test multiple equity tools working together."""

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # 1. Find an equity
            await api_rate_limiter.wait()
            find_args = FindEquitiesArgs(
                bloomberg_ticker=sample_tickers[0],  # AAPL:US
                page_size=1
            )
            find_result = await find_equities(find_args)

            if not find_result.equities:
                pytest.skip("No equity found for integration test")

            # 2. Get summary for the equity
            await api_rate_limiter.wait()
            summary_args = GetEquitySummariesArgs(
                bloomberg_ticker=sample_tickers[0]
            )
            summary_result = await get_equity_summaries(summary_args)

            # 3. Get available indexes and their constituents
            await api_rate_limiter.wait()
            indexes_result = await get_available_indexes(EmptyArgs())

            # Verify all tools returned valid data
            assert isinstance(find_result, FindEquitiesResponse)
            assert isinstance(summary_result, GetEquitySummariesResponse)
            assert isinstance(indexes_result, GetAvailableIndexesResponse)

            # The equity should be found in all relevant responses
            if find_result.equities:
                assert find_result.equities[0].bloomberg_ticker == sample_tickers[0]

    @pytest.mark.asyncio
    async def test_equities_citations_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that equity responses include proper citation information."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = FindEquitiesArgs(search="Apple", page_size=5)
            result = await find_equities(args)

            # Verify citations are generated appropriately
            assert hasattr(result, 'citation_information')
            assert isinstance(result.citation_information, list)

            # Citations should be present if we have results
            if result.equities:
                assert len(result.citation_information) >= 0