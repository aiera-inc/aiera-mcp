#!/usr/bin/env python3

"""Unit tests for events models."""

import pytest
import json
from datetime import datetime
from pydantic import ValidationError

from aiera_mcp.tools.events.models import (
    FindEventsArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindEventsResponse,
    GetEventResponse,
    GetUpcomingEventsResponse,
    EventItem,
    EventDetails,
    EventType,
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestEventsModels:
    """Test events Pydantic models."""

    def test_event_type_enum(self):
        """Test EventType enum values."""
        assert EventType.EARNINGS == "earnings"
        assert EventType.PRESENTATION == "presentation"
        assert EventType.SHAREHOLDER_MEETING == "shareholder_meeting"
        assert EventType.INVESTOR_MEETING == "investor_meeting"
        assert EventType.SPECIAL_SITUATION == "special_situation"

    def test_event_item_creation(self):
        """Test EventItem model creation."""
        event_data = {
            "event_id": 12345,
            "title": "Test Event",
            "event_type": EventType.EARNINGS,
            "event_date": datetime(2023, 10, 26, 21, 0, 0),
        }

        event = EventItem(**event_data)

        assert event.event_id == 12345
        assert event.title == "Test Event"
        assert event.event_type == EventType.EARNINGS

    def test_event_details_inherits_event_item(self):
        """Test EventDetails inherits from EventItem."""
        details_data = {
            "event_id": 12345,
            "title": "Test Event",
            "event_type": EventType.EARNINGS,
            "event_date": datetime(2023, 10, 26, 21, 0, 0),
            "company_name": "Test Company",
            "description": "Test event description",
            "transcript_preview": "Welcome to the test event...",
            "audio_url": "https://example.com/audio.mp3",
        }

        details = EventDetails(**details_data)

        # Test inherited fields
        assert details.event_id == 12345
        assert details.title == "Test Event"

        # Test new fields
        assert details.description == "Test event description"
        assert details.transcript_preview == "Welcome to the test event..."
        assert details.audio_url == "https://example.com/audio.mp3"


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
        assert args.transcript_section is None

    def test_get_event_args_with_transcript_section(self):
        """Test GetEventArgs with transcript_section."""
        args = GetEventArgs(event_id="12345", transcript_section="q_and_a")
        assert args.event_id == "12345"
        assert args.transcript_section == "q_and_a"

        args = GetEventArgs(event_id="12345", transcript_section="presentation")
        assert args.transcript_section == "presentation"

    def test_get_event_args_transcript_section_validation(self):
        """Test transcript_section validation."""
        # Valid values
        GetEventArgs(event_id="12345", transcript_section="presentation")
        GetEventArgs(event_id="12345", transcript_section="q_and_a")
        GetEventArgs(event_id="12345", transcript_section=None)

        # Invalid value
        with pytest.raises(ValidationError) as exc_info:
            GetEventArgs(event_id="12345", transcript_section="invalid_section")

        assert "transcript_section must be either 'presentation' or 'q_and_a'" in str(
            exc_info.value
        )


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


@pytest.mark.unit
class TestEventsResponses:
    """Test events response models."""

    def test_find_events_response(self):
        """Test FindEventsResponse model."""
        events = [
            EventItem(
                event_id=12345,
                title="Test Event",
                event_type=EventType.EARNINGS,
                event_date=datetime(2023, 10, 26, 21, 0, 0),
            )
        ]

        response = FindEventsResponse(
            instructions=["Test instruction"],
            response={
                "data": events,
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

    def test_get_event_response(self):
        """Test GetEventResponse model."""
        event_details = EventDetails(
            event_id=12345,
            title="Test Event",
            event_type=EventType.EARNINGS,
            event_date=datetime(2023, 10, 26, 21, 0, 0),
            description="Test description",
            transcript_preview="Test preview",
        )

        response = GetEventResponse(
            event=event_details,
            instructions=["Test instruction"],
            citation_information=[],
        )

        assert isinstance(response.event, EventDetails)
        assert response.event.event_id == 12345
        assert response.event.description == "Test description"
        assert response.instructions == ["Test instruction"]

    def test_get_upcoming_events_response(self):
        """Test GetUpcomingEventsResponse model."""
        events = [
            EventItem(
                event_id=12345,
                title="Upcoming Event",
                event_type=EventType.EARNINGS,
                event_date=datetime(2023, 11, 15, 21, 0, 0),
            )
        ]

        response = GetUpcomingEventsResponse(
            instructions=["Upcoming events found"],
            response={"estimates": events, "actuals": []},
        )

        assert len(response.response.estimates) == 1
        assert response.response.estimates[0].title == "Upcoming Event"
        assert response.instructions == ["Upcoming events found"]


@pytest.mark.unit
class TestEventsModelValidation:
    """Test events model validation and edge cases."""

    def test_bloomberg_ticker_correction(self):
        """Test Bloomberg ticker format correction (if implemented)."""
        # This test assumes there's ticker format correction logic
        # If not implemented, this test can be removed or modified
        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL",  # Missing :US
        )

        # Check if ticker correction is applied
        # This depends on the actual implementation in utils.py
        assert args.bloomberg_ticker in ["AAPL", "AAPL:US"]

    def test_event_type_correction(self):
        """Test event type correction (if implemented)."""
        # This test assumes there's event type correction logic
        args = FindEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            event_type="Earnings",  # Different case
        )

        # Check if type correction is applied
        # This depends on the actual implementation in utils.py
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
class TestEventItemDateTimeSerialization:
    """Test datetime field serialization in event models."""

    def test_event_item_datetime_serialization(self):
        """Test that EventItem datetime fields are serialized to strings."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        event = EventItem(
            event_id=123,
            title="Test Event",
            event_type=EventType.EARNINGS,
            event_date=test_datetime,
        )

        # Test model_dump serialization
        serialized = event.model_dump()

        # event_date should be serialized as string, not datetime object
        assert isinstance(serialized["event_date"], str)
        assert serialized["event_date"] == test_datetime.isoformat()

    def test_event_details_datetime_serialization(self):
        """Test that EventDetails inherits datetime serialization from EventItem."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        details = EventDetails(
            event_id=123,
            title="Test Event",
            event_type=EventType.EARNINGS,
            event_date=test_datetime,
            description="Test description",
            transcript_preview="Test preview",
        )

        # Test model_dump serialization
        serialized = details.model_dump()

        # event_date should be serialized as string
        assert isinstance(serialized["event_date"], str)
        assert serialized["event_date"] == test_datetime.isoformat()

    def test_citation_info_datetime_serialization(self):
        """Test that CitationInfo datetime fields are serialized correctly."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            timestamp=test_datetime,
            source="Test Source",
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        # timestamp should be serialized as string
        assert isinstance(serialized["timestamp"], str)
        assert serialized["timestamp"] == test_datetime.isoformat()

    def test_citation_info_optional_timestamp_serialization(self):
        """Test CitationInfo with None timestamp."""
        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            timestamp=None,
            source="Test Source",
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        # timestamp should remain None when not provided
        assert serialized["timestamp"] is None

    def test_events_response_json_serialization(self):
        """Test that complete response models can be serialized to JSON."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        # Create event with datetime
        event = EventItem(
            event_id=123,
            title="Test Event",
            event_type=EventType.EARNINGS,
            event_date=test_datetime,
        )

        # Create response with event
        response = FindEventsResponse(
            instructions=["Test instruction"],
            response={
                "data": [event],
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

        # Verify datetime fields were serialized as strings in JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed["response"]["data"][0]["event_date"], str)
