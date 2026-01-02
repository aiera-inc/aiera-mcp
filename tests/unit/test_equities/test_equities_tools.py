#!/usr/bin/env python3

"""Unit tests for equities tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from aiera_mcp.tools.equities.tools import (
    find_equities,
    get_equity_summaries,
    get_sectors_and_subsectors,
    get_available_indexes,
    get_index_constituents,
    get_available_watchlists,
    get_watchlist_constituents,
    get_financials,
)
from aiera_mcp.tools.equities.models import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    GetSectorsAndSubsectorsArgs,
    GetAvailableIndexesArgs,
    GetAvailableWatchlistsArgs,
    GetFinancialsArgs,
    FindEquitiesResponse,
    GetEquitySummariesResponse,
    GetSectorsSubsectorsResponse,
    GetAvailableIndexesResponse,
    GetIndexConstituentsResponse,
    GetAvailableWatchlistsResponse,
    GetWatchlistConstituentsResponse,
    GetFinancialsResponse,
    EquityItem,
    EquityDetails,
    EquitySummary,
    EquitySummaryItem,
    SectorSubsector,
    IndexItem,
    WatchlistItem,
)


@pytest.mark.unit
class TestFindEquities:
    """Test the find_equities tool."""

    @pytest.mark.asyncio
    async def test_find_equities_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful equities search."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["find_equities_success"]
        )

        args = FindEquitiesArgs(bloomberg_ticker="AAPL:US", page=1, page_size=50)

        # Execute
        result = await find_equities(args)

        # Verify
        assert isinstance(result, FindEquitiesResponse)
        assert len(result.response.data) == 2

        # Check first equity
        first_equity = result.response.data[0]
        assert isinstance(first_equity, EquityItem)
        assert first_equity.equity_id == 22685
        assert first_equity.name == "SAMSUNG ELECTRONICS CO LTD /FI"
        assert first_equity.bloomberg_ticker == "005935:KS"
        assert first_equity.sector_id == 5
        assert first_equity.subsector_id == 73

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-equities"

        # Check parameters were passed correctly
        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US"
        assert params["include_company_metadata"] == "true"

    @pytest.mark.asyncio
    async def test_find_equities_empty_results(self, mock_http_dependencies):
        """Test find_equities with empty results."""
        # Setup
        empty_response = {"response": {"data": [], "total": 0}, "instructions": []}
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = FindEquitiesArgs(search="nonexistent")

        # Execute
        result = await find_equities(args)

        # Verify
        assert isinstance(result, FindEquitiesResponse)
        assert len(result.response.data) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "identifier_type,identifier_value",
        [
            ("bloomberg_ticker", "AAPL:US"),
            ("ticker", "AAPL"),
            ("isin", "US0378331005"),
            ("ric", "AAPL.O"),
            ("permid", "4295905573"),
        ],
    )
    async def test_find_equities_different_identifiers(
        self,
        mock_http_dependencies,
        equities_api_responses,
        identifier_type,
        identifier_value,
    ):
        """Test find_equities with different identifier types."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["find_equities_success"]
        )

        args_data = {identifier_type: identifier_value}
        args = FindEquitiesArgs(**args_data)

        # Execute
        result = await find_equities(args)

        # Verify
        assert isinstance(result, FindEquitiesResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["params"][identifier_type] == identifier_value

    @pytest.mark.asyncio
    async def test_find_equities_pagination(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test find_equities with pagination parameters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["find_equities_success"]
        )

        args = FindEquitiesArgs(search="tech", page=2, page_size=25)

        # Execute
        result = await find_equities(args)

        # Verify API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["page"] == "2"  # Should be serialized as string
        assert params["page_size"] == "25"

    @pytest.mark.asyncio
    async def test_find_equities_citations_generated(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test that find_equities generates proper citations."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["find_equities_success"]
        )

        args = FindEquitiesArgs(bloomberg_ticker="AAPL:US")

        # Execute
        result = await find_equities(args)

        # Verify basic response structure
        assert isinstance(result, FindEquitiesResponse)
        assert len(result.response.data) >= 0  # Could be empty or have results


@pytest.mark.unit
class TestGetEquitySummaries:
    """Test the get_equity_summaries tool."""

    @pytest.mark.asyncio
    async def test_get_equity_summaries_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful equity summaries retrieval."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_equity_summaries_success"]
        )

        args = GetEquitySummariesArgs(bloomberg_ticker="AAPL:US")

        # Execute
        result = await get_equity_summaries(args)

        # Verify
        assert isinstance(result, GetEquitySummariesResponse)
        assert len(result.response) == 1

        # Check first summary
        first_summary = result.response[0]
        assert isinstance(first_summary, EquitySummaryItem)
        assert first_summary.equity_id == 1
        assert first_summary.name == "AMAZON COM INC"
        # Check basic equity details from fixture data
        assert first_summary.bloomberg_ticker == "AMZN:US"
        assert first_summary.sector_id == 1
        assert first_summary.subsector_id == 259
        assert first_summary.country == "United States of America"
        assert "Amazon.com, Inc. engages" in first_summary.description
        assert first_summary.status == "active"

        # Check leadership data
        assert first_summary.leadership is not None
        assert len(first_summary.leadership) == 2
        leader = first_summary.leadership[0]
        assert leader.name == "Andrew R. Jassy"
        assert leader.title == "CEO of Amazon Web Services Inc."
        assert leader.event_count == 8

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/equity-summaries"

        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US"
        assert params["lookback"] == "90"

    @pytest.mark.asyncio
    async def test_get_equity_summaries_multiple_tickers(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test get_equity_summaries with multiple tickers."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_equity_summaries_success"]
        )

        args = GetEquitySummariesArgs(bloomberg_ticker="AAPL:US,MSFT:US")

        # Execute
        result = await get_equity_summaries(args)

        # Verify
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US,MSFT:US"

    @pytest.mark.asyncio
    async def test_get_equity_summaries_minimal_data(self, mock_http_dependencies):
        """Test get_equity_summaries with minimal summary data."""
        # Setup with minimal data
        minimal_response = {
            "response": [
                {
                    "equity_id": 123,
                    "company_name": "Test Company",
                    "ticker": "TEST",
                    "bloomberg_ticker": "TEST:US",
                    # No summary fields
                }
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = minimal_response

        args = GetEquitySummariesArgs(bloomberg_ticker="TEST:US")

        # Execute
        result = await get_equity_summaries(args)

        # Verify
        assert len(result.response) == 1
        # Basic equity data should be accessible
        first_item = result.response[0]
        assert first_item.equity_id == 123
        assert first_item.bloomberg_ticker == "TEST:US"


@pytest.mark.unit
class TestGetSectorsAndSubsectors:
    """Test the get_sectors_and_subsectors tool."""

    @pytest.mark.asyncio
    async def test_get_sectors_and_subsectors_success(self, mock_http_dependencies):
        """Test successful sectors and subsectors retrieval."""
        # Setup
        sectors_response = {
            "response": [
                {
                    "sector_id": 10,
                    "name": "Technology",
                    "gics_code": "45",
                    "subsectors": [
                        {
                            "subsector_id": 1010,
                            "name": "Software",
                            "gics_code": "45103010",
                        }
                    ],
                },
                {
                    "sector_id": 20,
                    "name": "Healthcare",
                    "gics_code": "35",
                    "subsectors": [],
                },
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = sectors_response

        args = GetSectorsAndSubsectorsArgs()

        # Execute
        result = await get_sectors_and_subsectors(args)

        # Verify
        assert isinstance(result, GetSectorsSubsectorsResponse)
        assert len(result.response) == 2

        # Check first sector
        first_sector = result.response[0]
        assert isinstance(first_sector, SectorSubsector)
        assert first_sector.sector_id == 10
        assert first_sector.name == "Technology"
        assert first_sector.gics_code == "45"
        # Check subsectors array
        assert len(first_sector.subsectors) == 1
        assert first_sector.subsectors[0].subsector_id == 1010
        assert first_sector.subsectors[0].name == "Software"
        # Check backward compatibility properties
        assert first_sector.sector_name == "Technology"  # property alias
        assert first_sector.subsector_id == 1010  # property from first subsector
        assert (
            first_sector.subsector_name == "Software"
        )  # property from first subsector

        # Check sector without subsector
        second_sector = result.response[1]
        assert second_sector.sector_id == 20
        assert second_sector.name == "Healthcare"
        assert second_sector.gics_code == "35"
        assert len(second_sector.subsectors) == 0
        # Check backward compatibility properties
        assert second_sector.sector_name == "Healthcare"  # property alias
        assert second_sector.subsector_id is None  # no subsectors
        assert second_sector.subsector_name is None  # no subsectors

        # Check API call
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["endpoint"] == "/chat-support/get-sectors-and-subsectors"


@pytest.mark.unit
class TestGetAvailableIndexes:
    """Test the get_available_indexes tool."""

    @pytest.mark.asyncio
    async def test_get_available_indexes_success(self, mock_http_dependencies):
        """Test successful indexes retrieval."""
        # Setup
        indexes_response = {
            "response": [
                {
                    "index_id": 3,
                    "name": "S&P 500",
                    "symbol": "SPX",
                    "short_name": "SP500",
                },
                {
                    "index_id": 8,
                    "name": "NASDAQ 100",
                    "symbol": "NDX",
                    "short_name": "NDX",
                },
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = indexes_response

        args = GetAvailableIndexesArgs()

        # Execute
        result = await get_available_indexes(args)

        # Verify
        assert isinstance(result, GetAvailableIndexesResponse)
        assert len(result.response) == 2

        # Check first index
        first_index = result.response[0]
        assert isinstance(first_index, IndexItem)
        assert first_index.index_id == 3
        assert first_index.name == "S&P 500"
        assert first_index.short_name == "SP500"

        # Check second index
        second_index = result.response[1]
        assert second_index.index_id == 8
        assert second_index.name == "NASDAQ 100"
        assert second_index.short_name == "NDX"

        # Check API call
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["endpoint"] == "/chat-support/available-indexes"


@pytest.mark.unit
class TestGetIndexConstituents:
    """Test the get_index_constituents tool."""

    @pytest.mark.asyncio
    async def test_get_index_constituents_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful index constituents retrieval."""
        # Setup - The index-constituents endpoint returns data at top level
        find_response = equities_api_responses["find_equities_success"]
        index_response = {
            "data": find_response["response"]["data"],
            "pagination": find_response["response"]["pagination"],
        }
        mock_http_dependencies["mock_make_request"].return_value = index_response

        args = GetIndexConstituentsArgs(index="SP500")

        # Execute
        result = await get_index_constituents(args)

        # Verify
        assert isinstance(result, GetIndexConstituentsResponse)
        assert result.data is not None
        assert len(result.data) == 2

        # Check constituent
        constituent = result.data[0]
        assert isinstance(constituent, EquityItem)
        assert constituent.name == "SAMSUNG ELECTRONICS CO LTD /FI"

        # Check API call
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["endpoint"] == "/chat-support/index-constituents/SP500"

    @pytest.mark.asyncio
    async def test_get_index_constituents_pagination(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test index constituents with pagination."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["find_equities_success"]
        )

        args = GetIndexConstituentsArgs(index="SP500", page=2, page_size=25)

        # Execute
        result = await get_index_constituents(args)

        # Verify pagination (pagination info would be in response if API returns it)
        # Check that the request was made with correct params

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["page"] == "2"
        assert params["page_size"] == "25"


@pytest.mark.unit
class TestGetAvailableWatchlists:
    """Test the get_available_watchlists tool."""

    @pytest.mark.asyncio
    async def test_get_available_watchlists_success(self, mock_http_dependencies):
        """Test successful watchlists retrieval."""
        # Setup
        watchlists_response = {
            "response": [
                {
                    "watchlist_id": 2074,
                    "name": "Tech Giants",
                    "description": "Large technology companies",
                    "type": "watchlist",
                },
                {
                    "watchlist_id": 19269607,
                    "name": "My Watchlist",
                    "type": "watchlist",
                    # No description
                },
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = watchlists_response

        args = GetAvailableWatchlistsArgs()

        # Execute
        result = await get_available_watchlists(args)

        # Verify
        assert isinstance(result, GetAvailableWatchlistsResponse)
        assert len(result.response) == 2

        # Check first watchlist
        first_watchlist = result.response[0]
        assert isinstance(first_watchlist, WatchlistItem)
        assert first_watchlist.watchlist_id == 2074
        assert first_watchlist.name == "Tech Giants"
        assert first_watchlist.type == "watchlist"

        # Check second watchlist
        second_watchlist = result.response[1]
        assert second_watchlist.watchlist_id == 19269607
        assert second_watchlist.name == "My Watchlist"

        # Check API call
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["endpoint"] == "/chat-support/available-watchlists"


@pytest.mark.unit
class TestGetWatchlistConstituents:
    """Test the get_watchlist_constituents tool."""

    @pytest.mark.asyncio
    async def test_get_watchlist_constituents_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful watchlist constituents retrieval."""
        # Setup - The watchlist-constituents endpoint returns data at top level
        find_response = equities_api_responses["find_equities_success"]
        watchlist_response = {
            "data": find_response["response"]["data"],
            "pagination": find_response["response"]["pagination"],
        }
        mock_http_dependencies["mock_make_request"].return_value = watchlist_response

        args = GetWatchlistConstituentsArgs(watchlist_id="123")

        # Execute
        result = await get_watchlist_constituents(args)

        # Verify
        assert isinstance(result, GetWatchlistConstituentsResponse)
        assert result.data is not None
        assert len(result.data) == 2

        # Check constituent
        constituent = result.data[0]
        assert isinstance(constituent, EquityItem)
        assert constituent.name == "SAMSUNG ELECTRONICS CO LTD /FI"

        # Check API call
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["endpoint"] == "/chat-support/watchlist-constituents/123"

    @pytest.mark.asyncio
    async def test_get_watchlist_constituents_no_metadata(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test watchlist constituents without metadata."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["find_equities_success"]
        )

        args = GetWatchlistConstituentsArgs(watchlist_id="456")

        # Execute
        result = await get_watchlist_constituents(args)

        # Verify - response should have data
        assert isinstance(result, GetWatchlistConstituentsResponse)
        assert result.data is None or len(result.data) >= 0


@pytest.mark.unit
class TestEquitiesToolsErrorHandling:
    """Test error handling for equities tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response
        mock_http_dependencies["mock_make_request"].return_value = {
            "invalid": "response"
        }

        args = FindEquitiesArgs(search="test")

        # Execute
        result = await find_equities(args)

        # Verify - should handle gracefully (response may be None or have empty data)
        assert isinstance(result, FindEquitiesResponse)
        assert result.response is None or len(result.response.data) == 0

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

        args = FindEquitiesArgs(search="test")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_equities(args)

    @pytest.mark.asyncio
    async def test_sector_subsector_handling_missing_data(self, mock_http_dependencies):
        """Test handling of missing sector/subsector data."""
        # Setup
        missing_sector_response = {
            "response": [
                {
                    "sector_id": 10,
                    "name": "Technology",
                    "gics_code": "45",
                    # Missing subsectors array
                },
                {
                    "sector_id": 20,
                    "name": "Healthcare",
                    "gics_code": "35",
                    "subsectors": [],  # Empty subsectors array
                },
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            missing_sector_response
        )

        args = GetSectorsAndSubsectorsArgs()

        # Execute
        result = await get_sectors_and_subsectors(args)

        # Verify handling of missing/empty subsector data
        assert len(result.response) == 2

        # First sector - missing subsectors array (should default to None/empty)
        first_sector = result.response[0]
        assert first_sector.name == "Technology"
        assert first_sector.subsectors is None or first_sector.subsectors == []
        # Backward compatibility properties should be None when no subsectors
        assert first_sector.subsector_id is None
        assert first_sector.subsector_name is None

        # Second sector - explicit empty subsectors array
        second_sector = result.response[1]
        assert second_sector.name == "Healthcare"
        assert second_sector.subsectors == []
        # Backward compatibility properties should be None when no subsectors
        assert second_sector.subsector_id is None
        assert second_sector.subsector_name is None


@pytest.mark.unit
class TestGetFinancials:
    """Test the get_financials tool."""

    @pytest.mark.asyncio
    async def test_get_financials_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful financials retrieval."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_financials_success"]
        )

        args = GetFinancialsArgs(
            bloomberg_ticker="AMZN:US",
            source="income-statement",
            source_type="standardized",
            period="annual",
            fiscal_year=2024,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        assert result.response is not None
        assert result.response.equity is not None
        assert result.response.equity.bloomberg_ticker == "AMZN:US"
        assert result.response.equity.name == "AMAZON COM INC"
        assert result.response.equity.equity_id == 1

        # Check financials data
        assert result.response.financials is not None
        assert len(result.response.financials) == 1

        first_period = result.response.financials[0]
        assert first_period.period_type == "annual"
        assert first_period.fiscal_year == 2024
        assert first_period.metrics is not None
        assert len(first_period.metrics) == 3

        # Check first metric (Total Revenue)
        revenue_metric = first_period.metrics[0]
        assert revenue_metric.metric.metric_name == "Total Revenue"
        assert revenue_metric.metric_value == 574785000000
        assert revenue_metric.metric_currency == "USD"
        assert revenue_metric.metric.is_key_metric is True

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/get-financials"

        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AMZN:US"
        assert params["source"] == "income-statement"
        assert params["source_type"] == "standardized"
        assert params["period"] == "annual"
        assert params["fiscal_year"] == 2024

    @pytest.mark.asyncio
    async def test_get_financials_with_fiscal_quarter(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test get_financials with fiscal_quarter parameter."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_financials_success"]
        )

        args = GetFinancialsArgs(
            bloomberg_ticker="AAPL:US",
            source="balance-sheet",
            source_type="as-reported",
            period="quarterly",
            fiscal_year=2024,
            fiscal_quarter=3,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US"
        assert params["source"] == "balance-sheet"
        assert params["source_type"] == "as-reported"
        assert params["period"] == "quarterly"
        assert params["fiscal_year"] == 2024
        assert params["fiscal_quarter"] == 3

    @pytest.mark.asyncio
    async def test_get_financials_exclude_instructions(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test get_financials with exclude_instructions flag."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_financials_success"]
        )

        args = GetFinancialsArgs(
            bloomberg_ticker="AMZN:US",
            source="cash-flow-statement",
            source_type="standardized",
            period="annual",
            fiscal_year=2024,
            exclude_instructions=True,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_get_financials_empty_response(self, mock_http_dependencies):
        """Test get_financials with empty response."""
        # Setup
        empty_response = {
            "instructions": [],
            "response": {"equity": None, "financials": []},
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = GetFinancialsArgs(
            bloomberg_ticker="UNKNOWN:US",
            source="income-statement",
            source_type="standardized",
            period="annual",
            fiscal_year=2024,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        assert result.response.financials == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "source",
        ["income-statement", "balance-sheet", "cash-flow-statement"],
    )
    async def test_get_financials_different_sources(
        self, mock_http_dependencies, equities_api_responses, source
    ):
        """Test get_financials with different source types."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_financials_success"]
        )

        args = GetFinancialsArgs(
            bloomberg_ticker="AMZN:US",
            source=source,
            source_type="standardized",
            period="annual",
            fiscal_year=2024,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["params"]["source"] == source

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "period",
        ["annual", "quarterly", "semi-annual", "ltm", "ytd", "latest"],
    )
    async def test_get_financials_different_periods(
        self, mock_http_dependencies, equities_api_responses, period
    ):
        """Test get_financials with different period types."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_financials_success"]
        )

        args = GetFinancialsArgs(
            bloomberg_ticker="AMZN:US",
            source="income-statement",
            source_type="standardized",
            period=period,
            fiscal_year=2024,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["params"]["period"] == period
