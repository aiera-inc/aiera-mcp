#!/usr/bin/env python3

"""Unit tests for filings models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from aiera_mcp.tools.filings.models import (
    FindFilingsArgs,
    GetFilingArgs,
    FindFilingsResponse,
    GetFilingResponse,
    FilingItem,
    FilingDetails,
    FilingSummary,
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestFilingsModels:
    """Test filings Pydantic models."""

    def test_filing_item_creation(self):
        """Test FilingItem model creation."""
        from aiera_mcp.tools.filings.models import EquityInfo

        filing_data = {
            "filing_id": 12345,
            "title": "Annual Report",
            "filing_date": datetime(2023, 10, 27),
            "period_end_date": datetime(2023, 9, 30),
            "is_amendment": 0,  # Changed to integer
            "equity": EquityInfo(name="Test Company", bloomberg_ticker="TEST:US"),
            "form_number": "10-K",  # Changed from form_type
        }

        filing = FilingItem(**filing_data)

        assert filing.filing_id == 12345
        assert filing.equity.name == "Test Company"
        assert filing.equity.bloomberg_ticker == "TEST:US"
        assert filing.form_number == "10-K"
        assert filing.title == "Annual Report"
        assert filing.filing_date == datetime(2023, 10, 27)
        assert filing.period_end_date == datetime(2023, 9, 30)
        assert filing.is_amendment == 0

    def test_filing_item_optional_fields(self):
        """Test FilingItem with only required fields."""
        minimal_data = {
            "filing_id": 12345,
            "title": "Annual Report",
            "filing_date": datetime(2023, 10, 27),
            "is_amendment": 0,
        }

        filing = FilingItem(**minimal_data)

        assert filing.filing_id == 12345
        assert filing.equity is None
        assert filing.period_end_date is None
        assert filing.form_number is None

    def test_filing_summary_creation(self):
        """Test FilingSummary model creation."""
        summary_data = {
            "summary": "This is a test summary",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "financial_highlights": {
                "revenue": "$100M",
                "net_income": "$20M",
                "gross_margin": "45%",
            },
        }

        summary = FilingSummary(**summary_data)

        assert summary.summary == "This is a test summary"
        assert len(summary.key_points) == 3
        assert summary.key_points[0] == "Point 1"
        assert summary.financial_highlights["revenue"] == "$100M"
        assert summary.financial_highlights["net_income"] == "$20M"

    def test_filing_summary_defaults(self):
        """Test FilingSummary with default values."""
        summary = FilingSummary()

        assert summary.summary is None
        assert summary.key_points == []
        assert summary.financial_highlights == {}

    def test_filing_details_inherits_filing_item(self):
        """Test FilingDetails inherits from FilingItem."""
        from aiera_mcp.tools.filings.models import EquityInfo

        details_data = {
            "filing_id": 12345,
            "title": "Annual Report",
            "filing_date": datetime(2023, 10, 27),
            "is_amendment": 0,
            "equity": EquityInfo(name="Test Company", bloomberg_ticker="TEST:US"),
            "form_number": "10-K",
            "summary": FilingSummary(
                summary="Test summary",
                key_points=["Point 1"],
                financial_highlights={"revenue": "$100M"},
            ),
            "content_preview": "This annual report contains...",
            "document_count": 3,
        }

        details = FilingDetails(**details_data)

        # Test inherited fields
        assert details.filing_id == 12345
        assert details.equity.name == "Test Company"
        assert details.form_number == "10-K"

        # Test new fields
        assert details.summary.summary == "Test summary"
        assert details.content_preview == "This annual report contains..."
        assert details.document_count == 3


@pytest.mark.unit
class TestFindFilingsArgs:
    """Test FindFilingsArgs model."""

    def test_valid_find_filings_args(self):
        """Test valid FindFilingsArgs creation."""
        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            form_number="10-K",
            page=1,
            page_size=50,
        )

        assert args.start_date == "2023-10-01"
        assert args.end_date == "2023-10-31"
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.form_number == "10-K"
        assert args.page == 1
        assert args.page_size == 50

    def test_find_filings_args_defaults(self):
        """Test FindFilingsArgs with default values."""
        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        assert args.page == 1  # Default value
        assert args.page_size == 50  # Default value
        assert args.bloomberg_ticker is None
        assert args.form_number is None
        assert args.watchlist_id is None
        assert args.originating_prompt is None  # Default value
        assert args.include_base_instructions is True  # Default value

    def test_find_filings_args_with_originating_prompt(self):
        """Test FindFilingsArgs with originating_prompt field."""
        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            originating_prompt="Find all 10-K filings for Apple",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "Find all 10-K filings for Apple"
        assert args.include_base_instructions is False

    def test_find_filings_args_date_format_validation(self):
        """Test date format validation."""
        # Valid date format
        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")
        assert args.start_date == "2023-10-01"

        # Invalid date formats should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            FindFilingsArgs(start_date="10/01/2023", end_date="2023-10-31")

        assert "String should match pattern" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FindFilingsArgs(start_date="2023-10-01", end_date="invalid-date")

        assert "String should match pattern" in str(exc_info.value)

    def test_find_filings_args_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid pagination
        args = FindFilingsArgs(
            start_date="2023-10-01", end_date="2023-10-31", page=5, page_size=25
        )
        assert args.page == 5
        assert args.page_size == 25

        # Page must be >= 1
        with pytest.raises(ValidationError):
            FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31", page=0)

        # Page size must be between 1 and 100
        with pytest.raises(ValidationError):
            FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31", page_size=0)

        with pytest.raises(ValidationError):
            FindFilingsArgs(
                start_date="2023-10-01", end_date="2023-10-31", page_size=101
            )

    @pytest.mark.parametrize(
        "field_name,field_value",
        [
            ("watchlist_id", 123),
            ("index_id", 456),
            ("sector_id", 789),
            ("subsector_id", 101),
        ],
    )
    def test_find_filings_args_numeric_field_serialization(
        self, field_name, field_value
    ):
        """Test that numeric fields are serialized as strings."""
        args_data = {
            "start_date": "2023-10-01",
            "end_date": "2023-10-31",
            field_name: field_value,
        }
        args = FindFilingsArgs(**args_data)

        # Model dump should serialize numeric fields as strings
        dumped = args.model_dump(exclude_none=True)
        assert dumped[field_name] == str(field_value)

    def test_find_filings_args_form_number_variations(self):
        """Test various SEC form number formats."""
        form_numbers = ["10-K", "10-Q", "8-K", "DEF 14A", "SC 13D", "S-1"]

        for form_number in form_numbers:
            args = FindFilingsArgs(
                start_date="2023-10-01", end_date="2023-10-31", form_number=form_number
            )
            assert args.form_number == form_number

    def test_bloomberg_ticker_validation(self):
        """Test Bloomberg ticker validation and correction."""
        # Test with properly formatted ticker
        args = FindFilingsArgs(
            start_date="2023-10-01", end_date="2023-10-31", bloomberg_ticker="AAPL:US"
        )
        assert args.bloomberg_ticker == "AAPL:US"

        # Test with multiple tickers
        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US,MSFT:US,GOOGL:US",
        )
        assert args.bloomberg_ticker == "AAPL:US,MSFT:US,GOOGL:US"


@pytest.mark.unit
class TestGetFilingArgs:
    """Test GetFilingArgs model."""

    def test_valid_get_filing_args(self):
        """Test valid GetFilingArgs creation."""
        args = GetFilingArgs(filing_id="12345")  # String as per model definition
        assert args.filing_id == "12345"
        assert args.originating_prompt is None
        assert args.include_base_instructions is True

    def test_get_filing_args_with_originating_prompt(self):
        """Test GetFilingArgs with originating_prompt field."""
        args = GetFilingArgs(
            filing_id="12345",
            originating_prompt="Get details for this 10-K filing",
            include_base_instructions=False,
        )
        assert args.originating_prompt == "Get details for this 10-K filing"
        assert args.include_base_instructions is False

    def test_get_filing_args_required_field(self):
        """Test that filing_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            GetFilingArgs()

        assert "filing_id" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)


