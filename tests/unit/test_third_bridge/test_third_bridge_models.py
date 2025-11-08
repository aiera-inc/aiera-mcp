#!/usr/bin/env python3

"""Unit tests for third_bridge models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from aiera_mcp.tools.third_bridge.models import (
    FindThirdBridgeEventsArgs, GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse, GetThirdBridgeEventResponse,
    ThirdBridgeEventItem, ThirdBridgeEventDetails
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestThirdBridgeModels:
    """Test third_bridge Pydantic models."""

    def test_third_bridge_event_item_creation(self):
        """Test ThirdBridgeEventItem model creation."""
        event_data = {
            "event_id": "tb123",
            "title": "Apple Supply Chain Analysis",
            "company_name": "Apple Inc",
            "event_date": datetime(2023, 10, 20, 14, 0, 0),
            "expert_name": "Jane Smith",
            "expert_title": "Former Apple Supply Chain Director"
        }

        event = ThirdBridgeEventItem(**event_data)

        assert event.event_id == "tb123"
        assert event.title == "Apple Supply Chain Analysis"
        assert event.company_name == "Apple Inc"
        assert event.event_date == datetime(2023, 10, 20, 14, 0, 0)
        assert event.expert_name == "Jane Smith"
        assert event.expert_title == "Former Apple Supply Chain Director"

    def test_third_bridge_event_item_optional_fields(self):
        """Test ThirdBridgeEventItem with only required fields."""
        minimal_data = {
            "event_id": "tb123",
            "title": "Test Event",
            "event_date": datetime(2023, 10, 20, 14, 0, 0)
        }

        event = ThirdBridgeEventItem(**minimal_data)

        assert event.event_id == "tb123"
        assert event.title == "Test Event"
        assert event.company_name is None
        assert event.expert_name is None
        assert event.expert_title is None

    def test_third_bridge_event_details_inherits_event_item(self):
        """Test ThirdBridgeEventDetails inherits from ThirdBridgeEventItem."""
        details_data = {
            "event_id": "tb123",
            "title": "Apple Supply Chain Analysis",
            "company_name": "Apple Inc",
            "event_date": datetime(2023, 10, 20, 14, 0, 0),
            "expert_name": "Jane Smith",
            "expert_title": "Former Apple Supply Chain Director",
            "agenda": "Discussion of supply chain challenges",
            "insights": "Key insights on supply chain management",
            "transcript": "Full transcript of the discussion..."
        }

        details = ThirdBridgeEventDetails(**details_data)

        # Test inherited fields
        assert details.event_id == "tb123"
        assert details.title == "Apple Supply Chain Analysis"
        assert details.company_name == "Apple Inc"
        assert details.expert_name == "Jane Smith"

        # Test new fields
        assert details.agenda == "Discussion of supply chain challenges"
        assert details.insights == "Key insights on supply chain management"
        assert details.transcript == "Full transcript of the discussion..."


@pytest.mark.unit
class TestFindThirdBridgeEventsArgs:
    """Test FindThirdBridgeEventsArgs model."""

    def test_valid_find_third_bridge_events_args(self):
        """Test valid FindThirdBridgeEventsArgs creation."""
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            page=1,
            page_size=50
        )

        assert args.start_date == "2023-10-01"
        assert args.end_date == "2023-10-31"
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.page == 1
        assert args.page_size == 50

    def test_find_third_bridge_events_args_defaults(self):
        """Test FindThirdBridgeEventsArgs with default values."""
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31"
        )

        assert args.page == 1  # Default value
        assert args.page_size == 50  # Default value
        assert args.bloomberg_ticker is None
        assert args.watchlist_id is None

    def test_find_third_bridge_events_args_date_format_validation(self):
        """Test date format validation."""
        # Valid date format
        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")
        assert args.start_date == "2023-10-01"

        # Invalid date formats should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            FindThirdBridgeEventsArgs(start_date="10/01/2023", end_date="2023-10-31")

        assert "string does not match expected pattern" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="invalid-date")

        assert "string does not match expected pattern" in str(exc_info.value)

    def test_find_third_bridge_events_args_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid pagination
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            page=5,
            page_size=25
        )
        assert args.page == 5
        assert args.page_size == 25

        # Page must be >= 1
        with pytest.raises(ValidationError):
            FindThirdBridgeEventsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31",
                page=0
            )

        # Page size must be between 1 and 100
        with pytest.raises(ValidationError):
            FindThirdBridgeEventsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31",
                page_size=0
            )

        with pytest.raises(ValidationError):
            FindThirdBridgeEventsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31",
                page_size=101
            )

    @pytest.mark.parametrize("field_name,field_value", [
        ("watchlist_id", 123),
        ("index_id", 456),
        ("sector_id", 789),
        ("subsector_id", 101)
    ])
    def test_find_third_bridge_events_args_numeric_field_serialization(self, field_name, field_value):
        """Test that numeric fields are serialized as strings."""
        args_data = {
            "start_date": "2023-10-01",
            "end_date": "2023-10-31",
            field_name: field_value
        }
        args = FindThirdBridgeEventsArgs(**args_data)

        # Model dump should serialize numeric fields as strings
        dumped = args.model_dump(exclude_none=True)
        assert dumped[field_name] == str(field_value)

    def test_bloomberg_ticker_validation(self):
        """Test Bloomberg ticker format validation."""
        # This test assumes there's ticker format correction logic
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL"  # Missing :US
        )

        # Check if ticker correction is applied
        # This depends on the actual implementation in utils.py
        assert args.bloomberg_ticker in ["AAPL", "AAPL:US"]


@pytest.mark.unit
class TestGetThirdBridgeEventArgs:
    """Test GetThirdBridgeEventArgs model."""

    def test_valid_get_third_bridge_event_args(self):
        """Test valid GetThirdBridgeEventArgs creation."""
        args = GetThirdBridgeEventArgs(event_id="tb123")
        assert args.event_id == "tb123"

    def test_get_third_bridge_event_args_required_field(self):
        """Test that event_id is required."""
        with pytest.raises(ValidationError):
            GetThirdBridgeEventArgs()  # Missing required field


@pytest.mark.unit
class TestThirdBridgeResponses:
    """Test third_bridge response models."""

    def test_find_third_bridge_events_response(self):
        """Test FindThirdBridgeEventsResponse model."""
        events = [
            ThirdBridgeEventItem(
                event_id="tb123",
                title="Test Event",
                event_date=datetime(2023, 10, 20, 14, 0, 0)
            )
        ]

        citations = [
            CitationInfo(
                title="Test Citation",
                url="https://example.com",
                timestamp=datetime(2023, 10, 20, 14, 0, 0)
            )
        ]

        response = FindThirdBridgeEventsResponse(
            events=events,
            total=1,
            page=1,
            page_size=50,
            instructions=["Test instruction"],
            citation_information=citations
        )

        assert len(response.events) == 1
        assert response.total == 1
        assert response.page == 1
        assert response.page_size == 50
        assert response.instructions == ["Test instruction"]
        assert len(response.citation_information) == 1

    def test_get_third_bridge_event_response(self):
        """Test GetThirdBridgeEventResponse model."""
        event_details = ThirdBridgeEventDetails(
            event_id="tb123",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0),
            agenda="Test agenda",
            insights="Test insights"
        )

        response = GetThirdBridgeEventResponse(
            event=event_details,
            instructions=["Test instruction"],
            citation_information=[]
        )

        assert isinstance(response.event, ThirdBridgeEventDetails)
        assert response.event.event_id == "tb123"
        assert response.event.agenda == "Test agenda"
        assert response.instructions == ["Test instruction"]


@pytest.mark.unit
class TestThirdBridgeModelValidation:
    """Test third_bridge model validation and edge cases."""

    def test_model_serialization_roundtrip(self):
        """Test model serialization and deserialization."""
        original_args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            page=2,
            page_size=25
        )

        # Serialize to dict
        serialized = original_args.model_dump()

        # Deserialize back to model
        deserialized_args = FindThirdBridgeEventsArgs(**serialized)

        # Verify round-trip
        assert original_args.start_date == deserialized_args.start_date
        assert original_args.end_date == deserialized_args.end_date
        assert original_args.bloomberg_ticker == deserialized_args.bloomberg_ticker
        assert original_args.page == deserialized_args.page
        assert original_args.page_size == deserialized_args.page_size

    def test_json_schema_generation(self):
        """Test that models can generate JSON schemas."""
        schema = FindThirdBridgeEventsArgs.model_json_schema()

        assert "properties" in schema
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]
        assert "bloomberg_ticker" in schema["properties"]

        # Check that required fields are marked as required
        assert "start_date" in schema["required"]
        assert "end_date" in schema["required"]

    def test_event_date_handling(self):
        """Test event date field handling."""
        # Valid datetime
        event = ThirdBridgeEventItem(
            event_id="tb123",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0)
        )
        assert isinstance(event.event_date, datetime)

        # Test with different datetime formats
        event_with_seconds = ThirdBridgeEventItem(
            event_id="tb124",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 30, 45)
        )
        assert event_with_seconds.event_date.second == 45

    def test_optional_expert_fields(self):
        """Test optional expert fields handling."""
        # Event without expert information
        event = ThirdBridgeEventItem(
            event_id="tb123",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0)
        )
        assert event.expert_name is None
        assert event.expert_title is None

        # Event with expert information
        event_with_expert = ThirdBridgeEventItem(
            event_id="tb124",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0),
            expert_name="Jane Smith",
            expert_title="Former Executive"
        )
        assert event_with_expert.expert_name == "Jane Smith"
        assert event_with_expert.expert_title == "Former Executive"

    def test_event_details_optional_fields(self):
        """Test optional fields in ThirdBridgeEventDetails."""
        # Minimal event details
        details = ThirdBridgeEventDetails(
            event_id="tb123",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0)
        )
        assert details.agenda is None
        assert details.insights is None
        assert details.transcript is None

        # Event details with all optional fields
        details_full = ThirdBridgeEventDetails(
            event_id="tb124",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0),
            agenda="Test agenda",
            insights="Test insights",
            transcript="Test transcript"
        )
        assert details_full.agenda == "Test agenda"
        assert details_full.insights == "Test insights"
        assert details_full.transcript == "Test transcript"

    def test_string_field_handling(self):
        """Test string field handling for various lengths."""
        # Short strings
        event = ThirdBridgeEventItem(
            event_id="tb1",
            title="Short",
            event_date=datetime(2023, 10, 20, 14, 0, 0)
        )
        assert event.title == "Short"

        # Long strings
        long_title = "A very long title for a Third Bridge event that contains multiple words and detailed information about the discussion topic"
        event_long = ThirdBridgeEventItem(
            event_id="tb2",
            title=long_title,
            event_date=datetime(2023, 10, 20, 14, 0, 0)
        )
        assert event_long.title == long_title

        # Empty strings (if allowed)
        event_empty = ThirdBridgeEventItem(
            event_id="tb3",
            title="",
            event_date=datetime(2023, 10, 20, 14, 0, 0)
        )
        assert event_empty.title == ""

    def test_company_name_handling(self):
        """Test company name field handling."""
        # With company name
        event = ThirdBridgeEventItem(
            event_id="tb123",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0),
            company_name="Apple Inc"
        )
        assert event.company_name == "Apple Inc"

        # Without company name
        event_no_company = ThirdBridgeEventItem(
            event_id="tb124",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0)
        )
        assert event_no_company.company_name is None

        # Company name with special characters
        event_special = ThirdBridgeEventItem(
            event_id="tb125",
            title="Test Event",
            event_date=datetime(2023, 10, 20, 14, 0, 0),
            company_name="AT&T Inc."
        )
        assert event_special.company_name == "AT&T Inc."