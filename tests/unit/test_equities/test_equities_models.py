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
    SectorSubsector,
    IndexItem,
    WatchlistItem,
    FinancialMetricInfo,
    FinancialMetricItem,
    FinancialPeriodItem,
    FinancialEquityInfo,
    FinancialsResponseData,
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestEquitiesModels:
    """Test equities Pydantic models."""

    def test_equity_item_creation(self):
        """Test EquityItem model creation."""
        equity_data = {
            "equity_id": 12345,
            "name": "Test Company",
            "bloomberg_ticker": "TEST:US",
            "company_id": 67890,
            "sector_id": 10,
            "subsector_id": 1010,
            "primary_equity": True,
        }

        equity = EquityItem(**equity_data)

        assert equity.equity_id == 12345
        assert equity.name == "Test Company"
        assert equity.bloomberg_ticker == "TEST:US"
        assert equity.company_id == 67890
        assert equity.sector_id == 10
        assert equity.subsector_id == 1010
        assert equity.primary_equity is True

    def test_equity_item_optional_fields(self):
        """Test EquityItem with only required fields."""
        minimal_data = {
            "equity_id": 12345,
            "bloomberg_ticker": "TEST:US",
        }

        equity = EquityItem(**minimal_data)

        assert equity.equity_id == 12345
        assert equity.bloomberg_ticker == "TEST:US"
        assert equity.name is None
        assert equity.company_id is None
        assert equity.sector_id is None
        assert equity.subsector_id is None
        assert equity.primary_equity is None

    def test_equity_summary_creation(self):
        """Test EquitySummary model creation."""
        summary_data = {
            "description": "Test company description",
            "recent_events": ["Event 1", "Event 2"],
            "key_metrics": {
                "pe_ratio": 25.5,
                "price_to_book": 3.2,
                "dividend_yield": 2.1,
            },
            "analyst_coverage": {
                "avg_rating": "Buy",
                "price_target": "$150.00",
                "num_analysts": 12,
            },
        }

        summary = EquitySummary(**summary_data)

        assert summary.description == "Test company description"
        assert len(summary.recent_events) == 2
        assert summary.recent_events[0] == "Event 1"
        assert summary.key_metrics["pe_ratio"] == 25.5
        assert summary.analyst_coverage["avg_rating"] == "Buy"
        assert summary.analyst_coverage["num_analysts"] == 12

    def test_equity_summary_defaults(self):
        """Test EquitySummary with default values."""
        summary = EquitySummary()

        assert summary.description is None
        assert summary.recent_events == []
        assert summary.key_metrics == {}
        assert summary.analyst_coverage == {}

    def test_equity_details_inherits_equity_item(self):
        """Test EquityDetails inherits from EquityItem."""
        details_data = {
            "equity_id": 12345,
            "name": "Test Company",
            "bloomberg_ticker": "TEST:US",
            "company_id": 67890,
            "summary": EquitySummary(
                description="Test description",
                recent_events=["Event 1"],
                key_metrics={"pe_ratio": 25.5},
            ),
            "identifiers": {
                "isin": "US1234567890",
                "cusip": "123456789",
                "ric": "TEST.O",
            },
        }

        details = EquityDetails(**details_data)

        # Test inherited fields
        assert details.equity_id == 12345
        assert details.name == "Test Company"
        assert details.bloomberg_ticker == "TEST:US"

        # Test new fields
        assert details.summary.description == "Test description"
        assert len(details.summary.recent_events) == 1
        assert details.identifiers["isin"] == "US1234567890"
        assert details.identifiers["cusip"] == "123456789"

    def test_sector_subsector_creation(self):
        """Test SectorSubsector model creation."""
        sector_data = {
            "sector_id": 10,
            "name": "Technology",
            "subsectors": [{"subsector_id": 1010, "name": "Software"}],
        }

        sector = SectorSubsector(**sector_data)

        assert sector.sector_id == 10
        assert sector.name == "Technology"
        assert sector.sector_name == "Technology"  # backward compatibility property
        assert sector.subsector_id == 1010  # backward compatibility property
        assert sector.subsector_name == "Software"  # backward compatibility property
        assert len(sector.subsectors) == 1
        assert sector.subsectors[0].name == "Software"

    def test_sector_subsector_no_subsector(self):
        """Test SectorSubsector without subsector."""
        sector_data = {"sector_id": 20, "name": "Healthcare"}

        sector = SectorSubsector(**sector_data)

        assert sector.sector_id == 20
        assert sector.name == "Healthcare"
        assert sector.sector_name == "Healthcare"  # backward compatibility property
        assert sector.subsector_id is None  # backward compatibility property
        assert sector.subsector_name is None  # backward compatibility property

    def test_index_item_creation(self):
        """Test IndexItem model creation."""
        index_data = {"index_id": 1, "name": "S&P 500", "short_name": "SPX"}

        index = IndexItem(**index_data)

        assert index.index_id == 1
        assert index.name == "S&P 500"
        assert index.index_name == "S&P 500"  # backward compatibility property
        assert index.short_name == "SPX"

    def test_watchlist_item_creation(self):
        """Test WatchlistItem model creation."""
        watchlist_data = {
            "watchlist_id": 123,
            "name": "Tech Giants",
            "type": "user",
        }

        watchlist = WatchlistItem(**watchlist_data)

        assert watchlist.watchlist_id == 123
        assert watchlist.name == "Tech Giants"
        assert (
            watchlist.watchlist_name == "Tech Giants"
        )  # backward compatibility property
        assert watchlist.type == "user"

    def test_watchlist_item_no_type(self):
        """Test WatchlistItem without type."""
        watchlist_data = {"watchlist_id": 456, "name": "My Watchlist"}

        watchlist = WatchlistItem(**watchlist_data)

        assert watchlist.watchlist_id == 456
        assert watchlist.name == "My Watchlist"
        assert (
            watchlist.watchlist_name == "My Watchlist"
        )  # backward compatibility property
        assert watchlist.type is None


