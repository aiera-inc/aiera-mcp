#!/usr/bin/env python3

"""Unit tests for research tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

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
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "find_research_success"
        ]

        args = FindResearchArgs(
            search="cloud computing",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        assert result.response is not None
        assert len(result.response["data"]) == 2
        assert (
            result.response["data"][0]["title"]
            == "Amazon Web Services: Cloud Computing Growth Outlook"
        )

        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-research"

    @pytest.mark.asyncio
    async def test_find_research_with_all_filters(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with all filter parameters."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "find_research_success"
        ]

        args = FindResearchArgs(
            search="AI",
            author_person_ids="5001,5002",
            organization_names="Goldman Sachs,Morgan Stanley",
            region_types="North America",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["search"] == "AI"
        assert params["author_person_ids"] == "5001,5002"
        assert params["organization_names"] == "Goldman Sachs,Morgan Stanley"
        assert params["region_types"] == "North America"
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-12-31"

    @pytest.mark.asyncio
    async def test_find_research_no_filters(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with no filters."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "find_research_success"
        ]

        args = FindResearchArgs()

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        # None fields should be excluded
        assert "search" not in params
        assert "author_person_ids" not in params
        assert "organization_names" not in params
        assert "region_types" not in params
        assert "start_date" not in params
        assert "end_date" not in params

    @pytest.mark.asyncio
    async def test_find_research_exclude_instructions(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test find_research with exclude_instructions."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "find_research_success"
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
            "response": {
                "pagination": {
                    "total_count": 0,
                    "current_page": 1,
                    "total_pages": 0,
                    "page_size": 50,
                },
                "data": [],
            },
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = FindResearchArgs(search="nonexistent xyz123")

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        assert result.response is not None
        assert len(result.response["data"]) == 0


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
    @pytest.mark.parametrize(
        "exception_type", [ConnectionError, ValueError, TimeoutError]
    )
    async def test_find_research_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated from find_research."""
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
