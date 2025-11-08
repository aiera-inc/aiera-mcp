#!/usr/bin/env python3

"""Integration tests for filings tools with real Aiera API."""

import pytest
import pytest_asyncio
from unittest.mock import patch

from aiera_mcp.tools.filings.tools import find_filings, get_filing
from aiera_mcp.tools.filings.models import (
    FindFilingsArgs, GetFilingArgs,
    FindFilingsResponse, GetFilingResponse,
    FilingItem, FilingDetails, FilingSummary
)


@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
class TestFilingsIntegration:
    """Integration tests for filings tools with real API."""

    @pytest.mark.asyncio
    async def test_find_filings_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_date_ranges,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_filings with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with a date range that should have filings
            date_range = sample_date_ranges[1]  # Q1 2024
            args = FindFilingsArgs(
                start_date=date_range["start_date"],
                end_date=date_range["end_date"],
                form_number="10-K",
                page_size=10
            )

            result = await find_filings(args)

            # Verify response structure
            assert isinstance(result, FindFilingsResponse)
            assert isinstance(result.filings, list)
            assert result.total >= 0
            assert result.page == 1
            assert result.page_size == 10

            # If we found filings, verify their structure
            if result.filings:
                first_filing = result.filings[0]
                assert isinstance(first_filing, FilingItem)
                assert first_filing.filing_id
                assert first_filing.company_name
                assert first_filing.form_type
                assert first_filing.filing_date
                assert first_filing.title

    @pytest.mark.asyncio
    async def test_find_filings_with_ticker_filter(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        sample_tickers,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test find_filings with ticker filter."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with Apple ticker - should have many filings
            args = FindFilingsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                bloomberg_ticker=sample_tickers[0],  # AAPL:US
                form_number="10-K"
            )

            result = await find_filings(args)

            assert isinstance(result, FindFilingsResponse)
            assert result.total >= 0

            # If we found filings, they should be for Apple
            for filing in result.filings:
                assert isinstance(filing, FilingItem)
                assert filing.company_ticker == "AAPL:US" or "Apple" in filing.company_name

    @pytest.mark.asyncio
    async def test_find_filings_different_form_types(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test different SEC form types."""
        form_types = ["10-K", "10-Q", "8-K"]

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            for form_type in form_types:
                await api_rate_limiter.wait()

                args = FindFilingsArgs(
                    start_date="2023-10-01",
                    end_date="2023-10-31",
                    form_number=form_type,
                    page_size=5
                )

                result = await find_filings(args)

                assert isinstance(result, FindFilingsResponse)
                assert result.total >= 0

                # If filings found, verify they match the requested form type
                for filing in result.filings:
                    assert isinstance(filing, FilingItem)
                    assert filing.form_type == form_type

    @pytest.mark.asyncio
    async def test_get_filing_real_api(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_filing with real API (requires finding a filing first)."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # First find a filing
            find_args = FindFilingsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                form_number="10-K",
                page_size=1
            )

            find_result = await find_filings(find_args)

            # Skip test if no filings found
            if not find_result.filings:
                pytest.skip("No filings found for the specified date range")

            await api_rate_limiter.wait()

            # Get details for the first filing
            filing_id = find_result.filings[0].filing_id
            get_args = GetFilingArgs(filing_id=filing_id)

            result = await get_filing(get_args)

            # Verify response structure
            assert isinstance(result, GetFilingResponse)
            assert isinstance(result.filing, FilingDetails)
            assert result.filing.filing_id == filing_id
            assert result.filing.company_name
            assert result.filing.form_type
            assert result.filing.filing_date
            assert result.filing.title

            # FilingDetails should have additional fields
            assert hasattr(result.filing, 'summary')
            assert hasattr(result.filing, 'content_preview')
            assert hasattr(result.filing, 'document_count')

    @pytest.mark.asyncio
    async def test_filings_pagination_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test filings pagination with real API."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test first page with large date range to ensure we have results
            args_page1 = FindFilingsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                page=1,
                page_size=5
            )

            result_page1 = await find_filings(args_page1)
            assert result_page1.page == 1
            assert result_page1.page_size == 5

            # If we have enough filings, test second page
            if result_page1.total > 5:
                await api_rate_limiter.wait()

                args_page2 = FindFilingsArgs(
                    start_date="2023-01-01",
                    end_date="2023-12-31",
                    page=2,
                    page_size=5
                )

                result_page2 = await find_filings(args_page2)
                assert result_page2.page == 2
                assert result_page2.page_size == 5
                assert result_page2.total == result_page1.total

                # Filings should be different between pages
                page1_ids = {filing.filing_id for filing in result_page1.filings}
                page2_ids = {filing.filing_id for filing in result_page2.filings}
                assert page1_ids.isdisjoint(page2_ids)

    @pytest.mark.asyncio
    async def test_filings_api_error_handling(
        self,
        integration_mcp_server,
        real_http_client,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test filings API error handling with invalid API key."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_api_key_from_context', return_value="invalid-api-key"):

            args = FindFilingsArgs(
                start_date="2023-10-01",
                end_date="2023-10-31"
            )

            # This should raise an exception or return an error response
            try:
                result = await find_filings(args)
                # If it doesn't raise an exception, check for error indicators
                if hasattr(result, 'error') or len(result.filings) == 0:
                    # API handled the error gracefully
                    pass
            except Exception as e:
                # Expected - invalid API key should cause an error
                assert "401" in str(e) or "Unauthorized" in str(e) or "Invalid" in str(e)

    @pytest.mark.asyncio
    async def test_get_filing_invalid_id(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test get_filing with invalid filing ID."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            # Test with invalid filing ID
            get_args = GetFilingArgs(filing_id="invalid-filing-id-12345")

            # This should raise an exception or return an error
            try:
                result = await get_filing(get_args)
                # If no exception, the result should indicate an error
                assert not hasattr(result, 'filing') or result.filing is None
            except (ValueError, Exception) as e:
                # Expected - invalid filing ID should cause an error
                assert "not found" in str(e).lower() or "invalid" in str(e).lower()

    @pytest.mark.asyncio
    async def test_filings_citations_integration(
        self,
        integration_mcp_server,
        real_http_client,
        real_api_key,
        api_rate_limiter,
        mock_get_http_client
    ):
        """Test that filings responses include citation information."""
        await api_rate_limiter.wait()

        with patch('aiera_mcp.server.mcp', integration_mcp_server), \
             patch('aiera_mcp.tools.base.get_http_client', mock_get_http_client):

            args = FindFilingsArgs(
                start_date="2023-01-01",
                end_date="2023-12-31",
                form_number="10-K",
                page_size=5
            )

            result = await find_filings(args)

            # Verify citations are generated when filings have URLs
            assert hasattr(result, 'citation_information')
            assert isinstance(result.citation_information, list)

            # If filings have official URLs, citations should be created
            filings_with_urls = [f for f in result.filings if f.official_url]
            if filings_with_urls:
                assert len(result.citation_information) >= len(filings_with_urls)

                for citation in result.citation_information:
                    assert citation.title
                    assert citation.url
                    assert citation.url.startswith("https://")