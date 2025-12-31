#!/usr/bin/env python3

"""Unit tests for search tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import asyncio

from aiera_mcp.tools.search.tools import search_transcripts, search_filings
from aiera_mcp.tools.search.models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    TranscriptSearchItem,
)


@pytest.mark.unit
class TestSearchTranscripts:
    """Test the search_transcripts tool."""

    @pytest.mark.asyncio
    async def test_search_transcripts_success(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test successful transcript search."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_transcripts_success"
        ]

        args = SearchTranscriptsArgs(
            query_text="inflation costs",
            event_ids=[2108591],
            equity_ids=[1],
            start_date="2022-01-01",
            end_date="2022-12-31",
            max_results=20,
        )

        # Execute
        result = await search_transcripts(args)

        # Verify
        assert isinstance(result, SearchTranscriptsResponse)
        assert result.response is not None
        assert len(result.response.result) == 2

        # Check first result
        first_result = result.response.result[0]
        assert isinstance(first_result, TranscriptSearchItem)
        assert first_result.score > 0
        assert "inflation" in first_result.text.lower()
        assert first_result.title == "Q1 2022 Amazon.com Inc Earnings Call"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/chat-support/search/transcripts"

    @pytest.mark.asyncio
    async def test_search_transcripts_empty_results(self, mock_http_dependencies):
        """Test search_transcripts with no results."""
        # Setup
        empty_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = SearchTranscriptsArgs(
            query_text="nonexistent query term xyz123",
            event_ids=[999999],
            equity_ids=[1],
            max_results=20,
        )

        # Execute
        result = await search_transcripts(args)

        # Verify
        assert isinstance(result, SearchTranscriptsResponse)
        assert result.response is not None
        assert len(result.response.result) == 0

    @pytest.mark.asyncio
    async def test_search_transcripts_with_section_filter(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_transcripts with transcript section filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_transcripts_success"
        ]

        args = SearchTranscriptsArgs(
            query_text="earnings",
            event_ids=[2108591],
            equity_ids=[1],
            transcript_section="q_and_a",
            max_results=10,
        )

        # Execute
        result = await search_transcripts(args)

        # Verify the call included the section filter
        assert isinstance(result, SearchTranscriptsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        assert "post_filter" in data
        # The section filter should be in must clauses
        must_clauses = data["post_filter"]["bool"]["must"]
        section_filter = [c for c in must_clauses if "transcript_section" in str(c)]
        assert len(section_filter) > 0

    @pytest.mark.asyncio
    async def test_search_transcripts_with_event_type(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_transcripts with event type filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_transcripts_success"
        ]

        args = SearchTranscriptsArgs(
            query_text="guidance",
            event_ids=[2108591],
            equity_ids=[1],
            event_type="presentation",
            max_results=20,
        )

        # Execute
        result = await search_transcripts(args)

        # Verify
        assert isinstance(result, SearchTranscriptsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        event_type_filter = [
            c for c in must_clauses if "transcript_event_type" in str(c)
        ]
        assert len(event_type_filter) > 0

    @pytest.mark.asyncio
    async def test_search_transcripts_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_transcripts with exclude_instructions."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_transcripts_success"
        ]

        args = SearchTranscriptsArgs(
            query_text="inflation",
            event_ids=[2108591],
            equity_ids=[1],
            exclude_instructions=True,
            max_results=20,
        )

        # Execute
        result = await search_transcripts(args)

        # Verify instructions are empty
        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_search_transcripts_fallback_on_timeout(self, mock_http_dependencies):
        """Test that search_transcripts falls back to standard search on timeout."""
        # Setup - first call times out, second succeeds
        fallback_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].side_effect = [
            asyncio.TimeoutError("ML inference timed out"),
            fallback_response,
        ]

        args = SearchTranscriptsArgs(
            query_text="test query",
            event_ids=[1],
            equity_ids=[1],
            max_results=20,
        )

        # Execute
        result = await search_transcripts(args)

        # Verify fallback was used (2 calls made)
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        assert isinstance(result, SearchTranscriptsResponse)


@pytest.mark.unit
class TestSearchFilings:
    """Test the search_filings tool."""

    @pytest.mark.asyncio
    async def test_search_filings_success(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test successful filing search."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_filing_chunks_success"
        ]

        args = SearchFilingsArgs(
            query_text="executive compensation",
            equity_ids=[1],
            filing_type="DEF14A",
            start_date="2023-01-01",
            end_date="2023-12-31",
            max_results=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify
        assert isinstance(result, SearchFilingsResponse)
        assert result.response is not None
        assert len(result.response.result) == 1

        # Check first result
        first_result = result.response.result[0]
        assert first_result["_score"] > 0
        assert first_result["title"] == "Amazon.com Inc - DEF 14A"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/chat-support/search/filing-chunks"

    @pytest.mark.asyncio
    async def test_search_filings_empty_results(self, mock_http_dependencies):
        """Test search_filings with no results."""
        # Setup
        empty_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = SearchFilingsArgs(
            query_text="nonexistent xyz123",
            equity_ids=[999999],
            max_results=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify
        assert isinstance(result, SearchFilingsResponse)
        assert result.response is not None
        assert len(result.response.result) == 0

    @pytest.mark.asyncio
    async def test_search_filings_with_filing_type_filter(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_filings with filing type filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_filing_chunks_success"
        ]

        args = SearchFilingsArgs(
            query_text="risk factors",
            equity_ids=[1],
            filing_type="10-K",
            max_results=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify the call included the filing type filter
        assert isinstance(result, SearchFilingsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        assert "post_filter" in data
        must_clauses = data["post_filter"]["bool"]["must"]
        filing_type_filter = [c for c in must_clauses if "filing_type" in str(c)]
        assert len(filing_type_filter) > 0

    @pytest.mark.asyncio
    async def test_search_filings_with_date_range(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_filings with date range filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_filing_chunks_success"
        ]

        args = SearchFilingsArgs(
            query_text="revenue",
            equity_ids=[1],
            start_date="2023-01-01",
            end_date="2023-12-31",
            max_results=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify the call included the date range filter
        assert isinstance(result, SearchFilingsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        date_filter = [c for c in must_clauses if "range" in str(c)]
        assert len(date_filter) > 0

    @pytest.mark.asyncio
    async def test_search_filings_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_filings with exclude_instructions."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_filing_chunks_success"
        ]

        args = SearchFilingsArgs(
            query_text="compensation",
            equity_ids=[1],
            exclude_instructions=True,
            max_results=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify instructions are empty
        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_search_filings_fallback_on_timeout(self, mock_http_dependencies):
        """Test that search_filings falls back to standard search on timeout."""
        # Setup - first call times out, second succeeds
        fallback_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].side_effect = [
            asyncio.TimeoutError("ML inference timed out"),
            fallback_response,
        ]

        args = SearchFilingsArgs(
            query_text="test query",
            equity_ids=[1],
            max_results=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify fallback was used (2 calls made)
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        assert isinstance(result, SearchFilingsResponse)

    @pytest.mark.asyncio
    async def test_search_filings_fallback_uses_correct_endpoint(
        self, mock_http_dependencies
    ):
        """Test that search_filings fallback uses the correct filing-chunks endpoint."""
        # Setup - first call returns empty, triggering fallback
        mock_http_dependencies["mock_make_request"].side_effect = [
            {"response": {}},  # Empty response triggers fallback
            {"instructions": [], "response": {"result": []}},
        ]

        args = SearchFilingsArgs(
            query_text="test query",
            equity_ids=[1],
            max_results=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify both calls used filing-chunks endpoint
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        for call in mock_http_dependencies["mock_make_request"].call_args_list:
            assert call[1]["endpoint"] == "/chat-support/search/filing-chunks"


@pytest.mark.unit
class TestSearchToolsErrorHandling:
    """Test error handling for search tools."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, ValueError])
    async def test_search_transcripts_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated from search_transcripts.

        Note: TimeoutError is handled specially - the search tools catch it and
        fall back to standard search, so it's not tested here.
        """
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = SearchTranscriptsArgs(
            query_text="test",
            event_ids=[1],
            equity_ids=[1],
            max_results=20,
        )

        # Execute & Verify
        with pytest.raises(exception_type):
            await search_transcripts(args)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, ValueError])
    async def test_search_filings_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated from search_filings.

        Note: TimeoutError is handled specially - the search tools catch it and
        fall back to standard search, so it's not tested here.
        """
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = SearchFilingsArgs(
            query_text="test",
            equity_ids=[1],
            max_results=20,
        )

        # Execute & Verify
        with pytest.raises(exception_type):
            await search_filings(args)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("max_results", [10, 50, 100])
    async def test_search_transcripts_respects_max_results(
        self, mock_http_dependencies, sample_api_responses, max_results
    ):
        """Test that search_transcripts respects max_results parameter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_transcripts_success"
        ]

        args = SearchTranscriptsArgs(
            query_text="test",
            event_ids=[1],
            equity_ids=[1],
            max_results=max_results,
        )

        # Execute
        await search_transcripts(args)

        # Verify max_results was passed in query
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        assert data["size"] == max_results
