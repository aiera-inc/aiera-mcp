#!/usr/bin/env python3

"""Unit tests for search models."""

import pytest
import json
from datetime import datetime
from pydantic import ValidationError

from aiera_mcp.tools.search.models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    TranscriptSearchItem,
    TranscriptSearchCitation,
    TranscriptSearchCitationMetadata,
    TranscriptSearchResult,
    TranscriptSearchResponseData,
    FilingSearchItem,
    FilingSearchCitation,
    FilingSearchCitationMetadata,
    SearchResponseData,
)


@pytest.mark.unit
class TestSearchTranscriptsArgs:
    """Test SearchTranscriptsArgs model."""

    def test_valid_search_transcripts_args(self):
        """Test valid SearchTranscriptsArgs creation."""
        args = SearchTranscriptsArgs(
            query_text="earnings guidance",
            event_ids=[1, 2, 3],
            equity_ids=[100, 200],
            start_date="2024-01-01",
            end_date="2024-12-31",
            transcript_section="q_and_a",
            event_type="earnings",
            max_results=20,
        )

        assert args.query_text == "earnings guidance"
        assert args.event_ids == [1, 2, 3]
        assert args.equity_ids == [100, 200]
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.transcript_section == "q_and_a"
        assert args.event_type == "earnings"
        assert args.max_results == 20

    def test_search_transcripts_args_defaults(self):
        """Test SearchTranscriptsArgs default values."""
        args = SearchTranscriptsArgs(
            query_text="test query",
            event_ids=[1],
            equity_ids=[1],
        )

        assert args.start_date == ""
        assert args.end_date == ""
        assert args.transcript_section == ""
        assert args.event_type == "earnings"
        assert args.max_results == 20
        assert args.originating_prompt is None
        assert args.include_base_instructions is True
        assert args.exclude_instructions is False

    def test_search_transcripts_args_with_originating_prompt(self):
        """Test SearchTranscriptsArgs with originating_prompt field."""
        args = SearchTranscriptsArgs(
            query_text="earnings",
            event_ids=[1],
            equity_ids=[1],
            originating_prompt="What did management say about inflation?",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "What did management say about inflation?"
        assert args.include_base_instructions is False

    def test_search_transcripts_args_required_fields(self):
        """Test that query_text is required."""
        with pytest.raises(ValidationError):
            SearchTranscriptsArgs()


@pytest.mark.unit
class TestSearchFilingsArgs:
    """Test SearchFilingsArgs model."""

    def test_valid_search_filings_args(self):
        """Test valid SearchFilingsArgs creation."""
        args = SearchFilingsArgs(
            query_text="risk factors",
            equity_ids=[100, 200],
            filing_ids=["filing123", "filing456"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            filing_type="10-K",
            max_results=30,
        )

        assert args.query_text == "risk factors"
        assert args.equity_ids == [100, 200]
        assert args.filing_ids == ["filing123", "filing456"]
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.filing_type == "10-K"
        assert args.max_results == 30

    def test_search_filings_args_defaults(self):
        """Test SearchFilingsArgs default values."""
        args = SearchFilingsArgs(
            query_text="test query",
            equity_ids=[1],
        )

        assert args.filing_ids == []
        assert args.start_date == ""
        assert args.end_date == ""
        assert args.filing_type == ""
        assert args.max_results == 20
        assert args.originating_prompt is None
        assert args.include_base_instructions is True
        assert args.exclude_instructions is False

    def test_search_filings_args_with_originating_prompt(self):
        """Test SearchFilingsArgs with originating_prompt field."""
        args = SearchFilingsArgs(
            query_text="compensation",
            equity_ids=[1],
            originating_prompt="What is the CEO compensation?",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "What is the CEO compensation?"
        assert args.include_base_instructions is False

    def test_search_filings_args_required_fields(self):
        """Test that query_text is required."""
        with pytest.raises(ValidationError):
            SearchFilingsArgs()


@pytest.mark.unit
class TestTranscriptSearchItem:
    """Test TranscriptSearchItem model."""

    def test_transcript_search_item_creation(self):
        """Test TranscriptSearchItem model creation."""
        item = TranscriptSearchItem(
            _score=9.5,
            date="2024-01-15T10:00:00",
            primary_company_id=1,
            content_id=12345,
            transcript_event_id=67890,
            transcript_section="q_and_a",
            text="This is the matching transcript text",
            primary_equity_id=100,
            title="Q1 2024 Earnings Call",
            citation_information=TranscriptSearchCitation(
                title="Q1 2024 Earnings Call",
                url="https://example.com/transcript",
                metadata=TranscriptSearchCitationMetadata(
                    type="event",
                    company_id=1,
                    event_id=67890,
                ),
            ),
        )

        assert item.score == 9.5
        assert item.transcript_item_id == 12345  # Aliased from content_id
        assert item.transcript_event_id == 67890
        assert item.transcript_section == "q_and_a"
        assert item.text == "This is the matching transcript text"
        assert item.title == "Q1 2024 Earnings Call"

    def test_transcript_search_item_date_parsing(self):
        """Test date parsing from ISO format string."""
        item = TranscriptSearchItem(
            _score=8.0,
            date="2024-01-15T10:30:00Z",
            primary_company_id=1,
            content_id=123,
            transcript_event_id=456,
            transcript_section=None,
            text="Test text",
            primary_equity_id=1,
            title="Test",
            citation_information=TranscriptSearchCitation(
                title="Test",
                url="https://example.com",
            ),
        )

        assert isinstance(item.date, datetime)
        assert item.date.year == 2024
        assert item.date.month == 1
        assert item.date.day == 15

    def test_transcript_search_item_serialization(self):
        """Test that TranscriptSearchItem serializes properly to JSON."""
        item = TranscriptSearchItem(
            _score=9.0,
            date="2024-01-15T10:00:00",
            primary_company_id=1,
            content_id=123,
            transcript_event_id=456,
            transcript_section="presentation",
            text="Test",
            primary_equity_id=1,
            title="Test Event",
            citation_information=TranscriptSearchCitation(
                title="Test",
                url="https://example.com",
            ),
        )

        serialized = item.model_dump()
        json_str = json.dumps(serialized)

        assert isinstance(json_str, str)
        assert "date" in json_str
        # Date should be serialized as ISO string
        assert isinstance(serialized["date"], str)

    def test_transcript_search_item_null_section(self):
        """Test TranscriptSearchItem with null transcript_section."""
        item = TranscriptSearchItem(
            _score=7.5,
            date="2024-01-15T10:00:00",
            primary_company_id=1,
            content_id=123,
            transcript_event_id=456,
            transcript_section=None,  # Can be null
            text="Test",
            primary_equity_id=1,
            title="Test",
            citation_information=TranscriptSearchCitation(
                title="Test",
                url="https://example.com",
            ),
        )

        assert item.transcript_section is None


@pytest.mark.unit
class TestFilingSearchItem:
    """Test FilingSearchItem model."""

    def test_filing_search_item_creation(self):
        """Test FilingSearchItem model creation."""
        item = FilingSearchItem(
            _score=12.5,
            date="2024-03-15T00:00:00",
            primary_company_id=1,
            content_id="content123",
            filing_id="filing456",
            company_common_name="Apple",
            text="Risk factor disclosure text",
            primary_equity_id=100,
            title="Apple Inc - 10-K",
            filing_type="10-K",
            citation_information=FilingSearchCitation(
                title="Apple Inc - 10-K",
                url="https://example.com/filing",
                metadata=FilingSearchCitationMetadata(
                    type="filing",
                    company_id=1,
                    filing_id=456,
                ),
            ),
        )

        assert item.score == 12.5
        assert item.content_id == "content123"
        assert item.filing_id == "filing456"
        assert item.company_common_name == "Apple"
        assert item.text == "Risk factor disclosure text"
        assert item.filing_type == "10-K"

    def test_filing_search_item_optional_fields(self):
        """Test FilingSearchItem with optional fields as None."""
        item = FilingSearchItem(
            _score=10.0,
            date="2024-03-15T00:00:00",
            primary_company_id=1,
            content_id="content123",
            filing_id="filing456",
            text="Test text",
            primary_equity_id=1,
            title="Test Filing",
            citation_information=FilingSearchCitation(
                title="Test",
                url="https://example.com",
            ),
        )

        assert item.company_common_name is None
        assert item.filing_type is None

    def test_filing_search_item_date_serialization(self):
        """Test FilingSearchItem date serialization."""
        item = FilingSearchItem(
            _score=10.0,
            date="2024-03-15T00:00:00Z",
            primary_company_id=1,
            content_id="123",
            filing_id="456",
            text="Test",
            primary_equity_id=1,
            title="Test",
            citation_information=FilingSearchCitation(
                title="Test",
                url="https://example.com",
            ),
        )

        serialized = item.model_dump()
        assert isinstance(serialized["date"], str)
        assert "2024-03-15" in serialized["date"]


@pytest.mark.unit
class TestSearchResponses:
    """Test search response models."""

    def test_search_transcripts_response(self):
        """Test SearchTranscriptsResponse model."""
        items = [
            TranscriptSearchItem(
                _score=9.0,
                date="2024-01-15T10:00:00",
                primary_company_id=1,
                content_id=123,
                transcript_event_id=456,
                transcript_section="q_and_a",
                text="Test text",
                primary_equity_id=1,
                title="Test Event",
                citation_information=TranscriptSearchCitation(
                    title="Test",
                    url="https://example.com",
                ),
            )
        ]

        response = SearchTranscriptsResponse(
            instructions=["Test instruction"],
            response=TranscriptSearchResponseData(result=items),
        )

        assert len(response.response.result) == 1
        assert response.instructions == ["Test instruction"]

    def test_search_filings_response(self):
        """Test SearchFilingsResponse model."""
        response = SearchFilingsResponse(
            instructions=["Test instruction"],
            response=SearchResponseData(result=[{"test": "data"}]),
        )

        assert len(response.response.result) == 1
        assert response.instructions == ["Test instruction"]

    def test_search_response_empty_results(self):
        """Test search responses with empty results."""
        transcript_response = SearchTranscriptsResponse(
            instructions=[],
            response=TranscriptSearchResponseData(result=[]),
        )
        assert transcript_response.response.result == []

        filing_response = SearchFilingsResponse(
            instructions=[],
            response=SearchResponseData(result=[]),
        )
        assert filing_response.response.result == []

    def test_search_response_null_response(self):
        """Test search responses with null response."""
        transcript_response = SearchTranscriptsResponse(
            instructions=[],
            response=None,
        )
        assert transcript_response.response is None

        filing_response = SearchFilingsResponse(
            instructions=[],
            response=None,
        )
        assert filing_response.response is None


@pytest.mark.unit
class TestSearchCitationModels:
    """Test citation models for search results."""

    def test_transcript_search_citation_metadata(self):
        """Test TranscriptSearchCitationMetadata creation."""
        metadata = TranscriptSearchCitationMetadata(
            type="event",
            url_target="aiera",
            company_id=1,
            event_id=12345,
            transcript_item_id=67890,
        )

        assert metadata.type == "event"
        assert metadata.url_target == "aiera"
        assert metadata.company_id == 1
        assert metadata.event_id == 12345
        assert metadata.transcript_item_id == 67890

    def test_transcript_search_citation(self):
        """Test TranscriptSearchCitation creation."""
        citation = TranscriptSearchCitation(
            title="Q1 2024 Earnings Call",
            url="https://example.com/transcript",
            metadata=TranscriptSearchCitationMetadata(
                type="event",
                company_id=1,
            ),
        )

        assert citation.title == "Q1 2024 Earnings Call"
        assert citation.url == "https://example.com/transcript"
        assert citation.metadata.type == "event"

    def test_transcript_search_citation_minimal(self):
        """Test TranscriptSearchCitation with minimal data."""
        citation = TranscriptSearchCitation(
            title="Test",
            url="https://example.com",
        )

        assert citation.title == "Test"
        assert citation.metadata is None

    def test_filing_search_citation_metadata(self):
        """Test FilingSearchCitationMetadata creation."""
        metadata = FilingSearchCitationMetadata(
            type="filing",
            url_target="aiera",
            company_id=1,
            content_id=12345,
            filing_id=67890,
        )

        assert metadata.type == "filing"
        assert metadata.content_id == 12345
        assert metadata.filing_id == 67890

    def test_filing_search_citation(self):
        """Test FilingSearchCitation creation."""
        citation = FilingSearchCitation(
            title="Apple Inc - 10-K",
            url="https://example.com/filing",
            metadata=FilingSearchCitationMetadata(
                type="filing",
                company_id=1,
            ),
        )

        assert citation.title == "Apple Inc - 10-K"
        assert citation.url == "https://example.com/filing"


@pytest.mark.unit
class TestSearchModelSerialization:
    """Test serialization of search models."""

    def test_search_transcripts_args_json_schema(self):
        """Test that SearchTranscriptsArgs generates valid JSON schema."""
        schema = SearchTranscriptsArgs.model_json_schema()

        assert "properties" in schema
        assert "query_text" in schema["properties"]
        assert "event_ids" in schema["properties"]
        assert "equity_ids" in schema["properties"]
        assert "max_results" in schema["properties"]

    def test_search_filings_args_json_schema(self):
        """Test that SearchFilingsArgs generates valid JSON schema."""
        schema = SearchFilingsArgs.model_json_schema()

        assert "properties" in schema
        assert "query_text" in schema["properties"]
        assert "equity_ids" in schema["properties"]
        assert "filing_type" in schema["properties"]

    def test_transcript_search_item_roundtrip(self):
        """Test TranscriptSearchItem serialization roundtrip."""
        original = TranscriptSearchItem(
            _score=9.5,
            date="2024-01-15T10:00:00",
            primary_company_id=1,
            content_id=123,
            transcript_event_id=456,
            transcript_section="q_and_a",
            text="Test text",
            primary_equity_id=1,
            title="Test",
            citation_information=TranscriptSearchCitation(
                title="Test",
                url="https://example.com",
            ),
        )

        # Serialize to dict
        serialized = original.model_dump()

        # Serialize to JSON and back
        json_str = json.dumps(serialized)
        parsed = json.loads(json_str)

        # Verify key fields
        assert parsed["score"] == 9.5
        assert parsed["transcript_item_id"] == 123
        assert parsed["text"] == "Test text"
