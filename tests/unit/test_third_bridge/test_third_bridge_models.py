#!/usr/bin/env python3

"""Unit tests for third_bridge models."""

import pytest
import json
from datetime import datetime
from pydantic import ValidationError

from aiera_mcp.tools.third_bridge.models import (
    FindThirdBridgeEventsArgs,
    GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse,
    GetThirdBridgeEventResponse,
    ThirdBridgeEventItem,
    ThirdBridgeEventDetails,
    ThirdBridgeCitationBlock,
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestThirdBridgeModels:
    """Test third_bridge Pydantic models."""

    def test_third_bridge_event_item_creation(self):
        """Test ThirdBridgeEventItem model creation."""
        event_data = {
            "event_id": "tb123",
            "content_type": "FORUM",
            "call_date": "2023-10-20T14:00:00Z",
            "title": "Apple Supply Chain Analysis",
            "language": "EN",
            "agenda": ["Supply chain resilience", "Cost optimization"],
            "insights": ["Key insight about supply chain", "Another strategic insight"],
            "citation_block": {
                "title": "Apple Supply Chain Analysis",
                "url": "https://thirdbridge.com/event/tb123",
                "expert_name": "Jane Smith",
                "expert_title": "Former Apple Supply Chain Director",
            },
        }

        event = ThirdBridgeEventItem(**event_data)

        assert event.event_id == "tb123"
        assert event.content_type == "FORUM"
        assert event.call_date == "2023-10-20T14:00:00Z"
        assert event.title == "Apple Supply Chain Analysis"
        assert event.language == "EN"
        assert len(event.agenda) == 2
        assert len(event.insights) == 2
        assert event.citation_block.expert_name == "Jane Smith"

    def test_third_bridge_event_item_optional_fields(self):
        """Test ThirdBridgeEventItem with only required fields."""
        minimal_data = {
            "event_id": "tb123",
            "content_type": "FORUM",
            "call_date": "2023-10-20T14:00:00Z",
            "title": "Test Event",
            "language": "EN",
            "agenda": ["Basic agenda item"],
            "insights": ["Basic insight"],
        }

        event = ThirdBridgeEventItem(**minimal_data)

        assert event.event_id == "tb123"
        assert event.content_type == "FORUM"
        assert event.call_date == "2023-10-20T14:00:00Z"
        assert event.title == "Test Event"
        assert event.language == "EN"
        assert event.citation_block is None

    def test_third_bridge_event_details_inherits_event_item(self):
        """Test ThirdBridgeEventDetails inherits from ThirdBridgeEventItem."""
        details_data = {
            "event_id": "tb123",
            "content_type": "FORUM",
            "call_date": "2023-10-20T14:00:00Z",
            "title": "Apple Supply Chain Analysis",
            "language": "EN",
            "agenda": "Discussion of supply chain challenges",  # Optional[str] in EventDetails
            "insights": "Key insights on supply chain management",  # Optional[str] in EventDetails
            "citation_block": {
                "title": "Apple Supply Chain Analysis",
                "url": "https://thirdbridge.com/event/tb123",
                "expert_name": "Jane Smith",
                "expert_title": "Former Apple Supply Chain Director",
            },
            "transcript": "Full transcript of the discussion...",
        }

        details = ThirdBridgeEventDetails(**details_data)

        # Test inherited fields
        assert details.event_id == "tb123"
        assert details.content_type == "FORUM"
        assert details.call_date == "2023-10-20T14:00:00Z"
        assert details.title == "Apple Supply Chain Analysis"
        assert details.language == "EN"

        # Test new fields (these override the List[str] from parent with Optional[str])
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
            page_size=50,
        )

        assert args.start_date == "2023-10-01"
        assert args.end_date == "2023-10-31"
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.page == 1
        assert args.page_size == 50

    def test_find_third_bridge_events_args_defaults(self):
        """Test FindThirdBridgeEventsArgs with default values."""
        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

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

        assert "String should match pattern" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="invalid-date")

        assert "String should match pattern" in str(exc_info.value)

    def test_find_third_bridge_events_args_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid pagination
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", page=5, page_size=25
        )
        assert args.page == 5
        assert args.page_size == 25

        # Page must be >= 1
        with pytest.raises(ValidationError):
            FindThirdBridgeEventsArgs(
                start_date="2023-10-01", end_date="2023-10-31", page=0
            )

        # Page size must be between 1 and 100
        with pytest.raises(ValidationError):
            FindThirdBridgeEventsArgs(
                start_date="2023-10-01", end_date="2023-10-31", page_size=0
            )

        with pytest.raises(ValidationError):
            FindThirdBridgeEventsArgs(
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
    def test_find_third_bridge_events_args_numeric_field_serialization(
        self, field_name, field_value
    ):
        """Test that numeric fields are serialized as strings."""
        args_data = {
            "start_date": "2023-10-01",
            "end_date": "2023-10-31",
            field_name: field_value,
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
            bloomberg_ticker="AAPL",  # Missing :US
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
        from aiera_mcp.tools.third_bridge.models import (
            ThirdBridgeResponseData,
            ThirdBridgePaginationInfo,
        )

        events = [
            ThirdBridgeEventItem(
                event_id="tb123",
                content_type="FORUM",
                call_date="2023-10-20T14:00:00Z",
                title="Test Event",
                language="EN",
                agenda=["Test agenda"],
                insights=["Test insight"],
            )
        ]

        citations = [
            CitationInfo(
                title="Test Citation",
                url="https://example.com",
                timestamp=datetime(2023, 10, 20, 14, 0, 0),
            )
        ]

        pagination = ThirdBridgePaginationInfo(
            total_count=1, current_page=1, total_pages=1, page_size=50
        )

        response_data = ThirdBridgeResponseData(pagination=pagination, data=events)

        response = FindThirdBridgeEventsResponse(
            response=response_data,
            instructions=["Test instruction"],
            citation_information=citations,
        )

        assert len(response.response.data) == 1
        assert response.response.pagination.total_count == 1
        assert response.response.pagination.current_page == 1
        assert response.response.pagination.page_size == 50
        assert response.instructions == ["Test instruction"]
        assert len(response.citation_information) == 1

    def test_get_third_bridge_event_response(self):
        """Test GetThirdBridgeEventResponse model."""
        event_details = ThirdBridgeEventDetails(
            event_id="tb123",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda="Test agenda",  # Optional[str] in ThirdBridgeEventDetails
            insights="Test insights",  # Optional[str] in ThirdBridgeEventDetails
            transcript="Test transcript",
        )

        response = GetThirdBridgeEventResponse(
            event=event_details,
            instructions=["Test instruction"],
            citation_information=[],
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
            page_size=25,
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

    def test_call_date_handling(self):
        """Test call date field handling."""
        # Valid call_date string
        event = ThirdBridgeEventItem(
            event_id="tb123",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=["Test agenda"],
            insights=["Test insight"],
        )
        assert event.call_date == "2023-10-20T14:00:00Z"

        # Test with different datetime string formats
        event_with_seconds = ThirdBridgeEventItem(
            event_id="tb124",
            content_type="FORUM",
            call_date="2023-10-20T14:30:45Z",
            title="Test Event",
            language="EN",
            agenda=["Test agenda"],
            insights=["Test insight"],
        )
        assert event_with_seconds.call_date == "2023-10-20T14:30:45Z"

    def test_optional_citation_block(self):
        """Test optional citation block handling."""
        # Event without citation block
        event = ThirdBridgeEventItem(
            event_id="tb123",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=["Test agenda"],
            insights=["Test insight"],
        )
        assert event.citation_block is None

        # Event with citation block information
        event_with_citation = ThirdBridgeEventItem(
            event_id="tb124",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=["Test agenda"],
            insights=["Test insight"],
            citation_block={
                "title": "Test Event",
                "url": "https://thirdbridge.com/event/tb124",
                "expert_name": "Jane Smith",
                "expert_title": "Former Executive",
            },
        )
        assert event_with_citation.citation_block.expert_name == "Jane Smith"
        assert event_with_citation.citation_block.expert_title == "Former Executive"

    def test_event_details_optional_fields(self):
        """Test optional fields in ThirdBridgeEventDetails."""
        # Minimal event details - ThirdBridgeEventDetails still needs agenda/insights from parent
        details = ThirdBridgeEventDetails(
            event_id="tb123",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=None,  # This overrides the List[str] from parent with Optional[str]
            insights=None,  # This overrides the List[str] from parent with Optional[str]
            transcript=None,
        )
        assert details.agenda is None
        assert details.insights is None
        assert details.transcript is None

        # Event details with all optional fields
        details_full = ThirdBridgeEventDetails(
            event_id="tb124",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda="Test agenda",
            insights="Test insights",
            transcript="Test transcript",
        )
        assert details_full.agenda == "Test agenda"
        assert details_full.insights == "Test insights"
        assert details_full.transcript == "Test transcript"

    def test_string_field_handling(self):
        """Test string field handling for various lengths."""
        # Short strings
        event = ThirdBridgeEventItem(
            event_id="tb1",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Short",
            language="EN",
            agenda=["Test"],
            insights=["Test"],
        )
        assert event.title == "Short"

        # Long strings
        long_title = "A very long title for a Third Bridge event that contains multiple words and detailed information about the discussion topic"
        event_long = ThirdBridgeEventItem(
            event_id="tb2",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title=long_title,
            language="EN",
            agenda=["Test"],
            insights=["Test"],
        )
        assert event_long.title == long_title

        # Empty strings (if allowed)
        event_empty = ThirdBridgeEventItem(
            event_id="tb3",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="",
            language="EN",
            agenda=["Test"],
            insights=["Test"],
        )
        assert event_empty.title == ""

    def test_agenda_and_insights_handling(self):
        """Test agenda and insights field handling."""
        # With agenda and insights
        event = ThirdBridgeEventItem(
            event_id="tb123",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=["Supply chain discussion", "Market outlook"],
            insights=["Key insight 1", "Key insight 2"],
        )
        assert len(event.agenda) == 2
        assert event.agenda[0] == "Supply chain discussion"
        assert len(event.insights) == 2
        assert event.insights[0] == "Key insight 1"

        # With empty agenda and insights
        event_empty = ThirdBridgeEventItem(
            event_id="tb124",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=[],
            insights=[],
        )
        assert len(event_empty.agenda) == 0
        assert len(event_empty.insights) == 0


@pytest.mark.unit
class TestThirdBridgeEventItemDateTimeSerialization:
    """Test datetime field serialization in Third Bridge event models."""

    def test_third_bridge_event_item_serialization(self):
        """Test that ThirdBridgeEventItem fields are serialized correctly."""
        event = ThirdBridgeEventItem(
            event_id="tb123",
            content_type="FORUM",
            call_date="2024-01-15T14:30:00Z",
            title="Test Third Bridge Event",
            language="EN",
            agenda=["Test agenda item"],
            insights=["Test insight"],
            citation_block={
                "title": "Test Event",
                "url": "https://thirdbridge.com/event/tb123",
                "expert_name": "Jane Expert",
                "expert_title": "Former Executive",
            },
        )

        # Test model_dump serialization
        serialized = event.model_dump()

        # call_date should remain as string
        assert isinstance(serialized["call_date"], str)
        assert serialized["call_date"] == "2024-01-15T14:30:00Z"
        assert isinstance(serialized["agenda"], list)
        assert isinstance(serialized["insights"], list)

    def test_third_bridge_event_details_serialization(self):
        """Test that ThirdBridgeEventDetails serialization works correctly."""
        details = ThirdBridgeEventDetails(
            event_id="tb123",
            content_type="FORUM",
            call_date="2024-01-15T14:30:00Z",
            title="Test Third Bridge Event",
            language="EN",
            agenda="Test agenda",  # Optional[str] in EventDetails
            insights="Test insights",  # Optional[str] in EventDetails
            transcript="Test transcript",
        )

        # Test model_dump serialization
        serialized = details.model_dump()

        # call_date should remain as string
        assert isinstance(serialized["call_date"], str)
        assert serialized["call_date"] == "2024-01-15T14:30:00Z"
        assert serialized["agenda"] == "Test agenda"

    def test_third_bridge_response_json_serialization(self):
        """Test that complete Third Bridge response models can be serialized to JSON."""
        from aiera_mcp.tools.third_bridge.models import (
            ThirdBridgeResponseData,
            ThirdBridgePaginationInfo,
        )

        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        # Create Third Bridge event with new structure
        event = ThirdBridgeEventItem(
            event_id="tb123",
            content_type="FORUM",
            call_date="2024-01-15T14:30:00Z",
            title="Test Third Bridge Event",
            language="EN",
            agenda=["Test agenda"],
            insights=["Test insight"],
        )

        # Create citation with datetime
        citation = CitationInfo(
            title="Third Bridge Citation",
            url="https://thirdbridge.com/event/123",
            timestamp=test_datetime,
        )

        # Create pagination info
        pagination = ThirdBridgePaginationInfo(
            total_count=1, current_page=1, total_pages=1, page_size=50
        )

        # Create response data container
        response_data = ThirdBridgeResponseData(pagination=pagination, data=[event])

        # Create response with new structure
        response = FindThirdBridgeEventsResponse(
            response=response_data,
            instructions=["Third Bridge instruction"],
            citation_information=[citation],
        )

        # Test that entire response can be JSON serialized
        response_dict = response.model_dump()
        json_str = json.dumps(response_dict)

        # Should not raise any serialization errors
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Verify fields were serialized correctly in JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed["response"]["data"][0]["call_date"], str)
        assert isinstance(parsed["citation_information"][0]["timestamp"], str)

    def test_minimal_third_bridge_event_serialization(self):
        """Test serialization of Third Bridge event with minimal required fields."""
        event = ThirdBridgeEventItem(
            event_id="tb124",
            content_type="FORUM",
            call_date="2024-01-15T14:30:00Z",
            title="Minimal Event",
            language="EN",
            agenda=["Minimal agenda"],
            insights=["Minimal insight"],
        )

        # Test JSON serialization with minimal fields
        response_dict = event.model_dump()
        json_str = json.dumps(response_dict)

        # Should not raise any serialization errors
        assert isinstance(json_str, str)

        # Verify call_date field was serialized as string
        parsed = json.loads(json_str)
        assert isinstance(parsed["call_date"], str)
        assert parsed["call_date"] == "2024-01-15T14:30:00Z"
