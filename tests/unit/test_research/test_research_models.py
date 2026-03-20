#!/usr/bin/env python3

"""Unit tests for research models."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.research.models import (
    FindResearchArgs,
    GetResearchArgs,
    FindResearchResponse,
    GetResearchResponse,
)


@pytest.mark.unit
class TestFindResearchArgs:
    """Test FindResearchArgs model."""

    def test_valid_find_research_args_all_fields(self):
        """Test valid FindResearchArgs creation with all fields."""
        args = FindResearchArgs(
            start_date="2024-01-01",
            end_date="2024-12-31",
            author_ids=["12345"],
            aiera_provider_ids=["krypton"],
            regions=["Americas"],
            countries=["US", "GB"],
            search_after=["score1", "id1"],
            page_size=25,
        )

        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.author_ids == ["12345"]
        assert args.aiera_provider_ids == ["krypton"]
        assert args.regions == ["Americas"]
        assert args.countries == ["US", "GB"]
        assert args.search_after == ["score1", "id1"]

    def test_find_research_args_all_optional(self):
        """Test that all FindResearchArgs fields are optional."""
        args = FindResearchArgs()

        assert args.start_date is None
        assert args.end_date is None
        assert args.author_ids is None
        assert args.aiera_provider_ids is None
        assert args.regions is None
        assert args.countries is None
        assert args.search_after is None
        assert args.originating_prompt is None
        assert args.self_identification is None
        assert args.include_base_instructions is True
        assert args.exclude_instructions is False
        assert args.page_size == 25

    def test_find_research_args_with_originating_prompt(self):
        """Test FindResearchArgs with originating_prompt field."""
        args = FindResearchArgs(
            originating_prompt="Find recent research on AI trends",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "Find recent research on AI trends"
        assert args.include_base_instructions is False

    def test_find_research_args_partial_filters(self):
        """Test FindResearchArgs with only some filters set."""
        args = FindResearchArgs(
            start_date="2024-06-01",
        )

        assert args.start_date == "2024-06-01"
        assert args.end_date is None

    def test_find_research_args_numeric_string_coercion(self):
        """Test that numeric fields accept string values."""
        args = FindResearchArgs(
            page_size="25",
        )

        assert args.page_size == 25

    def test_find_research_args_search_after(self):
        """Test that search_after accepts array values for cursor-based pagination."""
        args = FindResearchArgs(
            search_after=["1234567890", "abc123"],
        )
        assert args.search_after == ["1234567890", "abc123"]


@pytest.mark.unit
class TestGetResearchArgs:
    """Test GetResearchArgs model."""

    def test_valid_get_research_args(self):
        """Test valid GetResearchArgs creation."""
        args = GetResearchArgs(document_id="8001234")

        assert args.document_id == "8001234"

    def test_get_research_args_required_field(self):
        """Test that document_id is required."""
        with pytest.raises(ValidationError):
            GetResearchArgs()

    def test_get_research_args_with_originating_prompt(self):
        """Test GetResearchArgs with originating_prompt field."""
        args = GetResearchArgs(
            document_id="8001234",
            originating_prompt="Get details on this research report",
            include_base_instructions=False,
        )

        assert args.document_id == "8001234"
        assert args.originating_prompt == "Get details on this research report"
        assert args.include_base_instructions is False

    def test_get_research_args_defaults(self):
        """Test GetResearchArgs default values."""
        args = GetResearchArgs(document_id="123")

        assert args.originating_prompt is None
        assert args.self_identification is None
        assert args.include_base_instructions is True
        assert args.exclude_instructions is False


@pytest.mark.unit
class TestResearchResponses:
    """Test research response models."""

    def test_find_research_response(self):
        """Test FindResearchResponse model."""
        response = FindResearchResponse(
            instructions=["Test instruction"],
            response=[{"research_id": "123", "title": "Test Report"}],
        )

        assert response.instructions == ["Test instruction"]
        assert response.response is not None
        assert len(response.response) == 1

    def test_get_research_response(self):
        """Test GetResearchResponse model."""
        response = GetResearchResponse(
            instructions=["Test instruction"],
            response=[{"research_id": "123", "title": "Test Report"}],
        )

        assert response.instructions == ["Test instruction"]
        assert response.response is not None

    def test_find_research_response_null(self):
        """Test FindResearchResponse with null response."""
        response = FindResearchResponse(
            instructions=[],
            response=None,
        )
        assert response.response is None

    def test_get_research_response_null(self):
        """Test GetResearchResponse with null response."""
        response = GetResearchResponse(
            instructions=[],
            response=None,
        )
        assert response.response is None


@pytest.mark.unit
class TestResearchModelSerialization:
    """Test serialization of research models."""

    def test_find_research_args_json_schema(self):
        """Test that FindResearchArgs generates valid JSON schema."""
        schema = FindResearchArgs.model_json_schema()

        assert "properties" in schema
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]
        assert "author_ids" in schema["properties"]
        assert "aiera_provider_ids" in schema["properties"]
        assert "regions" in schema["properties"]
        assert "countries" in schema["properties"]
        assert "search_after" in schema["properties"]
        assert "page_size" in schema["properties"]
        # Equity/group filter fields should be present
        assert "bloomberg_ticker" in schema["properties"]
        assert "index_id" in schema["properties"]
        assert "watchlist_id" in schema["properties"]
        assert "sector_id" in schema["properties"]
        assert "subsector_id" in schema["properties"]
        # page is not present (uses cursor-based pagination via search_after)
        assert "page" not in schema["properties"]

    def test_get_research_args_json_schema(self):
        """Test that GetResearchArgs generates valid JSON schema."""
        schema = GetResearchArgs.model_json_schema()

        assert "properties" in schema
        assert "document_id" in schema["properties"]

    def test_find_research_args_excludes_none(self):
        """Test that model_dump excludes None fields."""
        args = FindResearchArgs(start_date="2024-01-01")
        dumped = args.model_dump(exclude_none=True)

        assert "start_date" in dumped
        assert "end_date" not in dumped
        assert "search_after" not in dumped
        assert "author_ids" not in dumped
