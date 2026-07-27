#!/usr/bin/env python3

"""Unit tests for search tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

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
)


@pytest.mark.unit
class TestSearchTranscripts:
    """search_transcripts is a thin pass-through to POST /chat-support/search-transcripts.

    Hybrid query construction and ranking live in aiera-api, so these tests assert
    only that parameters are forwarded and the response is parsed.
    """

    @staticmethod
    def _payload(mock_http_dependencies):
        return mock_http_dependencies["mock_make_request"].call_args[1]["data"]

    @pytest.mark.asyncio
    async def test_calls_new_endpoint(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_transcripts_success"]

        result = await search_transcripts(
            SearchTranscriptsArgs(query_text="ai capex", size=25)
        )

        assert isinstance(result, SearchTranscriptsResponse)
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "POST"
        assert call[1]["endpoint"] == "/chat-support/search-transcripts"
        # single call — no client-side hybrid fallback anymore
        assert mock_http_dependencies["mock_make_request"].call_count == 1

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "response": {"result": []},
        }

        result = await search_transcripts(
            SearchTranscriptsArgs(query_text="nonexistent xyz123", size=25)
        )

        assert isinstance(result, SearchTranscriptsResponse)
        assert len(result.response["result"]) == 0

    @pytest.mark.asyncio
    async def test_forwards_query_text_and_size(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_transcripts_success"]

        await search_transcripts(
            SearchTranscriptsArgs(query_text="revenue guidance", size=25)
        )

        payload = self._payload(mock_http_dependencies)
        assert payload["query_text"] == "revenue guidance"
        assert payload["size"] == 25

    @pytest.mark.asyncio
    async def test_forwards_filters(self, mock_http_dependencies, sample_api_responses):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_transcripts_success"]

        await search_transcripts(
            SearchTranscriptsArgs(
                query_text="margins",
                event_ids=[12345],
                equity_ids=[100],
                start_date="2024-01-01",
                end_date="2024-12-31",
                event_type="presentation",
                transcript_section="q_and_a",
                size=25,
            )
        )

        payload = self._payload(mock_http_dependencies)
        assert payload["event_ids"] == [12345]
        assert payload["equity_ids"] == [100]
        assert payload["start_date"] == "2024-01-01"
        assert payload["end_date"] == "2024-12-31"
        assert payload["event_type"] == "presentation"
        assert payload["transcript_section"] == "q_and_a"

    @pytest.mark.asyncio
    async def test_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_transcripts_success"]

        result = await search_transcripts(
            SearchTranscriptsArgs(query_text="ai", exclude_instructions=True, size=25)
        )

        assert result.instructions == []


@pytest.mark.unit
class TestSearchFilings:
    """search_filings is a thin pass-through to POST /chat-support/search-filings."""

    @staticmethod
    def _payload(mock_http_dependencies):
        return mock_http_dependencies["mock_make_request"].call_args[1]["data"]

    @pytest.mark.asyncio
    async def test_calls_new_endpoint(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_filing_chunks_success"]

        result = await search_filings(
            SearchFilingsArgs(query_text="risk factors", size=25)
        )

        assert isinstance(result, SearchFilingsResponse)
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "POST"
        assert call[1]["endpoint"] == "/chat-support/search-filings"
        assert mock_http_dependencies["mock_make_request"].call_count == 1

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "response": {"result": []},
        }

        result = await search_filings(
            SearchFilingsArgs(query_text="nonexistent xyz123", size=25)
        )

        assert isinstance(result, SearchFilingsResponse)
        assert len(result.response["result"]) == 0

    @pytest.mark.asyncio
    async def test_forwards_filters(self, mock_http_dependencies, sample_api_responses):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_filing_chunks_success"]

        await search_filings(
            SearchFilingsArgs(
                query_text="executive compensation",
                filing_ids=["555"],
                equity_ids=[100],
                start_date="2023-01-01",
                end_date="2023-12-31",
                filing_type="DEF14A",
                size=25,
            )
        )

        payload = self._payload(mock_http_dependencies)
        assert payload["filing_ids"] == ["555"]
        assert payload["equity_ids"] == [100]
        assert payload["start_date"] == "2023-01-01"
        assert payload["end_date"] == "2023-12-31"
        assert payload["filing_type"] == "DEF14A"

    @pytest.mark.asyncio
    async def test_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_filing_chunks_success"]

        result = await search_filings(
            SearchFilingsArgs(query_text="debt", exclude_instructions=True, size=25)
        )

        assert result.instructions == []


@pytest.mark.unit
class TestSearchResearch:
    """search_research is now a thin pass-through to POST /chat-support/search-research.

    Query construction (neural k-NN, filters, recency default, ticker-suffix handling)
    lives in aiera-api, so these tests assert only that parameters are forwarded and the
    response is parsed — not the OpenSearch query shape.
    """

    @staticmethod
    def _payload(mock_http_dependencies):
        return mock_http_dependencies["mock_make_request"].call_args[1]["data"]

    @pytest.mark.asyncio
    async def test_search_research_calls_new_endpoint(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_research_chunks_success"]

        result = await search_research(
            SearchResearchArgs(query_text="cloud computing growth", size=25)
        )

        assert isinstance(result, SearchResearchResponse)
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "POST"
        assert call[1]["endpoint"] == "/chat-support/search-research"
        # single call — no client-side hybrid fallback anymore
        assert mock_http_dependencies["mock_make_request"].call_count == 1

    @pytest.mark.asyncio
    async def test_search_research_empty_results(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "response": {"result": []},
        }

        result = await search_research(
            SearchResearchArgs(query_text="nonexistent xyz123", size=25)
        )

        assert isinstance(result, SearchResearchResponse)
        assert len(result.response["result"]) == 0

    @pytest.mark.asyncio
    async def test_forwards_query_text_and_size(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_research_chunks_success"]

        await search_research(SearchResearchArgs(query_text="revenue", size=25))

        payload = self._payload(mock_http_dependencies)
        assert payload["query_text"] == "revenue"
        assert payload["size"] == 25

    @pytest.mark.asyncio
    async def test_omits_unset_filters(
        self, mock_http_dependencies, sample_api_responses
    ):
        # the tool only forwards params that were set; aiera-api applies the defaults
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_research_chunks_success"]

        await search_research(SearchResearchArgs(query_text="price of oil", size=25))

        payload = self._payload(mock_http_dependencies)
        for key in (
            "start_date",
            "end_date",
            "document_ids",
            "author_ids",
            "aiera_provider_ids",
            "asset_classes",
            "asset_types",
        ):
            assert key not in payload

    @pytest.mark.asyncio
    async def test_forwards_all_filters(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_research_chunks_success"]

        await search_research(
            SearchResearchArgs(
                query_text="credit outlook",
                document_ids=["8001234"],
                start_date="2024-01-01",
                end_date="2024-12-31",
                author_ids=["12345"],
                aiera_provider_ids=["krypton"],
                asset_classes=["Equity"],
                asset_types=["Common Stock"],
                size=25,
            )
        )

        payload = self._payload(mock_http_dependencies)
        assert payload["document_ids"] == ["8001234"]
        assert payload["start_date"] == "2024-01-01"
        assert payload["end_date"] == "2024-12-31"
        assert payload["author_ids"] == ["12345"]
        assert payload["aiera_provider_ids"] == ["krypton"]
        assert payload["asset_classes"] == ["Equity"]
        assert payload["asset_types"] == ["Common Stock"]

    @pytest.mark.asyncio
    async def test_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_research_chunks_success"]

        result = await search_research(
            SearchResearchArgs(
                query_text="cloud computing", exclude_instructions=True, size=25
            )
        )

        assert result.instructions == []


@pytest.mark.unit
class TestSearchToolsErrorHandling:
    """Test error handling for search tools."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, ValueError])
    async def test_search_transcripts_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Network errors from search_transcripts propagate to the caller."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = SearchTranscriptsArgs(
            query_text="test",
            event_ids=[1],
            equity_ids=[1],
            size=25,
        )

        # Execute & Verify
        with pytest.raises(exception_type):
            await search_transcripts(args)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, ValueError])
    async def test_search_filings_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Network errors from search_filings propagate to the caller."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = SearchFilingsArgs(
            query_text="test",
            equity_ids=[1],
            size=25,
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
    """search_company_docs is a thin pass-through to POST /chat-support/search-company-docs."""

    @staticmethod
    def _payload(mock_http_dependencies):
        return mock_http_dependencies["mock_make_request"].call_args[1]["data"]

    @pytest.mark.asyncio
    async def test_calls_new_endpoint(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_company_doc_chunks_success"]

        result = await search_company_docs(
            SearchCompanyDocsArgs(query_text="sustainability", size=25)
        )

        assert isinstance(result, SearchCompanyDocsResponse)
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "POST"
        assert call[1]["endpoint"] == "/chat-support/search-company-docs"
        assert mock_http_dependencies["mock_make_request"].call_count == 1

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "response": {"result": []},
        }

        result = await search_company_docs(
            SearchCompanyDocsArgs(query_text="nonexistent xyz123", size=25)
        )

        assert isinstance(result, SearchCompanyDocsResponse)
        assert len(result.response["result"]) == 0

    @pytest.mark.asyncio
    async def test_forwards_filters(self, mock_http_dependencies, sample_api_responses):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_company_doc_chunks_success"]

        await search_company_docs(
            SearchCompanyDocsArgs(
                query_text="ESG",
                company_doc_ids=[777],
                company_ids=[100],
                categories=["ESG"],
                keywords=["carbon"],
                start_date="2024-01-01",
                end_date="2024-12-31",
                size=25,
            )
        )

        payload = self._payload(mock_http_dependencies)
        assert payload["company_doc_ids"] == [777]
        assert payload["company_ids"] == [100]
        assert payload["categories"] == ["ESG"]
        assert payload["keywords"] == ["carbon"]
        assert payload["start_date"] == "2024-01-01"
        assert payload["end_date"] == "2024-12-31"

    @pytest.mark.asyncio
    async def test_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_company_doc_chunks_success"]

        result = await search_company_docs(
            SearchCompanyDocsArgs(
                query_text="policy", exclude_instructions=True, size=25
            )
        )

        assert result.instructions == []


