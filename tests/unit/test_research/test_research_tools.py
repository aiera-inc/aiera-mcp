#!/usr/bin/env python3

"""Unit tests for research tools."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from aiera_mcp.tools.research.tools import (
    find_research,
    get_research,
    get_research_providers,
)
from aiera_mcp.tools.research.models import (
    FindResearchArgs,
    GetResearchArgs,
    GetResearchProvidersArgs,
    FindResearchResponse,
    GetResearchResponse,
    GetResearchProvidersResponse,
)


# Sample response matching the /find-research endpoint format (cursor-based pagination)
FIND_RESEARCH_RESPONSE = {
    "instructions": [
        "This data is provided for institutional finance professionals...",
    ],
    "response": {
        "result": [
            {
                "research_id": "8001234",
                "document_id": "D001",
                "aiera_provider_id": "krypton",
                "title": "Amazon.com Inc - Research Report",
                "abstract": None,
                "published_datetime": "2024-06-15T00:00:00",
                "organization_name": "Goldman Sachs",
                "organization_type": "Broker",
                "product_category": "Research",
                "product_focus": "Equity",
                "language": "English",
                "page_count": 12,
                "subjects": ["Technology"],
                "asset_classes": ["Equity"],
                "asset_types": [],
                "authors": [
                    {
                        "name": "Jane Smith",
                        "author_id": "5001",
                    }
                ],
                "regions": [],
                "countries": [{"code": "US", "primary_indicator": True}],
                "citation_information": {
                    "title": "Amazon.com Inc - Research Report",
                    "url": "https://example.com/research/8001234",
                    "metadata": {
                        "type": "research",
                        "url_target": "aiera",
                        "document_id": "D001",
                    },
                },
            }
        ],
        "pagination": {
            "total": 1,
            "page_size": 50,
            "has_next_page": False,
            "next_search_after": None,
        },
    },
}


@pytest.mark.unit
class TestFindResearch:
    """Test the find_research tool."""

    @pytest.mark.asyncio
    async def test_find_research_success(self, mock_http_dependencies):
        """Test successful research search."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs(
            start_date="2024-01-01",
            end_date="2024-12-31",
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        assert result.response is not None
        assert len(result.response["result"]) == 1

        # Check first result
        first_result = result.response["result"][0]
        assert first_result["title"] == "Amazon.com Inc - Research Report"
        assert first_result["research_id"] == "8001234"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-research"

    @pytest.mark.asyncio
    async def test_find_research_with_author_ids(self, mock_http_dependencies):
        """Test find_research maps author_ids to author_person_ids."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs(
            author_ids=["12345", "67890"],
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        # Should be mapped to author_person_ids as comma-separated string
        assert "author_person_ids" in params
        assert params["author_person_ids"] == "12345,67890"
        # Original key should be removed
        assert "author_ids" not in params

    @pytest.mark.asyncio
    async def test_find_research_with_provider_ids(self, mock_http_dependencies):
        """Test find_research maps aiera_provider_ids to provider_ids."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs(
            aiera_provider_ids=["krypton", "krypton-test"],
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        # Should be mapped to provider_ids as comma-separated string
        assert "provider_ids" in params
        assert params["provider_ids"] == "krypton,krypton-test"
        # Original key should be removed
        assert "aiera_provider_ids" not in params

    @pytest.mark.asyncio
    async def test_find_research_with_regions_and_countries(
        self, mock_http_dependencies
    ):
        """Test find_research maps regions and countries to comma-separated strings."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs(
            regions=["Americas", "EMEA"],
            countries=["US", "GB"],
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["regions"] == "Americas,EMEA"
        assert params["countries"] == "US,GB"

    @pytest.mark.asyncio
    async def test_find_research_with_search_after(self, mock_http_dependencies):
        """Test find_research with search_after cursor pagination."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs(
            search_after=["1234567890", "abc123"],
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["search_after"] == "1234567890,abc123"

    @pytest.mark.asyncio
    async def test_find_research_with_all_filters(self, mock_http_dependencies):
        """Test find_research with all filter parameters."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs(
            start_date="2024-01-01",
            end_date="2024-12-31",
            author_ids=["12345"],
            aiera_provider_ids=["krypton"],
            regions=["Americas"],
            countries=["US"],
            page_size=25,
        )

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-12-31"
        assert params["author_person_ids"] == "12345"
        assert params["provider_ids"] == "krypton"
        assert params["regions"] == "Americas"
        assert params["countries"] == "US"

    @pytest.mark.asyncio
    async def test_find_research_no_filters(self, mock_http_dependencies):
        """Test find_research with no filters."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs()

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        # Should only have defaults (page_size, include_base_instructions)
        assert "start_date" not in params
        assert "search_after" not in params

    @pytest.mark.asyncio
    async def test_find_research_exclude_instructions(self, mock_http_dependencies):
        """Test find_research with exclude_instructions."""
        mock_http_dependencies["mock_make_request"].return_value = (
            FIND_RESEARCH_RESPONSE
        )

        args = FindResearchArgs(
            start_date="2024-01-01",
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
                "result": [],
                "pagination": {
                    "total": 0,
                    "page_size": 50,
                    "has_next_page": False,
                    "next_search_after": None,
                },
            },
        }
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = FindResearchArgs(start_date="2024-01-01")

        result = await find_research(args)

        assert isinstance(result, FindResearchResponse)
        assert result.response is not None
        assert len(result.response["result"]) == 0


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

        args = GetResearchArgs(document_id="8001234")

        result = await get_research(args)

        assert isinstance(result, GetResearchResponse)
        assert result.response is not None

        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-research"

    @pytest.mark.asyncio
    async def test_get_research_passes_document_id_and_include_content(
        self, mock_http_dependencies, sample_api_responses
    ):
        """Test that get_research passes document_id and include_content in params."""
        research_responses = sample_api_responses.get("research", {})
        mock_http_dependencies["mock_make_request"].return_value = research_responses[
            "get_research_success"
        ]

        args = GetResearchArgs(document_id="8001234")

        await get_research(args)

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["document_id"] == "8001234"
        assert params["include_content"] == "true"

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
            document_id="8001234",
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
            document_id="8001234",
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

        args = FindResearchArgs(start_date="2024-01-01")

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

        args = GetResearchArgs(document_id="123")

        with pytest.raises(exception_type):
            await get_research(args)


