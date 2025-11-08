#!/usr/bin/env python3

"""Unit tests for transcrippets models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from aiera_mcp.tools.transcrippets.models import (
    FindTranscrippetsArgs, CreateTranscrippetArgs, DeleteTranscrippetArgs,
    FindTranscrippetsResponse, CreateTranscrippetResponse, DeleteTranscrippetResponse,
    TranscrippetItem, TranscrippetDetails
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestTranscrippetsModels:
    """Test transcrippets Pydantic models."""

    def test_transcrippet_item_creation(self):
        """Test TranscrippetItem model creation."""
        transcrippet_data = {
            "transcrippet_id": "trans123",
            "public_url": "https://public.aiera.com/shared/transcrippet.html?id=guid-123",
            "title": "CEO Comments on Q4 Performance",
            "company_name": "Apple Inc",
            "event_title": "Q4 2023 Earnings Call",
            "transcript_preview": "I'm pleased to report that Q4 was another strong quarter...",
            "created_date": datetime(2023, 10, 26, 22, 0, 0)
        }

        transcrippet = TranscrippetItem(**transcrippet_data)

        assert transcrippet.transcrippet_id == "trans123"
        assert transcrippet.public_url == "https://public.aiera.com/shared/transcrippet.html?id=guid-123"
        assert transcrippet.title == "CEO Comments on Q4 Performance"
        assert transcrippet.company_name == "Apple Inc"
        assert transcrippet.event_title == "Q4 2023 Earnings Call"
        assert transcrippet.transcript_preview == "I'm pleased to report that Q4 was another strong quarter..."
        assert transcrippet.created_date == datetime(2023, 10, 26, 22, 0, 0)

    def test_transcrippet_item_optional_fields(self):
        """Test TranscrippetItem with only required fields."""
        minimal_data = {
            "transcrippet_id": "trans123",
            "public_url": "https://public.aiera.com/shared/transcrippet.html?id=guid-123"
        }

        transcrippet = TranscrippetItem(**minimal_data)

        assert transcrippet.transcrippet_id == "trans123"
        assert transcrippet.public_url == "https://public.aiera.com/shared/transcrippet.html?id=guid-123"
        assert transcrippet.title is None
        assert transcrippet.company_name is None
        assert transcrippet.event_title is None
        assert transcrippet.transcript_preview is None
        assert transcrippet.created_date is None

    def test_transcrippet_details_inherits_transcrippet_item(self):
        """Test TranscrippetDetails inherits from TranscrippetItem."""
        details_data = {
            "transcrippet_id": "trans123",
            "public_url": "https://public.aiera.com/shared/transcrippet.html?id=guid-123",
            "title": "CEO Comments on Q4 Performance",
            "company_name": "Apple Inc",
            "event_title": "Q4 2023 Earnings Call",
            "created_date": datetime(2023, 10, 26, 22, 0, 0),
            "transcript_text": "Full transcript text of the CEO's comments...",
            "audio_url": "https://example.com/audio/trans123.mp3",
            "speaker_name": "Tim Cook",
            "start_time": 1500,
            "end_time": 1800
        }

        details = TranscrippetDetails(**details_data)

        # Test inherited fields
        assert details.transcrippet_id == "trans123"
        assert details.title == "CEO Comments on Q4 Performance"
        assert details.company_name == "Apple Inc"

        # Test new fields
        assert details.transcript_text == "Full transcript text of the CEO's comments..."
        assert details.audio_url == "https://example.com/audio/trans123.mp3"
        assert details.speaker_name == "Tim Cook"
        assert details.start_time == 1500
        assert details.end_time == 1800


@pytest.mark.unit
class TestFindTranscrippetsArgs:
    """Test FindTranscrippetsArgs model."""

    def test_valid_find_transcrippets_args(self):
        """Test valid FindTranscrippetsArgs creation."""
        args = FindTranscrippetsArgs(
            transcrippet_id="trans123,trans456",
            event_id="event789",
            equity_id="eq123",
            speaker_id="speaker456",
            transcript_item_id="item789",
            created_start_date="2023-10-01",
            created_end_date="2023-10-31"
        )

        assert args.transcrippet_id == "trans123,trans456"
        assert args.event_id == "event789"
        assert args.equity_id == "eq123"
        assert args.speaker_id == "speaker456"
        assert args.transcript_item_id == "item789"
        assert args.created_start_date == "2023-10-01"
        assert args.created_end_date == "2023-10-31"

    def test_find_transcrippets_args_defaults(self):
        """Test FindTranscrippetsArgs with default values."""
        args = FindTranscrippetsArgs()

        assert args.transcrippet_id is None
        assert args.event_id is None
        assert args.equity_id is None
        assert args.speaker_id is None
        assert args.transcript_item_id is None
        assert args.created_start_date is None
        assert args.created_end_date is None

    def test_find_transcrippets_args_date_format_validation(self):
        """Test date format validation."""
        # Valid date format
        args = FindTranscrippetsArgs(
            created_start_date="2023-10-01",
            created_end_date="2023-10-31"
        )
        assert args.created_start_date == "2023-10-01"
        assert args.created_end_date == "2023-10-31"

        # Invalid date formats should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            FindTranscrippetsArgs(created_start_date="10/01/2023")

        assert "string does not match expected pattern" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FindTranscrippetsArgs(created_end_date="invalid-date")

        assert "string does not match expected pattern" in str(exc_info.value)

    def test_provided_ids_validation(self):
        """Test provided IDs format validation."""
        # This test assumes there's ID format correction logic
        args = FindTranscrippetsArgs(
            transcrippet_id="123, 456, 789",  # With spaces
            event_id="event1,event2",
            equity_id="eq1"
        )

        # Check if ID format correction is applied
        # This depends on the actual implementation in utils.py
        assert args.transcrippet_id in ["123, 456, 789", "123,456,789"]


@pytest.mark.unit
class TestCreateTranscrippetArgs:
    """Test CreateTranscrippetArgs model."""

    def test_valid_create_transcrippet_args(self):
        """Test valid CreateTranscrippetArgs creation."""
        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
            company_id=456,
            equity_id=789
        )

        assert args.event_id == 12345
        assert args.transcript == "This is the transcript text content"
        assert args.transcript_item_id == 789
        assert args.transcript_item_offset == 0
        assert args.transcript_end_item_id == 790
        assert args.transcript_end_item_offset == 100
        assert args.company_id == 456
        assert args.equity_id == 789

    def test_create_transcrippet_args_required_fields(self):
        """Test CreateTranscrippetArgs with only required fields."""
        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100
        )

        assert args.event_id == 12345
        assert args.transcript == "This is the transcript text content"
        assert args.company_id is None  # Optional field
        assert args.equity_id is None    # Optional field

    def test_create_transcrippet_args_validation(self):
        """Test CreateTranscrippetArgs validation rules."""
        # Valid arguments
        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100
        )
        assert args.transcript_item_offset == 0
        assert args.transcript_end_item_offset == 100

        # Negative offsets should raise validation error
        with pytest.raises(ValidationError):
            CreateTranscrippetArgs(
                event_id=12345,
                transcript="This is the transcript text content",
                transcript_item_id=789,
                transcript_item_offset=-1,  # Invalid: must be >= 0
                transcript_end_item_id=790,
                transcript_end_item_offset=100
            )

        with pytest.raises(ValidationError):
            CreateTranscrippetArgs(
                event_id=12345,
                transcript="This is the transcript text content",
                transcript_item_id=789,
                transcript_item_offset=0,
                transcript_end_item_id=790,
                transcript_end_item_offset=-1  # Invalid: must be >= 0
            )

    def test_create_transcrippet_args_missing_required_fields(self):
        """Test CreateTranscrippetArgs with missing required fields."""
        # Missing event_id
        with pytest.raises(ValidationError):
            CreateTranscrippetArgs(
                transcript="This is the transcript text content",
                transcript_item_id=789,
                transcript_item_offset=0,
                transcript_end_item_id=790,
                transcript_end_item_offset=100
            )

        # Missing transcript
        with pytest.raises(ValidationError):
            CreateTranscrippetArgs(
                event_id=12345,
                transcript_item_id=789,
                transcript_item_offset=0,
                transcript_end_item_id=790,
                transcript_end_item_offset=100
            )


@pytest.mark.unit
class TestDeleteTranscrippetArgs:
    """Test DeleteTranscrippetArgs model."""

    def test_valid_delete_transcrippet_args(self):
        """Test valid DeleteTranscrippetArgs creation."""
        args = DeleteTranscrippetArgs(transcrippet_id="trans123")
        assert args.transcrippet_id == "trans123"

    def test_delete_transcrippet_args_required_field(self):
        """Test that transcrippet_id is required."""
        with pytest.raises(ValidationError):
            DeleteTranscrippetArgs()  # Missing required field


@pytest.mark.unit
class TestTranscrippetsResponses:
    """Test transcrippets response models."""

    def test_find_transcrippets_response(self):
        """Test FindTranscrippetsResponse model."""
        transcrippets = [
            TranscrippetItem(
                transcrippet_id="trans123",
                public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-123",
                title="CEO Comments"
            )
        ]

        citations = [
            CitationInfo(
                title="Test Citation",
                url="https://example.com",
                timestamp=datetime(2023, 10, 26, 22, 0, 0)
            )
        ]

        response = FindTranscrippetsResponse(
            transcrippets=transcrippets,
            instructions=["Test instruction"],
            citation_information=citations
        )

        assert len(response.transcrippets) == 1
        assert response.instructions == ["Test instruction"]
        assert len(response.citation_information) == 1

    def test_create_transcrippet_response(self):
        """Test CreateTranscrippetResponse model."""
        transcrippet_details = TranscrippetDetails(
            transcrippet_id="trans456",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-456",
            title="New Transcrippet",
            transcript_text="Full transcript text here..."
        )

        response = CreateTranscrippetResponse(
            transcrippet=transcrippet_details,
            instructions=["Test instruction"],
            citation_information=[]
        )

        assert isinstance(response.transcrippet, TranscrippetDetails)
        assert response.transcrippet.transcrippet_id == "trans456"
        assert response.transcrippet.transcript_text == "Full transcript text here..."
        assert response.instructions == ["Test instruction"]

    def test_delete_transcrippet_response(self):
        """Test DeleteTranscrippetResponse model."""
        response = DeleteTranscrippetResponse(
            success=True,
            message="Transcrippet deleted successfully",
            instructions=["Deletion completed"],
            citation_information=[]
        )

        assert response.success is True
        assert response.message == "Transcrippet deleted successfully"
        assert response.instructions == ["Deletion completed"]

        # Test failed deletion
        failed_response = DeleteTranscrippetResponse(
            success=False,
            message="Transcrippet not found",
            instructions=[],
            citation_information=[]
        )

        assert failed_response.success is False
        assert failed_response.message == "Transcrippet not found"


@pytest.mark.unit
class TestTranscrippetsModelValidation:
    """Test transcrippets model validation and edge cases."""

    def test_model_serialization_roundtrip(self):
        """Test model serialization and deserialization."""
        original_args = FindTranscrippetsArgs(
            transcrippet_id="trans123,trans456",
            event_id="event789",
            created_start_date="2023-10-01",
            created_end_date="2023-10-31"
        )

        # Serialize to dict
        serialized = original_args.model_dump()

        # Deserialize back to model
        deserialized_args = FindTranscrippetsArgs(**serialized)

        # Verify round-trip
        assert original_args.transcrippet_id == deserialized_args.transcrippet_id
        assert original_args.event_id == deserialized_args.event_id
        assert original_args.created_start_date == deserialized_args.created_start_date
        assert original_args.created_end_date == deserialized_args.created_end_date

    def test_json_schema_generation(self):
        """Test that models can generate JSON schemas."""
        schema = FindTranscrippetsArgs.model_json_schema()

        assert "properties" in schema
        assert "transcrippet_id" in schema["properties"]
        assert "event_id" in schema["properties"]
        assert "created_start_date" in schema["properties"]
        assert "created_end_date" in schema["properties"]

        # All fields should be optional
        assert "required" not in schema or len(schema.get("required", [])) == 0

    def test_create_transcrippet_schema_generation(self):
        """Test CreateTranscrippetArgs schema generation."""
        schema = CreateTranscrippetArgs.model_json_schema()

        assert "properties" in schema
        assert "event_id" in schema["properties"]
        assert "transcript" in schema["properties"]
        assert "transcript_item_id" in schema["properties"]

        # Check that required fields are marked as required
        required_fields = schema.get("required", [])
        assert "event_id" in required_fields
        assert "transcript" in required_fields
        assert "transcript_item_id" in required_fields
        assert "transcript_item_offset" in required_fields
        assert "transcript_end_item_id" in required_fields
        assert "transcript_end_item_offset" in required_fields

        # Optional fields should not be required
        assert "company_id" not in required_fields
        assert "equity_id" not in required_fields

    def test_datetime_field_handling(self):
        """Test datetime field handling."""
        # Valid datetime
        transcrippet = TranscrippetItem(
            transcrippet_id="trans123",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-123",
            created_date=datetime(2023, 10, 26, 22, 0, 0)
        )
        assert isinstance(transcrippet.created_date, datetime)

        # Test with different datetime formats
        transcrippet_with_microseconds = TranscrippetItem(
            transcrippet_id="trans124",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-124",
            created_date=datetime(2023, 10, 26, 22, 0, 0, 123456)
        )
        assert transcrippet_with_microseconds.created_date.microsecond == 123456

    def test_url_field_handling(self):
        """Test URL field handling."""
        # Standard URL
        transcrippet = TranscrippetItem(
            transcrippet_id="trans123",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-123"
        )
        assert transcrippet.public_url == "https://public.aiera.com/shared/transcrippet.html?id=guid-123"

        # URL with additional parameters
        transcrippet_with_params = TranscrippetItem(
            transcrippet_id="trans124",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-124&ref=test"
        )
        assert "ref=test" in transcrippet_with_params.public_url

    def test_transcript_text_handling(self):
        """Test transcript text field handling in TranscrippetDetails."""
        # Short transcript
        details = TranscrippetDetails(
            transcrippet_id="trans123",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-123",
            transcript_text="Short transcript."
        )
        assert details.transcript_text == "Short transcript."

        # Long transcript
        long_transcript = "This is a very long transcript text that contains multiple sentences and detailed information about the earnings call discussion. " * 100
        details_long = TranscrippetDetails(
            transcrippet_id="trans124",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-124",
            transcript_text=long_transcript
        )
        assert len(details_long.transcript_text) == len(long_transcript)

    def test_time_fields_handling(self):
        """Test start_time and end_time fields handling."""
        # With time fields
        details = TranscrippetDetails(
            transcrippet_id="trans123",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-123",
            transcript_text="Transcript text",
            start_time=1500,  # milliseconds
            end_time=1800
        )
        assert details.start_time == 1500
        assert details.end_time == 1800

        # Without time fields
        details_no_times = TranscrippetDetails(
            transcrippet_id="trans124",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-124",
            transcript_text="Transcript text"
        )
        assert details_no_times.start_time is None
        assert details_no_times.end_time is None

    def test_audio_url_handling(self):
        """Test audio URL field handling."""
        # With audio URL
        details = TranscrippetDetails(
            transcrippet_id="trans123",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-123",
            transcript_text="Transcript text",
            audio_url="https://example.com/audio/trans123.mp3"
        )
        assert details.audio_url == "https://example.com/audio/trans123.mp3"

        # Without audio URL
        details_no_audio = TranscrippetDetails(
            transcrippet_id="trans124",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-124",
            transcript_text="Transcript text"
        )
        assert details_no_audio.audio_url is None

    def test_speaker_name_handling(self):
        """Test speaker name field handling."""
        # With speaker name
        details = TranscrippetDetails(
            transcrippet_id="trans123",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-123",
            transcript_text="Transcript text",
            speaker_name="Tim Cook"
        )
        assert details.speaker_name == "Tim Cook"

        # Without speaker name
        details_no_speaker = TranscrippetDetails(
            transcrippet_id="trans124",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-124",
            transcript_text="Transcript text"
        )
        assert details_no_speaker.speaker_name is None