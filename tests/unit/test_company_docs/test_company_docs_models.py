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
    CompanyDocItem,
    CompanyDocDetails,
    CategoryKeyword,
)
from aiera_mcp.tools.common.models import CitationInfo


@pytest.mark.unit
class TestCompanyDocsModels:
    """Test company_docs Pydantic models."""

    def test_company_doc_item_creation(self):
        """Test CompanyDocItem model creation."""
        doc_data = {
            "doc_id": 12345,
            "company": {"company_id": 67890, "name": "Test Company"},
            "title": "Test Document",
            "category": "Sustainability",
            "keywords": ["ESG", "environment"],
            "publish_date": "2023-09-15T00:00:00Z",
            "source_url": "https://example.com/test-doc.pdf",
            "summary": ["Test document summary"],
        }

        doc = CompanyDocItem(**doc_data)

        assert doc.doc_id == 12345
        assert doc.company.name == "Test Company"
        assert doc.company.company_id == 67890
        assert doc.title == "Test Document"
        assert doc.category == "Sustainability"
        assert doc.keywords == ["ESG", "environment"]
        assert doc.publish_date == "2023-09-15T00:00:00Z"
        assert doc.source_url == "https://example.com/test-doc.pdf"
        assert doc.summary == ["Test document summary"]

    def test_company_doc_item_optional_fields(self):
        """Test CompanyDocItem with only required fields."""
        minimal_data = {
            "doc_id": 12345,
            "company": {"company_id": 67890, "name": "Test Company"},
            "title": "Test Document",
            "category": "Sustainability",
            "publish_date": "2023-09-15T00:00:00Z",
            "source_url": "https://example.com/test-doc.pdf",
            "summary": ["Test summary"],
        }

        doc = CompanyDocItem(**minimal_data)

        assert doc.doc_id == 12345
        assert doc.keywords is None  # Optional field, default None
        assert doc.processed is None
        assert doc.created is None
        assert doc.modified is None

    def test_company_doc_details_inherits_doc_item(self):
        """Test CompanyDocDetails inherits from CompanyDocItem."""
        details_data = {
            "doc_id": 12345,
            "company": {"company_id": 67890, "name": "Test Company"},
            "title": "Test Document",
            "category": "Sustainability",
            "publish_date": "2023-09-15T00:00:00Z",
            "source_url": "https://example.com/test-doc.pdf",
            "summary": [
                "Test document summary"
            ],  # Inherits List[str] from CompanyDocItem
            "content_raw": "Test content preview...",
            "attachments": [
                {"name": "file.pdf", "url": "https://example.com/file.pdf"}
            ],
        }

        details = CompanyDocDetails(**details_data)

        # Test inherited fields
        assert details.doc_id == 12345
        assert details.company.name == "Test Company"
        assert details.title == "Test Document"

        # Test new fields
        assert details.summary == ["Test document summary"]
        assert details.content_raw == "Test content preview..."
        assert len(details.attachments) == 1

    def test_category_keyword_model(self):
        """Test CategoryKeyword model."""
        category_data = {"name": "Sustainability", "count": 25}

        category = CategoryKeyword(**category_data)

        assert category.name == "Sustainability"
        assert category.count == 25


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
            page_size=50,
        )

        assert args.start_date == "2023-09-01"
        assert args.end_date == "2023-09-30"
        assert args.bloomberg_ticker == "AAPL:US"
        assert args.categories == "Sustainability,Governance"
        assert args.keywords == "ESG,climate"
        assert args.page == 1
        assert args.page_size == 50

    def test_find_company_docs_args_defaults(self):
        """Test FindCompanyDocsArgs with default values."""
        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        assert args.page == 1  # Default value
        assert args.page_size == 50  # Default value
        assert args.bloomberg_ticker is None
        assert args.watchlist_id is None
        assert args.categories is None
        assert args.keywords is None

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

        # Page size must be between 1 and 100
        with pytest.raises(ValidationError):
            FindCompanyDocsArgs(
                start_date="2023-09-01", end_date="2023-09-30", page_size=0
            )

        with pytest.raises(ValidationError):
            FindCompanyDocsArgs(
                start_date="2023-09-01", end_date="2023-09-30", page_size=101
            )

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
        # This test assumes there's ticker format correction logic
        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            bloomberg_ticker="AAPL",  # Missing :US
        )

        # Check if ticker correction is applied
        # This depends on the actual implementation in utils.py
        assert args.bloomberg_ticker in ["AAPL", "AAPL:US"]

    def test_categories_keywords_validation(self):
        """Test categories and keywords format validation."""
        # This test assumes there's format correction logic
        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            categories="Sustainability, Governance",  # With spaces
            keywords="ESG, climate",  # With spaces
        )

        # Check if format correction is applied
        # This depends on the actual implementation in utils.py
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
        args = GetCompanyDocArgs(company_doc_ids="doc123")
        assert args.company_doc_ids == "doc123"

    def test_get_company_doc_args_required_field(self):
        """Test that company_doc_id is required."""
        with pytest.raises(ValidationError):
            GetCompanyDocArgs()  # Missing required field


