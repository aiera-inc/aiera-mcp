#!/usr/bin/env python3

"""Unit tests for search tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import asyncio

from aiera_mcp.tools.search.tools import (
    search_transcripts,
    search_filings,
    search_research,
    search_company_docs,
    search_thirdbridge,
)
from aiera_mcp.tools.search.models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchCompanyDocsArgs,
    SearchThirdbridgeArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResearchResponse,
    SearchCompanyDocsResponse,
    SearchThirdbridgeResponse,
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
            size=20,
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
            size=20,
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
            size=10,
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
            size=20,
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
            size=20,
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
            size=20,
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
            size=20,
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
            size=20,
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
            size=20,
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
            size=20,
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
            size=20,
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
            size=20,
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
            size=20,
        )

        # Execute
        result = await search_filings(args)

        # Verify both calls used filing-chunks endpoint
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        for call in mock_http_dependencies["mock_make_request"].call_args_list:
            assert call[1]["endpoint"] == "/chat-support/search/filing-chunks"


@pytest.mark.unit
class TestSearchResearch:
    """Test the search_research tool."""

    @pytest.mark.asyncio
    async def test_search_research_success(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test successful research search."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="cloud computing growth",
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify
        assert isinstance(result, SearchResearchResponse)
        assert result.response is not None
        assert len(result.response.result) == 1

        # Check first result
        first_result = result.response.result[0]
        assert first_result["_score"] > 0
        assert first_result["title"] == "Amazon.com Inc - Research Report"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/chat-support/search/research-chunks"

    @pytest.mark.asyncio
    async def test_search_research_empty_results(self, mock_http_dependencies):
        """Test search_research with no results."""
        # Setup
        empty_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = SearchResearchArgs(
            query_text="nonexistent xyz123",
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify
        assert isinstance(result, SearchResearchResponse)
        assert result.response is not None
        assert len(result.response.result) == 0

    @pytest.mark.asyncio
    async def test_search_research_with_date_range(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_research with date range filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="revenue",
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify the call included the date range filter
        assert isinstance(result, SearchResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        date_filter = [c for c in must_clauses if "range" in str(c)]
        assert len(date_filter) > 0

    @pytest.mark.asyncio
    async def test_search_research_with_document_ids(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_research with document_ids filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="market analysis",
            document_ids=["8001234", "8001235"],
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify the call included the document_ids filter
        assert isinstance(result, SearchResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        document_id_filter = [c for c in must_clauses if "parent_research_id" in str(c)]
        assert len(document_id_filter) > 0

    @pytest.mark.asyncio
    async def test_search_research_with_author_id(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_research with author_id filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="macro strategy",
            author_ids=["12345"],
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify the call included the author_ids filter
        assert isinstance(result, SearchResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        author_filter = [c for c in must_clauses if "authors.person_id" in str(c)]
        assert len(author_filter) == 1
        assert author_filter[0]["terms"]["authors.person_id"] == ["12345"]

    @pytest.mark.asyncio
    async def test_search_research_with_all_filters(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_research with all filter parameters combined."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="credit outlook",
            document_ids=["8001234"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            author_ids=["12345"],
            aiera_provider_ids=["krypton"],
            asset_classes=["Equity"],
            asset_types=["Common Stock"],
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify all filters are present
        assert isinstance(result, SearchResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        # Should have 6 filters: parent_research_id, date range, author, aiera_provider_id, asset_classes, asset_types
        assert len(must_clauses) == 6

    @pytest.mark.asyncio
    async def test_search_research_with_asset_classes(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_research with asset_classes filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="equity analysis",
            asset_classes=["Equity", "Fixed Income"],
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify the call included the asset_classes filter
        assert isinstance(result, SearchResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        asset_classes_filter = [c for c in must_clauses if "asset_classes" in str(c)]
        assert len(asset_classes_filter) == 1
        assert asset_classes_filter[0]["terms"]["asset_classes"] == [
            "Equity",
            "Fixed Income",
        ]

    @pytest.mark.asyncio
    async def test_search_research_with_asset_types(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_research with asset_types filter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="stock analysis",
            asset_types=["Common Stock"],
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify the call included the asset_types filter
        assert isinstance(result, SearchResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        asset_types_filter = [c for c in must_clauses if "asset_types" in str(c)]
        assert len(asset_types_filter) == 1
        assert asset_types_filter[0]["terms"]["asset_types"] == ["Common Stock"]

    @pytest.mark.asyncio
    async def test_search_research_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_research with exclude_instructions."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = SearchResearchArgs(
            query_text="cloud computing",
            exclude_instructions=True,
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify instructions are empty
        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_search_research_fallback_on_timeout(self, mock_http_dependencies):
        """Test that search_research falls back to standard search on timeout."""
        # Setup - first call times out, second succeeds
        fallback_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].side_effect = [
            asyncio.TimeoutError("ML inference timed out"),
            fallback_response,
        ]

        args = SearchResearchArgs(
            query_text="test query",
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify fallback was used (2 calls made)
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        assert isinstance(result, SearchResearchResponse)

    @pytest.mark.asyncio
    async def test_search_research_fallback_uses_correct_endpoint(
        self, mock_http_dependencies
    ):
        """Test that search_research fallback uses the correct research-chunks endpoint."""
        # Setup - first call returns empty, triggering fallback
        mock_http_dependencies["mock_make_request"].side_effect = [
            {"response": {}},  # Empty response triggers fallback
            {"instructions": [], "response": {"result": []}},
        ]

        args = SearchResearchArgs(
            query_text="test query",
            size=20,
        )

        # Execute
        result = await search_research(args)

        # Verify both calls used research-chunks endpoint
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        for call in mock_http_dependencies["mock_make_request"].call_args_list:
            assert call[1]["endpoint"] == "/chat-support/search/research-chunks"


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
            size=20,
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
            size=20,
        )

        # Execute & Verify
        with pytest.raises(exception_type):
            await search_filings(args)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("size", [10, 50, 100])
    async def test_search_transcripts_respects_size(
        self, mock_http_dependencies, sample_api_responses, size
    ):
        """Test that search_transcripts respects size parameter."""
        # Setup
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_transcripts_success"
        ]

        args = SearchTranscriptsArgs(
            query_text="test",
            event_ids=[1],
            equity_ids=[1],
            size=size,
        )

        # Execute
        await search_transcripts(args)

        # Verify size was passed in query
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        assert data["size"] == size


@pytest.mark.unit
class TestSearchCompanyDocs:
    """Test the search_company_docs tool."""

    @pytest.mark.asyncio
    async def test_search_company_docs_success(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test successful company docs search."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_company_doc_chunks_success"
        ]

        args = SearchCompanyDocsArgs(
            query_text="sustainability initiatives",
            company_ids=[1],
            size=20,
        )

        result = await search_company_docs(args)

        assert isinstance(result, SearchCompanyDocsResponse)
        assert result.response is not None
        assert len(result.response.result) == 1

        first_result = result.response.result[0]
        assert first_result["_score"] > 0
        assert first_result["title"] == "Amazon.com Inc - Sustainability Report 2024"

        mock_http_dependencies["mock_make_request"].assert_called()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/chat-support/search/company-doc-chunks"

    @pytest.mark.asyncio
    async def test_search_company_docs_empty_results(self, mock_http_dependencies):
        """Test search_company_docs with no results."""
        empty_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = SearchCompanyDocsArgs(
            query_text="nonexistent xyz123",
            size=20,
        )

        result = await search_company_docs(args)

        assert isinstance(result, SearchCompanyDocsResponse)
        assert result.response is not None
        assert len(result.response.result) == 0

    @pytest.mark.asyncio
    async def test_search_company_docs_with_company_doc_ids(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_company_docs with company_doc_ids filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_company_doc_chunks_success"
        ]

        args = SearchCompanyDocsArgs(
            query_text="capital allocation",
            company_doc_ids=[3001234, 3001235],
            size=20,
        )

        result = await search_company_docs(args)

        assert isinstance(result, SearchCompanyDocsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        doc_id_filter = [c for c in must_clauses if "company_doc_id" in str(c)]
        assert len(doc_id_filter) > 0

    @pytest.mark.asyncio
    async def test_search_company_docs_with_categories(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_company_docs with categories filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_company_doc_chunks_success"
        ]

        args = SearchCompanyDocsArgs(
            query_text="earnings",
            categories=["Investor Presentation", "Press Release"],
            size=20,
        )

        result = await search_company_docs(args)

        assert isinstance(result, SearchCompanyDocsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        category_filter = [c for c in must_clauses if "category.keyword" in str(c)]
        assert len(category_filter) == 1
        assert category_filter[0]["terms"]["category.keyword"] == [
            "Investor Presentation",
            "Press Release",
        ]

    @pytest.mark.asyncio
    async def test_search_company_docs_with_keywords(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_company_docs with keywords filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_company_doc_chunks_success"
        ]

        args = SearchCompanyDocsArgs(
            query_text="ESG report",
            keywords=["sustainability", "ESG"],
            size=20,
        )

        result = await search_company_docs(args)

        assert isinstance(result, SearchCompanyDocsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        keywords_filter = [c for c in must_clauses if "keywords" in str(c)]
        assert len(keywords_filter) == 1

    @pytest.mark.asyncio
    async def test_search_company_docs_with_date_range(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_company_docs with date range filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_company_doc_chunks_success"
        ]

        args = SearchCompanyDocsArgs(
            query_text="quarterly results",
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=20,
        )

        result = await search_company_docs(args)

        assert isinstance(result, SearchCompanyDocsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        date_filter = [c for c in must_clauses if "range" in str(c)]
        assert len(date_filter) > 0

    @pytest.mark.asyncio
    async def test_search_company_docs_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_company_docs with exclude_instructions."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_company_doc_chunks_success"
        ]

        args = SearchCompanyDocsArgs(
            query_text="sustainability",
            exclude_instructions=True,
            size=20,
        )

        result = await search_company_docs(args)

        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_search_company_docs_fallback_on_timeout(
        self, mock_http_dependencies
    ):
        """Test that search_company_docs falls back to standard search on timeout."""
        fallback_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].side_effect = [
            asyncio.TimeoutError("ML inference timed out"),
            fallback_response,
        ]

        args = SearchCompanyDocsArgs(
            query_text="test query",
            size=20,
        )

        result = await search_company_docs(args)

        assert mock_http_dependencies["mock_make_request"].call_count == 2
        assert isinstance(result, SearchCompanyDocsResponse)

    @pytest.mark.asyncio
    async def test_search_company_docs_fallback_uses_correct_endpoint(
        self, mock_http_dependencies
    ):
        """Test that search_company_docs fallback uses the correct endpoint."""
        mock_http_dependencies["mock_make_request"].side_effect = [
            {"response": {}},
            {"instructions": [], "response": {"result": []}},
        ]

        args = SearchCompanyDocsArgs(
            query_text="test query",
            size=20,
        )

        result = await search_company_docs(args)

        assert mock_http_dependencies["mock_make_request"].call_count == 2
        for call in mock_http_dependencies["mock_make_request"].call_args_list:
            assert call[1]["endpoint"] == "/chat-support/search/company-doc-chunks"


@pytest.mark.unit
class TestSearchThirdbridge:
    """Test the search_thirdbridge tool."""

    @pytest.mark.asyncio
    async def test_search_thirdbridge_success(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test successful Third Bridge search."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_thirdbridge_success"
        ]

        args = SearchThirdbridgeArgs(
            query_text="semiconductor supply chain",
            company_ids=[1],
            size=20,
        )

        result = await search_thirdbridge(args)

        assert isinstance(result, SearchThirdbridgeResponse)
        assert result.response is not None
        assert len(result.response.result) == 1

        first_result = result.response.result[0]
        assert first_result["_score"] > 0
        assert (
            first_result["event_title"]
            == "Expert Call: Semiconductor Supply Chain Dynamics"
        )

        mock_http_dependencies["mock_make_request"].assert_called()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/chat-support/search/thirdbridge"

    @pytest.mark.asyncio
    async def test_search_thirdbridge_empty_results(self, mock_http_dependencies):
        """Test search_thirdbridge with no results."""
        empty_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = SearchThirdbridgeArgs(
            query_text="nonexistent xyz123",
            size=20,
        )

        result = await search_thirdbridge(args)

        assert isinstance(result, SearchThirdbridgeResponse)
        assert result.response is not None
        assert len(result.response.result) == 0

    @pytest.mark.asyncio
    async def test_search_thirdbridge_with_company_ids(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_thirdbridge with company_ids filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_thirdbridge_success"
        ]

        args = SearchThirdbridgeArgs(
            query_text="competitive landscape",
            company_ids=[1, 42],
            size=20,
        )

        result = await search_thirdbridge(args)

        assert isinstance(result, SearchThirdbridgeResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        company_filter = [c for c in must_clauses if "primary_company_ids" in str(c)]
        assert len(company_filter) > 0
        # Should be a bool with should matching both primary and secondary
        bool_clause = company_filter[0]["bool"]
        assert len(bool_clause["should"]) == 2
        assert bool_clause["should"][0]["terms"]["primary_company_ids"] == [1, 42]
        assert bool_clause["should"][1]["terms"]["secondary_company_ids"] == [1, 42]
        assert bool_clause["minimum_should_match"] == 1

    @pytest.mark.asyncio
    async def test_search_thirdbridge_with_thirdbridge_ids(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_thirdbridge with thirdbridge_ids filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_thirdbridge_success"
        ]

        args = SearchThirdbridgeArgs(
            query_text="market dynamics",
            thirdbridge_ids=["TB-12345", "TB-67890"],
            size=20,
        )

        result = await search_thirdbridge(args)

        assert isinstance(result, SearchThirdbridgeResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        tb_filter = [c for c in must_clauses if "thirdbridge_id" in str(c)]
        assert len(tb_filter) > 0

    @pytest.mark.asyncio
    async def test_search_thirdbridge_with_date_range(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_thirdbridge with date range filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_thirdbridge_success"
        ]

        args = SearchThirdbridgeArgs(
            query_text="pricing trends",
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=20,
        )

        result = await search_thirdbridge(args)

        assert isinstance(result, SearchThirdbridgeResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        date_filter = [c for c in must_clauses if "range" in str(c)]
        assert len(date_filter) > 0

    @pytest.mark.asyncio
    async def test_search_thirdbridge_with_content_type(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_thirdbridge with event_content_type filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_thirdbridge_success"
        ]

        args = SearchThirdbridgeArgs(
            query_text="expert opinion",
            event_content_type="Interview",
            size=20,
        )

        result = await search_thirdbridge(args)

        assert isinstance(result, SearchThirdbridgeResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        content_type_filter = [
            c for c in must_clauses if "event_content_type" in str(c)
        ]
        assert len(content_type_filter) > 0

    @pytest.mark.asyncio
    async def test_search_thirdbridge_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test search_thirdbridge with exclude_instructions."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_thirdbridge_success"
        ]

        args = SearchThirdbridgeArgs(
            query_text="supply chain",
            exclude_instructions=True,
            size=20,
        )

        result = await search_thirdbridge(args)

        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_search_thirdbridge_fallback_on_timeout(self, mock_http_dependencies):
        """Test that search_thirdbridge falls back to standard search on timeout."""
        fallback_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].side_effect = [
            asyncio.TimeoutError("ML inference timed out"),
            fallback_response,
        ]

        args = SearchThirdbridgeArgs(
            query_text="test query",
            size=20,
        )

        result = await search_thirdbridge(args)

        assert mock_http_dependencies["mock_make_request"].call_count == 2
        assert isinstance(result, SearchThirdbridgeResponse)

    @pytest.mark.asyncio
    async def test_search_thirdbridge_fallback_uses_correct_endpoint(
        self, mock_http_dependencies
    ):
        """Test that search_thirdbridge fallback uses the correct endpoint."""
        mock_http_dependencies["mock_make_request"].side_effect = [
            {"response": {}},
            {"instructions": [], "response": {"result": []}},
        ]

        args = SearchThirdbridgeArgs(
            query_text="test query",
            size=20,
        )

        result = await search_thirdbridge(args)

        assert mock_http_dependencies["mock_make_request"].call_count == 2
        for call in mock_http_dependencies["mock_make_request"].call_args_list:
            assert call[1]["endpoint"] == "/chat-support/search/thirdbridge"
