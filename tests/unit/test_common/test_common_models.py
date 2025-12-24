#!/usr/bin/env python3

"""Unit tests for common models."""

import pytest
import json
from pydantic import ValidationError

from aiera_mcp.tools.common.models import (
    CitationInfo,
    BaseAieraResponse,
    PaginatedResponse,
    BaseAieraArgs,
    EmptyArgs,
    SearchArgs,
)


@pytest.mark.unit
class TestCitationInfo:
    """Test CitationInfo model."""

    def test_citation_info_creation(self):
        """Test CitationInfo model creation."""
        from aiera_mcp.tools.common.models import CitationMetadata

        citation_data = {
            "title": "Test Citation",
            "url": "https://example.com/document",
            "metadata": CitationMetadata(type="event", company_id=123),
        }

        citation = CitationInfo(**citation_data)

        assert citation.title == "Test Citation"
        assert citation.url == "https://example.com/document"
        assert citation.metadata.type == "event"
        assert citation.metadata.company_id == 123

    def test_citation_info_minimal(self):
        """Test CitationInfo with only optional fields."""
        citation = CitationInfo(title="Minimal Citation")

        assert citation.title == "Minimal Citation"
        assert citation.url is None
        assert citation.metadata is None

    def test_citation_info_with_metadata(self):
        """Test CitationInfo with metadata."""
        from aiera_mcp.tools.common.models import CitationMetadata

        metadata = CitationMetadata(
            type="filing",
            url_target="aiera",
            company_id=456,
            filing_id=789,
        )

        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            metadata=metadata,
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        assert serialized["title"] == "Test Citation"
        assert serialized["url"] == "https://example.com"
        assert serialized["metadata"]["type"] == "filing"
        assert serialized["metadata"]["company_id"] == 456

    def test_citation_info_optional_metadata_serialization(self):
        """Test CitationInfo with None metadata."""
        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            metadata=None,
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        # metadata should remain None when not provided
        assert serialized["metadata"] is None

    def test_citation_info_json_serialization(self):
        """Test that CitationInfo can be fully serialized to JSON."""
        from aiera_mcp.tools.common.models import CitationMetadata

        citation = CitationInfo(
            title="JSON Test Citation",
            url="https://example.com/json",
            metadata=CitationMetadata(type="event", event_id=123),
        )

        # Test full JSON serialization
        serialized = citation.model_dump()
        json_str = json.dumps(serialized)

        # Should not raise any serialization errors
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Verify structure in JSON
        parsed = json.loads(json_str)
        assert parsed["title"] == "JSON Test Citation"
        assert parsed["metadata"]["type"] == "event"


@pytest.mark.unit
class TestBaseModels:
    """Test base model classes."""

    def test_base_aiera_args(self):
        """Test BaseAieraArgs model."""
        args = BaseAieraArgs()
        assert isinstance(args, BaseAieraArgs)

    def test_empty_args(self):
        """Test EmptyArgs model."""
        args = EmptyArgs()
        assert isinstance(args, EmptyArgs)
        assert isinstance(args, BaseAieraArgs)

    def test_search_args(self):
        """Test SearchArgs model."""
        # With all fields
        args = SearchArgs(search="test query", page=2, page_size=25)
        assert args.search == "test query"
        assert args.page == 2
        assert args.page_size == 25

        # With defaults
        args_default = SearchArgs()
        assert args_default.search is None
        assert args_default.page == 1
        assert args_default.page_size == 50

    def test_base_aiera_response(self):
        """Test BaseAieraResponse model."""
        response = BaseAieraResponse(instructions=["Test instruction"])

        assert response.instructions == ["Test instruction"]
        assert response.error is None

        # Test serialization
        serialized = response.model_dump()
        json_str = json.dumps(serialized)

        # Should serialize without errors
        assert isinstance(json_str, str)

        # Verify structure
        parsed = json.loads(json_str)
        assert parsed["instructions"] == ["Test instruction"]

    def test_paginated_response(self):
        """Test PaginatedResponse model."""
        response = PaginatedResponse(
            total=100,
            page=2,
            page_size=25,
            instructions=["Paginated results"],
        )

        assert response.total == 100
        assert response.page == 2
        assert response.page_size == 25
        assert response.instructions == ["Paginated results"]

        # Test JSON serialization with pagination
        serialized = response.model_dump()
        json_str = json.dumps(serialized)

        # Should serialize without errors
        assert isinstance(json_str, str)

        # Verify structure
        parsed = json.loads(json_str)
        assert parsed["total"] == 100
        assert parsed["page"] == 2
        assert parsed["page_size"] == 25


@pytest.mark.unit
class TestCommonModelValidation:
    """Test common model validation and edge cases."""

    def test_citation_info_validation(self):
        """Test CitationInfo field validation."""
        # All fields are optional in CitationInfo
        citation = CitationInfo()
        assert citation.title is None

        # Valid URL formats (basic test)
        citation = CitationInfo(
            title="URL Test", url="https://example.com/path/to/document"
        )
        assert citation.url == "https://example.com/path/to/document"

    def test_citation_metadata_edge_cases(self):
        """Test CitationMetadata handling edge cases."""
        from aiera_mcp.tools.common.models import CitationMetadata

        # Test with different metadata configurations
        configs_to_test = [
            {"type": "event", "event_id": 123},
            {"type": "filing", "filing_id": 456, "company_id": 789},
            {"type": "company_doc", "company_doc_id": 101, "url_target": "aiera"},
        ]

        for config in configs_to_test:
            metadata = CitationMetadata(**config)
            citation = CitationInfo(title=f"Test {config['type']}", metadata=metadata)

            serialized = citation.model_dump()
            json_str = json.dumps(serialized)

            # Should handle all configurations
            parsed = json.loads(json_str)
            assert parsed["metadata"]["type"] == config["type"]

    def test_model_inheritance(self):
        """Test model inheritance relationships."""
        # PaginatedResponse should inherit from BaseAieraResponse
        response = PaginatedResponse(total=10, page=1, page_size=10)
        assert isinstance(response, BaseAieraResponse)
        assert isinstance(response, PaginatedResponse)

        # EmptyArgs should inherit from BaseAieraArgs
        args = EmptyArgs()
        assert isinstance(args, BaseAieraArgs)
        assert isinstance(args, EmptyArgs)

        # SearchArgs should inherit from BaseAieraArgs
        search_args = SearchArgs()
        assert isinstance(search_args, BaseAieraArgs)
        assert isinstance(search_args, SearchArgs)