@pytest.mark.unit
class TestFilingsResponses:
    """Test filings response models."""

    def test_find_filings_response(self):
        """Test FindFilingsResponse model."""
        from aiera_mcp.tools.filings.models import EquityInfo, ApiResponseData

        filings = [
            FilingItem(
                filing_id=12345,
                title="Annual Report",
                filing_date=datetime(2023, 10, 27),
                is_amendment=0,
                equity=EquityInfo(name="Test Company", bloomberg_ticker="TEST:US"),
                form_number="10-K",
            )
        ]

        response = FindFilingsResponse(
            instructions=["Test instruction"], response=ApiResponseData(data=filings)
        )

        assert len(response.response.data) == 1
        assert response.instructions == ["Test instruction"]
        assert response.response.data[0].equity.name == "Test Company"

    def test_get_filing_response(self):
        """Test GetFilingResponse model."""
        from aiera_mcp.tools.filings.models import EquityInfo

        filing_details = FilingDetails(
            filing_id=12345,
            title="Annual Report",
            filing_date=datetime(2023, 10, 27),
            is_amendment=0,
            equity=EquityInfo(name="Test Company", bloomberg_ticker="TEST:US"),
            form_number="10-K",
            summary=FilingSummary(
                summary="Test summary",
                key_points=["Point 1"],
                financial_highlights={"revenue": "$100M"},
            ),
            content_preview="Content preview",
            document_count=1,
        )

        response = GetFilingResponse(filing=filing_details)

        assert isinstance(response.filing, FilingDetails)
        assert response.filing.filing_id == 12345
        assert response.filing.summary.summary == "Test summary"

    def test_get_filing_response_no_filing(self):
        """Test GetFilingResponse with no filing (robustness to empty response)."""
        response = GetFilingResponse(filing=None, instructions=["Filing not found"])

        assert response.filing is None
        assert response.instructions == ["Filing not found"]


