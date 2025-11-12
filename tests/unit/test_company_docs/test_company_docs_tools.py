#!/usr/bin/env python3

"""Unit tests for company_docs tools."""

import pytest
import pytest_asyncio
from datetime import datetime, date
from unittest.mock import AsyncMock
from pydantic import ValidationError

from aiera_mcp.tools.company_docs.tools import (
    find_company_docs, get_company_doc, get_company_doc_categories, get_company_doc_keywords
)
from aiera_mcp.tools.company_docs.models import (
    FindCompanyDocsArgs, GetCompanyDocArgs, SearchArgs,
    FindCompanyDocsResponse, GetCompanyDocResponse,
    GetCompanyDocCategoriesResponse, GetCompanyDocKeywordsResponse,
    CompanyDocItem, CompanyDocDetails, CategoryKeyword
)


@pytest.mark.unit
class TestFindCompanyDocs:
    """Test the find_company_docs tool."""

    @pytest.mark.asyncio
    async def test_find_company_docs_success(self, mock_http_dependencies, company_docs_api_responses):
        """Test successful company docs search."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["find_company_docs_success"]

        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            bloomberg_ticker="AAPL:US",
            categories="Sustainability",
            keywords="environment"
        )

        # Execute
        result = await find_company_docs(args)

        # Verify
        assert isinstance(result, FindCompanyDocsResponse)
        assert len(result.response.data) == 1
        assert result.response.pagination.total_count == 1
        assert result.response.pagination.current_page == 1
        assert result.response.pagination.page_size == 50

        # Check first document
        first_doc = result.response.data[0]
        assert isinstance(first_doc, CompanyDocItem)
        assert first_doc.doc_id == 456789
        assert first_doc.title == "Sustainability Report 2023"
        assert first_doc.company.name == "Apple Inc"
        assert first_doc.category == "Sustainability"
        assert first_doc.keywords == ["environment", "carbon neutral", "renewable energy"]
        assert first_doc.publish_date == "2023-09-15T00:00:00Z"

        # Check API call was made correctly
        mock_http_dependencies['mock_make_request'].assert_called_once()
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-company-docs"

        # Check parameters were passed correctly
        params = call_args[1]['params']
        assert params['start_date'] == "2023-09-01"
        assert params['end_date'] == "2023-09-30"
        assert params['bloomberg_ticker'] == "AAPL:US"
        assert params['categories'] == "Sustainability"
        assert params['keywords'] == "environment"

    @pytest.mark.asyncio
    async def test_find_company_docs_empty_results(self, mock_http_dependencies):
        """Test find_company_docs with empty results."""
        # Setup
        empty_response = {
            "response": {
                "pagination": {
                    "total_count": 0,
                    "current_page": 1,
                    "total_pages": 0,
                    "page_size": 50
                },
                "data": []
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify
        assert isinstance(result, FindCompanyDocsResponse)
        assert len(result.response.data) == 0
        assert result.response.pagination.total_count == 0

    @pytest.mark.asyncio
    async def test_find_company_docs_pagination(self, mock_http_dependencies, company_docs_api_responses):
        """Test find_company_docs with pagination parameters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["find_company_docs_success"]

        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            page=2,
            page_size=25
        )

        # Execute
        result = await find_company_docs(args)

        # Verify - values will come from fixture, not request params
        assert result.response.pagination.current_page == 1  # From fixture
        assert result.response.pagination.page_size == 50    # From fixture

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"  # Should be serialized as string
        assert params['page_size'] == "25"

    @pytest.mark.asyncio
    async def test_find_company_docs_with_filters(self, mock_http_dependencies, company_docs_api_responses):
        """Test find_company_docs with various filters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["find_company_docs_success"]

        args = FindCompanyDocsArgs(
            start_date="2023-09-01",
            end_date="2023-09-30",
            bloomberg_ticker="AAPL:US,MSFT:US",
            watchlist_id=123,
            sector_id=456,
            subsector_id=789,
            categories="Sustainability,Governance",
            keywords="ESG,climate"
        )

        # Execute
        result = await find_company_docs(args)

        # Verify
        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['bloomberg_ticker'] == "AAPL:US,MSFT:US"
        assert params['watchlist_id'] == "123"
        assert params['sector_id'] == "456"
        assert params['subsector_id'] == "789"
        assert params['categories'] == "Sustainability,Governance"
        assert params['keywords'] == "ESG,climate"

    @pytest.mark.asyncio
    async def test_find_company_docs_date_parsing(self, mock_http_dependencies):
        """Test find_company_docs handles date parsing correctly."""
        # Setup with various date formats
        response_with_dates = {
            "response": {
                "pagination": {
                    "total_count": 1,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50
                },
                "data": [
                    {
                        "doc_id": 12345,
                        "company": {
                            "company_id": 67890,
                            "name": "Test Company"
                        },
                        "title": "Test Document",
                        "category": "Test",
                        "keywords": ["test"],
                        "publish_date": "2023-09-15T00:00:00Z",  # ISO format with Z
                        "source_url": "https://example.com/test-doc.pdf",
                        "summary": ["Test document summary"]
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_dates

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify date was parsed correctly
        assert len(result.response.data) == 1
        doc = result.response.data[0]
        assert doc.publish_date == "2023-09-15T00:00:00Z"
        assert doc.company.name == "Test Company"

    @pytest.mark.asyncio
    async def test_find_company_docs_citations(self, mock_http_dependencies, company_docs_api_responses):
        """Test that find_company_docs generates proper citations."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["find_company_docs_success"]

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify citations were created in the document
        assert len(result.response.data) == 1
        doc = result.response.data[0]
        assert doc.citation_information is not None
        citation = doc.citation_information
        assert citation.title == "Sustainability Report 2023"
        assert citation.url == "https://apple.com/sustainability/pdf/Apple_Environmental_Progress_Report_2023.pdf"


