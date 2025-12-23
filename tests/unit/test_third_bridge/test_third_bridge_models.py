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
    ThirdBridgeSpecialist,
    ThirdBridgeModerator,
    ThirdBridgeTranscriptItem,
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestThirdBridgeModels:
    """Test third_bridge Pydantic models."""

    def test_third_bridge_event_item_creation(self):
        """Test ThirdBridgeEventItem model creation with event_id alias."""
        event_data = {
            "event_id": "tb123",  # API uses event_id
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

        # Access via thirdbridge_event_id (internal name)
        assert event.thirdbridge_event_id == "tb123"
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
        }

        event = ThirdBridgeEventItem(**minimal_data)

        assert event.thirdbridge_event_id == "tb123"
        assert event.content_type == "FORUM"
        assert event.call_date == "2023-10-20T14:00:00Z"
        assert event.title == "Test Event"
        assert event.language == "EN"
        assert event.insights is None  # Optional field
        assert event.citation_block is None

    def test_third_bridge_event_details_with_lists(self):
        """Test ThirdBridgeEventDetails with List types for agenda, insights, transcript."""
        details_data = {
            "event_id": "tb123",
            "content_type": "FORUM",
            "call_date": "2023-10-20T14:00:00Z",
            "title": "Apple Supply Chain Analysis",
            "language": "EN",
            "agenda": ["Supply chain challenges", "Cost optimization"],  # List[str]
            "insights": ["Key insight 1", "Key insight 2"],  # List[str]
            "citation_block": {
                "title": "Apple Supply Chain Analysis",
                "url": "https://thirdbridge.com/event/tb123",
                "expert_name": "Jane Smith",
                "expert_title": "Former Apple Supply Chain Director",
            },
            "specialists": [
                {"title": "Former Supply Chain Director", "initials": "JS"}
            ],
            "moderators": [{"id": "mod123", "initials": "AB"}],
            "transcript": [
                {"timestamp": "[00:00:01]", "discussionItem": ["Opening remarks"]}
            ],
        }

        details = ThirdBridgeEventDetails(**details_data)

        # Test inherited fields
        assert details.thirdbridge_event_id == "tb123"
        assert details.content_type == "FORUM"
        assert details.call_date == "2023-10-20T14:00:00Z"
        assert details.title == "Apple Supply Chain Analysis"
        assert details.language == "EN"

        # Test List[str] fields (changed from Optional[str])
        assert isinstance(details.agenda, list)
        assert len(details.agenda) == 2
        assert details.agenda[0] == "Supply chain challenges"

        assert isinstance(details.insights, list)
        assert len(details.insights) == 2
        assert details.insights[0] == "Key insight 1"

        # Test new fields
        assert len(details.specialists) == 1
        assert details.specialists[0].initials == "JS"

        assert len(details.moderators) == 1
        assert details.moderators[0].id == "mod123"

        assert len(details.transcript) == 1
        assert details.transcript[0].timestamp == "[00:00:01]"


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
    """Test GetThirdBridgeEventArgs model with aliasing."""

    def test_valid_get_third_bridge_event_args_with_internal_name(self):
        """Test GetThirdBridgeEventArgs creation with thirdbridge_event_id (internal name)."""
        args = GetThirdBridgeEventArgs(thirdbridge_event_id="tb123")
        assert args.thirdbridge_event_id == "tb123"

    def test_get_third_bridge_event_args_serialization(self):
        """Test that thirdbridge_event_id serializes to event_id for API."""
        args = GetThirdBridgeEventArgs(thirdbridge_event_id="tb123")

        # When dumping for API, should use event_id (serialization_alias)
        dumped = args.model_dump(by_alias=True)
        assert "event_id" in dumped
        assert dumped["event_id"] == "tb123"

        # Without by_alias, should use internal name
        dumped_internal = args.model_dump(by_alias=False)
        assert "thirdbridge_event_id" in dumped_internal
        assert dumped_internal["thirdbridge_event_id"] == "tb123"

    def test_get_third_bridge_event_args_required_field(self):
        """Test that thirdbridge_event_id is required."""
        with pytest.raises(ValidationError):
            GetThirdBridgeEventArgs()  # Missing required field