@pytest.mark.unit
class TestGetResearchProviders:
    """Test the get_research_providers tool."""

    @pytest.mark.asyncio
    async def test_get_research_providers_success(self, mock_http_dependencies):
        """Test successful research providers retrieval."""
        providers_response = {
            "instructions": [
                "This data is provided for institutional finance professionals...",
            ],
            "response": [
                {
                    "provider_id": "krypton",
                    "name": "Krypton Research",
                    "description": "Independent research provider",
                },
                {
                    "provider_id": "acme",
                    "name": "Acme Analytics",
                    "description": "Global equity research",
                },
            ],
        }
        mock_http_dependencies["mock_make_request"].return_value = providers_response

        args = GetResearchProvidersArgs()

        result = await get_research_providers(args)

        assert isinstance(result, GetResearchProvidersResponse)
        assert result.response is not None
        assert len(result.response) == 2
        assert result.response[0]["provider_id"] == "krypton"
        assert result.response[1]["name"] == "Acme Analytics"

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/get-research-providers"

    @pytest.mark.asyncio
    async def test_get_research_providers_exclude_instructions(
        self, mock_http_dependencies
    ):
        """Test get_research_providers with exclude_instructions."""
        providers_response = {
            "instructions": [
                "This data is provided for institutional finance professionals...",
            ],
            "response": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = providers_response

        args = GetResearchProvidersArgs(exclude_instructions=True)

        result = await get_research_providers(args)

        assert isinstance(result, GetResearchProvidersResponse)
        assert result.instructions == []

    @pytest.mark.asyncio
    async def test_get_research_providers_with_originating_prompt(
        self, mock_http_dependencies
    ):
        """Test get_research_providers passes originating_prompt."""
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "response": [],
        }

        args = GetResearchProvidersArgs(
            originating_prompt="What research providers are available?"
        )

        await get_research_providers(args)

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["originating_prompt"] == "What research providers are available?"

    @pytest.mark.asyncio
    async def test_get_research_providers_empty_response(self, mock_http_dependencies):
        """Test get_research_providers with empty response."""
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "response": [],
        }

        args = GetResearchProvidersArgs()

        result = await get_research_providers(args)

        assert isinstance(result, GetResearchProvidersResponse)
        assert result.response == []
