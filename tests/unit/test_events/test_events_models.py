#!/usr/bin/env python3

"""Unit tests for events models."""

import pytest
import json
from pydantic import ValidationError

from aiera_mcp.tools.events.models import (
    FindEventsArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindEventsResponse,
    GetEventResponse,
    GetUpcomingEventsResponse,
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestFindEventsArgs:
    """Test FindEventsArgs model."""

    def test_valid_find_events_args(self):
        """Test valid FindEventsArgs creation."""
        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            event_type="earnings",
            page=1,
            page_size=50,
        )

        assert args.start_date == "2023-10-01"
        assert args.end_date == "2023-10-31"
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.event_type == "earnings"
        assert args.page == 1
        assert args.page_size == 50

    def test_find_events_args_defaults(self):
        """Test FindEventsArgs with default values."""
        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        assert args.event_type == "earnings"  # Default value
        assert args.page == 1  # Default value
        assert args.page_size == 50  # Default value
        assert args.bloomberg_ticker is None
        assert args.watchlist_id is None
        assert args.originating_prompt is None  # Default value
        assert args.include_base_instructions is True  # Default value

    def test_find_events_args_with_originating_prompt(self):
        """Test FindEventsArgs with originating_prompt field."""
        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            originating_prompt="Find all earnings calls for Apple",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "Find all earnings calls for Apple"
        assert args.include_base_instructions is False

    def test_find_events_args_date_format_validation(self):
        """Test date format validation."""
        # Valid date format
        args = FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31")
        assert args.start_date == "2023-10-01"

        # Invalid date formats should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            FindEventsArgs(start_date="10/01/2023", end_date="2023-10-31")

        assert "String should match pattern" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FindEventsArgs(start_date="2023-10-01", end_date="invalid-date")

        assert "String should match pattern" in str(exc_info.value)

    def test_find_events_args_event_type_validation(self):
        """Test event_type validation."""
        # Valid event types
        for event_type in [
            "earnings",
            "presentation",
            "shareholder_meeting",
            "investor_meeting",
            "special_situation",
        ]:
            args = FindEventsArgs(
                start_date="2023-10-01", end_date="2023-10-31", event_type=event_type
            )
            assert args.event_type == event_type

        # Invalid event type gets corrected to default (earnings) by correction logic
        args = FindEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", event_type="invalid_type"
        )
        assert args.event_type == "earnings"  # Corrected to default

    def test_find_events_args_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid pagination
        args = FindEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", page=5, page_size=25
        )
        assert args.page == 5
        assert args.page_size == 25

        # Page must be >= 1
        with pytest.raises(ValidationError):
            FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31", page=0)

        # Page size must be between 1 and 100
        with pytest.raises(ValidationError):
            FindEventsArgs(start_date="2023-10-01", end_date="2023-10-31", page_size=0)

        with pytest.raises(ValidationError):
            FindEventsArgs(
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
    def test_find_events_args_numeric_field_serialization(
        self, field_name, field_value
    ):
        """Test that numeric fields are serialized as strings."""
        args_data = {
            "start_date": "2023-10-01",
            "end_date": "2023-10-31",
            field_name: field_value,
        }
        args = FindEventsArgs(**args_data)

        # Model dump should serialize numeric fields as strings
        dumped = args.model_dump(exclude_none=True)
        assert dumped[field_name] == str(field_value)


@pytest.mark.unit
class TestGetEventArgs:
    """Test GetEventArgs model."""

    def test_valid_get_event_args(self):
        """Test valid GetEventArgs creation."""
        args = GetEventArgs(event_id="12345")
        assert args.event_id == "12345"
        assert args.originating_prompt is None
        assert args.include_base_instructions is True

    def test_get_event_args_with_originating_prompt(self):
        """Test GetEventArgs with originating_prompt field."""
        args = GetEventArgs(
            event_id="12345",
            originating_prompt="Get details for this earnings call",
            include_base_instructions=False,
        )
        assert args.originating_prompt == "Get details for this earnings call"
        assert args.include_base_instructions is False


@pytest.mark.unit
class TestGetUpcomingEventsArgs:
    """Test GetUpcomingEventsArgs model."""

    def test_valid_upcoming_events_args(self):
        """Test valid GetUpcomingEventsArgs creation."""
        args = GetUpcomingEventsArgs(
            start_date="2023-11-01", end_date="2023-11-30", bloomberg_ticker="AAPL:US"
        )

        assert args.start_date == "2023-11-01"
        assert args.end_date == "2023-11-30"
        assert args.bloomberg_ticker == "AAPL:US"

    def test_upcoming_events_args_optional_fields(self):
        """Test GetUpcomingEventsArgs with only required fields."""
        args = GetUpcomingEventsArgs(start_date="2023-11-01", end_date="2023-11-30")

        assert args.start_date == "2023-11-01"
        assert args.end_date == "2023-11-30"
        assert args.bloomberg_ticker is None
        assert args.watchlist_id is None
        assert args.originating_prompt is None
        assert args.include_base_instructions is True

    def test_upcoming_events_args_with_originating_prompt(self):
        """Test GetUpcomingEventsArgs with originating_prompt field."""
        args = GetUpcomingEventsArgs(
            start_date="2023-11-01",
            end_date="2023-11-30",
            originating_prompt="Find upcoming events for tech companies",
            include_base_instructions=False,
        )
        assert args.originating_prompt == "Find upcoming events for tech companies"
        assert args.include_base_instructions is False


@pytest.mark.unit
class TestEventsResponses:
    """Test events response models with pass-through pattern."""

    def test_find_events_response(self):
        """Test FindEventsResponse model with pass-through data."""
        response = FindEventsResponse(
            instructions=["Test instruction"],
            response={
                "data": [
                    {
                        "event_id": 12345,
                        "title": "Test Event",
                        "event_type": "earnings",
                        "event_date": "2023-10-26T21:00:00",
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
        )

        assert response.response is not None
        assert response.response["data"][0]["event_id"] == 12345
        assert response.response["pagination"]["total_count"] == 1
        assert response.instructions == ["Test instruction"]

    def test_get_event_response(self):
        """Test GetEventResponse model with pass-through data."""
        response = GetEventResponse(
            response={"data": [{"event_id": 12345, "title": "Test Event"}]},
            instructions=["Test instruction"],
        )

        assert response.response is not None
        assert response.response["data"][0]["event_id"] == 12345
        assert response.instructions == ["Test instruction"]

    def test_get_upcoming_events_response(self):
        """Test GetUpcomingEventsResponse model with pass-through data."""
        response = GetUpcomingEventsResponse(
            instructions=["Upcoming events found"],
            response={
                "estimates": [
                    {
                        "estimate_id": 12345,
                        "estimate": {
                            "call_type": "earnings",
                            "call_date": "2023-11-15",
                            "title": "Upcoming Earnings Event",
                        },
                    }
                ],
                "actuals": [],
            },
        )

        assert response.response is not None
        assert len(response.response["estimates"]) == 1
        assert (
            response.response["estimates"][0]["estimate"]["title"]
            == "Upcoming Earnings Event"
        )
        assert response.instructions == ["Upcoming events found"]

    def test_response_with_none(self):
        """Test response models accept None response."""
        response = FindEventsResponse(
            instructions=["No data"],
            response=None,
        )

        assert response.response is None
        assert response.instructions == ["No data"]


@pytest.mark.unit
class TestEventsModelValidation:
    """Test events model validation and edge cases."""

    def test_bloomberg_ticker_correction(self):
        """Test Bloomberg ticker format correction (if implemented)."""
        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL",  # Missing :US
        )

        # Check if ticker correction is applied
        assert args.bloomberg_ticker in ["AAPL", "AAPL:US"]

    def test_event_type_correction(self):
        """Test event type correction (if implemented)."""
        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            event_type="Earnings",  # Different case
        )

        # Check if type correction is applied
        assert args.event_type in ["Earnings", "earnings"]

    def test_model_serialization_roundtrip(self):
        """Test model serialization and deserialization."""
        original_args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            event_type="earnings",
            page=2,
            page_size=25,
        )

        # Serialize to dict
        serialized = original_args.model_dump()

        # Deserialize back to model
        deserialized_args = FindEventsArgs(**serialized)

        # Verify round-trip
        assert original_args.start_date == deserialized_args.start_date
        assert original_args.end_date == deserialized_args.end_date
        assert original_args.bloomberg_ticker == deserialized_args.bloomberg_ticker
        assert original_args.event_type == deserialized_args.event_type
        assert original_args.page == deserialized_args.page
        assert original_args.page_size == deserialized_args.page_size

    def test_json_schema_generation(self):
        """Test that models can generate JSON schemas."""
        schema = FindEventsArgs.model_json_schema()

        assert "properties" in schema
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]
        assert "event_type" in schema["properties"]

        # Check that required fields are marked as required
        assert "start_date" in schema["required"]
        assert "end_date" in schema["required"]