@pytest.mark.unit
class TestFindEquitiesArgs:
    """Test FindEquitiesArgs model."""

    def test_valid_find_equities_args(self):
        """Test valid FindEquitiesArgs creation."""
        args = FindEquitiesArgs(
            bloomberg_ticker="AAPL:US",
            isin="US0378331005",
            ticker="AAPL",
            search="Apple",
            page=1,
            page_size=50,
        )

        assert args.bloomberg_ticker == "AAPL:US"
        assert args.isin == "US0378331005"
        assert args.ticker == "AAPL"
        assert args.search == "Apple"
        assert args.page == 1
        assert args.page_size == 50

    def test_find_equities_args_defaults(self):
        """Test FindEquitiesArgs with default values."""
        args = FindEquitiesArgs()

        assert args.page == 1  # Default value
        assert args.page_size == 50  # Default value
        assert args.bloomberg_ticker is None
        assert args.isin is None
        assert args.ric is None
        assert args.ticker is None
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

        # Page size must be between 1 and 100
        with pytest.raises(ValidationError):
            FindEquitiesArgs(page_size=0)

        with pytest.raises(ValidationError):
            FindEquitiesArgs(page_size=101)

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
            ("ticker", "AAPL"),
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

        # Test with multiple tickers
        args = FindEquitiesArgs(bloomberg_ticker="AAPL:US,MSFT:US,GOOGL:US")
        assert args.bloomberg_ticker == "AAPL:US,MSFT:US,GOOGL:US"


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
        args = GetIndexConstituentsArgs(index="SP500", page=1, page_size=50)

        assert args.index == "SP500"
        assert args.page == 1
        assert args.page_size == 50

    def test_get_index_constituents_args_defaults(self):
        """Test GetIndexConstituentsArgs with default values."""
        args = GetIndexConstituentsArgs(index="SP500")

        assert args.index == "SP500"
        assert args.page == 1
        assert args.page_size == 50
        assert args.originating_prompt is None

    def test_get_index_constituents_args_with_originating_prompt(self):
        """Test GetIndexConstituentsArgs with originating_prompt field."""
        args = GetIndexConstituentsArgs(
            index="SP500",
            originating_prompt="Get S&P 500 constituents",
        )
        assert args.originating_prompt == "Get S&P 500 constituents"

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
        args = GetWatchlistConstituentsArgs(watchlist_id=123, page=1, page_size=50)

        assert args.watchlist_id == 123  # Stored as int
        assert args.page == 1
        assert args.page_size == 50

    def test_get_watchlist_constituents_args_defaults(self):
        """Test GetWatchlistConstituentsArgs with default values."""
        args = GetWatchlistConstituentsArgs(watchlist_id=123)

        assert args.watchlist_id == 123  # Stored as int
        assert args.page == 1
        assert args.page_size == 50
        assert args.originating_prompt is None

    def test_get_watchlist_constituents_args_with_originating_prompt(self):
        """Test GetWatchlistConstituentsArgs with originating_prompt field."""
        args = GetWatchlistConstituentsArgs(
            watchlist_id=123,
            originating_prompt="Get my watchlist constituents",
        )
        assert args.originating_prompt == "Get my watchlist constituents"

    def test_get_watchlist_constituents_args_required_field(self):
        """Test that watchlist_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            GetWatchlistConstituentsArgs()

        assert "watchlist_id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)


@pytest.mark.unit
class TestEquitiesResponses:
    """Test equities response models."""

    def test_find_equities_response(self):
        """Test FindEquitiesResponse model."""
        equities = [
            EquityItem(
                equity_id=12345,
                name="Test Company",
                bloomberg_ticker="TEST:US",
            )
        ]

        response = FindEquitiesResponse(
            instructions=["Test instruction"],
            response={
                "data": equities,
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
        )

        assert len(response.response.data) == 1
        assert response.response.pagination.total_count == 1
        assert response.response.pagination.current_page == 1
        assert response.response.pagination.page_size == 50
        assert response.instructions == ["Test instruction"]

    def test_get_equity_summaries_response(self):
        """Test GetEquitySummariesResponse model."""
        from aiera_mcp.tools.equities.models import EquitySummaryItem

        summaries = [
            EquitySummaryItem(
                equity_id=12345,
                name="Test Company",
                bloomberg_ticker="TEST:US",
            )
        ]

        response = GetEquitySummariesResponse(
            instructions=["Test instruction"], response=summaries
        )

        assert len(response.response) == 1
        assert isinstance(response.response[0], EquitySummaryItem)
        assert response.response[0].name == "Test Company"
        assert response.instructions == ["Test instruction"]

    def test_get_sectors_subsectors_response(self):
        """Test GetSectorsSubsectorsResponse model."""
        sectors = [
            SectorSubsector(
                sector_id=10,
                name="Technology",
                subsectors=[{"subsector_id": 1010, "name": "Software"}],
            )
        ]

        response = GetSectorsSubsectorsResponse(response=sectors)

        assert len(response.response) == 1
        assert response.response[0].name == "Technology"
        assert (
            response.response[0].sector_name == "Technology"
        )  # backward compatibility

    def test_get_available_indexes_response(self):
        """Test GetAvailableIndexesResponse model."""
        indexes = [IndexItem(index_id=1, name="S&P 500", symbol="SPX")]

        response = GetAvailableIndexesResponse(
            instructions=["Indexes retrieved"], response=indexes
        )

        assert len(response.response) == 1
        assert response.response[0].name == "S&P 500"
        assert response.response[0].index_name == "S&P 500"  # backward compatibility
        assert response.instructions == ["Indexes retrieved"]

    def test_get_index_constituents_response(self):
        """Test GetIndexConstituentsResponse model."""
        from aiera_mcp.tools.equities.models import ApiPaginationInfo

        constituents = [
            EquityItem(
                equity_id=12345,
                name="Test Company",
                bloomberg_ticker="TEST:US",
            )
        ]

        response = GetIndexConstituentsResponse(
            data=constituents,
            pagination=ApiPaginationInfo(
                total_count=1, current_page=1, total_pages=1, page_size=50
            ),
        )

        assert len(response.data) == 1
        assert response.pagination.total_count == 1

    def test_get_available_watchlists_response(self):
        """Test GetAvailableWatchlistsResponse model."""
        watchlists = [WatchlistItem(watchlist_id=123, name="Tech Giants", type="user")]

        response = GetAvailableWatchlistsResponse(
            instructions=["Watchlists retrieved"], response=watchlists
        )

        assert len(response.response) == 1
        assert response.response[0].watchlist_name == "Tech Giants"
        assert response.instructions == ["Watchlists retrieved"]

    def test_get_watchlist_constituents_response(self):
        """Test GetWatchlistConstituentsResponse model."""
        from aiera_mcp.tools.equities.models import ApiPaginationInfo

        constituents = [
            EquityItem(
                equity_id=12345,
                name="Test Company",
                bloomberg_ticker="TEST:US",
            )
        ]

        response = GetWatchlistConstituentsResponse(
            data=constituents,
            pagination=ApiPaginationInfo(
                total_count=1, current_page=1, total_pages=1, page_size=50
            ),
        )

        assert len(response.data) == 1
        assert response.pagination.total_count == 1


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
        assert page_size_schema.get("default") == 50 or "anyOf" in page_size_schema

    def test_equity_summary_complex_data_types(self):
        """Test equity summary handles complex data types."""
        complex_metrics = {
            "pe_ratio": 25.5,
            "price_to_book": 3.2,
            "dividend_yield": 2.1,
            "beta": 1.15,
            "shares_outstanding": 16400000000,
            "revenue_growth": "15%",
            "is_profitable": True,
            "financial_ratios": {"current_ratio": 1.2, "debt_to_equity": 0.3},
            "segments": ["iPhone", "Services", "Mac", "iPad", "Wearables"],
        }

        complex_analyst_coverage = {
            "avg_rating": "Buy",
            "price_target": "$175.50",
            "price_target_high": "$200.00",
            "price_target_low": "$150.00",
            "num_analysts": 15,
            "rating_breakdown": {
                "strong_buy": 8,
                "buy": 5,
                "hold": 2,
                "sell": 0,
                "strong_sell": 0,
            },
        }

        summary = EquitySummary(
            description="Complex company description",
            recent_events=["Q4 Earnings", "Product Launch", "Acquisition"],
            key_metrics=complex_metrics,
            analyst_coverage=complex_analyst_coverage,
        )

        # Verify complex data is handled properly
        assert summary.key_metrics["pe_ratio"] == 25.5
        assert summary.key_metrics["is_profitable"] is True
        assert summary.key_metrics["financial_ratios"]["current_ratio"] == 1.2
        assert len(summary.key_metrics["segments"]) == 5

        assert summary.analyst_coverage["num_analysts"] == 15
        assert summary.analyst_coverage["rating_breakdown"]["strong_buy"] == 8

    def test_identifiers_dict_handling(self):
        """Test that identifiers dictionary handles various string types."""
        identifiers = {
            "isin": "US0378331005",
            "cusip": "037833100",
            "ric": "AAPL.O",
            "sedol": "2046251",
            "figi": "BBG000B9XRY4",
            "permid": "4295905573",
        }

        details = EquityDetails(
            equity_id=12345,
            name="Test Company",
            bloomberg_ticker="TEST:US",
            identifiers=identifiers,
        )

        assert details.identifiers["isin"] == "US0378331005"
        assert details.identifiers["cusip"] == "037833100"
        assert details.identifiers["ric"] == "AAPL.O"
        assert details.identifiers["permid"] == "4295905573"

        # Test serialization preserves all identifiers
        serialized = details.model_dump()
        assert len(serialized["identifiers"]) == 6
        assert serialized["identifiers"]["figi"] == "BBG000B9XRY4"


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
            fiscal_year=2024,
        )

        assert args.bloomberg_ticker == "AAPL:US"
        assert args.source == "income-statement"
        assert args.source_type == "standardized"
        assert args.period == "annual"
        assert args.fiscal_year == 2024
        assert args.fiscal_quarter is None  # Optional, not provided
        assert args.include_base_instructions is True  # Default value
        assert args.exclude_instructions is False  # Default value

    def test_get_financials_args_with_optional_fields(self):
        """Test GetFinancialsArgs with optional fields."""
        args = GetFinancialsArgs(
            bloomberg_ticker="MSFT:US",
            source="balance-sheet",
            source_type="as-reported",
            period="quarterly",
            fiscal_year=2024,
            fiscal_quarter=3,
            originating_prompt="Get Q3 2024 balance sheet for Microsoft",
            self_identification="test-session-123",
            include_base_instructions=False,
            exclude_instructions=True,
        )

        assert args.bloomberg_ticker == "MSFT:US"
        assert args.source == "balance-sheet"
        assert args.source_type == "as-reported"
        assert args.period == "quarterly"
        assert args.fiscal_year == 2024
        assert args.fiscal_quarter == 3
        assert args.originating_prompt == "Get Q3 2024 balance sheet for Microsoft"
        assert args.self_identification == "test-session-123"
        assert args.include_base_instructions is False
        assert args.exclude_instructions is True

    def test_get_financials_args_required_fields(self):
        """Test that required fields are enforced."""
        # Missing bloomberg_ticker
        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                source="income-statement",
                source_type="standardized",
                period="annual",
                fiscal_year=2024,
            )
        assert "bloomberg_ticker" in str(exc_info.value)

        # Missing source
        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source_type="standardized",
                period="annual",
                fiscal_year=2024,
            )
        assert "source" in str(exc_info.value)

        # Missing source_type
        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
                period="annual",
                fiscal_year=2024,
            )
        assert "source_type" in str(exc_info.value)

        # Missing period
        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
                source_type="standardized",
                fiscal_year=2024,
            )
        assert "period" in str(exc_info.value)

        # Missing fiscal_year
        with pytest.raises(ValidationError) as exc_info:
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
                source_type="standardized",
                period="annual",
            )
        assert "fiscal_year" in str(exc_info.value)

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
            fiscal_year=2024,
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
            fiscal_year=2024,
        )
        assert args.source_type == source_type

    @pytest.mark.parametrize(
        "period",
        ["annual", "quarterly", "semi-annual", "ltm", "ytd", "latest"],
    )
    def test_get_financials_args_valid_periods(self, period):
        """Test all valid period values."""
        args = GetFinancialsArgs(
            bloomberg_ticker="AAPL:US",
            source="income-statement",
            source_type="standardized",
            period=period,
            fiscal_year=2024,
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
                fiscal_year=2024,
            )

    def test_get_financials_args_invalid_source_type(self):
        """Test that invalid source_type values are rejected."""
        with pytest.raises(ValidationError):
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
                source_type="invalid-type",
                period="annual",
                fiscal_year=2024,
            )

    def test_get_financials_args_invalid_period(self):
        """Test that invalid period values are rejected."""
        with pytest.raises(ValidationError):
            GetFinancialsArgs(
                bloomberg_ticker="AAPL:US",
                source="income-statement",
                source_type="standardized",
                period="invalid-period",
                fiscal_year=2024,
            )

    def test_get_financials_args_json_schema(self):
        """Test that GetFinancialsArgs generates a valid JSON schema."""
        schema = GetFinancialsArgs.model_json_schema()

        assert "properties" in schema
        assert "bloomberg_ticker" in schema["properties"]
        assert "source" in schema["properties"]
        assert "source_type" in schema["properties"]
        assert "period" in schema["properties"]
        assert "fiscal_year" in schema["properties"]
        assert "fiscal_quarter" in schema["properties"]


@pytest.mark.unit
class TestFinancialsModels:
    """Test financial data models."""

    def test_financial_metric_info_creation(self):
        """Test FinancialMetricInfo model creation."""
        metric_info = FinancialMetricInfo(
            metric_name="Total Revenue",
            metric_format="currency",
            is_point_in_time=False,
            is_currency=True,
            is_per_share=False,
            is_key_metric=True,
            is_total=True,
            headers=["Income Statement", "Revenue"],
        )

        assert metric_info.metric_name == "Total Revenue"
        assert metric_info.metric_format == "currency"
        assert metric_info.is_currency is True
        assert metric_info.is_key_metric is True
        assert metric_info.headers == ["Income Statement", "Revenue"]

    def test_financial_metric_info_minimal(self):
        """Test FinancialMetricInfo with minimal data."""
        metric_info = FinancialMetricInfo(metric_name="Custom Metric")

        assert metric_info.metric_name == "Custom Metric"
        assert metric_info.metric_format is None
        assert metric_info.is_currency is None
        assert metric_info.headers is None

    def test_financial_metric_item_creation(self):
        """Test FinancialMetricItem model creation."""
        metric_item = FinancialMetricItem(
            metric=FinancialMetricInfo(
                metric_name="Net Income",
                is_currency=True,
                is_key_metric=True,
            ),
            metric_value=30425000000,
            metric_unit="USD",
            metric_currency="USD",
            metric_is_calculated=False,
        )

        assert metric_item.metric.metric_name == "Net Income"
        assert metric_item.metric_value == 30425000000
        assert metric_item.metric_currency == "USD"
        assert metric_item.metric_is_calculated is False

    def test_financial_period_item_creation(self):
        """Test FinancialPeriodItem model creation."""
        period_item = FinancialPeriodItem(
            period_type="annual",
            report_date="2024-12-31",
            period_duration="12M",
            calendar_year=2024,
            fiscal_year=2024,
            is_restated=False,
            metrics=[
                FinancialMetricItem(
                    metric=FinancialMetricInfo(metric_name="Revenue"),
                    metric_value=574785000000,
                )
            ],
        )

        assert period_item.period_type == "annual"
        assert period_item.fiscal_year == 2024
        assert len(period_item.metrics) == 1
        assert period_item.metrics[0].metric.metric_name == "Revenue"

    def test_financial_period_item_date_parsing(self):
        """Test FinancialPeriodItem date field parsing."""
        from datetime import date, datetime

        period_item = FinancialPeriodItem(
            period_type="quarterly",
            report_date="2024-09-30",
            earnings_date="2024-10-30T17:00:00",
            filing_date="2024-11-01T00:00:00",
            fiscal_year=2024,
            fiscal_quarter=3,
        )

        assert period_item.report_date == date(2024, 9, 30)
        assert isinstance(period_item.earnings_date, datetime)
        assert isinstance(period_item.filing_date, datetime)

    def test_financial_equity_info_creation(self):
        """Test FinancialEquityInfo model creation."""
        equity_info = FinancialEquityInfo(
            equity_id=1,
            company_id=1,
            name="AMAZON COM INC",
            bloomberg_ticker="AMZN:US",
            sector_id=1,
            subsector_id=259,
        )

        assert equity_info.equity_id == 1
        assert equity_info.name == "AMAZON COM INC"
        assert equity_info.bloomberg_ticker == "AMZN:US"

    def test_financials_response_data_creation(self):
        """Test FinancialsResponseData model creation."""
        response_data = FinancialsResponseData(
            equity=FinancialEquityInfo(
                equity_id=1,
                name="Test Company",
                bloomberg_ticker="TEST:US",
            ),
            financials=[
                FinancialPeriodItem(
                    period_type="annual",
                    fiscal_year=2024,
                    metrics=[],
                )
            ],
        )

        assert response_data.equity.bloomberg_ticker == "TEST:US"
        assert len(response_data.financials) == 1
        assert response_data.financials[0].fiscal_year == 2024

    def test_get_financials_response_creation(self):
        """Test GetFinancialsResponse model creation."""
        response = GetFinancialsResponse(
            instructions=["Test instruction"],
            response=[
                FinancialsResponseData(
                    equity=FinancialEquityInfo(
                        equity_id=1,
                        name="Test Company",
                        bloomberg_ticker="TEST:US",
                    ),
                    financials=[],
                )
            ],
        )

        assert response.instructions == ["Test instruction"]
        assert response.response[0].equity.name == "Test Company"
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
