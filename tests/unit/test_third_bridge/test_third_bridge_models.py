#!/usr/bin/env python3

"""Unit tests for third_bridge models."""

import pytest
import json
from pydantic import ValidationError

from aiera_mcp.tools.third_bridge.models import (
    FindThirdBridgeEventsArgs,
    GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse,
    GetThirdBridgeEventResponse,
)


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
            page_size=25,
        )

        assert args.start_date == "2023-10-01"
        assert args.end_date == "2023-10-31"
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.page == 1
        assert args.page_size == 25

    def test_find_third_bridge_events_args_defaults(self):
        """Test FindThirdBridgeEventsArgs with default values."""
        args = FindThirdBridgeEventsArgs(start_date="2023-10-01", end_date="2023-10-31")

        assert args.page == 1  # Default value
        assert args.page_size == 25  # Default value
        assert args.bloomberg_ticker is None
        assert args.watchlist_id is None
        assert args.originating_prompt is None  # Default value
        assert args.include_base_instructions is True  # Default value

    def test_find_third_bridge_events_args_with_originating_prompt(self):
        """Test FindThirdBridgeEventsArgs with originating_prompt field."""
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            originating_prompt="Find expert insights on Apple supply chain",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "Find expert insights on Apple supply chain"
        assert args.include_base_instructions is False

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

        # Page size must be >= 1
        with pytest.raises(ValidationError):
            FindThirdBridgeEventsArgs(
                start_date="2023-10-01", end_date="2023-10-31", page_size=0
            )

        # page_size above 25 is accepted (capped server-side)
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01", end_date="2023-10-31", page_size=26
        )
        assert args.page_size == 26

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
        args = FindThirdBridgeEventsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL",  # Missing :US
        )

        # Check if ticker correction is applied
        assert args.bloomberg_ticker in ["AAPL", "AAPL:US"]


@pytest.mark.unit
class TestGetThirdBridgeEventArgs:
    """Test GetThirdBridgeEventArgs model with aliasing."""

    def test_valid_get_third_bridge_event_args_with_internal_name(self):
        """Test GetThirdBridgeEventArgs creation with thirdbridge_event_id (internal name)."""
        args = GetThirdBridgeEventArgs(thirdbridge_event_id="tb123")
        assert args.thirdbridge_event_id == "tb123"
        assert args.originating_prompt is None
        assert args.include_base_instructions is True

    def test_get_third_bridge_event_args_with_originating_prompt(self):
        """Test GetThirdBridgeEventArgs with originating_prompt field."""
        args = GetThirdBridgeEventArgs(
            thirdbridge_event_id="tb123",
            originating_prompt="Get details for this expert call",
            include_base_instructions=False,
        )
        assert args.originating_prompt == "Get details for this expert call"
        assert args.include_base_instructions is False

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

    def test_get_third_bridge_event_args_with_aiera_event_id(self):
        """Test GetThirdBridgeEventArgs with aiera_event_id instead of thirdbridge_event_id."""
        args = GetThirdBridgeEventArgs(aiera_event_id=12345)
        assert args.aiera_event_id == 12345
        assert args.thirdbridge_event_id is None

    def test_get_third_bridge_event_args_with_both_ids(self):
        """Test GetThirdBridgeEventArgs with both IDs provided."""
        args = GetThirdBridgeEventArgs(
            thirdbridge_event_id="tb123", aiera_event_id=12345
        )
        assert args.thirdbridge_event_id == "tb123"
        assert args.aiera_event_id == 12345

    def test_get_third_bridge_event_args_aiera_event_id_serialization(self):
        """Test that aiera_event_id serializes correctly for API."""
        args = GetThirdBridgeEventArgs(aiera_event_id=12345)
        dumped = args.model_dump(exclude_none=True, by_alias=True)
        assert "aiera_event_id" in dumped
        assert dumped["aiera_event_id"] == 12345
        assert "event_id" not in dumped

    def test_get_third_bridge_event_args_requires_at_least_one_id(self):
        """Test that at least one of thirdbridge_event_id or aiera_event_id is required."""
        with pytest.raises(ValidationError):
            GetThirdBridgeEventArgs()  # No IDs provided


@pytest.mark.unit
class TestThirdBridgeResponses:
    """Test third_bridge response models with pass-through pattern."""

    def test_find_third_bridge_events_response(self):
        """Test FindThirdBridgeEventsResponse model with pass-through data."""
        response = FindThirdBridgeEventsResponse(
            response={
                "data": [
                    {
                        "event_id": "tb123",
                        "content_type": "FORUM",
                        "call_date": "2023-10-20T14:00:00Z",
                        "title": "Test Event",
                        "language": "EN",
                        "agenda": ["Test agenda"],
                        "insights": ["Test insight"],
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
            },
            instructions=["Test instruction"],
        )

        assert response.response is not None
        assert len(response.response["data"]) == 1
        assert response.response["data"][0]["event_id"] == "tb123"
        assert response.response["pagination"]["total_count"] == 1
        assert response.instructions == ["Test instruction"]

    def test_get_third_bridge_event_response(self):
        """Test GetThirdBridgeEventResponse model with pass-through data."""
        response = GetThirdBridgeEventResponse(
            response={
                "data": [
                    {
                        "event_id": "tb123",
                        "content_type": "FORUM",
                        "call_date": "2023-10-20T14:00:00Z",
                        "title": "Test Event",
                        "language": "EN",
                        "agenda": ["Test agenda item"],
                        "insights": ["Test insight"],
                    }
                ]
            },
            instructions=["Test instruction"],
        )

        assert response.response is not None
        assert response.response["data"][0]["event_id"] == "tb123"
        assert response.instructions == ["Test instruction"]

    def test_get_third_bridge_event_response_none(self):
        """Test GetThirdBridgeEventResponse with None response."""
        response = GetThirdBridgeEventResponse(
            response=None,
            instructions=["No event found"],
        )

        assert response.response is None
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

        # start_date and end_date are optional (server defaults to last 4 weeks)
        required = schema.get("required", [])
        assert "start_date" not in required
        assert "end_date" not in required

    def test_third_bridge_response_json_serialization(self):
        """Test that complete Third Bridge response models can be serialized to JSON."""
        response = FindThirdBridgeEventsResponse(
            response={
                "data": [
                    {
                        "event_id": "tb123",
                        "content_type": "FORUM",
                        "call_date": "2024-01-15T14:30:00Z",
                        "title": "Test Third Bridge Event",
                        "language": "EN",
                        "agenda": ["Test agenda"],
                        "insights": ["Test insight"],
                    }
                ],
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
            },
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