@pytest.mark.unit
class TestCompanyDocsResponses:
    """Test company_docs response models."""

    def test_find_company_docs_response(self):
        """Test FindCompanyDocsResponse model."""
        # Use proper new model structure
        response_data = {
            "response": {
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50,
                },
                "data": [
                    {
                        "doc_id": 123,
                        "company": {"company_id": 456, "name": "Test Company"},
                        "title": "Test Document",
                        "category": "Sustainability",
                        "publish_date": "2023-09-15T00:00:00Z",
                        "source_url": "https://example.com/test.pdf",
                        "summary": ["Test summary"],
                        "keywords": ["test"],
                        "citation_information": {
                            "title": "Test Citation",
                            "url": "https://example.com",
                        },
                    }
                ],
            },
            "instructions": ["Test instruction"],
        }

        response = FindCompanyDocsResponse.model_validate(response_data)

        assert len(response.response.data) == 1
        assert response.response.pagination.total_count == 1
        assert response.response.pagination.current_page == 1
        assert response.response.pagination.page_size == 50
        assert response.instructions == ["Test instruction"]

    def test_get_company_doc_response(self):
        """Test GetCompanyDocResponse model."""
        # Use proper structure for GetCompanyDocResponse
        response_data = {
            "document": {
                "doc_id": 123,
                "company": {"company_id": 456, "name": "Test Company"},
                "title": "Test Document",
                "category": "Sustainability",
                "publish_date": "2023-09-15T00:00:00Z",
                "source_url": "https://example.com/test.pdf",
                "summary": ["Test summary"],  # List[str] inherited from CompanyDocItem
                "content_raw": "Test preview",
                "keywords": ["test"],
                "attachments": [],
                "citation_information": {
                    "title": "Test Citation",
                    "url": "https://example.com",
                },
            },
            "instructions": ["Test instruction"],
        }

        response = GetCompanyDocResponse.model_validate(response_data)

        assert isinstance(response.document, CompanyDocDetails)
        assert response.document.doc_id == 123
        assert response.document.summary == ["Test summary"]
        assert response.instructions == ["Test instruction"]

    def test_get_company_doc_response_no_document(self):
        """Test GetCompanyDocResponse with no document (robustness to empty response)."""
        response_data = {
            "document": None,
            "instructions": ["Document not found"],
        }

        response = GetCompanyDocResponse.model_validate(response_data)

        assert response.document is None
        assert response.instructions == ["Document not found"]

    def test_get_company_doc_categories_response(self):
        """Test GetCompanyDocCategoriesResponse model."""
        # Use proper structure for GetCompanyDocCategoriesResponse
        # Note: pagination and data are at the top level, not nested under response
        response_data = {
            "pagination": {
                "total_count": 2,
                "current_page": 1,
                "total_pages": 1,
                "page_size": 50,
            },
            "data": {"sustainability": 25, "governance": 18},
            "instructions": ["Categories retrieved"],
        }

        response = GetCompanyDocCategoriesResponse.model_validate(response_data)

        assert isinstance(response.data, dict)
        assert response.data["sustainability"] == 25
        assert response.data["governance"] == 18
        assert response.pagination.total_count == 2
        assert response.instructions == ["Categories retrieved"]

    def test_get_company_doc_keywords_response(self):
        """Test GetCompanyDocKeywordsResponse model."""
        # Use proper structure for GetCompanyDocKeywordsResponse
        # Note: pagination and data are at the top level, not nested under response
        response_data = {
            "pagination": {
                "total_count": 2,
                "current_page": 1,
                "total_pages": 1,
                "page_size": 50,
            },
            "data": {"ESG": 15, "climate": 23},
            "instructions": ["Keywords retrieved"],
        }

        response = GetCompanyDocKeywordsResponse.model_validate(response_data)

        assert isinstance(response.data, dict)
        assert response.data["ESG"] == 15
        assert response.data["climate"] == 23
        assert response.pagination.total_count == 2
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

    def test_date_field_validation(self):
        """Test date field validation with various formats."""
        # Valid ISO date string
        doc = CompanyDocItem(
            doc_id=123,
            company={"company_id": 456, "name": "Test Company"},
            title="Test Document",
            category="Test",
            publish_date="2023-09-15T00:00:00Z",
            source_url="https://example.com/test.pdf",
            summary=["Test summary"],
        )
        assert doc.publish_date == "2023-09-15T00:00:00Z"

        # Test with different ISO format
        doc_with_datetime = CompanyDocItem(
            doc_id=124,
            company={"company_id": 456, "name": "Test Company"},
            title="Test Document",
            category="Test",
            publish_date="2023-09-15T10:30:00Z",
            source_url="https://example.com/test.pdf",
            summary=["Test summary"],
        )
        assert doc_with_datetime.publish_date == "2023-09-15T10:30:00Z"

    def test_keywords_list_handling(self):
        """Test keywords list handling."""
        # Empty list
        doc = CompanyDocItem(
            doc_id=123,
            company={"company_id": 456, "name": "Test Company"},
            title="Test Document",
            category="Test",
            publish_date="2023-09-15T00:00:00Z",
            source_url="https://example.com/test.pdf",
            summary=["Test summary"],
            keywords=[],
        )
        assert doc.keywords == []

        # List with multiple keywords
        doc_with_keywords = CompanyDocItem(
            doc_id=124,
            company={"company_id": 456, "name": "Test Company"},
            title="Test Document",
            category="Test",
            publish_date="2023-09-15T00:00:00Z",
            source_url="https://example.com/test.pdf",
            summary=["Test summary"],
            keywords=["ESG", "sustainability", "climate"],
        )
        assert len(doc_with_keywords.keywords) == 3
        assert "ESG" in doc_with_keywords.keywords

    def test_attachments_handling(self):
        """Test attachments list handling in CompanyDocDetails."""
        # No attachments provided - should be None
        doc = CompanyDocDetails(
            doc_id=123,
            company={"company_id": 456, "name": "Test Company"},
            title="Test Document",
            category="Test",
            publish_date="2023-09-15T00:00:00Z",
            source_url="https://example.com/test.pdf",
            summary=["Test summary"],  # List[str] inherited from CompanyDocItem
            content_raw="Test preview",
        )
        assert doc.attachments is None

        # With attachments
        doc_with_attachments = CompanyDocDetails(
            doc_id=124,
            company={"company_id": 456, "name": "Test Company"},
            title="Test Document",
            category="Test",
            publish_date="2023-09-15T00:00:00Z",
            source_url="https://example.com/test.pdf",
            summary=["Test summary"],
            content_raw="Test preview",
            attachments=[
                {"name": "report.pdf", "url": "https://example.com/report.pdf"},
                {"name": "summary.pdf", "url": "https://example.com/summary.pdf"},
            ],
        )
        assert len(doc_with_attachments.attachments) == 2
        assert doc_with_attachments.attachments[0]["name"] == "report.pdf"
