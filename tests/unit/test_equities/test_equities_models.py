#!/usr/bin/env python3

"""Unit tests for equities models."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.equities.models import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
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
class TestFindEquitiesArgs:
    """Test FindEquitiesArgs model."""

    def test_valid_find_equities_args(self):
        """Test valid FindEquitiesArgs creation."""
        args = FindEquitiesArgs(
            bloomberg_ticker="AAPL:US",
            isin="US0378331005",
            search="Apple",
            page=1,
            page_size=25,
        )

        assert args.bloomberg_ticker == "AAPL:US"
        assert args.isin == "US0378331005"
        assert args.search == "Apple"
        assert args.page == 1
        assert args.page_size == 25

    def test_find_equities_args_defaults(self):
        """Test FindEquitiesArgs with default values."""
        args = FindEquitiesArgs()

        assert args.page == 1  # Default value
        assert args.page_size == 25  # Default value
        assert args.bloomberg_ticker is None
        assert args.isin is None
        assert args.ric is None
        assert args.permid is None
        assert args.search is None
        assert args.originating_prompt is None  # Default value

    def test_find_equities_args_with_originating_prompt(self):
        """Test FindEquitiesArgs with originating_prompt field."""
        args = FindEquitiesArgs(
            bloomberg_ticker="AAPL:US",
            originating_prompt="Find information about Apple stock",
        )

        assert args.originating_prompt == "Find information about Apple stock"

    def test_find_equities_args_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid pagination
        args = FindEquitiesArgs(page=5, page_size=25)
        assert args.page == 5
        assert args.page_size == 25

        # Page must be >= 1
        with pytest.raises(ValidationError):
            FindEquitiesArgs(page=0)

        # Page size must be >= 1
        with pytest.raises(ValidationError):
            FindEquitiesArgs(page_size=0)

        # page_size above 25 is accepted (capped server-side)
        args = FindEquitiesArgs(page_size=26)
        assert args.page_size == 26

    def test_find_equities_args_numeric_field_serialization(self):
        """Test that numeric fields are serialized as strings."""
        args = FindEquitiesArgs(page=2, page_size=25)

        # Model dump should serialize numeric fields as strings
        dumped = args.model_dump(exclude_none=True)
        assert dumped["page"] == "2"
        assert dumped["page_size"] == "25"

    @pytest.mark.parametrize(
        "identifier_type,identifier_value",
        [
            ("bloomberg_ticker", "AAPL:US"),
            ("isin", "US0378331005"),
            ("ric", "AAPL.O"),
            ("permid", "4295905573"),
        ],
    )
    def test_find_equities_args_identifier_types(
        self, identifier_type, identifier_value
    ):
        """Test various identifier types."""
        args_data = {identifier_type: identifier_value}
        args = FindEquitiesArgs(**args_data)

        assert getattr(args, identifier_type) == identifier_value

    def test_bloomberg_ticker_validation(self):
        """Test Bloomberg ticker validation and correction."""
        # Test with properly formatted ticker
        args = FindEquitiesArgs(bloomberg_ticker="AAPL:US")
        assert args.bloomberg_ticker == "AAPL:US"

        # Test with multiple tickers (GOOGL:US is aliased to GOOG:US)
        args = FindEquitiesArgs(bloomberg_ticker="AAPL:US,MSFT:US,GOOGL:US")
        assert args.bloomberg_ticker == "AAPL:US,MSFT:US,GOOG:US"


@pytest.mark.unit
class TestGetEquitySummariesArgs:
    """Test GetEquitySummariesArgs model."""

    def test_valid_get_equity_summaries_args(self):
        """Test valid GetEquitySummariesArgs creation."""
        args = GetEquitySummariesArgs(bloomberg_ticker="AAPL:US")
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.originating_prompt is None
        assert args.include_base_instructions is True

    def test_get_equity_summaries_args_with_originating_prompt(self):
        """Test GetEquitySummariesArgs with originating_prompt field."""
        args = GetEquitySummariesArgs(
            bloomberg_ticker="AAPL:US",
            originating_prompt="Get summary for Apple",
            include_base_instructions=False,
        )
        assert args.originating_prompt == "Get summary for Apple"
        assert args.include_base_instructions is False

    def test_get_equity_summaries_args_required_field(self):
        """Test that bloomberg_ticker is required."""
        with pytest.raises(ValidationError) as exc_info:
            GetEquitySummariesArgs()

        assert "bloomberg_ticker" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_get_equity_summaries_args_multiple_tickers(self):
        """Test multiple tickers."""
        args = GetEquitySummariesArgs(bloomberg_ticker="AAPL:US,MSFT:US")
        assert args.bloomberg_ticker == "AAPL:US,MSFT:US"


@pytest.mark.unit
class TestGetIndexConstituentsArgs:
    """Test GetIndexConstituentsArgs model."""

    def test_valid_get_index_constituents_args(self):
        """Test valid GetIndexConstituentsArgs creation."""
        args = GetIndexConstituentsArgs(index="SP500", page=1, page_size=25)

        assert args.index == "SP500"
        assert args.page == 1
        assert args.page_size == 25

    def test_get_index_constituents_args_defaults(self):
        """Test GetIndexConstituentsArgs with default values."""
        args = GetIndexConstituentsArgs(index="SP500")

        assert args.index == "SP500"
        assert args.page == 1
        assert args.page_size == 25
        assert args.originating_prompt is None

    def test_get_index_constituents_args_required_field(self):
        """Test that index is required."""
        with pytest.raises(ValidationError) as exc_info:
            GetIndexConstituentsArgs()

        assert "index" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)


@pytest.mark.unit
class TestGetWatchlistConstituentsArgs:
    """Test GetWatchlistConstituentsArgs model."""

    def test_valid_get_watchlist_constituents_args(self):
        """Test valid GetWatchlistConstituentsArgs creation."""
        args = GetWatchlistConstituentsArgs(watchlist_id=123, page=1, page_size=25)

        assert args.watchlist_id == 123  # Stored as int
        assert args.page == 1
        assert args.page_size == 25

    def test_get_watchlist_constituents_args_defaults(self):
        """Test GetWatchlistConstituentsArgs with default values."""
        args = GetWatchlistConstituentsArgs(watchlist_id=123)

        assert args.watchlist_id == 123  # Stored as int
        assert args.page == 1
        assert args.page_size == 25
        assert args.originating_prompt is None

    def test_get_watchlist_constituents_args_required_field(self):
        """Test that watchlist_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            GetWatchlistConstituentsArgs()

        assert "watchlist_id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)