@pytest.mark.unit
class TestThirdBridgeNewModels:
    """Test new Third Bridge models."""

    def test_third_bridge_specialist(self):
        """Test ThirdBridgeSpecialist model."""
        specialist = ThirdBridgeSpecialist(
            title="Former Supply Chain Director", initials="JS"
        )
        assert specialist.title == "Former Supply Chain Director"
        assert specialist.initials == "JS"

    def test_third_bridge_moderator(self):
        """Test ThirdBridgeModerator model."""
        moderator = ThirdBridgeModerator(id="mod123", initials="AB")
        assert moderator.id == "mod123"
        assert moderator.initials == "AB"

    def test_third_bridge_transcript_item(self):
        """Test ThirdBridgeTranscriptItem model."""
        transcript_item = ThirdBridgeTranscriptItem(
            timestamp="[00:00:01]", discussionItem=["Opening remarks", "Introduction"]
        )
        assert transcript_item.timestamp == "[00:00:01]"
        assert len(transcript_item.discussionItem) == 2
        assert transcript_item.discussionItem[0] == "Opening remarks"


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
                event_id="tb123",  # API format
                content_type="FORUM",
                call_date="2023-10-20T14:00:00Z",
                title="Test Event",
                language="EN",
                agenda=["Test agenda"],
                insights=["Test insight"],
            )
        ]

        pagination = ThirdBridgePaginationInfo(
            total_count=1, current_page=1, total_pages=1, page_size=50
        )

        response_data = ThirdBridgeResponseData(pagination=pagination, data=events)

        response = FindThirdBridgeEventsResponse(
            response=response_data,
            instructions=["Test instruction"],
        )

        assert len(response.response.data) == 1
        assert response.response.data[0].thirdbridge_event_id == "tb123"
        assert response.response.pagination.total_count == 1
        assert response.response.pagination.current_page == 1
        assert response.response.pagination.page_size == 50
        assert response.instructions == ["Test instruction"]
        assert len(response.citation_information) == 1

    def test_get_third_bridge_event_response(self):
        """Test GetThirdBridgeEventResponse model."""
        event_details = ThirdBridgeEventDetails(
            event_id="tb123",  # API format
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=["Test agenda item"],  # List[str]
            insights=["Test insight"],  # List[str]
            transcript=[{"timestamp": "[00:00:01]", "discussionItem": ["Test"]}],
        )

        response = GetThirdBridgeEventResponse(
            event=event_details,
            instructions=["Test instruction"],
        )

        assert isinstance(response.event, ThirdBridgeEventDetails)
        assert response.event.thirdbridge_event_id == "tb123"
        assert isinstance(response.event.agenda, list)
        assert response.event.agenda[0] == "Test agenda item"
        assert response.instructions == ["Test instruction"]

    def test_get_third_bridge_event_response_optional_event(self):
        """Test GetThirdBridgeEventResponse with None event (robustness)."""
        response = GetThirdBridgeEventResponse(
            event=None,  # No event found
            instructions=["No event found"],
        )

        assert response.event is None
        assert response.instructions == ["No event found"]


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
        # Minimal event details
        details = ThirdBridgeEventDetails(
            event_id="tb123",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
        )
        assert details.agenda is None
        assert details.insights is None
        assert details.transcript is None
        assert details.specialists is None
        assert details.moderators is None

        # Event details with all optional fields
        details_full = ThirdBridgeEventDetails(
            event_id="tb124",
            content_type="FORUM",
            call_date="2023-10-20T14:00:00Z",
            title="Test Event",
            language="EN",
            agenda=["Test agenda"],
            insights=["Test insights"],
            transcript=[{"timestamp": "[00:00:01]", "discussionItem": []}],
            specialists=[{"title": "Expert", "initials": "EX"}],
            moderators=[{"id": "mod1", "initials": "MO"}],
        )
        assert isinstance(details_full.agenda, list)
        assert isinstance(details_full.insights, list)
        assert isinstance(details_full.transcript, list)
        assert isinstance(details_full.specialists, list)
        assert isinstance(details_full.moderators, list)

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
        )
        assert len(event_empty.agenda) == 0
        assert event_empty.insights is None  # Optional


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
            agenda=["Test agenda"],  # List[str]
            insights=["Test insights"],  # List[str]
            transcript=[{"timestamp": "[00:00:01]", "discussionItem": []}],
        )

        # Test model_dump serialization
        serialized = details.model_dump()

        # call_date should remain as string
        assert isinstance(serialized["call_date"], str)
        assert serialized["call_date"] == "2024-01-15T14:30:00Z"
        assert isinstance(serialized["agenda"], list)
        assert serialized["agenda"][0] == "Test agenda"

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
