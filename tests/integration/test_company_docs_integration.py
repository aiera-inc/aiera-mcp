#!/usr/bin/env python3

"""Integration tests for company docs tools with real Aiera API."""

import pytest
import pytest_asyncio
from unittest.mock import patch

from aiera_mcp.tools.company_docs.tools import (
    find_company_docs, get_company_doc, get_company_doc_categories, get_company_doc_keywords
)
from aiera_mcp.tools.company_docs.models import (
    FindCompanyDocsArgs, GetCompanyDocArgs, SearchArgs,
    FindCompanyDocsResponse, GetCompanyDocResponse,
    GetCompanyDocCategoriesResponse, GetCompanyDocKeywordsResponse,
    CompanyDocItem, CompanyDocDetails, CategoryKeyword
)


@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
class TestCompanyDocsIntegration:
    """Integration tests for company docs tools with real API."""

    @pytest.mark.asyncio
    async def test_find_company_docs_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_date_ranges,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_company_docs with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a date range that should have documents
            date_range = sample_date_ranges[1]  # Q1 2024
            args = FindCompanyDocsArgs(
                start_date=date_range["start_date"],
                end_date=date_range["end_date"],
                page_size=10
            )

            result = await find_company_docs(args)

            # Verify response structure
            assert isinstance(result, FindCompanyDocsResponse)
            assert isinstance(result.documents, list)
            assert result.total >= 0
            assert result.page == 1
            assert result.page_size == 10

            # If we found documents, verify their structure
            if result.documents:
                first_doc = result.documents[0]
                assert isinstance(first_doc, CompanyDocItem)
                assert first_doc.document_id
                assert first_doc.title
                assert first_doc.company_name
                assert first_doc.published_date

    @pytest.mark.asyncio
    async def test_find_company_docs_with_ticker_filter(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_company_docs with ticker filter."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with Apple ticker - should have many documents
            args = FindCompanyDocsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                bloomberg_ticker=sample_tickers[0],  # AAPL:US
                page_size=5
            )

            result = await find_company_docs(args)

            assert isinstance(result, FindCompanyDocsResponse)
            assert result.total >= 0

            # If we found documents, they should be for Apple or related
            for doc in result.documents:
                assert isinstance(doc, CompanyDocItem)
                assert doc.company_ticker == "AAPL:US" or "Apple" in doc.company_name

    @pytest.mark.asyncio
    async def test_find_company_docs_with_search(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_company_docs with search query."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test search for investor relations documents
            args = FindCompanyDocsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                search="investor presentation",
                page_size=5
            )

            result = await find_company_docs(args)

            assert isinstance(result, FindCompanyDocsResponse)
            assert result.total >= 0

            # If we found documents, they should be related to investor presentations
            for doc in result.documents:
                assert isinstance(doc, CompanyDocItem)
                # The search might find related documents, so we don't enforce strict matching

    @pytest.mark.asyncio
    async def test_find_company_docs_with_category(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_company_docs with category filter."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with presentation category (common document type)
            args = FindCompanyDocsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                category="presentation",
                page_size=5
            )

            result = await find_company_docs(args)

            assert isinstance(result, FindCompanyDocsResponse)
            assert result.total >= 0

            # If we found documents, they should be presentations
            for doc in result.documents:
                assert isinstance(doc, CompanyDocItem)
                assert doc.category == "presentation" or "presentation" in doc.category.lower()

    @pytest.mark.asyncio
    async def test_get_company_doc_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_company_doc with real API (requires finding a document first)."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # First find a document
            find_args = FindCompanyDocsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                page_size=1
            )

            find_result = await find_company_docs(find_args)

            # Skip test if no documents found
            if not find_result.documents:
                pytest.skip("No company documents found for the specified date range")

            await api_rate_limiter.wait()

            # Get details for the first document
            document_id = find_result.documents[0].document_id
            get_args = GetCompanyDocArgs(document_id=document_id)

            result = await get_company_doc(get_args)

            # Verify response structure
            assert isinstance(result, GetCompanyDocResponse)
            assert isinstance(result.document, CompanyDocDetails)
            assert result.document.document_id == document_id
            assert result.document.title
            assert result.document.company_name
            assert result.document.published_date

            # CompanyDocDetails should have additional fields
            assert hasattr(result.document, 'content_preview')
            assert hasattr(result.document, 'summary')
            assert hasattr(result.document, 'document_url')

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_company_doc_categories with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test without search to get all categories
            args = SearchArgs()

            result = await get_company_doc_categories(args)

            # Verify response structure
            assert isinstance(result, GetCompanyDocCategoriesResponse)
            assert isinstance(result.categories, list)

            # Should have some categories
            if result.categories:
                for category in result.categories:
                    assert isinstance(category, CategoryKeyword)
                    assert category.category_name

    @pytest.mark.asyncio
    async def test_get_company_doc_categories_with_search(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_company_doc_categories with search query."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test search for presentation categories
            args = SearchArgs(search="presentation")

            result = await get_company_doc_categories(args)

            assert isinstance(result, GetCompanyDocCategoriesResponse)

            # If we found categories, they should be related to presentations
            for category in result.categories:
                assert isinstance(category, CategoryKeyword)
                assert "presentation" in category.category_name.lower() or "present" in category.category_name.lower()

    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_company_doc_keywords with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test without search to get all keywords
            args = SearchArgs()

            result = await get_company_doc_keywords(args)

            # Verify response structure
            assert isinstance(result, GetCategoryKeywordsResponse)
            assert isinstance(result.keywords, list)

            # Should have some keywords
            if result.keywords:
                for keyword in result.keywords:
                    assert isinstance(keyword, CategoryKeyword)
                    assert keyword.keyword_name

    @pytest.mark.asyncio
    async def test_get_company_doc_keywords_with_search(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_company_doc_keywords with search query."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test search for financial keywords
            args = SearchArgs(search="financial")

            result = await get_company_doc_keywords(args)

            assert isinstance(result, GetCategoryKeywordsResponse)

            # If we found keywords, they should be related to financial
            for keyword in result.keywords:
                assert isinstance(keyword, CategoryKeyword)
                assert "financial" in keyword.keyword_name.lower() or "finance" in keyword.keyword_name.lower()

    @pytest.mark.asyncio
    async def test_company_docs_pagination_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test company docs pagination with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test first page with large date range to ensure we have results
            args_page1 = FindCompanyDocsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                page=1,
                page_size=5
            )

            result_page1 = await find_company_docs(args_page1)
            assert result_page1.page == 1
            assert result_page1.page_size == 5

            # If we have enough documents, test second page
            if result_page1.total > 5:
                await api_rate_limiter.wait()

                args_page2 = FindCompanyDocsArgs(
                    start_date="2023-01-01",
                    end_date="2023-12-31",
                    page=2,
                    page_size=5
                )

                result_page2 = await find_company_docs(args_page2)
                assert result_page2.page == 2
                assert result_page2.page_size == 5
                assert result_page2.total == result_page1.total

                # Documents should be different between pages
                page1_ids = {doc.document_id for doc in result_page1.documents}
                page2_ids = {doc.document_id for doc in result_page2.documents}
                assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_company_docs_api_error_handling(
        self,
        integration_mcp_server,
        real_http_client,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test company docs API error handling with invalid API key."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_api_key_from_context', return_value="invalid-api-key"):

            args = FindCompanyDocsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31"
            )

            # This should raise an exception or return an error response
            try:
                result = await find_company_docs(args)
                # If it doesn't raise an exception, check for error indicators
                if hasattr(result, 'error') or len(result.documents) == 0:
                    # API handled the error gracefully
                    pass
            except Exception as e:
                # Expected - invalid API key should cause an error
                assert "401" in str(e) or "Unauthorized" in str(e) or "Invalid" in str(e)

    @pytest.mark.asyncio
    async def test_get_company_doc_invalid_id(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_company_doc with invalid document ID."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with invalid document ID
            get_args = GetCompanyDocArgs(company_doc_id="invalid-document-id-12345")

            # This should raise an exception or return an error
            try:
                result = await get_company_doc(get_args)
                # If no exception, the result should indicate an error
                assert not hasattr(result, 'document') or result.document is None
            except (ValueError, Exception) as e:
                # Expected - invalid document ID should cause an error
                assert "not found" in str(e).lower() or "invalid" in str(e).lower()

    @pytest.mark.asyncio
    async def test_company_docs_multiple_tools_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test multiple company docs tools working together."""

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # 1. Get available categories
            await api_rate_limiter.wait()
            categories_result = await get_company_doc_categories(SearchArgs())

            # 2. Get available keywords
            await api_rate_limiter.wait()
            keywords_result = await get_company_doc_keywords(SearchArgs())

            # 3. Find documents using a category if available
            await api_rate_limiter.wait()
            if categories_result.categories:
                first_category = categories_result.categories[0].category_name
                find_args = FindCompanyDocsArgs(
                    start_date="2023-01-01",
                    end_date="2023-12-31",
                    category=first_category,
                    page_size=1
                )
                find_result = await find_company_docs(find_args)
            else:
                find_result = await find_company_docs(FindCompanyDocsArgs(
                    start_date="2023-01-01",
                    end_date="2023-12-31",
                    page_size=1
                ))

            # Verify all tools returned valid data
            assert isinstance(categories_result, GetCompanyDocCategoriesResponse)
            assert isinstance(keywords_result, GetCategoryKeywordsResponse)
            assert isinstance(find_result, FindCompanyDocsResponse)

    @pytest.mark.asyncio
    async def test_company_docs_citations_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that company docs responses include citation information."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = FindCompanyDocsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                page_size=5
            )

            result = await find_company_docs(args)

            # Verify citations are generated when documents have URLs
            assert hasattr(result, 'citation_information')
            assert isinstance(result.citation_information, list)

            # If documents have URLs, citations should be created
            docs_with_urls = [d for d in result.documents if d.document_url]
            if docs_with_urls:
                assert len(result.citation_information) >= len(docs_with_urls)

                for citation in result.citation_information:
                    assert citation.title
                    assert citation.url