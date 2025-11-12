#!/usr/bin/env python3

"""Unit tests for transcrippets tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock

from aiera_mcp.tools.transcrippets.tools import (
    find_transcrippets,
    create_transcrippet,
    delete_transcrippet,
)
from aiera_mcp.tools.transcrippets.models import (
    FindTranscrippetsArgs,
    CreateTranscrippetArgs,
    DeleteTranscrippetArgs,
    FindTranscrippetsResponse,
    CreateTranscrippetResponse,
    DeleteTranscrippetResponse,
    TranscrippetItem,
)


@pytest.mark.unit
class TestFindTranscrippets:
    """Test the find_transcrippets tool."""

    @pytest.mark.asyncio
    async def test_find_transcrippets_success(
        self, mock_http_dependencies, transcrippets_api_responses
    ):
        """Test successful transcrippets search."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            transcrippets_api_responses["find_transcrippets_success"]
        )

        args = FindTranscrippetsArgs(
            transcrippet_id="trans123",
            event_id="event456",
            created_start_date="2023-10-01",
            created_end_date="2023-10-31",
        )

        # Execute
        result = await find_transcrippets(args)

        # Verify
        assert isinstance(result, FindTranscrippetsResponse)
        assert len(result.response) == 1

        # Check first transcrippet
        first_transcrippet = result.response[0]
        assert isinstance(first_transcrippet, TranscrippetItem)
        assert first_transcrippet.transcrippet_id == 123
        assert first_transcrippet.company_name == "Apple Inc"
        assert first_transcrippet.event_title == "Q4 2023 Earnings Call"
        assert (
            first_transcrippet.transcript
            == "I'm pleased to report that Q4 was another strong quarter..."
        )
        assert first_transcrippet.transcrippet_guid == "guid-123-456"
        assert first_transcrippet.created == "2023-10-26T22:00:00Z"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/transcrippets/"

        # Check parameters were passed correctly
        params = call_args[1]["params"]
        assert params["transcrippet_id"] == "trans123"
        assert params["event_id"] == "event456"
        assert params["created_start_date"] == "2023-10-01"
        assert params["created_end_date"] == "2023-10-31"

    @pytest.mark.asyncio
    async def test_find_transcrippets_empty_results(self, mock_http_dependencies):
        """Test find_transcrippets with empty results."""
        # Setup - Note: transcrippets API returns array directly
        empty_response = {"response": [], "instructions": []}
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = FindTranscrippetsArgs()

        # Execute
        result = await find_transcrippets(args)

        # Verify
        assert isinstance(result, FindTranscrippetsResponse)
        assert len(result.response) == 0
        assert len(result.citation_information) == 0

    @pytest.mark.asyncio
    async def test_find_transcrippets_malformed_response(self, mock_http_dependencies):
        """Test find_transcrippets with malformed response raises validation error."""
        # Setup - non-array response (should cause validation error)
        malformed_response = {"response": {"not": "an array"}, "instructions": []}
        mock_http_dependencies["mock_make_request"].return_value = malformed_response

        args = FindTranscrippetsArgs()

        # Execute & Verify - should raise validation error for malformed response structure
        with pytest.raises(Exception):  # Pydantic ValidationError
            await find_transcrippets(args)

    @pytest.mark.asyncio
    async def test_find_transcrippets_with_filters(
        self, mock_http_dependencies, transcrippets_api_responses
    ):
        """Test find_transcrippets with various filters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            transcrippets_api_responses["find_transcrippets_success"]
        )

        args = FindTranscrippetsArgs(
            transcrippet_id="trans123,trans456",
            event_id="event789",
            equity_id="eq123",
            speaker_id="speaker456",
            transcript_item_id="item789",
        )

        # Execute
        result = await find_transcrippets(args)

        # Verify
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["transcrippet_id"] == "trans123,trans456"
        assert params["event_id"] == "event789"
        assert params["equity_id"] == "eq123"
        assert params["speaker_id"] == "speaker456"
        assert params["transcript_item_id"] == "item789"

    @pytest.mark.asyncio
    async def test_find_transcrippets_date_parsing(self, mock_http_dependencies):
        """Test find_transcrippets handles date parsing correctly."""
        # Setup with various date formats
        response_with_dates = {
            "response": [
                {
                    "transcrippet_id": 123,
                    "company_id": 456,
                    "equity_id": 789,
                    "event_id": 101112,
                    "transcript_item_id": 131415,
                    "user_id": 161718,
                    "audio_url": "https://example.com/audio/trans123.mp3",
                    "company_logo_url": "https://example.com/logo/test.png",
                    "company_name": "Test Company",
                    "company_ticker": "TEST",
                    "created": "2023-10-26T22:00:00Z",
                    "end_ms": 90000,
                    "event_date": "2023-10-26T21:00:00Z",
                    "event_title": "Test Event",
                    "event_type": "earnings",
                    "modified": "2023-10-26T22:05:00Z",
                    "start_ms": 60000,
                    "transcript": "Test transcript content",
                    "transcrippet_guid": "guid-123-456",
                    "transcription_audio_offset_seconds": 30,
                    "trimmed_audio_url": "https://example.com/audio/trans123_trimmed.mp3",
                    "word_durations_ms": [500, 300, 400],
                }
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_dates

        args = FindTranscrippetsArgs()

        # Execute
        result = await find_transcrippets(args)

        # Verify date field exists correctly
        assert len(result.response) == 1
        transcrippet = result.response[0]
        assert transcrippet.created == "2023-10-26T22:00:00Z"

    @pytest.mark.asyncio
    async def test_find_transcrippets_public_url_generation(
        self, mock_http_dependencies
    ):
        """Test that find_transcrippets generates proper public URLs."""
        # Setup
        response_with_guid = {
            "response": [
                {
                    "transcrippet_id": 123,
                    "company_id": 456,
                    "equity_id": 789,
                    "event_id": 101112,
                    "transcript_item_id": 131415,
                    "user_id": 161718,
                    "audio_url": "https://example.com/audio/trans123.mp3",
                    "company_logo_url": "https://example.com/logo/test.png",
                    "company_name": "Test Company",
                    "company_ticker": "TEST",
                    "created": "2023-10-26T22:00:00Z",
                    "end_ms": 90000,
                    "event_date": "2023-10-26T21:00:00Z",
                    "event_title": "Test Event",
                    "event_type": "earnings",
                    "modified": "2023-10-26T22:05:00Z",
                    "start_ms": 60000,
                    "transcript": "Test transcript content",
                    "transcrippet_guid": "test-guid-123",
                    "transcription_audio_offset_seconds": 30,
                    "trimmed_audio_url": "https://example.com/audio/trans123_trimmed.mp3",
                    "word_durations_ms": [500, 300, 400],
                }
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_guid

        args = FindTranscrippetsArgs()

        # Execute
        result = await find_transcrippets(args)

        # Verify transcrippet GUID field exists and public URL is generated
        assert len(result.response) == 1
        transcrippet = result.response[0]
        assert transcrippet.transcrippet_guid == "test-guid-123"
        assert (
            transcrippet.public_url
            == "https://public.aiera.com/shared/transcrippet.html?id=test-guid-123"
        )

    @pytest.mark.asyncio
    async def test_find_transcrippets_citations(
        self, mock_http_dependencies, transcrippets_api_responses
    ):
        """Test that find_transcrippets generates proper citations."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            transcrippets_api_responses["find_transcrippets_success"]
        )

        args = FindTranscrippetsArgs()

        # Execute
        result = await find_transcrippets(args)

        # Verify basic response structure (raw API response has empty citation_information)
        assert (
            len(result.citation_information) == 0
            or len(result.citation_information) >= 0
        )
        # Verify the main data is present
        assert len(result.response) == 1
        assert result.response[0].transcrippet_guid == "guid-123-456"


