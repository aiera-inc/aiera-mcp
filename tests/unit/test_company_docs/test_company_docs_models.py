#!/usr/bin/env python3

"""Unit tests for company_docs models."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.company_docs.models import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    FindCompanyDocsResponse,
    GetCompanyDocResponse,
    GetCompanyDocCategoriesResponse,
    GetCompanyDocKeywordsResponse,
)


@pytest.mark.unit
class TestFindCompanyDocsArgs:
    """Test FindCompanyDocsArgs model."""

    def test_valid_find_company_docs_args(self):
        """Test valid FindCompanyDocsArgs creation."""
        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            bloomberg_ticker="AAPL:US",
            categories="Sustainability,Governance",
            keywords="ESG,climate",
            page=1,
            page_size=25,
        )

        assert args.start_date == "2023-09-01"
        assert args.end_date == "2023-09-30"
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.categories == "Sustainability,Governance"
        assert args.keywords == "ESG,climate"
        assert args.page == 1
        assert args.page_size == 25

    def test_find_company_docs_args_defaults(self):
        """Test FindCompanyDocsArgs with default values."""
        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        assert args.page == 1  # Default value
        assert args.page_size == 25  # Default value
        assert args.bloomberg_ticker is None
        assert args.watchlist_id is None
        assert args.categories is None
        assert args.keywords is None
        assert args.originating_prompt is None  # Default value
        assert args.include_base_instructions is True  # Default value

    def test_find_company_docs_args_with_originating_prompt(self):
        """Test FindCompanyDocsArgs with originating_prompt field."""
        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            originating_prompt="Find sustainability reports for Apple",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "Find sustainability reports for Apple"
        assert args.include_base_instructions is False

    def test_find_company_docs_args_date_format_validation(self):
        """Test date format validation."""
        # Valid date format
        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")
        assert args.start_date == "2023-09-01"

        # Invalid date formats should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            FindCompanyDocsArgs(start_date="09/01/2023", end_date="2023-09-30")

        assert "String should match pattern" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            FindCompanyDocsArgs(start_date="2023-09-01", end_date="invalid-date")

        assert "String should match pattern" in str(exc_info.value)

    def test_find_company_docs_args_pagination_validation(self):
        """Test pagination parameter validation."""
        # Valid pagination
        args = FindCompanyDocsArgs(
            start_date="2023-09-01", end_date="2023-09-30", page=5, page_size=25
        )
        assert args.page == 5
        assert args.page_size == 25

        # Page must be >= 1
        with pytest.raises(ValidationError):
            FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30", page=0)

        # Page size must be >= 1
        with pytest.raises(ValidationError):
            FindCompanyDocsArgs(
                start_date="2023-09-01", end_date="2023-09-30", page_size=0
            )

        # page_size above 25 is accepted (capped server-side)
        args = FindCompanyDocsArgs(
            start_date="2023-09-01", end_date="2023-09-30", page_size=26
        )
        assert args.page_size == 26

    @pytest.mark.parametrize(
        "field_name,field_value",
        [
            ("watchlist_id", 123),
            ("index_id", 456),
            ("sector_id", 789),
            ("subsector_id", 101),
        ],
    )
    def test_find_company_docs_args_numeric_field_serialization(
        self, field_name, field_value
    ):
        """Test that numeric fields are serialized as strings."""
        args_data = {
            "start_date": "2023-09-01",
            "end_date": "2023-09-30",
            field_name: field_value,
        }
        args = FindCompanyDocsArgs(**args_data)

        # Model dump should serialize numeric fields as strings
        dumped = args.model_dump(exclude_none=True)
        assert dumped[field_name] == str(field_value)

    def test_bloomberg_ticker_validation(self):
        """Test Bloomberg ticker format validation."""
        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            bloomberg_ticker="AAPL",  # Missing :US
        )

        # Check if ticker correction is applied
        assert args.bloomberg_ticker in ["AAPL", "AAPL:US"]

    def test_categories_keywords_validation(self):
        """Test categories and keywords format validation."""
        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            categories="Sustainability, Governance",  # With spaces
            keywords="ESG, climate",  # With spaces
        )

        # Check if format correction is applied
        assert args.categories in [
            "Sustainability, Governance",
            "Sustainability,Governance",
        ]
        assert args.keywords in ["ESG, climate", "ESG,climate"]


@pytest.mark.unit
class TestGetCompanyDocArgs:
    """Test GetCompanyDocArgs model."""

    def test_valid_get_company_doc_args(self):
        """Test valid GetCompanyDocArgs creation."""
        args = GetCompanyDocArgs(company_doc_id="doc123")
        assert args.company_doc_id == "doc123"
        assert args.originating_prompt is None
        assert args.include_base_instructions is True

    def test_get_company_doc_args_with_originating_prompt(self):
        """Test GetCompanyDocArgs with originating_prompt field."""
        args = GetCompanyDocArgs(
            company_doc_id="doc123",
            originating_prompt="Get document details",
            include_base_instructions=False,
        )
        assert args.originating_prompt == "Get document details"
        assert args.include_base_instructions is False

    def test_get_company_doc_args_required_field(self):
        """Test that company_doc_id is required."""
        with pytest.raises(ValidationError):
            GetCompanyDocArgs()  # Missing required field


@pytest.mark.unit
class TestCompanyDocsResponses:
    """Test company_docs response models with pass-through pattern."""

    def test_find_company_docs_response(self):
        """Test FindCompanyDocsResponse model with pass-through data."""
        response = FindCompanyDocsResponse(
            instructions=["Test instruction"],
            response={
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
                "data": [
                    {
                        "doc_id": 123,
                        "company": {"company_id": 456, "name": "Test Company"},
                        "title": "Test Document",
                        "category": "Sustainability",
                        "publish_date": "2023-09-15T00:00:00Z",
                    }
                ],
            },
        )

        assert response.response is not None
        assert len(response.response["data"]) == 1
        assert response.response["pagination"]["total_count"] == 1
        assert response.instructions == ["Test instruction"]

    def test_get_company_doc_response(self):
        """Test GetCompanyDocResponse model with pass-through data."""
        response = GetCompanyDocResponse(
            response={
                "data": [
                    {
                        "doc_id": 123,
                        "company": {"company_id": 456, "name": "Test Company"},
                        "title": "Test Document",
                        "content_raw": "Test preview",
                    }
                ]
            },
            instructions=["Test instruction"],
        )

        assert response.response is not None
        assert response.response["data"][0]["doc_id"] == 123
        assert response.instructions == ["Test instruction"]

    def test_get_company_doc_response_none(self):
        """Test GetCompanyDocResponse with None response."""
        response = GetCompanyDocResponse(
            response=None,
            instructions=["Document not found"],
        )

        assert response.response is None
        assert response.instructions == ["Document not found"]

    def test_get_company_doc_categories_response(self):
        """Test GetCompanyDocCategoriesResponse model with pass-through data."""
        response = GetCompanyDocCategoriesResponse(
            response={
                "pagination": {
                    "total_count": 2,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
                "data": {"sustainability": 25, "governance": 18},
            },
            instructions=["Categories retrieved"],
        )

        assert response.response is not None
        assert response.response["data"]["sustainability"] == 25
        assert response.response["data"]["governance"] == 18
        assert response.response["pagination"]["total_count"] == 2
        assert response.instructions == ["Categories retrieved"]

    def test_get_company_doc_keywords_response(self):
        """Test GetCompanyDocKeywordsResponse model with pass-through data."""
        response = GetCompanyDocKeywordsResponse(
            response={
                "pagination": {
                    "total_count": 2,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 25,
                },
                "data": {"ESG": 15, "climate": 23},
            },
            instructions=["Keywords retrieved"],
        )

        assert response.response is not None
        assert response.response["data"]["ESG"] == 15
        assert response.response["data"]["climate"] == 23
        assert response.response["pagination"]["total_count"] == 2
        assert response.instructions == ["Keywords retrieved"]


@pytest.mark.unit
class TestCompanyDocsModelValidation:
    """Test company_docs model validation and edge cases."""

    def test_model_serialization_roundtrip(self):
        """Test model serialization and deserialization."""
        original_args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            bloomberg_ticker="AAPL:US",
            categories="Sustainability",
            keywords="ESG",
            page=2,
            page_size=25,
        )

        # Serialize to dict
        serialized = original_args.model_dump()

        # Deserialize back to model
        deserialized_args = FindCompanyDocsArgs(**serialized)

        # Verify round-trip
        assert original_args.start_date == deserialized_args.start_date
        assert original_args.end_date == deserialized_args.end_date
        assert original_args.bloomberg_ticker == deserialized_args.bloomberg_ticker
        assert original_args.categories == deserialized_args.categories
        assert original_args.keywords == deserialized_args.keywords
        assert original_args.page == deserialized_args.page
        assert original_args.page_size == deserialized_args.page_size

    def test_json_schema_generation(self):
        """Test that models can generate JSON schemas."""
        schema = FindCompanyDocsArgs.model_json_schema()

        assert "properties" in schema
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]
        assert "categories" in schema["properties"]
        assert "keywords" in schema["properties"]

        # Check that required fields are marked as required
        assert "start_date" in schema["required"]
        assert "end_date" in schema["required"]