@pytest.mark.unit
class TestEquitiesResponses:
    """Test equities response models with pass-through pattern."""

    def test_find_equities_response(self):
        """Test FindEquitiesResponse model with pass-through data."""
        response = FindEquitiesResponse(
            instructions=["Test instruction"],
            response={
                "data": [
                    {
                        "equity_id": 12345,
                        "name": "Test Company",
                        "bloomberg_ticker": "TEST:US",
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
            },
        )

        assert response.response is not None
        assert response.response["data"][0]["equity_id"] == 12345
        assert response.response["pagination"]["total_count"] == 1
        assert response.instructions == ["Test instruction"]

    def test_get_equity_summaries_response(self):
        """Test GetEquitySummariesResponse model with pass-through data."""
        response = GetEquitySummariesResponse(
            instructions=["Test instruction"],
            response=[
                {
                    "equity_id": 12345,
                    "name": "Test Company",
                    "bloomberg_ticker": "TEST:US",
                }
            ],
        )

        assert response.response is not None
        assert len(response.response) == 1
        assert response.response[0]["name"] == "Test Company"
        assert response.instructions == ["Test instruction"]

    def test_get_sectors_subsectors_response(self):
        """Test GetSectorsSubsectorsResponse model with pass-through data."""
        response = GetSectorsSubsectorsResponse(
            response=[
                {
                    "sector_id": 10,
                    "name": "Technology",
                    "subsectors": [{"subsector_id": 1010, "name": "Software"}],
                }
            ]
        )

        assert response.response is not None
        assert len(response.response) == 1
        assert response.response[0]["name"] == "Technology"

    def test_get_available_indexes_response(self):
        """Test GetAvailableIndexesResponse model with pass-through data."""
        response = GetAvailableIndexesResponse(
            instructions=["Indexes retrieved"],
            response=[{"index_id": 1, "name": "S&P 500", "symbol": "SPX"}],
        )

        assert response.response is not None
        assert len(response.response) == 1
        assert response.response[0]["name"] == "S&P 500"

    def test_get_index_constituents_response(self):
        """Test GetIndexConstituentsResponse model with pass-through data."""
        response = GetIndexConstituentsResponse(
            response={
                "data": [
                    {
                        "equity_id": 12345,
                        "name": "Test Company",
                        "bloomberg_ticker": "TEST:US",
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
            },
        )

        assert response.response is not None
        assert len(response.response["data"]) == 1
        assert response.response["pagination"]["total_count"] == 1

    def test_get_available_watchlists_response(self):
        """Test GetAvailableWatchlistsResponse model with pass-through data."""
        response = GetAvailableWatchlistsResponse(
            instructions=["Watchlists retrieved"],
            response=[{"watchlist_id": 123, "name": "Tech Giants", "type": "user"}],
        )

        assert response.response is not None
        assert len(response.response) == 1
        assert response.response[0]["name"] == "Tech Giants"

    def test_get_watchlist_constituents_response(self):
        """Test GetWatchlistConstituentsResponse model with pass-through data."""
        response = GetWatchlistConstituentsResponse(
            response={
                "data": [
                    {
                        "equity_id": 12345,
                        "name": "Test Company",
                        "bloomberg_ticker": "TEST:US",
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
            },
        )

        assert response.response is not None
        assert len(response.response["data"]) == 1

    def test_get_financials_response(self):
        """Test GetFinancialsResponse model with pass-through data."""
        response = GetFinancialsResponse(
            instructions=["Test instruction"],
            response=[{"equity": {"bloomberg_ticker": "TEST:US"}, "periods": []}],
        )

        assert response.response is not None
        assert response.response[0]["equity"]["bloomberg_ticker"] == "TEST:US"
        assert response.error is None

    def test_get_financials_response_with_error(self):
        """Test GetFinancialsResponse with error."""
        response = GetFinancialsResponse(
            instructions=[],
            response=None,
            error="Failed to retrieve financial data",
        )

        assert response.error == "Failed to retrieve financial data"
        assert response.response is None

    def test_get_ratios_response(self):
        """Test GetRatiosResponse model with pass-through data."""
        response = GetRatiosResponse(
            instructions=["Test instruction"],
            response=[{"equity": {"bloomberg_ticker": "TEST:US"}, "periods": []}],
        )

        assert response.response is not None
        assert response.error is None

    def test_get_ratios_response_with_error(self):
        """Test GetRatiosResponse with error."""
        response = GetRatiosResponse(
            instructions=[],
            response=None,
            error="Failed to retrieve ratio data",
        )

        assert response.error == "Failed to retrieve ratio data"
        assert response.response is None

    def test_get_kpis_and_segments_response(self):
        """Test GetKpisAndSegmentsResponse model with pass-through data."""
        response = GetKpisAndSegmentsResponse(
            instructions=["Test instruction"],
            response=[{"equity": {"bloomberg_ticker": "TEST:US"}, "periods": []}],
        )

        assert response.response is not None
        assert response.error is None

    def test_get_kpis_and_segments_response_with_error(self):
        """Test GetKpisAndSegmentsResponse with error."""
        response = GetKpisAndSegmentsResponse(
            instructions=[],
            response=None,
            error="Failed to retrieve KPIs and segments data",
        )

        assert response.error == "Failed to retrieve KPIs and segments data"
        assert response.response is None


@pytest.mark.unit
class TestEquitiesModelValidation:
    """Test equities model validation and edge cases."""

    def test_model_serialization_roundtrip(self):
        """Test model serialization and deserialization."""
        original_args = FindEquitiesArgs(
            bloomberg_ticker="AAPL:US", search="Apple", page=2, page_size=25
        )

        # Serialize to dict
        serialized = original_args.model_dump()

        # Deserialize back to model
        deserialized_args = FindEquitiesArgs(**serialized)

        # Verify round-trip
        assert original_args.bloomberg_ticker == deserialized_args.bloomberg_ticker
        assert original_args.search == deserialized_args.search
        assert original_args.page == deserialized_args.page
        assert original_args.page_size == deserialized_args.page_size

    def test_json_schema_generation(self):
        """Test that models can generate JSON schemas."""
        schema = FindEquitiesArgs.model_json_schema()

        assert "properties" in schema
        assert "bloomberg_ticker" in schema["properties"]
        assert "search" in schema["properties"]
        assert "page" in schema["properties"]
        assert "page_size" in schema["properties"]

        # Check page defaults - may be present as anyOf with constraints
        page_schema = schema["properties"]["page"]
        assert page_schema.get("default") == 1 or "anyOf" in page_schema

        page_size_schema = schema["properties"]["page_size"]
        assert page_size_schema.get("default") == 25 or "anyOf" in page_size_schema


@pytest.mark.unit
class TestGetFinancialsArgs:
    """Test GetFinancialsArgs model."""

    def test_valid_get_financials_args(self):
        """Test valid GetFinancialsArgs creation with all required fields."""
        args = GetFinancialsArgs(
            bloomberg_ticker="AAPL:US",
            source="income-statement",
            source_type="standardized",
            period="annual",
            calendar_year=2024,
        )

        assert args.bloomberg_ticker == "AAPL:US"
        assert args.source == "income-statement"
        assert args.source_type == "standardized"
        assert args.period == "annual"
        assert args.calendar_year == 2024
        assert args.calendar_quarter is None
        assert args.include_base_instructions is True
        assert args.exclude_instructions is False

    def test_get_financials_args_with_optional_fields(self):
        """Test GetFinancialsArgs with optional fields."""
        args = GetFinancialsArgs(
            bloomberg_ticker="MSFT:US",
            source="balance-sheet",
            source_type="as-reported",
            period="quarterly",
            calendar_year=2024,
            calendar_quarter=3,
            originating_prompt="Get Q3 2024 balance sheet for Microsoft",
            self_identification="test-session-123",
            include_base_instructions=False,
            exclude_instructions=True,
        )

        assert args.bloomberg_ticker == "MSFT:US"
        assert args.source == "balance-sheet"
        assert args.source_type == "as-reported"
        assert args.period == "quarterly"
        assert args.calendar_year == 2024
        assert args.calendar_quarter == 3

    def test_get_financials_args_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                source="income-statement",
                source_type="standardized",
                period="annual",
                calendar_year=2024,
            )
        assert "bloomberg_ticker" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                calendar_year=2024,
            )
        assert "source" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
            )
        assert "calendar_year" in str(exc_info.value)

    @pytest.mark.parametrize(
        "source",
        ["income-statement", "balance-sheet", "cash-flow-statement"],
    )
    def test_get_financials_args_valid_sources(self, source):
        """Test all valid source values."""
        args = GetFinancialsArgs(
            bloomberg_ticker="AAPL:US",
            source=source,
            source_type="standardized",
            period="annual",
            calendar_year=2024,
        )
        assert args.source == source

    @pytest.mark.parametrize(
        "source_type",
        ["as-reported", "standardized"],
    )
    def test_get_financials_args_valid_source_types(self, source_type):
        """Test all valid source_type values."""
        args = GetFinancialsArgs(
            bloomberg_ticker="AAPL:US",
            source="income-statement",
            source_type=source_type,
            period="annual",
            calendar_year=2024,
        )
        assert args.source_type == source_type

    @pytest.mark.parametrize(
        "period",
        ["annual", "quarterly", "semi-annual"],
    )
    def test_get_financials_args_valid_periods(self, period):
        """Test all valid period values."""
        args = GetFinancialsArgs(
            bloomberg_ticker="AAPL:US",
            source="income-statement",
            source_type="standardized",
            period=period,
            calendar_year=2024,
        )
        assert args.period == period

    def test_get_financials_args_invalid_source(self):
        """Test that invalid source values are rejected."""
        with pytest.raises(ValidationError):
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="invalid-source",
                source_type="standardized",
                period="annual",
                calendar_year=2024,
            )

    def test_get_financials_args_invalid_source_type(self):
        """Test that invalid source_type values are rejected."""
        with pytest.raises(ValidationError):
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
                source_type="invalid-type",
                period="annual",
                calendar_year=2024,
            )

    def test_get_financials_args_invalid_period(self):
        """Test that invalid period values are rejected."""
        with pytest.raises(ValidationError):
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
                source_type="standardized",
                period="invalid-period",
                calendar_year=2024,
            )

    def test_get_financials_args_json_schema(self):
        """Test that GetFinancialsArgs generates a valid JSON schema."""
        schema = GetFinancialsArgs.model_json_schema()

        assert "properties" in schema
        assert "bloomberg_ticker" in schema["properties"]
        assert "source" in schema["properties"]
        assert "source_type" in schema["properties"]
        assert "period" in schema["properties"]
        assert "calendar_year" in schema["properties"]
        assert "calendar_quarter" in schema["properties"]


