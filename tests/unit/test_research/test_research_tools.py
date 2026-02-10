#!/usr/bin/env python3

"""Unit tests for research tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
import asyncio

from aiera_mcp.tools.research.tools import find_research, get_research
from aiera_mcp.tools.research.models import (
    FindResearchArgs,
    GetResearchArgs,
    FindResearchResponse,
    GetResearchResponse,
)


@pytest.mark.unit
class TestFindResearch:
    """Test the find_research tool."""

    @pytest.mark.asyncio
    async def test_find_research_success(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test successful research search."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = FindResearchArgs(
            search="cloud computing",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        assert result.response is not None
        assert len(result.response["result"]) == 1

        # Check first result
        first_result = result.response["result"][0]
        assert first_result["_score"] > 0
        assert first_result["title"] == "Amazon.com Inc - Research Report"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "/chat-support/search/research"

    @pytest.mark.asyncio
    async def test_find_research_with_all_filters(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with all filter parameters."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = FindResearchArgs(
            search="AI",
            start_date="2024-01-01",
            end_date="2024-12-31",
            asset_classes=["FixedIncome"],
            asset_types=["CorporateHighYieldCredit"],
            author="Neha Khoda",
            aiera_provider_id="krypton",
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        # The search text should be in the hybrid query
        assert "hybrid" in str(data["query"])
        # The date range filter should be in must clauses
        must_clauses = data["post_filter"]["bool"]["must"]
        date_filter = [c for c in must_clauses if "range" in str(c)]
        assert len(date_filter) > 0
        # The asset_classes filter should be in must clauses
        asset_class_filter = [c for c in must_clauses if "asset_classes" in str(c)]
        assert len(asset_class_filter) > 0
        # The asset_types filter should be in must clauses
        asset_type_filter = [c for c in must_clauses if "asset_types" in str(c)]
        assert len(asset_type_filter) > 0
        # The author filter should be in must clauses
        author_filter = [c for c in must_clauses if "authors.display_name" in str(c)]
        assert len(author_filter) > 0
        # The aiera_provider_id filter should be in must clauses
        provider_filter = [c for c in must_clauses if "aiera_provider_id" in str(c)]
        assert len(provider_filter) > 0

    @pytest.mark.asyncio
    async def test_find_research_with_asset_classes(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with asset_classes filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = FindResearchArgs(
            asset_classes=["FixedIncome", "Equity"],
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        asset_filter = [c for c in must_clauses if "asset_classes" in str(c)]
        assert len(asset_filter) == 1
        assert asset_filter[0]["terms"]["asset_classes"] == ["FixedIncome", "Equity"]

    @pytest.mark.asyncio
    async def test_find_research_with_author(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with author filter."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = FindResearchArgs(
            author="Jim Reid",
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        must_clauses = data["post_filter"]["bool"]["must"]
        author_filter = [c for c in must_clauses if "authors.display_name" in str(c)]
        assert len(author_filter) == 1
        assert author_filter[0]["match"]["authors.display_name"] == "Jim Reid"

    @pytest.mark.asyncio
    async def test_find_research_no_filters(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with no filters."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = FindResearchArgs()

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        data = call_args[1]["data"]
        # No must clauses when no filters provided
        must_clauses = data["post_filter"]["bool"]["must"]
        assert len(must_clauses) == 0

    @pytest.mark.asyncio
    async def test_find_research_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with exclude_instructions."""
        search_responses = sample_api_responses.get("search", {})
        mock_http_dependencies["mock_make_request"].return_value = search_responses[
            "search_research_chunks_success"
        ]

        args = FindResearchArgs(
            search="test",
            exclude_instructions=True,
        )

        result = await find_research(args)

        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_find_research_empty_results(self, mock_http_dependencies):
        """Test find_research with no results."""
        empty_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = FindResearchArgs(search="nonexistent xyz123")

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        assert result.response is not None
        assert len(result.response["result"]) == 0

    @pytest.mark.asyncio
    async def test_find_research_fallback_on_timeout(self, mock_http_dependencies):
        """Test that find_research falls back to standard search on timeout."""
        # Setup - first call times out, second succeeds
        fallback_response = {
            "instructions": [],
            "response": {"result": []},
        }
        mock_http_dependencies["mock_make_request"].side_effect = [
            asyncio.TimeoutError("ML inference timed out"),
            fallback_response,
        ]

        args = FindResearchArgs(
            search="test query",
        )

        # Execute
        result = await find_research(args)

        # Verify fallback was used (2 calls made)
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        assert isinstance(result, FindResearchResponse)

    @pytest.mark.asyncio
    async def test_find_research_fallback_uses_correct_endpoint(
        self, mock_http_dependencies
    ):
        """Test that find_research fallback uses the correct research endpoint."""
        # Setup - first call returns empty, triggering fallback
        mock_http_dependencies["mock_make_request"].side_effect = [
            {"response": {}},  # Empty response triggers fallback
            {"instructions": [], "response": {"result": []}},
        ]

        args = FindResearchArgs(
            search="test query",
        )

        # Execute
        result = await find_research(args)

        # Verify both calls used the research endpoint
        assert mock_http_dependencies["mock_make_request"].call_count == 2
        for call in mock_http_dependencies["mock_make_request"].call_args_list:
            assert call[1]["endpoint"] == "/chat-support/search/research"


@pytest.mark.unit
class TestGetResearch:
    """Test the get_research tool."""

    @pytest.mark.asyncio
    async def test_get_research_success(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test successful research retrieval."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "get_research_success"
        ]

        args = GetResearchArgs(research_id="8001234")

        result = await get_research(args)

        assert isinstance(result, GetResearchResponse)
        assert result.response is not None
        assert result.response["research_id"] == 8001234
        assert (
            result.response["title"]
            == "Amazon Web Services: Cloud Computing Growth Outlook"
        )

        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/get-research"

    @pytest.mark.asyncio
    async def test_get_research_passes_research_id(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test that get_research passes research_id in params."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "get_research_success"
        ]

        args = GetResearchArgs(research_id="8001234")

        await get_research(args)

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["research_id"] == "8001234"

    @pytest.mark.asyncio
    async def test_get_research_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test get_research with exclude_instructions."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "get_research_success"
        ]

        args = GetResearchArgs(
            research_id="8001234",
            exclude_instructions=True,
        )

        result = await get_research(args)

        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_get_research_with_originating_prompt(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test get_research with originating_prompt."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "get_research_success"
        ]

        args = GetResearchArgs(
            research_id="8001234",
            originating_prompt="What does this research report say?",
        )

        await get_research(args)

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["originating_prompt"] == "What does this research report say?"


@pytest.mark.unit
class TestResearchToolsErrorHandling:
    """Test error handling for research tools."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, ValueError])
    async def test_find_research_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated from find_research.

        Note: TimeoutError is handled specially - find_research catches it and
        falls back to standard search, so it's not tested here.
        """
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = FindResearchArgs(search="test")

        with pytest.raises(exception_type):
            await find_research(args)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception_type", [ConnectionError, ValueError, TimeoutError]
    )
    async def test_get_research_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated from get_research."""
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

        args = GetResearchArgs(research_id="123")

        with pytest.raises(exception_type):
            await get_research(args)