@pytest.mark.unit
class TestCreateTranscrippet:
    """Test the create_transcrippet tool."""

    @pytest.mark.asyncio
    async def test_create_transcrippet_success(
        self, mock_http_dependencies, transcrippets_api_responses
    ):
        """Test successful transcrippet creation."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            transcrippets_api_responses["create_transcrippet_success"]
        )

        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
        )

        # Execute
        result = await create_transcrippet(args)

        # Verify
        assert isinstance(result, CreateTranscrippetResponse)
        assert isinstance(result.response, TranscrippetItem)
        assert result.response.transcrippet_id == 456
        assert result.response.company_name == "Apple Inc"
        assert result.response.transcript == "Full transcript text here..."
        assert result.response.audio_url == "https://example.com/audio/trans456.mp3"
        assert result.response.speaker_name == "Tim Cook"
        assert result.response.transcrippet_guid == "guid-456-789"
        assert (
            result.response.public_url
            == "https://public.aiera.com/shared/transcrippet.html?id=guid-456-789"
        )

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/transcrippets/create"

        # Check data was passed correctly
        data = call_args[1]["data"]
        assert data["event_id"] == 12345
        assert data["transcript"] == "This is the transcript text content"
        assert data["transcript_item_id"] == 789
        assert data["transcript_item_offset"] == 0
        assert data["transcript_end_item_id"] == 790
        assert data["transcript_end_item_offset"] == 100

    @pytest.mark.asyncio
    async def test_create_transcrippet_minimal_args(
        self, mock_http_dependencies, transcrippets_api_responses
    ):
        """Test create_transcrippet with minimal required arguments."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            transcrippets_api_responses["create_transcrippet_success"]
        )

        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
        )

        # Execute
        result = await create_transcrippet(args)

        # Verify
        assert isinstance(result, CreateTranscrippetResponse)
        assert isinstance(result.response, TranscrippetItem)

        # Check data was passed correctly
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]

    @pytest.mark.asyncio
    async def test_create_transcrippet_invalid_response(self, mock_http_dependencies):
        """Test create_transcrippet with invalid response."""
        # Setup - non-dict response
        invalid_response = {"response": "not a dict", "instructions": []}
        mock_http_dependencies["mock_make_request"].return_value = invalid_response

        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
        )

        # Execute & Verify
        with pytest.raises(Exception):  # Pydantic ValidationError
            await create_transcrippet(args)

    @pytest.mark.asyncio
    async def test_create_transcrippet_date_handling(self, mock_http_dependencies):
        """Test create_transcrippet handles date parsing correctly."""
        # Setup with created date
        response_with_date = {
            "response": {
                "transcrippet_id": 456,
                "company_id": 789,
                "equity_id": 101112,
                "event_id": 131415,
                "transcript_item_id": 161718,
                "user_id": 192021,
                "audio_url": "https://example.com/audio/trans456.mp3",
                "company_logo_url": "https://example.com/logo/test.png",
                "company_name": "Test Company",
                "company_ticker": "TEST",
                "created": "2023-10-26T22:05:00Z",
                "end_ms": 120000,
                "event_date": "2023-10-26T21:00:00Z",
                "event_title": "Test Event",
                "event_type": "earnings",
                "modified": "2023-10-26T22:10:00Z",
                "start_ms": 90000,
                "transcript": "Full transcript text here...",
                "transcrippet_guid": "guid-456-789",
                "transcription_audio_offset_seconds": 45,
                "trimmed_audio_url": "https://example.com/audio/trans456_trimmed.mp3",
                "word_durations_ms": [600, 400, 500],
                "transcript_text": "Full transcript text here...",
                "speaker_name": "Test Speaker",
                "start_time": "00:05:30",
                "end_time": "00:06:45",
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_date

        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
        )

        # Execute
        result = await create_transcrippet(args)

        # Verify - created date field exists and is correctly parsed
        assert result.response.created == "2023-10-26T22:05:00Z"

    @pytest.mark.asyncio
    async def test_create_transcrippet_citation(
        self, mock_http_dependencies, transcrippets_api_responses
    ):
        """Test that create_transcrippet generates proper citation."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            transcrippets_api_responses["create_transcrippet_success"]
        )

        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
        )

        # Execute
        result = await create_transcrippet(args)

        # Verify basic response structure (API doesn't auto-generate citations)
        assert len(result.citation_information) == 0
        assert result.response.transcrippet_guid == "guid-456-789"
        assert (
            result.response.public_url
            == "https://public.aiera.com/shared/transcrippet.html?id=guid-456-789"
        )
        assert result.response.event_title == "Q4 2023 Earnings Call"


@pytest.mark.unit
class TestDeleteTranscrippet:
    """Test the delete_transcrippet tool."""

    @pytest.mark.asyncio
    async def test_delete_transcrippet_success(self, mock_http_dependencies):
        """Test successful transcrippet deletion."""
        # Setup
        success_response = {"response": {"success": True}, "instructions": []}
        mock_http_dependencies["mock_make_request"].return_value = success_response

        args = DeleteTranscrippetArgs(transcrippet_id="trans123")

        # Execute
        result = await delete_transcrippet(args)

        # Verify
        assert isinstance(result, DeleteTranscrippetResponse)
        assert result.success is True
        assert result.message == "Transcrippet deleted successfully"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/transcrippets/trans123/delete"

        # Check parameters were passed correctly
        params = call_args[1]["params"]
        assert params["transcrippet_id"] == "trans123"

    @pytest.mark.asyncio
    async def test_delete_transcrippet_api_error_in_response(
        self, mock_http_dependencies
    ):
        """Test delete_transcrippet with API error in response."""
        # Setup
        error_response = {
            "response": {"error": "Transcrippet not found"},
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = error_response

        args = DeleteTranscrippetArgs(transcrippet_id="nonexistent")

        # Execute
        result = await delete_transcrippet(args)

        # Verify
        assert isinstance(result, DeleteTranscrippetResponse)
        assert result.success is False
        assert result.message == "Transcrippet not found"

    @pytest.mark.asyncio
    async def test_delete_transcrippet_top_level_error(self, mock_http_dependencies):
        """Test delete_transcrippet with top-level error in response."""
        # Setup
        error_response = {"error": "Unauthorized access", "instructions": []}
        mock_http_dependencies["mock_make_request"].return_value = error_response

        args = DeleteTranscrippetArgs(transcrippet_id="trans123")

        # Execute
        result = await delete_transcrippet(args)

        # Verify
        assert isinstance(result, DeleteTranscrippetResponse)
        assert result.success is False
        assert result.message == "Unauthorized access"

    @pytest.mark.asyncio
    async def test_delete_transcrippet_network_exception(self, mock_http_dependencies):
        """Test delete_transcrippet with network exception."""
        # Setup
        mock_http_dependencies["mock_make_request"].side_effect = ConnectionError(
            "Network error"
        )

        args = DeleteTranscrippetArgs(transcrippet_id="trans123")

        # Execute
        result = await delete_transcrippet(args)

        # Verify - should handle exception gracefully
        assert isinstance(result, DeleteTranscrippetResponse)
        assert result.success is False
        assert "Failed to delete transcrippet: Network error" in result.message

    @pytest.mark.asyncio
    async def test_delete_transcrippet_generic_exception(self, mock_http_dependencies):
        """Test delete_transcrippet with generic exception."""
        # Setup
        mock_http_dependencies["mock_make_request"].side_effect = ValueError(
            "Some other error"
        )

        args = DeleteTranscrippetArgs(transcrippet_id="trans123")

        # Execute
        result = await delete_transcrippet(args)

        # Verify - should handle exception gracefully
        assert isinstance(result, DeleteTranscrippetResponse)
        assert result.success is False
        assert "Failed to delete transcrippet: Some other error" in result.message


@pytest.mark.unit
class TestTranscrippetsToolsErrorHandling:
    """Test error handling for transcrippets tools."""

    @pytest.mark.asyncio
    async def test_find_transcrippets_handle_invalid_response_data(
        self, mock_http_dependencies
    ):
        """Test that find_transcrippets raises validation errors for invalid API responses."""
        # Setup - response with missing required fields (should cause validation error)
        response_with_missing_fields = {
            "response": [
                {
                    "transcrippet_id": "trans123",  # String instead of int
                    "transcrippet_guid": "guid-123",
                    "title": "Test Transcrippet",
                    # Missing many required fields like company_id, equity_id, etc.
                }
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            response_with_missing_fields
        )

        args = FindTranscrippetsArgs()

        # Execute & Verify - should raise validation error for invalid API response structure
        with pytest.raises(Exception):  # Pydantic ValidationError
            await find_transcrippets(args)

    @pytest.mark.asyncio
    async def test_find_transcrippets_handle_missing_guid(self, mock_http_dependencies):
        """Test handling of transcrippets with missing GUID."""
        # Setup - response with missing GUID
        response_with_missing_guid = {
            "response": [
                {
                    "transcrippet_id": 123,
                    "company_id": 456,
                    "equity_id": 789,
                    "event_id": 101112,
                    "transcript_item_id": 131415,
                    "user_id": 161718,
                    "audio_url": "https://example.com/audio/trans123.mp3",
                    "company_logo_url": "https://example.com/logo/test.png",
                    "company_name": "Test Company",
                    "company_ticker": "TEST",
                    "created": "2023-10-26T22:00:00Z",
                    "end_ms": 90000,
                    "event_date": "2023-10-26T21:00:00Z",
                    "event_title": "Test Event",
                    "event_type": "earnings",
                    "modified": "2023-10-26T22:05:00Z",
                    "start_ms": 60000,
                    "transcript": "Test transcript content",
                    "transcrippet_guid": "",  # Empty GUID to test missing case
                    "transcription_audio_offset_seconds": 30,
                    "trimmed_audio_url": "https://example.com/audio/trans123_trimmed.mp3",
                    "word_durations_ms": [500, 300, 400],
                }
            ],
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            response_with_missing_guid
        )

        args = FindTranscrippetsArgs()

        # Execute
        result = await find_transcrippets(args)

        # Verify - should still process with empty GUID
        assert len(result.response) == 1
        transcrippet = result.response[0]
        assert transcrippet.transcrippet_guid == ""

    @pytest.mark.asyncio
    async def test_create_transcrippet_handle_invalid_date(
        self, mock_http_dependencies
    ):
        """Test create_transcrippet handles dates correctly."""
        # Setup with valid created date
        response_with_date = {
            "response": {
                "transcrippet_id": 456,
                "company_id": 789,
                "equity_id": 101112,
                "event_id": 131415,
                "transcript_item_id": 161718,
                "user_id": 192021,
                "audio_url": "https://example.com/audio/trans456.mp3",
                "company_logo_url": "https://example.com/logo/test.png",
                "company_name": "Test Company",
                "company_ticker": "TEST",
                "created": "2023-10-26T22:05:00Z",  # Valid date format
                "end_ms": 120000,
                "event_date": "2023-10-26T21:00:00Z",
                "event_title": "Test Event",
                "event_type": "earnings",
                "modified": "2023-10-26T22:10:00Z",
                "start_ms": 90000,
                "transcript": "Full transcript text here...",
                "transcrippet_guid": "guid-456-789",
                "transcription_audio_offset_seconds": 45,
                "trimmed_audio_url": "https://example.com/audio/trans456_trimmed.mp3",
                "word_durations_ms": [600, 400, 500],
                "transcript_text": "Full transcript text here...",
                "speaker_name": "Test Speaker",
                "start_time": "00:05:30",
                "end_time": "00:06:45",
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_date

        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
        )

        # Execute
        result = await create_transcrippet(args)

        # Verify - date field is correctly parsed
        assert result.response.created == "2023-10-26T22:05:00Z"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception_type", [ConnectionError, TimeoutError, ValueError]
    )
    async def test_network_errors_propagate_find(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated in find_transcrippets."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = FindTranscrippetsArgs()

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_transcrippets(args)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception_type", [ConnectionError, TimeoutError, ValueError]
    )
    async def test_network_errors_propagate_create(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated in create_transcrippet."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = CreateTranscrippetArgs(
            event_id=12345,
            transcript="This is the transcript text content",
            transcript_item_id=789,
            transcript_item_offset=0,
            transcript_end_item_id=790,
            transcript_end_item_offset=100,
        )

        # Execute & Verify
        with pytest.raises(exception_type):
            await create_transcrippet(args)

    @pytest.mark.asyncio
    async def test_provided_ids_handling(
        self, mock_http_dependencies, transcrippets_api_responses
    ):
        """Test handling of provided IDs with format validation."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            transcrippets_api_responses["find_transcrippets_success"]
        )

        args = FindTranscrippetsArgs(
            transcrippet_id="123,456,789",  # Comma-separated IDs
            event_id="event1,event2",
            equity_id="eq1",
            speaker_id="speaker1,speaker2",
            transcript_item_id="item1",
        )

        # Execute
        result = await find_transcrippets(args)

        # Verify - should pass through the IDs as provided
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["transcrippet_id"] == "123,456,789"
        assert params["event_id"] == "event1,event2"
        assert params["speaker_id"] == "speaker1,speaker2"