@pytest.mark.unit
class TestGetRatiosArgs:
    """Test GetRatiosArgs model."""

    def test_valid_get_ratios_args(self):
        """Test valid GetRatiosArgs creation with all required fields."""
        args = GetRatiosArgs(
            bloomberg_ticker="AAPL:US",
            period="annual",
            calendar_year=2024,
        )

        assert args.bloomberg_ticker == "AAPL:US"
        assert args.period == "annual"
        assert args.calendar_year == 2024
        assert args.calendar_quarter is None

    def test_get_ratios_args_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            GetRatiosArgs(calendar_year=2024)
        assert "bloomberg_ticker" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            GetRatiosArgs(bloomberg_ticker="AAPL:US")
        assert "calendar_year" in str(exc_info.value)

    @pytest.mark.parametrize(
        "period",
        ["annual", "quarterly", "semi-annual"],
    )
    def test_get_ratios_args_valid_periods(self, period):
        """Test all valid period values."""
        args = GetRatiosArgs(
            bloomberg_ticker="AAPL:US",
            period=period,
            calendar_year=2024,
        )
        assert args.period == period

    def test_get_ratios_args_invalid_period(self):
        """Test that invalid period values are rejected."""
        with pytest.raises(ValidationError):
            GetRatiosArgs(
                bloomberg_ticker="AAPL:US",
                period="invalid-period",
                calendar_year=2024,
            )

    def test_get_ratios_args_json_schema(self):
        """Test that GetRatiosArgs generates a valid JSON schema."""
        schema = GetRatiosArgs.model_json_schema()

        assert "properties" in schema
        assert "bloomberg_ticker" in schema["properties"]
        assert "period" in schema["properties"]
        assert "calendar_year" in schema["properties"]
        assert "calendar_quarter" in schema["properties"]


