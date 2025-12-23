#!/usr/bin/env python3

"""Unit tests for common models."""

import pytest
import json
from datetime import datetime
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
        citation_data = {
            "title": "Test Citation",
            "url": "https://example.com/document",
            "timestamp": datetime(2024, 1, 15, 14, 30, 0),
            "source": "Test Source",
        }

        citation = CitationInfo(**citation_data)

        assert citation.title == "Test Citation"
        assert citation.url == "https://example.com/document"
        assert citation.timestamp == datetime(2024, 1, 15, 14, 30, 0)
        assert citation.source == "Test Source"

    def test_citation_info_minimal(self):
        """Test CitationInfo with only required fields."""
        citation = CitationInfo(title="Minimal Citation")

        assert citation.title == "Minimal Citation"
        assert citation.url is None
        assert citation.timestamp is None
        assert citation.source is None

    def test_citation_info_datetime_serialization(self):
        """Test that CitationInfo datetime fields are serialized to strings."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            timestamp=test_datetime,
            source="Test Source",
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        # timestamp should be serialized as string, not datetime object
        assert isinstance(serialized["timestamp"], str)
        assert serialized["timestamp"] == test_datetime.isoformat()

    def test_citation_info_optional_timestamp_serialization(self):
        """Test CitationInfo with None timestamp."""
        citation = CitationInfo(
            title="Test Citation",
            url="https://example.com",
            timestamp=None,
            source="Test Source",
        )

        # Test model_dump serialization
        serialized = citation.model_dump()

        # timestamp should remain None when not provided
        assert serialized["timestamp"] is None

    def test_citation_info_json_serialization(self):
        """Test that CitationInfo can be fully serialized to JSON."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        citation = CitationInfo(
            title="JSON Test Citation",
            url="https://example.com/json",
            timestamp=test_datetime,
            source="JSON Test",
        )

        # Test full JSON serialization
        serialized = citation.model_dump()
        json_str = json.dumps(serialized)

        # Should not raise any serialization errors
        assert isinstance(json_str, str)
        assert len(json_str) > 0

        # Verify datetime field was serialized as string in JSON
        parsed = json.loads(json_str)
        assert isinstance(parsed["timestamp"], str)
        assert parsed["timestamp"] == test_datetime.isoformat()


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
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        response = BaseAieraResponse(instructions=["Test instruction"])

        assert response.instructions == ["Test instruction"]
        assert len(response.citation_information) == 1

        # Test serialization
        serialized = response.model_dump()
        json_str = json.dumps(serialized)

        # Should serialize without errors
        assert isinstance(json_str, str)

        # Verify nested datetime serialization
        parsed = json.loads(json_str)
        assert isinstance(parsed["citation_information"][0]["timestamp"], str)

    def test_paginated_response(self):
        """Test PaginatedResponse model."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)

        citation = CitationInfo(title="Paginated Citation", timestamp=test_datetime)

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

        # Test JSON serialization with pagination and datetime
        serialized = response.model_dump()
        json_str = json.dumps(serialized)

        # Should serialize without errors
        assert isinstance(json_str, str)

        # Verify structure and datetime serialization
        parsed = json.loads(json_str)
        assert parsed["total"] == 100
        assert parsed["page"] == 2
        assert isinstance(parsed["citation_information"][0]["timestamp"], str)


@pytest.mark.unit
class TestCommonModelValidation:
    """Test common model validation and edge cases."""

    def test_citation_info_validation(self):
        """Test CitationInfo field validation."""
        # Title is required
        with pytest.raises(ValidationError):
            CitationInfo()  # Missing required title

        # Valid URL formats (basic test)
        citation = CitationInfo(
            title="URL Test", url="https://example.com/path/to/document"
        )
        assert citation.url == "https://example.com/path/to/document"

    def test_datetime_edge_cases(self):
        """Test datetime handling edge cases."""
        # Test with different datetime formats
        formats_to_test = [
            datetime(2024, 1, 1, 0, 0, 0),  # Midnight
            datetime(2024, 12, 31, 23, 59, 59),  # End of year
            datetime(2024, 6, 15, 12, 30, 45, 123456),  # With microseconds
        ]

        for test_dt in formats_to_test:
            citation = CitationInfo(
                title=f"DateTime Test {test_dt.isoformat()}", timestamp=test_dt
            )

            serialized = citation.model_dump()
            json_str = json.dumps(serialized)

            # Should handle all datetime formats
            parsed = json.loads(json_str)
            assert isinstance(parsed["timestamp"], str)
            assert parsed["timestamp"] == test_dt.isoformat()

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
