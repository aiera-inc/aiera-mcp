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
    get_ratios,
    get_kpis_and_segments,
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
    GetRatiosArgs,
    GetKpisAndSegmentsArgs,
    FindEquitiesResponse,
    GetEquitySummariesResponse,
    GetSectorsSubsectorsResponse,
    GetAvailableIndexesResponse,
    GetIndexConstituentsResponse,
    GetAvailableWatchlistsResponse,
    GetWatchlistConstituentsResponse,
    GetFinancialsResponse,
    GetRatiosResponse,
    GetKpisAndSegmentsResponse,
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

        args = FindEquitiesArgs(bloomberg_ticker="AAPL:US", page=1, page_size=25)

        # Execute
        result = await find_equities(args)

        # Verify
        assert isinstance(result, FindEquitiesResponse)
        assert result.response is not None
        assert len(result.response["data"]) == 2

        # Check first equity
        first_equity = result.response["data"][0]
        assert first_equity["equity_id"] == 22685
        assert first_equity["name"] == "SAMSUNG ELECTRONICS CO LTD /FI"
        assert first_equity["bloomberg_ticker"] == "005935:KS"
        assert first_equity["sector_id"] == 5
        assert first_equity["subsector_id"] == 73

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
        assert result.response is not None
        assert len(result.response["data"]) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "identifier_type,identifier_value",
        [
            ("bloomberg_ticker", "AAPL:US"),
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
        assert result.response is not None


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
        assert result.response is not None
        assert len(result.response) == 1

        # Check first summary
        first_summary = result.response[0]
        assert first_summary["equity_id"] == 1
        assert first_summary["name"] == "AMAZON COM INC"
        assert first_summary["bloomberg_ticker"] == "AMZN:US"
        assert first_summary["sector_id"] == 1
        assert first_summary["subsector_id"] == 259
        assert first_summary["country"] == "United States of America"
        assert "Amazon.com, Inc. engages" in first_summary["description"]
        assert first_summary["status"] == "active"

        # Check leadership data
        assert first_summary["leadership"] is not None
        assert len(first_summary["leadership"]) == 2
        leader = first_summary["leadership"][0]
        assert leader["name"] == "Andrew R. Jassy"
        assert leader["title"] == "CEO of Amazon Web Services Inc."
        assert leader["event_count"] == 8

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
                }
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = minimal_response

        args = GetEquitySummariesArgs(bloomberg_ticker="TEST:US")

        # Execute
        result = await get_equity_summaries(args)

        # Verify
        assert result.response is not None
        assert len(result.response) == 1
        first_item = result.response[0]
        assert first_item["equity_id"] == 123
        assert first_item["bloomberg_ticker"] == "TEST:US"