@pytest.mark.unit
class TestFilingsModelValidation:
    """Test filings model validation and edge cases."""

    def test_model_serialization_roundtrip(self):
        """Test model serialization and deserialization."""
        original_args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            form_number="10-K",
            page=2,
            page_size=25,
        )

        # Serialize to dict
        serialized = original_args.model_dump()

        # Deserialize back to model
        deserialized_args = FindFilingsArgs(**serialized)

        # Verify round-trip
        assert original_args.start_date == deserialized_args.start_date
        assert original_args.end_date == deserialized_args.end_date
        assert original_args.bloomberg_ticker == deserialized_args.bloomberg_ticker
        assert original_args.form_number == deserialized_args.form_number
        assert original_args.page == deserialized_args.page
        assert original_args.page_size == deserialized_args.page_size

    def test_json_schema_generation(self):
        """Test that models can generate JSON schemas."""
        schema = FindFilingsArgs.model_json_schema()

        assert "properties" in schema
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]
        assert "form_number" in schema["properties"]

        # Check that required fields are marked as required
        assert "start_date" in schema["required"]
        assert "end_date" in schema["required"]

    def test_filing_item_date_handling(self):
        """Test filing item handles different date formats."""
        # Test with date object
        filing = FilingItem(
            filing_id=123,
            title="Test",
            filing_date=datetime(2023, 10, 27),  # FilingItem uses datetime, not date
            is_amendment=0,
        )
        assert filing.filing_date == datetime(2023, 10, 27)

    def test_filing_summary_empty_collections(self):
        """Test filing summary handles empty collections properly."""
        summary = FilingSummary(
            summary="Test summary", key_points=[], financial_highlights={}
        )

        assert summary.summary == "Test summary"
        assert summary.key_points == []
        assert summary.financial_highlights == {}

        # Test serialization of empty collections
        serialized = summary.model_dump()
        assert serialized["key_points"] == []
        assert serialized["financial_highlights"] == {}

    def test_filing_details_optional_summary(self):
        """Test filing details with None summary."""
        details = FilingDetails(
            filing_id=123,
            title="Test",
            filing_date=datetime(2023, 10, 27),
            is_amendment=0,
            summary=None,
            content_preview="Preview",
            document_count=1,
        )

        assert details.summary is None
        assert details.content_preview == "Preview"

    def test_financial_highlights_various_types(self):
        """Test financial highlights can contain various data types."""
        highlights = {
            "revenue": "$394.3B",
            "net_income": 97000000000,  # Numeric
            "gross_margin": 44.1,  # Float
            "growth_rate": "16%",  # String
            "is_profitable": True,  # Boolean
            "segments": ["iPhone", "Services", "Mac"],  # List
        }

        summary = FilingSummary(summary="Test", financial_highlights=highlights)

        assert summary.financial_highlights["revenue"] == "$394.3B"
        assert summary.financial_highlights["net_income"] == 97000000000
        assert summary.financial_highlights["gross_margin"] == 44.1
        assert summary.financial_highlights["is_profitable"] is True
        assert len(summary.financial_highlights["segments"]) == 3
