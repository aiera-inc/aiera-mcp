#!/usr/bin/env python3

"""Unit tests for filings tools."""

import pytest
import pytest_asyncio
from datetime import datetime, date
from unittest.mock import AsyncMock

from aiera_mcp.tools.filings.tools import find_filings, get_filing
from aiera_mcp.tools.filings.models import (
    FindFilingsArgs, GetFilingArgs,
    FindFilingsResponse, GetFilingResponse,
    FilingItem, FilingDetails, FilingSummary
)


@pytest.mark.unit
class TestFindFilings:
    """Test the find_filings tool."""

    @pytest.mark.asyncio
    async def test_find_filings_success(self, mock_http_dependencies, filings_api_responses):
        """Test successful filings search."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = filings_api_responses["find_filings_success"]

        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            form_number="10-K"
        )

        # Execute
        result = await find_filings(args)

        # Verify
        assert isinstance(result, FindFilingsResponse)
        assert len(result.filings) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 50

        # Check first filing
        first_filing = result.filings[0]
        assert isinstance(first_filing, FilingItem)
        assert first_filing.filing_id == "filing789"
        assert first_filing.company_name == "Apple Inc"
        assert first_filing.company_ticker == "AAPL"
        assert first_filing.form_type == "10-K"
        assert first_filing.title == "Annual Report"
        assert first_filing.filing_date == date(2023, 10, 27)
        assert first_filing.period_end_date == date(2023, 9, 30)
        assert not first_filing.is_amendment

        # Check API call was made correctly
        mock_http_dependencies['mock_make_request'].assert_called_once()
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-filings"

        # Check parameters were passed correctly
        params = call_args[1]['params']
        assert params['start_date'] == "2023-10-01"
        assert params['end_date'] == "2023-10-31"
        assert params['bloomberg_ticker'] == "AAPL:US"
        assert params['form_number'] == "10-K"

    @pytest.mark.asyncio
    async def test_find_filings_empty_results(self, mock_http_dependencies):
        """Test find_filings with empty results."""
        # Setup
        empty_response = {
            "response": {"data": [], "total": 0},
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = empty_response

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify
        assert isinstance(result, FindFilingsResponse)
        assert len(result.filings) == 0
        assert result.total == 0
        assert len(result.citation_information) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_number", ["10-K", "10-Q", "8-K", "DEF 14A"])
    async def test_find_filings_different_form_types(self, mock_http_dependencies, filings_api_responses, form_number):
        """Test find_filings with different form types."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = filings_api_responses["find_filings_success"]

        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            form_number=form_number
        )

        # Execute
        result = await find_filings(args)

        # Verify
        assert isinstance(result, FindFilingsResponse)
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['params']['form_number'] == form_number

    @pytest.mark.asyncio
    async def test_find_filings_pagination(self, mock_http_dependencies, filings_api_responses):
        """Test find_filings with pagination parameters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = filings_api_responses["find_filings_success"]

        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            page=2,
            page_size=25
        )

        # Execute
        result = await find_filings(args)

        # Verify
        assert result.page == 2
        assert result.page_size == 25

        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['page'] == "2"  # Should be serialized as string
        assert params['page_size'] == "25"

    @pytest.mark.asyncio
    async def test_find_filings_with_filters(self, mock_http_dependencies, filings_api_responses):
        """Test find_filings with various filters."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = filings_api_responses["find_filings_success"]

        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US,MSFT:US",
            watchlist_id=123,
            sector_id=456,
            subsector_id=789
        )

        # Execute
        result = await find_filings(args)

        # Verify
        call_args = mock_http_dependencies['mock_make_request'].call_args
        params = call_args[1]['params']
        assert params['bloomberg_ticker'] == "AAPL:US,MSFT:US"
        assert params['watchlist_id'] == "123"
        assert params['sector_id'] == "456"
        assert params['subsector_id'] == "789"

    @pytest.mark.asyncio
    async def test_find_filings_citations_generated(self, mock_http_dependencies, filings_api_responses):
        """Test that find_filings generates proper citations."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = filings_api_responses["find_filings_success"]

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify citations were created
        assert len(result.citation_information) == 1
        first_citation = result.citation_information[0]
        assert "Apple Inc" in first_citation.title
        assert "10-K" in first_citation.title
        assert first_citation.url == "https://sec.gov/filing/filing789"
        assert first_citation.timestamp is not None


@pytest.mark.unit
class TestGetFiling:
    """Test the get_filing tool."""

    @pytest.mark.asyncio
    async def test_get_filing_success(self, mock_http_dependencies, filings_api_responses):
        """Test successful filing retrieval."""
        # Setup
        mock_http_dependencies['mock_make_request'].return_value = filings_api_responses["get_filing_success"]

        args = GetFilingArgs(filing_id="filing789")

        # Execute
        result = await get_filing(args)

        # Verify
        assert isinstance(result, GetFilingResponse)
        assert isinstance(result.filing, FilingDetails)
        assert result.filing.filing_id == "filing789"
        assert result.filing.company_name == "Apple Inc"
        assert result.filing.form_type == "10-K"
        assert result.filing.title == "Annual Report"
        assert result.filing.content_preview is not None
        assert result.filing.document_count == 1

        # Check filing summary
        assert result.filing.summary is not None
        assert isinstance(result.filing.summary, FilingSummary)
        assert "Apple Inc's annual report" in result.filing.summary.summary
        assert len(result.filing.summary.key_points) == 3
        assert "Record revenue" in result.filing.summary.key_points[0]
        assert "$394.3B" in result.filing.summary.financial_highlights["revenue"]

        # Check API call parameters
        call_args = mock_http_dependencies['mock_make_request'].call_args
        assert call_args[1]['method'] == "GET"
        assert call_args[1]['endpoint'] == "/chat-support/find-filings"

        # Check field mapping (filing_id -> filing_ids)
        params = call_args[1]['params']
        assert 'filing_ids' in params
        assert params['filing_ids'] == "filing789"
        assert 'filing_id' not in params
        assert params['include_content'] == "true"

    @pytest.mark.asyncio
    async def test_get_filing_not_found(self, mock_http_dependencies):
        """Test get_filing when filing is not found."""
        # Setup - empty response
        mock_http_dependencies['mock_make_request'].return_value = {
            "response": {"data": []},
            "instructions": []
        }

        args = GetFilingArgs(filing_id="nonexistent")

        # Execute & Verify
        with pytest.raises(ValueError, match="Filing not found: nonexistent"):
            await get_filing(args)

    @pytest.mark.asyncio
    async def test_get_filing_date_parsing(self, mock_http_dependencies):
        """Test get_filing handles date parsing correctly."""
        # Setup with various date formats
        response_with_dates = {
            "response": {
                "data": [
                    {
                        "id": "filing123",
                        "company_name": "Test Company",
                        "form_type": "10-K",
                        "title": "Test Filing",
                        "filing_date": "2023-10-27T00:00:00Z",  # ISO format with Z
                        "period_end_date": "2023-09-30T00:00:00Z",
                        "is_amendment": False
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_dates

        args = GetFilingArgs(filing_id="filing123")

        # Execute
        result = await get_filing(args)

        # Verify dates were parsed correctly
        assert isinstance(result.filing.filing_date, date)
        assert result.filing.filing_date.year == 2023
        assert result.filing.filing_date.month == 10
        assert result.filing.filing_date.day == 27

        assert isinstance(result.filing.period_end_date, date)
        assert result.filing.period_end_date.year == 2023
        assert result.filing.period_end_date.month == 9
        assert result.filing.period_end_date.day == 30

    @pytest.mark.asyncio
    async def test_get_filing_with_minimal_summary(self, mock_http_dependencies):
        """Test get_filing with minimal summary data."""
        # Setup with minimal data
        minimal_response = {
            "response": {
                "data": [
                    {
                        "id": "filing123",
                        "company_name": "Test Company",
                        "form_type": "10-K",
                        "title": "Test Filing",
                        "filing_date": "2023-10-27T00:00:00Z",
                        "is_amendment": False,
                        # No summary fields
                    }
                ]
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = minimal_response

        args = GetFilingArgs(filing_id="filing123")

        # Execute
        result = await get_filing(args)

        # Verify
        assert result.filing.summary is None  # Should be None when no summary data


@pytest.mark.unit
class TestFilingsToolsErrorHandling:
    """Test error handling for filings tools."""

    @pytest.mark.asyncio
    async def test_handle_malformed_response(self, mock_http_dependencies):
        """Test handling of malformed API responses."""
        # Setup - malformed response
        mock_http_dependencies['mock_make_request'].return_value = {"invalid": "response"}

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify - should handle gracefully with empty results
        assert isinstance(result, FindFilingsResponse)
        assert len(result.filings) == 0
        assert result.total == 0

    @pytest.mark.asyncio
    async def test_handle_missing_date_fields(self, mock_http_dependencies):
        """Test handling of filings with missing or invalid date fields."""
        # Setup - response with missing/invalid dates
        response_with_bad_dates = {
            "response": {
                "data": [
                    {
                        "id": "filing123",
                        "company_name": "Test Company",
                        "form_type": "10-K",
                        "title": "Test Filing",
                        "filing_date": "invalid-date",  # Invalid date
                        "is_amendment": False
                    },
                    {
                        "id": "filing456",
                        "company_name": "Test Company 2",
                        "form_type": "10-Q",
                        "title": "Test Filing 2",
                        # Missing filing_date
                        "is_amendment": False
                    }
                ],
                "total": 2
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = response_with_bad_dates

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify - should still process filings with fallback dates
        assert len(result.filings) == 2
        for filing in result.filings:
            assert isinstance(filing.filing_date, date)  # Should have fallback date (today)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("exception_type", [ConnectionError, TimeoutError, ValueError])
    async def test_network_errors_propagate(self, mock_http_dependencies, exception_type):
        """Test that network errors are properly propagated."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies['mock_make_request'].side_effect = exception_type("Test error")

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute & Verify
        with pytest.raises(exception_type):
            await find_filings(args)

    @pytest.mark.asyncio
    async def test_amendment_flag_handling(self, mock_http_dependencies):
        """Test proper handling of amendment flags."""
        # Setup with amendment filing
        amendment_response = {
            "response": {
                "data": [
                    {
                        "id": "filing_amend",
                        "company_name": "Test Company",
                        "form_type": "10-K/A",
                        "title": "Annual Report Amendment",
                        "filing_date": "2023-10-27T00:00:00Z",
                        "is_amendment": True,
                        "official_url": "https://sec.gov/filing/filing_amend"
                    }
                ],
                "total": 1
            },
            "instructions": []
        }
        mock_http_dependencies['mock_make_request'].return_value = amendment_response

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify amendment handling
        assert len(result.filings) == 1
        filing = result.filings[0]
        assert filing.is_amendment is True
        assert "10-K/A" in filing.form_type
        assert "Amendment" in filing.title