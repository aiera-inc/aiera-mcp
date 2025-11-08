#!/usr/bin/env python3

"""Unit tests for equities tools."""

import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock

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


@pytest.mark.unit
class TestFindEquities:
    """Test the find_equities tool."""

    @pytest.mark.asyncio
    async def test_find_equities_success(self, mock_http_dependencies, equities_api_responses):
        """Test successful equities search."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["find_equities_success"]

        args = FindEquitiesArgs(
            bloomberg_ticker="AAPL:US",
            page=1,
            page_size=50
        )

        # Execute
        result = await find_equities(args)

        # Verify
        assert isinstance(result, FindEquitiesResponse)
        assert len(result.equities) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 50

        # Check first equity
        first_equity = result.equities[0]
        assert isinstance(first_equity, EquityItem)
        assert first_equity.equity_id == "equity123"
        assert first_equity.company_name == "Apple Inc"
        assert first_equity.ticker == "AAPL"
        assert first_equity.bloomberg_ticker == "AAPL:US"
        assert first_equity.exchange == "NASDAQ"
        assert first_equity.sector == "Technology"
        assert first_equity.subsector == "Consumer Electronics"
        assert first_equity.country == "United States"
        assert first_equity.market_cap == 3000000000000

        # Check API call was made correctly
        mock_http_dependencies['mock_make_request'].assert_called_once()
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-equities"

        # Check parameters were passed correctly
        params = call_args[1]['params']
        assert params['bloomberg_ticker'] == "AAPL:US"
        assert params['include_company_metadata'] == "true"

    @pytest.mark.asyncio
    async def test_find_equities_empty_results(self, mock_http_dependencies):
        """Test find_equities with empty results."""
        # Setup
        empty_response = {
            "response": {"data": [], "total": 0},
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = FindEquitiesArgs(search="nonexistent")

        # Execute
        result = await find_equities(args)

        # Verify
        assert isinstance(result, FindEquitiesResponse)
        assert len(result.equities) == 0
        assert result.total == 0
        assert len(result.citation_information) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("identifier_type,identifier_value", [
        ("bloomberg_ticker", "AAPL:US"),
        ("ticker", "AAPL"),
        ("isin", "US0378331005"),
        ("ric", "AAPL.O"),
        ("permid", "4295905573")
    ])
    async def test_find_equities_different_identifiers(self, mock_http_dependencies, equities_api_responses, identifier_type, identifier_value):
        """Test find_equities with different identifier types."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["find_equities_success"]

        args_data = {identifier_type: identifier_value}
        args = FindEquitiesArgs(**args_data)

        # Execute
        result = await find_equities(args)

        # Verify
        assert isinstance(result, FindEquitiesResponse)
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['params'][identifier_type] == identifier_value

    @pytest.mark.asyncio
    async def test_find_equities_pagination(self, mock_http_dependencies, equities_api_responses):
        """Test find_equities with pagination parameters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["find_equities_success"]

        args = FindEquitiesArgs(
            search="tech",
            page=2,
            page_size=25
        )

        # Execute
        result = await find_equities(args)

        # Verify
        assert result.page == 2
        assert result.page_size == 25

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"  # Should be serialized as string
        assert params['page_size'] == "25"

    @pytest.mark.asyncio
    async def test_find_equities_citations_generated(self, mock_http_dependencies, equities_api_responses):
        """Test that find_equities generates proper citations."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["find_equities_success"]

        args = FindEquitiesArgs(bloomberg_ticker="AAPL:US")

        # Execute
        result = await find_equities(args)

        # Verify citations were created
        assert len(result.citation_information) == 1
        first_citation = result.citation_information[0]
        assert "Apple Inc" in first_citation.title
        assert "AAPL" in first_citation.title
        assert first_citation.source == "Aiera Equity Database"