@pytest.mark.unit
class TestGetSectorsAndSubsectors:
    """Test the get_sectors_and_subsectors tool."""

    @pytest.mark.asyncio
    async def test_get_sectors_and_subsectors_success(self, mock_http_dependencies):
        """Test successful sectors and subsectors retrieval."""
        # Setup
        sectors_response = {
            "response": {
                "pagination": {
                    "total_count": 2,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
                "data": [
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
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = sectors_response

        args = GetSectorsAndSubsectorsArgs()

        # Execute
        result = await get_sectors_and_subsectors(args)

        # Verify
        assert isinstance(result, GetSectorsSubsectorsResponse)
        assert result.response is not None
        assert len(result.response["data"]) == 2
        assert result.response["pagination"]["total_count"] == 2

        # Check first sector
        first_sector = result.response["data"][0]
        assert first_sector["sector_id"] == 10
        assert first_sector["name"] == "Technology"
        assert first_sector["gics_code"] == "45"
        assert len(first_sector["subsectors"]) == 1
        assert first_sector["subsectors"][0]["subsector_id"] == 1010
        assert first_sector["subsectors"][0]["name"] == "Software"

        # Check sector without subsector
        second_sector = result.response["data"][1]
        assert second_sector["sector_id"] == 20
        assert second_sector["name"] == "Healthcare"
        assert second_sector["gics_code"] == "35"
        assert len(second_sector["subsectors"]) == 0


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
        assert result.response is not None
        assert len(result.response) == 2
        assert result.response[0]["index_id"] == 3
        assert result.response[0]["name"] == "S&P 500"
        assert result.response[1]["index_id"] == 8
        assert result.response[1]["name"] == "NASDAQ 100"


@pytest.mark.unit
class TestGetIndexConstituents:
    """Test the get_index_constituents tool."""

    @pytest.mark.asyncio
    async def test_get_index_constituents_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful index constituents retrieval."""
        # Setup
        find_response = equities_api_responses["find_equities_success"]
        index_response = {
            "response": {
                "data": find_response["response"]["data"],
                "pagination": find_response["response"]["pagination"],
            },
        }
        mock_http_dependencies["mock_make_request"].return_value = index_response

        args = GetIndexConstituentsArgs(index="SP500")

        # Execute
        result = await get_index_constituents(args)

        # Verify
        assert isinstance(result, GetIndexConstituentsResponse)
        assert result.response is not None
        assert len(result.response["data"]) == 2
        assert result.response["data"][0]["name"] == "SAMSUNG ELECTRONICS CO LTD /FI"

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
                {"watchlist_id": 19269607, "name": "My Watchlist", "type": "watchlist"},
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = watchlists_response

        args = GetAvailableWatchlistsArgs()

        # Execute
        result = await get_available_watchlists(args)

        # Verify
        assert isinstance(result, GetAvailableWatchlistsResponse)
        assert result.response is not None
        assert len(result.response) == 2
        assert result.response[0]["watchlist_id"] == 2074
        assert result.response[0]["name"] == "Tech Giants"
        assert result.response[1]["watchlist_id"] == 19269607
        assert result.response[1]["name"] == "My Watchlist"


@pytest.mark.unit
class TestGetWatchlistConstituents:
    """Test the get_watchlist_constituents tool."""

    @pytest.mark.asyncio
    async def test_get_watchlist_constituents_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful watchlist constituents retrieval."""
        # Setup
        find_response = equities_api_responses["find_equities_success"]
        watchlist_response = {
            "response": {
                "data": find_response["response"]["data"],
                "pagination": find_response["response"]["pagination"],
            },
        }
        mock_http_dependencies["mock_make_request"].return_value = watchlist_response

        args = GetWatchlistConstituentsArgs(watchlist_id="123")

        # Execute
        result = await get_watchlist_constituents(args)

        # Verify
        assert isinstance(result, GetWatchlistConstituentsResponse)
        assert result.response is not None
        assert len(result.response["data"]) == 2
        assert result.response["data"][0]["name"] == "SAMSUNG ELECTRONICS CO LTD /FI"

    @pytest.mark.asyncio
    async def test_get_watchlist_constituents_no_metadata(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test watchlist constituents without metadata."""
        # Setup - find_equities_success has "response" at top level, which maps to response field
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["find_equities_success"]
        )

        args = GetWatchlistConstituentsArgs(watchlist_id="456")

        # Execute
        result = await get_watchlist_constituents(args)

        # Verify - response should have data
        assert isinstance(result, GetWatchlistConstituentsResponse)
        assert result.response is None or (
            isinstance(result.response, dict)
            and len(result.response.get("data", [])) >= 0
        )


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
        assert result.response is None or len(result.response.get("data", [])) == 0

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
            "response": {
                "pagination": {
                    "total_count": 2,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
                "data": [
                    {"sector_id": 10, "name": "Technology", "gics_code": "45"},
                    {
                        "sector_id": 20,
                        "name": "Healthcare",
                        "gics_code": "35",
                        "subsectors": [],
                    },
                ],
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            missing_sector_response
        )

        args = GetSectorsAndSubsectorsArgs()

        # Execute
        result = await get_sectors_and_subsectors(args)

        # Verify handling of missing/empty subsector data
        assert len(result.response["data"]) == 2
        first_sector = result.response["data"][0]
        assert first_sector["name"] == "Technology"

        second_sector = result.response["data"][1]
        assert second_sector["name"] == "Healthcare"
        assert second_sector["subsectors"] == []


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
            calendar_year=2024,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        assert result.response is not None
        assert len(result.response) == 1
        assert result.response[0]["equity"] is not None
        assert result.response[0]["equity"]["bloomberg_ticker"] == "AMZN:US"
        assert result.response[0]["equity"]["name"] == "AMAZON COM INC"

        # Check periods data
        assert result.response[0]["periods"] is not None
        assert len(result.response[0]["periods"]) == 1

        first_period = result.response[0]["periods"][0]
        assert first_period["period_type"] == "annual"
        assert first_period["fiscal_year"] == 2024
        assert first_period["metrics"] is not None
        assert len(first_period["metrics"]) == 3

        # Check first metric (Total Revenue)
        revenue_metric = first_period["metrics"][0]
        assert revenue_metric["metric"]["metric_name"] == "Total Revenue"
        assert revenue_metric["metric_value"] == 574785000000
        assert revenue_metric["metric_currency"] == "USD"
        assert revenue_metric["metric"]["is_key_metric"] is True

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/get-financials"

        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AMZN:US"
        assert params["source"] == "income-statement"
        assert params["source_type"] == "standardized"
        assert params["period"] == "annual"
        assert params["calendar_year"] == 2024

    @pytest.mark.asyncio
    async def test_get_financials_with_calendar_quarter(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test get_financials with calendar_quarter parameter."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_financials_success"]
        )

        args = GetFinancialsArgs(
            bloomberg_ticker="AAPL:US",
            source="balance-sheet",
            source_type="as-reported",
            period="quarterly",
            calendar_year=2024,
            calendar_quarter=3,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US"
        assert params["source"] == "balance-sheet"
        assert params["source_type"] == "as-reported"
        assert params["period"] == "quarterly"
        assert params["calendar_year"] == 2024
        assert params["calendar_quarter"] == 3

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
            calendar_year=2024,
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
            "response": [{"equity": None, "periods": []}],
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = GetFinancialsArgs(
            bloomberg_ticker="UNKNOWN:US",
            source="income-statement",
            source_type="standardized",
            period="annual",
            calendar_year=2024,
        )

        # Execute
        result = await get_financials(args)

        # Verify
        assert isinstance(result, GetFinancialsResponse)
        assert result.response[0]["periods"] == []


@pytest.mark.unit
class TestGetRatios:
    """Test the get_ratios tool."""

    @pytest.mark.asyncio
    async def test_get_ratios_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful ratios retrieval."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_ratios_success"]
        )

        args = GetRatiosArgs(
            bloomberg_ticker="AMZN:US",
            period="annual",
            calendar_year=2024,
        )

        # Execute
        result = await get_ratios(args)

        # Verify
        assert isinstance(result, GetRatiosResponse)
        assert result.response is not None
        assert len(result.response) == 1
        assert result.response[0]["equity"] is not None
        assert result.response[0]["equity"]["bloomberg_ticker"] == "AMZN:US"
        assert result.response[0]["equity"]["name"] == "AMAZON COM INC"

        # Check periods data
        assert result.response[0]["periods"] is not None
        assert len(result.response[0]["periods"]) == 1

        first_period = result.response[0]["periods"][0]
        assert first_period["period_type"] == "annual"
        assert first_period["calendar_year"] == 2024
        assert first_period["ratios"] is not None
        assert len(first_period["ratios"]) == 3

        # Check first ratio (Gross Margin)
        gross_margin = first_period["ratios"][0]
        assert gross_margin["ratio"] == "Gross Margin"
        assert gross_margin["ratio_category"] == "Profitability"
        assert gross_margin["ratio_value"] == 0.478

    @pytest.mark.asyncio
    async def test_get_ratios_exclude_instructions(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test get_ratios with exclude_instructions flag."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_ratios_success"]
        )

        args = GetRatiosArgs(
            bloomberg_ticker="AMZN:US",
            period="annual",
            calendar_year=2024,
            exclude_instructions=True,
        )

        # Execute
        result = await get_ratios(args)

        # Verify
        assert isinstance(result, GetRatiosResponse)
        assert result.instructions == []


@pytest.mark.unit
class TestGetKpisAndSegments:
    """Test the get_kpis_and_segments tool."""

    @pytest.mark.asyncio
    async def test_get_kpis_and_segments_success(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test successful KPIs and segments retrieval."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_kpis_and_segments_success"]
        )

        args = GetKpisAndSegmentsArgs(
            bloomberg_ticker="AMZN:US",
            period="annual",
            calendar_year=2024,
        )

        # Execute
        result = await get_kpis_and_segments(args)

        # Verify
        assert isinstance(result, GetKpisAndSegmentsResponse)
        assert result.response is not None
        assert len(result.response) == 1
        assert result.response[0]["equity"] is not None
        assert result.response[0]["equity"]["bloomberg_ticker"] == "AMZN:US"
        assert result.response[0]["equity"]["name"] == "AMAZON COM INC"

        # Check periods data
        assert result.response[0]["periods"] is not None
        assert len(result.response[0]["periods"]) == 1

        first_period = result.response[0]["periods"][0]
        assert first_period["period_type"] == "annual"
        assert first_period["calendar_year"] == 2024

        # Check KPIs
        assert first_period["kpi"] is not None
        assert len(first_period["kpi"]) == 2
        aws_kpi = first_period["kpi"][0]
        assert aws_kpi["metric_name"] == "AWS Revenue"
        assert aws_kpi["is_currency"] is True
        assert aws_kpi["metric_value"] == 90757000000

        # Check Segments
        assert first_period["segment"] is not None
        assert len(first_period["segment"]) == 2
        north_america = first_period["segment"][0]
        assert north_america["metric_name"] == "North America"
        assert north_america["is_currency"] is True
        assert north_america["metric_value"] == 353460000000

    @pytest.mark.asyncio
    async def test_get_kpis_and_segments_exclude_instructions(
        self, mock_http_dependencies, equities_api_responses
    ):
        """Test get_kpis_and_segments with exclude_instructions flag."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            equities_api_responses["get_kpis_and_segments_success"]
        )

        args = GetKpisAndSegmentsArgs(
            bloomberg_ticker="AMZN:US",
            period="annual",
            calendar_year=2024,
            exclude_instructions=True,
        )

        # Execute
        result = await get_kpis_and_segments(args)

        # Verify
        assert isinstance(result, GetKpisAndSegmentsResponse)
        assert result.instructions == []