@pytest.mark.unit
class TestSearchThirdbridge:
    """search_thirdbridge is a thin pass-through to POST /chat-support/search-thirdbridge."""

    @staticmethod
    def _payload(mock_http_dependencies):
        return mock_http_dependencies["mock_make_request"].call_args[1]["data"]

    @pytest.mark.asyncio
    async def test_calls_new_endpoint(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_thirdbridge_success"]

        result = await search_thirdbridge(
            SearchThirdbridgeArgs(query_text="supply chain", size=25)
        )

        assert isinstance(result, SearchThirdbridgeResponse)
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "POST"
        assert call[1]["endpoint"] == "/chat-support/search-thirdbridge"
        assert mock_http_dependencies["mock_make_request"].call_count == 1

    @pytest.mark.asyncio
    async def test_empty_results(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "response": {"result": []},
        }

        result = await search_thirdbridge(
            SearchThirdbridgeArgs(query_text="nonexistent xyz123", size=25)
        )

        assert isinstance(result, SearchThirdbridgeResponse)
        assert len(result.response["result"]) == 0

    @pytest.mark.asyncio
    async def test_forwards_filters(self, mock_http_dependencies, sample_api_responses):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_thirdbridge_success"]

        await search_thirdbridge(
            SearchThirdbridgeArgs(
                query_text="pricing",
                company_ids=[100],
                thirdbridge_ids=["tb-1"],
                aiera_event_ids=[9001],
                start_date="2024-01-01",
                end_date="2024-12-31",
                event_content_type="Interview",
                size=25,
            )
        )

        payload = self._payload(mock_http_dependencies)
        assert payload["company_ids"] == [100]
        assert payload["thirdbridge_ids"] == ["tb-1"]
        assert payload["aiera_event_ids"] == [9001]
        assert payload["start_date"] == "2024-01-01"
        assert payload["end_date"] == "2024-12-31"
        assert payload["event_content_type"] == "Interview"

    @pytest.mark.asyncio
    async def test_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        mock_http_dependencies["mock_make_request"].return_value = sample_api_responses[
            "search"
        ]["search_thirdbridge_success"]

        result = await search_thirdbridge(
            SearchThirdbridgeArgs(
                query_text="expert", exclude_instructions=True, size=25
            )
        )

        assert result.instructions == []