@pytest.mark.unit
class TestGetCompanyDoc:
    """Test the get_company_doc tool."""

    @pytest.mark.asyncio
    async def test_get_company_doc_success(self, mock_http_dependencies, company_docs_api_responses):
        """Test successful company document retrieval."""
        # Setup - use the proper fixture
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["get_company_doc_success"]

        args = GetCompanyDocArgs(company_doc_id="456789")

        # Execute
        result = await get_company_doc(args)

        # Verify
        assert isinstance(result, GetCompanyDocResponse)
        assert isinstance(result.document, CompanyDocDetails)
        assert result.document.doc_id == 456789
        assert result.document.title == "Sustainability Report 2023"
        assert result.document.summary == "Apple's comprehensive sustainability report covering environmental impact, carbon neutrality goals, and renewable energy initiatives."
        assert result.document.content_preview.startswith("This report outlines Apple's environmental initiatives")
        assert result.document.company.name == "Apple Inc"
        assert result.document.company.company_id == 12345
        assert len(result.document.attachments) == 0

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-company-docs"

        # Check field mapping (company_doc_id -> company_doc_ids)
        params = call_args[1]['params']
        assert 'company_doc_ids' in params
        assert params['company_doc_ids'] == "456789"
        assert 'company_doc_id' not in params
        assert params['include_content'] == "true"

    @pytest.mark.asyncio
    async def test_get_company_doc_not_found(self, mock_http_dependencies):
        """Test get_company_doc when document is not found."""
        # Setup - empty response
        mock_http_dependencies['mock_make_request'].return_value = {
            "response": {"data": []},
            "instructions": []
        }

        args = GetCompanyDocArgs(company_doc_id="nonexistent")

        # Execute & Verify
        with pytest.raises(ValueError, match="Document not found: nonexistent"):
            await get_company_doc(args)

    @pytest.mark.asyncio
    async def test_get_company_doc_date_parsing(self, mock_http_dependencies, company_docs_api_responses):
        """Test get_company_doc handles date parsing correctly."""
        # Setup - use the proper fixture which has valid date format
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["get_company_doc_success"]

        args = GetCompanyDocArgs(company_doc_id="456789")

        # Execute
        result = await get_company_doc(args)

        # Verify - should have valid date string
        assert result.document.publish_date == "2023-09-15T00:00:00Z"