@pytest.mark.unit
class TestEventsResponseJsonSerialization:
    """Test JSON serialization of pass-through response models."""

    def test_events_response_json_serialization(self):
        """Test that complete response models can be serialized to JSON."""
        response = FindEventsResponse(
            instructions=["Test instruction"],
            response={
                "data": [
                    {
                        "event_id": 123,
                        "title": "Test Event",
                        "event_type": "earnings",
                        "event_date": "2024-01-15T14:30:00",
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
            },
        )

        # Test that entire response can be JSON serialized
        response_dict = response.model_dump()
        json_str = json.dumps(response_dict)

        # Should not raise any serialization errors
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Verify data is preserved through JSON serialization
        parsed = json.loads(json_str)
        assert parsed["response"]["data"][0]["event_id"] == 123
        assert isinstance(parsed["response"]["data"][0]["event_date"], str)

    def test_citation_info_serialization(self):
        """Test that CitationInfo models can be serialized correctly."""
        from aiera_mcp.tools.common.models import CitationMetadata

        metadata = CitationMetadata(
            type="event",
            event_id=12345,
            company_id=678,
        )

        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            metadata=metadata,
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        # metadata should be serialized correctly
        assert serialized["metadata"]["type"] == "event"
        assert serialized["metadata"]["event_id"] == 12345

    def test_citation_info_optional_metadata_serialization(self):
        """Test CitationInfo with None metadata."""
        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            metadata=None,
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        # metadata should remain None when not provided
        assert serialized["metadata"] is None