@pytest.mark.unit
class TestGetEquitySummaries:
    """Test the get_equity_summaries tool."""

    @pytest.mark.asyncio
    async def test_get_equity_summaries_success(self, mock_http_dependencies, equities_api_responses):
        """Test successful equity summaries retrieval."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["get_equity_summaries_success"]

        args = GetEquitySummariesArgs(bloomberg_ticker="AAPL:US")

        # Execute
        result = await get_equity_summaries(args)

        # Verify
        assert isinstance(result, GetEquitySummariesResponse)
        assert len(result.summaries) == 1

        # Check first summary
        first_summary = result.summaries[0]
        assert isinstance(first_summary, EquityDetails)
        assert first_summary.equity_id == "equity123"
        assert first_summary.company_name == "Apple Inc"
        assert first_summary.summary is not None

        # Check summary details
        summary = first_summary.summary
        assert isinstance(summary, EquitySummary)
        assert "Apple Inc. designs, manufactures" in summary.description
        assert len(summary.recent_events) == 2
        assert "Q4 2023 Earnings Call" in summary.recent_events[0]
        assert summary.key_metrics["pe_ratio"] == 28.5
        assert summary.analyst_coverage["avg_rating"] == "Buy"

        # Check identifiers
        assert first_summary.identifiers["isin"] == "US0378331005"
        assert first_summary.identifiers["cusip"] == "037833100"

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/equity-summaries"

        params = call_args[1]['params']
        assert params['bloomberg_ticker'] == "AAPL:US"
        assert params['lookback'] == "90"

    @pytest.mark.asyncio
    async def test_get_equity_summaries_multiple_tickers(self, mock_http_dependencies, equities_api_responses):
        """Test get_equity_summaries with multiple tickers."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["get_equity_summaries_success"]

        args = GetEquitySummariesArgs(bloomberg_ticker="AAPL:US,MSFT:US")

        # Execute
        result = await get_equity_summaries(args)

        # Verify
        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['bloomberg_ticker'] == "AAPL:US,MSFT:US"

    @pytest.mark.asyncio
    async def test_get_equity_summaries_minimal_data(self, mock_http_dependencies):
        """Test get_equity_summaries with minimal summary data."""
        # Setup with minimal data
        minimal_response = {
            "response": {
                "data": [
                    {
                        "id": "equity123",
                        "company_name": "Test Company",
                        "ticker": "TEST",
                        "bloomberg_ticker": "TEST:US",
                        # No summary fields
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = minimal_response

        args = GetEquitySummariesArgs(bloomberg_ticker="TEST:US")

        # Execute
        result = await get_equity_summaries(args)

        # Verify
        assert len(result.summaries) == 1
        assert result.summaries[0].summary is None  # Should be None when no summary data


@pytest.mark.unit
class TestGetSectorsAndSubsectors:
    """Test the get_sectors_and_subsectors tool."""

    @pytest.mark.asyncio
    async def test_get_sectors_and_subsectors_success(self, mock_http_dependencies):
        """Test successful sectors and subsectors retrieval."""
        # Setup
        sectors_response = {
            "response": {
                "data": [
                    {
                        "sector_id": "10",
                        "sector_name": "Technology",
                        "subsector_id": "1010",
                        "subsector_name": "Software"
                    },
                    {
                        "sector_id": "20",
                        "sector_name": "Healthcare",
                        "subsector_id": None,
                        "subsector_name": None
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = sectors_response

        args = SearchArgs()

        # Execute
        result = await get_sectors_and_subsectors(args)

        # Verify
        assert isinstance(result, GetSectorsSubsectorsResponse)
        assert len(result.sectors) == 2

        # Check first sector
        first_sector = result.sectors[0]
        assert isinstance(first_sector, SectorSubsector)
        assert first_sector.sector_id == "10"
        assert first_sector.sector_name == "Technology"
        assert first_sector.subsector_id == "1010"
        assert first_sector.subsector_name == "Software"

        # Check sector without subsector
        second_sector = result.sectors[1]
        assert second_sector.sector_id == "20"
        assert second_sector.sector_name == "Healthcare"
        assert second_sector.subsector_id is None
        assert second_sector.subsector_name is None

        # Check API call
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['endpoint'] == "/chat-support/get-sectors-and-subsectors"


@pytest.mark.unit
class TestGetAvailableIndexes:
    """Test the get_available_indexes tool."""

    @pytest.mark.asyncio
    async def test_get_available_indexes_success(self, mock_http_dependencies):
        """Test successful indexes retrieval."""
        # Setup
        indexes_response = {
            "response": {
                "data": [
                    {
                        "id": "SP500",
                        "name": "S&P 500",
                        "symbol": "SPX"
                    },
                    {
                        "symbol": "NDX",
                        "name": "NASDAQ 100"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = indexes_response

        args = EmptyArgs()

        # Execute
        result = await get_available_indexes(args)

        # Verify
        assert isinstance(result, GetAvailableIndexesResponse)
        assert len(result.indexes) == 2

        # Check first index
        first_index = result.indexes[0]
        assert isinstance(first_index, IndexItem)
        assert first_index.index_id == "SP500"
        assert first_index.index_name == "S&P 500"
        assert first_index.symbol == "SPX"

        # Check second index (fallback to symbol for ID)
        second_index = result.indexes[1]
        assert second_index.index_id == "NDX"  # Should use symbol as fallback
        assert second_index.index_name == "NASDAQ 100"

        # Check API call
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['endpoint'] == "/chat-support/available-indexes"


@pytest.mark.unit
class TestGetIndexConstituents:
    """Test the get_index_constituents tool."""

    @pytest.mark.asyncio
    async def test_get_index_constituents_success(self, mock_http_dependencies, equities_api_responses):
        """Test successful index constituents retrieval."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["find_equities_success"]

        args = GetIndexConstituentsArgs(index="SP500")

        # Execute
        result = await get_index_constituents(args)

        # Verify
        assert isinstance(result, GetIndexConstituentsResponse)
        assert result.index_name == "SP500"
        assert len(result.constituents) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 50

        # Check constituent
        constituent = result.constituents[0]
        assert isinstance(constituent, EquityItem)
        assert constituent.company_name == "Apple Inc"

        # Check API call
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['endpoint'] == "/chat-support/index-constituents/SP500"

    @pytest.mark.asyncio
    async def test_get_index_constituents_pagination(self, mock_http_dependencies, equities_api_responses):
        """Test index constituents with pagination."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["find_equities_success"]

        args = GetIndexConstituentsArgs(
            index="SP500",
            page=2,
            page_size=25
        )

        # Execute
        result = await get_index_constituents(args)

        # Verify pagination
        assert result.page == 2
        assert result.page_size == 25

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"
        assert params['page_size'] == "25"


@pytest.mark.unit
class TestGetAvailableWatchlists:
    """Test the get_available_watchlists tool."""

    @pytest.mark.asyncio
    async def test_get_available_watchlists_success(self, mock_http_dependencies):
        """Test successful watchlists retrieval."""
        # Setup
        watchlists_response = {
            "response": {
                "data": [
                    {
                        "id": "123",
                        "name": "Tech Giants",
                        "description": "Large technology companies"
                    },
                    {
                        "id": "456",
                        "name": "My Watchlist"
                        # No description
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = watchlists_response

        args = EmptyArgs()

        # Execute
        result = await get_available_watchlists(args)

        # Verify
        assert isinstance(result, GetAvailableWatchlistsResponse)
        assert len(result.watchlists) == 2

        # Check first watchlist
        first_watchlist = result.watchlists[0]
        assert isinstance(first_watchlist, WatchlistItem)
        assert first_watchlist.watchlist_id == "123"
        assert first_watchlist.watchlist_name == "Tech Giants"
        assert first_watchlist.description == "Large technology companies"

        # Check second watchlist (no description)
        second_watchlist = result.watchlists[1]
        assert second_watchlist.watchlist_id == "456"
        assert second_watchlist.watchlist_name == "My Watchlist"
        assert second_watchlist.description is None

        # Check API call
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['endpoint'] == "/chat-support/available-watchlists"


@pytest.mark.unit
class TestGetWatchlistConstituents:
    """Test the get_watchlist_constituents tool."""

    @pytest.mark.asyncio
    async def test_get_watchlist_constituents_success(self, mock_http_dependencies, equities_api_responses):
        """Test successful watchlist constituents retrieval."""
        # Setup - modify response to include metadata
        response_with_metadata = equities_api_responses["find_equities_success"].copy()
        response_with_metadata["response"]["metadata"] = {"watchlist_name": "Tech Giants"}
        mock_http_dependencies['mock_make_request'].return_value = response_with_metadata

        args = GetWatchlistConstituentsArgs(watchlist_id="123")

        # Execute
        result = await get_watchlist_constituents(args)

        # Verify
        assert isinstance(result, GetWatchlistConstituentsResponse)
        assert result.watchlist_name == "Tech Giants"
        assert len(result.constituents) == 1
        assert result.total == 1

        # Check constituent
        constituent = result.constituents[0]
        assert isinstance(constituent, EquityItem)
        assert constituent.company_name == "Apple Inc"

        # Check API call
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['endpoint'] == "/chat-support/watchlist-constituents/123"

    @pytest.mark.asyncio
    async def test_get_watchlist_constituents_no_metadata(self, mock_http_dependencies, equities_api_responses):
        """Test watchlist constituents without metadata."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = equities_api_responses["find_equities_success"]

        args = GetWatchlistConstituentsArgs(watchlist_id="456")

        # Execute
        result = await get_watchlist_constituents(args)

        # Verify - should fall back to watchlist ID for name
        assert result.watchlist_name == "Watchlist 456"


@pytest.mark.unit
class TestEquitiesToolsErrorHandling:
    """Test error handling for equities tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response
        mock_http_dependencies['mock_make_request'].return_value = {"invalid": "response"}

        args = FindEquitiesArgs(search="test")

        # Execute
        result = await find_equities(args)

        # Verify - should handle gracefully with empty results
        assert isinstance(result, FindEquitiesResponse)
        assert len(result.equities) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_handle_missing_market_cap(self, mock_http_dependencies):
        """Test handling of equities with missing market cap."""
        # Setup - response with missing market cap
        response_no_market_cap = {
            "response": {
                "data": [
                    {
                        "id": "equity123",
                        "company_name": "Test Company",
                        "ticker": "TEST",
                        "bloomberg_ticker": "TEST:US",
                        # Missing market_cap
                    }
                ],
                "total": 1
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_no_market_cap

        args = FindEquitiesArgs(bloomberg_ticker="TEST:US")

        # Execute
        result = await find_equities(args)

        # Verify - should still process equity
        assert len(result.equities) == 1
        equity = result.equities[0]
        assert equity.market_cap is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, TimeoutError, ValueError])
    async def test_network_errors_propagate(self, mock_http_dependencies, exception_type):
        """Test that network errors are properly propagated."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies['mock_make_request'].side_effect = exception_type("Test error")

        args = FindEquitiesArgs(search="test")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_equities(args)

    @pytest.mark.asyncio
    async def test_market_cap_handling_large_numbers(self, mock_http_dependencies):
        """Test proper handling of large market cap numbers."""
        # Setup with very large market cap
        large_market_cap_response = {
            "response": {
                "data": [
                    {
                        "id": "equity123",
                        "company_name": "Mega Corp",
                        "ticker": "MEGA",
                        "bloomberg_ticker": "MEGA:US",
                        "market_cap": 5000000000000.0  # 5 trillion
                    }
                ],
                "total": 1
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = large_market_cap_response

        args = FindEquitiesArgs(bloomberg_ticker="MEGA:US")

        # Execute
        result = await find_equities(args)

        # Verify large number is handled correctly
        assert len(result.equities) == 1
        equity = result.equities[0]
        assert equity.market_cap == 5000000000000.0

    @pytest.mark.asyncio
    async def test_sector_subsector_handling_missing_data(self, mock_http_dependencies):
        """Test handling of missing sector/subsector data."""
        # Setup
        missing_sector_response = {
            "response": {
                "data": [
                    {
                        "sector_id": "10",
                        "sector_name": "Technology"
                        # Missing subsector fields
                    },
                    {
                        "sector_id": "20",
                        "sector_name": "Healthcare",
                        "subsector_id": "",  # Empty string
                        "subsector_name": ""
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = missing_sector_response

        args = SearchArgs()

        # Execute
        result = await get_sectors_and_subsectors(args)

        # Verify handling of missing/empty subsector data
        assert len(result.sectors) == 2

        # First sector - completely missing subsector
        first_sector = result.sectors[0]
        assert first_sector.subsector_id is None
        assert first_sector.subsector_name is None

        # Second sector - empty subsector strings should be None
        second_sector = result.sectors[1]
        assert second_sector.subsector_id is None or second_sector.subsector_id == ""
        assert second_sector.subsector_name is None or second_sector.subsector_name == ""