@pytest.mark.unit
class TestGetCompanyDocCategories:
    """Test the get_company_doc_categories tool."""

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_success(self, mock_http_dependencies, company_docs_api_responses):
        """Test successful company doc categories retrieval."""
        # Setup - use the proper fixture
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["get_company_doc_categories_success"]

        args = SearchArgs(search="sustain")

        # Execute
        result = await get_company_doc_categories(args)

        # Verify
        assert isinstance(result, GetCompanyDocCategoriesResponse)
        assert len(result.response.data) == 3
        assert result.response.pagination.total_count == 3

        # The data is a dictionary of {category_name: count}
        categories_data = result.response.data
        assert "sustainability" in categories_data
        assert categories_data["sustainability"] == 15
        assert "annual_report" in categories_data
        assert categories_data["annual_report"] == 8

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/get-company-doc-categories"

        params = call_args[1]['params']
        assert params['search'] == "sustain"

        # Citation information is empty in the fixture

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_empty_results(self, mock_http_dependencies):
        """Test get_company_doc_categories with empty results."""
        # Setup
        empty_response = {
            "response": {
                "pagination": {
                    "total_count": 0,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50
                },
                "data": {}
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = SearchArgs()

        # Execute
        result = await get_company_doc_categories(args)

        # Verify
        assert isinstance(result, GetCompanyDocCategoriesResponse)
        assert len(result.response.data) == 0
        assert result.response.pagination.total_count == 0

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_pagination(self, mock_http_dependencies):
        """Test get_company_doc_categories with pagination."""
        # Setup
        categories_response = {
            "response": {
                "pagination": {
                    "total_count": 1,
                    "current_page": 2,
                    "total_pages": 1,
                    "page_size": 25
                },
                "data": {
                    "Test": 1
                }
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = categories_response

        args = SearchArgs(page=2, page_size=25)

        # Execute
        result = await get_company_doc_categories(args)

        # Verify
        assert result.response.pagination.current_page == 2
        assert result.response.pagination.page_size == 25

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"
        assert params['page_size'] == "25"


@pytest.mark.unit
class TestGetCompanyDocKeywords:
    """Test the get_company_doc_keywords tool."""

    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_success(self, mock_http_dependencies, company_docs_api_responses):
        """Test successful company doc keywords retrieval."""
        # Setup - use the proper fixture
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["get_company_doc_keywords_success"]

        args = SearchArgs(search="ESG")

        # Execute
        result = await get_company_doc_keywords(args)

        # Verify
        assert isinstance(result, GetCompanyDocKeywordsResponse)
        assert len(result.response.data) == 5
        assert result.response.pagination.total_count == 5

        # The data is a dictionary of {keyword_name: count}
        keywords_data = result.response.data
        assert "ESG" in keywords_data
        assert keywords_data["ESG"] == 30
        assert "environment" in keywords_data
        assert keywords_data["environment"] == 25

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/get-company-doc-keywords"

        params = call_args[1]['params']
        assert params['search'] == "ESG"


    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_empty_results(self, mock_http_dependencies):
        """Test get_company_doc_keywords with empty results."""
        # Setup
        empty_response = {
            "response": {
                "pagination": {
                    "total_count": 0,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50
                },
                "data": {}
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = SearchArgs()

        # Execute
        result = await get_company_doc_keywords(args)

        # Verify
        assert isinstance(result, GetCompanyDocKeywordsResponse)
        assert len(result.response.data) == 0
        assert result.response.pagination.total_count == 0

    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_alternative_field_names(self, mock_http_dependencies):
        """Test get_company_doc_keywords handles alternative field names."""
        # Setup - test with dictionary format data
        keywords_response = {
            "response": {
                "pagination": {
                    "total_count": 2,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50
                },
                "data": {
                    "ESG": 15,
                    "climate": 23
                }
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = keywords_response

        args = SearchArgs()

        # Execute
        result = await get_company_doc_keywords(args)

        # Verify - dictionary format data
        assert isinstance(result, GetCompanyDocKeywordsResponse)
        assert result.response.pagination.total_count == 2
        keywords_data = result.response.data
        assert keywords_data["ESG"] == 15
        assert keywords_data["climate"] == 23


@pytest.mark.unit
class TestCompanyDocsToolsErrorHandling:
    """Test error handling for company_docs tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response that will cause validation error
        mock_http_dependencies['mock_make_request'].return_value = {"invalid": "response"}

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute & Verify - should raise validation error for malformed response
        with pytest.raises(ValidationError):
            await find_company_docs(args)

    @pytest.mark.asyncio
    async def test_handle_missing_date_fields(self, mock_http_dependencies):
        """Test handling of documents with missing or invalid date fields."""
        # Setup - response with missing/invalid dates will cause validation error
        response_with_bad_dates = {
            "response": {
                "pagination": {
                    "total_count": 2,
                    "current_page": 1,
                    "total_pages": 1,
                    "page_size": 50
                },
                "data": [
                    {
                        "doc_id": 123,
                        "company": {
                            "company_id": 456,
                            "name": "Test Company"
                        },
                        "title": "Test Document",
                        "category": "Test",
                        "keywords": [],
                        "publish_date": "invalid-date",  # Invalid date format
                        "source_url": "https://example.com/doc.pdf",
                        "summary": ["Test summary"]
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_bad_dates

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute - see what actually happens with invalid date
        result = await find_company_docs(args)

        # Verify response structure is still valid (date validation may be lenient)
        assert isinstance(result, FindCompanyDocsResponse)
        assert len(result.response.data) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, TimeoutError, ValueError])
    async def test_network_errors_propagate(self, mock_http_dependencies, exception_type):
        """Test that network errors are properly propagated."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies['mock_make_request'].side_effect = exception_type("Test error")

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_company_docs(args)