#!/usr/bin/env python3

"""Unit tests for company_docs tools."""

import pytest
import pytest_asyncio
from datetime import datetime, date
from unittest.mock import AsyncMock

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
        assert len(result.documents) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 50

        # Check first document
        first_doc = result.documents[0]
        assert isinstance(first_doc, CompanyDocItem)
        assert first_doc.doc_id == "doc456"
        assert first_doc.title == "Sustainability Report 2023"
        assert first_doc.company_name == "Apple Inc"
        assert first_doc.category == "Sustainability"
        assert first_doc.keywords == ["environment", "carbon neutral", "renewable energy"]
        assert isinstance(first_doc.publish_date, date)

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
            "response": {"data": [], "total": 0},
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify
        assert isinstance(result, FindCompanyDocsResponse)
        assert len(result.documents) == 0
        assert result.total == 0
        assert len(result.citation_information) == 0

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

        # Verify
        assert result.page == 2
        assert result.page_size == 25

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
                "data": [
                    {
                        "id": "doc123",
                        "company_name": "Test Company",
                        "title": "Test Document",
                        "category": "Test",
                        "keywords": ["test"],
                        "publish_date": "2023-09-15T00:00:00Z",  # ISO format with Z
                        "document_type": "report"
                    }
                ],
                "total": 1
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_dates

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify date was parsed correctly
        assert len(result.documents) == 1
        doc = result.documents[0]
        assert isinstance(doc.publish_date, date)
        assert doc.publish_date.year == 2023
        assert doc.publish_date.month == 9
        assert doc.publish_date.day == 15

    @pytest.mark.asyncio
    async def test_find_company_docs_citations(self, mock_http_dependencies, company_docs_api_responses):
        """Test that find_company_docs generates proper citations."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = company_docs_api_responses["find_company_docs_success"]

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify citations were created
        assert len(result.citation_information) == 1
        citation = result.citation_information[0]
        assert citation.title == "Sustainability Report 2023"
        assert citation.url == "https://apple.com/sustainability/pdf/Apple_Environmental_Progress_Report_2023.pdf"
        assert citation.timestamp is not None


@pytest.mark.unit
class TestGetCompanyDoc:
    """Test the get_company_doc tool."""

    @pytest.mark.asyncio
    async def test_get_company_doc_success(self, mock_http_dependencies):
        """Test successful company document retrieval."""
        # Setup
        response_with_details = {
            "response": {
                "data": [
                    {
                        "id": "doc456",
                        "company_name": "Apple Inc",
                        "title": "Sustainability Report 2023",
                        "category": "Sustainability",
                        "keywords": ["environment", "carbon neutral"],
                        "publish_date": "2023-09-15T00:00:00Z",
                        "document_type": "report",
                        "summary": "Apple's comprehensive sustainability report for 2023",
                        "content_preview": "This report details Apple's progress toward carbon neutrality...",
                        "attachments": [{"name": "report.pdf", "url": "https://example.com/report.pdf"}],
                        "url": "https://apple.com/sustainability/pdf/Apple_Environmental_Progress_Report_2023.pdf"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_details

        args = GetCompanyDocArgs(company_doc_id="doc456")

        # Execute
        result = await get_company_doc(args)

        # Verify
        assert isinstance(result, GetCompanyDocResponse)
        assert isinstance(result.document, CompanyDocDetails)
        assert result.document.doc_id == "doc456"
        assert result.document.title == "Sustainability Report 2023"
        assert result.document.summary == "Apple's comprehensive sustainability report for 2023"
        assert result.document.content_preview is not None
        assert len(result.document.attachments) == 1

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-company-docs"

        # Check field mapping (company_doc_id -> company_doc_ids)
        params = call_args[1]['params']
        assert 'company_doc_ids' in params
        assert params['company_doc_ids'] == "doc456"
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
    async def test_get_company_doc_date_parsing(self, mock_http_dependencies):
        """Test get_company_doc handles date parsing correctly."""
        # Setup with invalid date
        response_with_bad_date = {
            "response": {
                "data": [
                    {
                        "id": "doc456",
                        "company_name": "Apple Inc",
                        "title": "Test Document",
                        "category": "Test",
                        "keywords": [],
                        "publish_date": "invalid-date",  # Invalid date
                        "document_type": "report"
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_bad_date

        args = GetCompanyDocArgs(company_doc_id="doc456")

        # Execute
        result = await get_company_doc(args)

        # Verify - should have fallback date
        assert isinstance(result.document.publish_date, date)


@pytest.mark.unit
class TestGetCompanyDocCategories:
    """Test the get_company_doc_categories tool."""

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_success(self, mock_http_dependencies):
        """Test successful company doc categories retrieval."""
        # Setup
        categories_response = {
            "response": {
                "data": [
                    {"name": "Sustainability", "count": 25},
                    {"name": "Governance", "count": 18},
                    {"name": "Financial", "count": 42}
                ],
                "total": 3
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = categories_response

        args = SearchArgs(search="sustain")

        # Execute
        result = await get_company_doc_categories(args)

        # Verify
        assert isinstance(result, GetCompanyDocCategoriesResponse)
        assert len(result.categories) == 3
        assert all(isinstance(cat, CategoryKeyword) for cat in result.categories)

        # Check first category
        first_category = result.categories[0]
        assert first_category.name == "Sustainability"
        assert first_category.count == 25

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/get-company-doc-categories"

        params = call_args[1]['params']
        assert params['search'] == "sustain"

        # Check citation was created
        assert len(result.citation_information) == 1
        assert result.citation_information[0].title == "Company Document Categories"
        assert result.citation_information[0].source == "Aiera"

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_empty_results(self, mock_http_dependencies):
        """Test get_company_doc_categories with empty results."""
        # Setup
        empty_response = {
            "response": {"data": [], "total": 0},
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = SearchArgs()

        # Execute
        result = await get_company_doc_categories(args)

        # Verify
        assert isinstance(result, GetCompanyDocCategoriesResponse)
        assert len(result.categories) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_pagination(self, mock_http_dependencies):
        """Test get_company_doc_categories with pagination."""
        # Setup
        categories_response = {
            "response": {
                "data": [{"name": "Test", "count": 1}],
                "total": 1
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = categories_response

        args = SearchArgs(page=2, page_size=25)

        # Execute
        result = await get_company_doc_categories(args)

        # Verify
        assert result.page == 2
        assert result.page_size == 25

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"
        assert params['page_size'] == "25"


@pytest.mark.unit
class TestGetCompanyDocKeywords:
    """Test the get_company_doc_keywords tool."""

    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_success(self, mock_http_dependencies):
        """Test successful company doc keywords retrieval."""
        # Setup
        keywords_response = {
            "response": {
                "data": [
                    {"name": "ESG", "count": 15},
                    {"name": "climate", "count": 23},
                    {"name": "diversity", "count": 8}
                ],
                "total": 3
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = keywords_response

        args = SearchArgs(search="ESG")

        # Execute
        result = await get_company_doc_keywords(args)

        # Verify
        assert isinstance(result, GetCompanyDocKeywordsResponse)
        assert len(result.keywords) == 3
        assert all(isinstance(keyword, CategoryKeyword) for keyword in result.keywords)

        # Check first keyword
        first_keyword = result.keywords[0]
        assert first_keyword.name == "ESG"
        assert first_keyword.count == 15

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/get-company-doc-keywords"

        params = call_args[1]['params']
        assert params['search'] == "ESG"

        # Check citation was created
        assert len(result.citation_information) == 1
        assert result.citation_information[0].title == "Company Document Keywords"
        assert result.citation_information[0].source == "Aiera"

    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_empty_results(self, mock_http_dependencies):
        """Test get_company_doc_keywords with empty results."""
        # Setup
        empty_response = {
            "response": {"data": [], "total": 0},
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = SearchArgs()

        # Execute
        result = await get_company_doc_keywords(args)

        # Verify
        assert isinstance(result, GetCompanyDocKeywordsResponse)
        assert len(result.keywords) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_alternative_field_names(self, mock_http_dependencies):
        """Test get_company_doc_keywords handles alternative field names."""
        # Setup - some APIs might return 'keyword' instead of 'name'
        keywords_response = {
            "response": {
                "data": [
                    {"keyword": "ESG", "count": 15},  # Alternative field name
                    {"name": "climate", "count": 23}   # Standard field name
                ],
                "total": 2
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = keywords_response

        args = SearchArgs()

        # Execute
        result = await get_company_doc_keywords(args)

        # Verify - should handle both field name formats
        assert len(result.keywords) == 2
        names = [kw.name for kw in result.keywords]
        assert "ESG" in names
        assert "climate" in names


@pytest.mark.unit
class TestCompanyDocsToolsErrorHandling:
    """Test error handling for company_docs tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response
        mock_http_dependencies['mock_make_request'].return_value = {"invalid": "response"}

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify - should handle gracefully with empty results
        assert isinstance(result, FindCompanyDocsResponse)
        assert len(result.documents) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_handle_missing_date_fields(self, mock_http_dependencies):
        """Test handling of documents with missing or invalid date fields."""
        # Setup - response with missing/invalid dates
        response_with_bad_dates = {
            "response": {
                "data": [
                    {
                        "id": "doc123",
                        "company_name": "Test Company",
                        "title": "Test Document",
                        "category": "Test",
                        "keywords": [],
                        "publish_date": "invalid-date",  # Invalid date
                        "document_type": "report"
                    },
                    {
                        "id": "doc456",
                        "company_name": "Test Company 2",
                        "title": "Test Document 2",
                        "category": "Test",
                        "keywords": []
                        # Missing publish_date
                    }
                ],
                "total": 2
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_bad_dates

        args = FindCompanyDocsArgs(start_date="2023-09-01", end_date="2023-09-30")

        # Execute
        result = await find_company_docs(args)

        # Verify - should still process documents with fallback dates
        assert len(result.documents) == 2
        for doc in result.documents:
            assert isinstance(doc.publish_date, date)  # Should have fallback date

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