@pytest.mark.unit
class TestGetKpisAndSegmentsArgs:
    """Test GetKpisAndSegmentsArgs model."""

    def test_valid_get_kpis_and_segments_args(self):
        """Test valid GetKpisAndSegmentsArgs creation with all required fields."""
        args = GetKpisAndSegmentsArgs(
            bloomberg_ticker="AAPL:US",
            period="annual",
            calendar_year=2024,
        )

        assert args.bloomberg_ticker == "AAPL:US"
        assert args.period == "annual"
        assert args.calendar_year == 2024
        assert args.calendar_quarter is None

    def test_get_kpis_and_segments_args_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            GetKpisAndSegmentsArgs(calendar_year=2024)
        assert "bloomberg_ticker" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            GetKpisAndSegmentsArgs(bloomberg_ticker="AAPL:US")
        assert "calendar_year" in str(exc_info.value)

    @pytest.mark.parametrize(
        "period",
        ["annual", "quarterly", "semi-annual"],
    )
    def test_get_kpis_and_segments_args_valid_periods(self, period):
        """Test all valid period values."""
        args = GetKpisAndSegmentsArgs(
            bloomberg_ticker="AAPL:US",
            period=period,
            calendar_year=2024,
        )
        assert args.period == period

    def test_get_kpis_and_segments_args_invalid_period(self):
        """Test that invalid period values are rejected."""
        with pytest.raises(ValidationError):
            GetKpisAndSegmentsArgs(
                bloomberg_ticker="AAPL:US",
                period="invalid-period",
                calendar_year=2024,
            )

    def test_get_kpis_and_segments_args_json_schema(self):
        """Test that GetKpisAndSegmentsArgs generates a valid JSON schema."""
        schema = GetKpisAndSegmentsArgs.model_json_schema()

        assert "properties" in schema
        assert "bloomberg_ticker" in schema["properties"]
        assert "period" in schema["properties"]
        assert "calendar_year" in schema["properties"]
        assert "calendar_quarter" in schema["properties"]
