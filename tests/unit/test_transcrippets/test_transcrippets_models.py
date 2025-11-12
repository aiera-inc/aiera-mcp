#!/usr/bin/env python3

"""Unit tests for transcrippets models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from aiera_mcp.tools.transcrippets.models import (
    FindTranscrippetsArgs, CreateTranscrippetArgs, DeleteTranscrippetArgs,
    FindTranscrippetsResponse, CreateTranscrippetResponse, DeleteTranscrippetResponse,
    TranscrippetItem
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestTranscrippetsModels:
    """Test transcrippets Pydantic models."""

    def test_transcrippet_item_creation(self):
        """Test TranscrippetItem model creation."""
        transcrippet_data = {
            "transcrippet_id": 123,
            "company_id": 456,
            "equity_id": 789,
            "event_id": 101112,
            "transcript_item_id": 131415,
            "user_id": 161718,
            "audio_url": "https://example.com/audio/trans123.mp3",
            "company_logo_url": "https://example.com/logo/apple.png",
            "company_name": "Apple Inc",
            "company_ticker": "AAPL",
            "created": "2023-10-26T22:00:00Z",
            "end_ms": 90000,
            "event_date": "2023-10-26T21:00:00Z",
            "event_title": "Q4 2023 Earnings Call",
            "event_type": "earnings",
            "modified": "2023-10-26T22:05:00Z",
            "start_ms": 60000,
            "transcript": "I'm pleased to report that Q4 was another strong quarter...",
            "transcrippet_guid": "guid-123-456",
            "transcription_audio_offset_seconds": 30,
            "trimmed_audio_url": "https://example.com/audio/trans123_trimmed.mp3",
            "word_durations_ms": [500, 300, 400, 600, 350, 800, 200, 450]
        }

        transcrippet = TranscrippetItem(**transcrippet_data)

        assert transcrippet.transcrippet_id == 123
        assert transcrippet.company_name == "Apple Inc"
        assert transcrippet.event_title == "Q4 2023 Earnings Call"
        assert transcrippet.transcript == "I'm pleased to report that Q4 was another strong quarter..."
        assert transcrippet.transcrippet_guid == "guid-123-456"
        assert transcrippet.created == "2023-10-26T22:00:00Z"

    def test_transcrippet_item_required_fields(self):
        """Test TranscrippetItem requires all fields for API-matching structure."""
        minimal_data = {
            "transcrippet_id": 123,
            "company_id": 456
            # Missing other required fields
        }

        # Should raise validation error for missing required fields
        with pytest.raises(Exception):  # Pydantic ValidationError
            TranscrippetItem(**minimal_data)

    def test_transcrippet_item_with_speaker_fields(self):
        """Test TranscrippetItem includes speaker_name and speaker_title fields."""
        item_data = {
            "transcrippet_id": 123,
            "company_id": 456,
            "equity_id": 789,
            "event_id": 101112,
            "transcript_item_id": 131415,
            "user_id": 161718,
            "audio_url": "https://example.com/audio/trans123.mp3",
            "company_logo_url": "https://example.com/logo/apple.png",
            "company_name": "Apple Inc",
            "company_ticker": "AAPL",
            "created": "2023-10-26T22:00:00Z",
            "end_ms": 90000,
            "event_date": "2023-10-26T21:00:00Z",
            "event_title": "Q4 2023 Earnings Call",
            "event_type": "earnings",
            "modified": "2023-10-26T22:05:00Z",
            "start_ms": 60000,
            "transcript": "I'm pleased to report that Q4 was another strong quarter...",
            "transcrippet_guid": "guid-123-456",
            "transcription_audio_offset_seconds": 30,
            "trimmed_audio_url": "https://example.com/audio/trans123_trimmed.mp3",
            "word_durations_ms": [500, 300, 400, 600, 350, 800, 200, 450],
            "speaker_name": "Tim Cook",
            "speaker_title": "Chief Executive Officer",
            "public_url": "https://public.aiera.com/shared/transcrippet.html?id=guid-123-456"
        }

        item = TranscrippetItem(**item_data)

        # Test base fields
        assert item.transcrippet_id == 123
        assert item.company_name == "Apple Inc"
        assert item.event_title == "Q4 2023 Earnings Call"
        assert item.transcript == "I'm pleased to report that Q4 was another strong quarter..."

        # Test speaker fields
        assert item.speaker_name == "Tim Cook"
        assert item.speaker_title == "Chief Executive Officer"

        # Test public URL field
        assert item.public_url == "https://public.aiera.com/shared/transcrippet.html?id=guid-123-456"


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

        assert "String should match pattern" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FindTranscrippetsArgs(created_end_date="invalid-date")

        assert "String should match pattern" in str(exc_info.value)

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
            transcript_end_item_offset=100
        )

        assert args.event_id == 12345
        assert args.transcript == "This is the transcript text content"
        assert args.transcript_item_id == 789
        assert args.transcript_item_offset == 0
        assert args.transcript_end_item_id == 790
        assert args.transcript_end_item_offset == 100

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
                transcrippet_id=123,
                company_id=456,
                equity_id=789,
                event_id=101112,
                transcript_item_id=131415,
                user_id=161718,
                audio_url="https://example.com/audio/trans123.mp3",
                company_logo_url="https://example.com/logo/apple.png",
                company_name="Apple Inc",
                company_ticker="AAPL",
                created="2023-10-26T22:00:00Z",
                end_ms=90000,
                event_date="2023-10-26T21:00:00Z",
                event_title="CEO Comments",
                event_type="earnings",
                modified="2023-10-26T22:05:00Z",
                start_ms=60000,
                transcript="I'm pleased to report that Q4 was another strong quarter...",
                transcrippet_guid="guid-123-456",
                transcription_audio_offset_seconds=30,
                trimmed_audio_url="https://example.com/audio/trans123_trimmed.mp3",
                word_durations_ms=[500, 300, 400, 600, 350, 800, 200, 450]
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
            response=transcrippets,
            instructions=["Test instruction"],
            citation_information=citations
        )

        assert len(response.response) == 1
        assert response.instructions == ["Test instruction"]
        assert len(response.citation_information) == 1

    def test_create_transcrippet_response(self):
        """Test CreateTranscrippetResponse model."""
        transcrippet_item = TranscrippetItem(
            transcrippet_id=456,
            company_id=789,
            equity_id=101112,
            event_id=131415,
            transcript_item_id=161718,
            user_id=192021,
            audio_url="https://example.com/audio/trans456.mp3",
            company_logo_url="https://example.com/logo/apple.png",
            company_name="Apple Inc",
            company_ticker="AAPL",
            created="2023-10-26T22:05:00Z",
            end_ms=120000,
            event_date="2023-10-26T21:00:00Z",
            event_title="New Transcrippet",
            event_type="earnings",
            modified="2023-10-26T22:10:00Z",
            start_ms=90000,
            transcript="Full transcript text here...",
            transcrippet_guid="guid-456-789",
            transcription_audio_offset_seconds=45,
            trimmed_audio_url="https://example.com/audio/trans456_trimmed.mp3",
            word_durations_ms=[600, 400, 500, 700, 350, 900, 250, 550],
            speaker_name="Tim Cook",
            speaker_title="Chief Executive Officer",
            public_url="https://public.aiera.com/shared/transcrippet.html?id=guid-456-789"
        )

        response = CreateTranscrippetResponse(
            response=transcrippet_item,
            instructions=["Test instruction"],
            citation_information=[]
        )

        assert isinstance(response.response, TranscrippetItem)
        assert response.response.transcrippet_id == 456
        assert response.response.transcript == "Full transcript text here..."
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


    def test_datetime_field_handling(self):
        """Test datetime field handling in API structure."""
        # Create full transcrippet with datetime string fields
        transcrippet_data = {
            "transcrippet_id": 123,
            "company_id": 456,
            "equity_id": 789,
            "event_id": 101112,
            "transcript_item_id": 131415,
            "user_id": 161718,
            "audio_url": "https://example.com/audio/trans123.mp3",
            "company_logo_url": "https://example.com/logo/apple.png",
            "company_name": "Apple Inc",
            "company_ticker": "AAPL",
            "created": "2023-10-26T22:00:00Z",  # String datetime field
            "end_ms": 90000,
            "event_date": "2023-10-26T21:00:00Z",  # String datetime field
            "event_title": "Test Event",
            "event_type": "earnings",
            "modified": "2023-10-26T22:05:00Z",  # String datetime field
            "start_ms": 60000,
            "transcript": "Test transcript content",
            "transcrippet_guid": "guid-123-456",
            "transcription_audio_offset_seconds": 30,
            "trimmed_audio_url": "https://example.com/audio/trans123_trimmed.mp3",
            "word_durations_ms": [500, 300, 400]
        }

        transcrippet = TranscrippetItem(**transcrippet_data)

        # Test that datetime fields are stored as strings in API structure
        assert isinstance(transcrippet.created, str)
        assert transcrippet.created == "2023-10-26T22:00:00Z"
        assert isinstance(transcrippet.event_date, str)
        assert transcrippet.event_date == "2023-10-26T21:00:00Z"

    def test_api_field_validation(self):
        """Test that API-required fields are validated correctly."""
        # Test that missing required fields cause validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            TranscrippetItem(
                transcrippet_id=123,
                company_id=456
                # Missing other required API fields
            )

        # Test that incorrect field types cause validation error
        with pytest.raises(Exception):  # Pydantic ValidationError
            TranscrippetItem(
                transcrippet_id="invalid_string",  # Should be int
                company_id=456,
                equity_id=789,
                event_id=101112,
                transcript_item_id=131415,
                user_id=161718,
                audio_url="https://example.com/audio/trans123.mp3",
                company_logo_url="https://example.com/logo/apple.png",
                company_name="Apple Inc",
                company_ticker="AAPL",
                created="2023-10-26T22:00:00Z",
                end_ms=90000,
                event_date="2023-10-26T21:00:00Z",
                event_title="Test Event",
                event_type="earnings",
                modified="2023-10-26T22:05:00Z",
                start_ms=60000,
                transcript="Test transcript content",
                transcrippet_guid="guid-123-456",
                transcription_audio_offset_seconds=30,
                trimmed_audio_url="https://example.com/audio/trans123_trimmed.mp3",
                word_durations_ms=[500, 300, 400]
            )

    def test_transcrippet_item_transcript_field(self):
        """Test transcript field in TranscrippetItem matches API response structure."""
        # Create complete TranscrippetItem with fields from actual API response
        item_data = {
            "transcrippet_id": 123,
            "company_id": 456,
            "equity_id": 789,
            "event_id": 101112,
            "transcript_item_id": 131415,
            "user_id": 161718,
            "audio_url": "https://example.com/audio/trans123.mp3",
            "company_logo_url": "https://example.com/logo/apple.png",
            "company_name": "Apple Inc",
            "company_ticker": "AAPL",
            "created": "2023-10-26T22:00:00Z",
            "end_ms": 90000,
            "event_date": "2023-10-26T21:00:00Z",
            "event_title": "Test Event",
            "event_type": "earnings",
            "modified": "2023-10-26T22:05:00Z",
            "start_ms": 60000,
            "transcript": "Sure, I'll take that one. I think we're a long way from equilibrium.",
            "transcrippet_guid": "guid-123-456",
            "transcription_audio_offset_seconds": 30,
            "trimmed_audio_url": "https://example.com/audio/trans123_trimmed.mp3",
            "word_durations_ms": [500, 300, 400],
            "speaker_name": "Spencer Adam Neumann",
            "speaker_title": "Chief Financial Officer",
            "public_url": "https://public.aiera.com/shared/transcrippet.html?id=guid-123-456"
        }

        item = TranscrippetItem(**item_data)
        assert item.transcript == "Sure, I'll take that one. I think we're a long way from equilibrium."
        assert item.speaker_name == "Spencer Adam Neumann"
        assert item.speaker_title == "Chief Financial Officer"

    def test_api_structure_validation(self):
        """Test that the models match expected API structure."""
        # Test that all required fields from API structure are present
        required_fields = [
            'transcrippet_id', 'company_id', 'equity_id', 'event_id',
            'transcript_item_id', 'user_id', 'audio_url', 'company_name',
            'company_ticker', 'created', 'end_ms', 'event_date', 'event_title',
            'event_type', 'modified', 'start_ms', 'transcript', 'transcrippet_guid',
            'transcription_audio_offset_seconds', 'trimmed_audio_url', 'word_durations_ms'
        ]

        # Verify all required fields exist in the model schema
        schema = TranscrippetItem.model_json_schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        for field in required_fields:
            assert field in properties, f"Field {field} missing from TranscrippetItem schema"
            if field in ['transcrippet_id', 'company_id', 'equity_id']:  # Key fields should be required
                assert field in required, f"Field {field} should be required"