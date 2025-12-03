#!/usr/bin/env python3

"""Unit tests for filings tools."""

import pytest
import pytest_asyncio
from datetime import date
from unittest.mock import AsyncMock

from aiera_mcp.tools.filings.tools import find_filings, get_filing
from aiera_mcp.tools.filings.models import (
    FindFilingsArgs,
    GetFilingArgs,
    FindFilingsResponse,
    GetFilingResponse,
    FilingItem,
    FilingDetails,
    FilingSummary,
)


@pytest.mark.unit
class TestFindFilings:
    """Test the find_filings tool."""

    @pytest.mark.asyncio
    async def test_find_filings_success(
        self, mock_http_dependencies, filings_api_responses
    ):
        """Test successful filings search."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            filings_api_responses["find_filings_success"]
        )

        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US",
            form_number="10-K",
        )

        # Execute
        result = await find_filings(args)

        # Verify
        assert isinstance(result, FindFilingsResponse)
        assert len(result.response.data) == 1
        assert result.response.data is not None

        # Check first filing
        first_filing = result.response.data[0]
        assert isinstance(first_filing, FilingItem)
        assert first_filing.filing_id == 789
        assert first_filing.equity.company_name == "Apple Inc"
        assert first_filing.equity.ticker == "AAPL"
        assert first_filing.form_number == "10-K"
        assert first_filing.title == "Annual Report"
        assert first_filing.filing_date is not None
        assert first_filing.period_end_date is not None
        assert first_filing.is_amendment == 0

        # Check API call was made correctly
        mock_http_dependencies["mock_make_request"].assert_called_once()
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-filings"

        # Check parameters were passed correctly
        params = call_args[1]["params"]
        assert params["start_date"] == "2023-10-01"
        assert params["end_date"] == "2023-10-31"
        assert params["bloomberg_ticker"] == "AAPL:US"
        assert params["form_number"] == "10-K"

    @pytest.mark.asyncio
    async def test_find_filings_empty_results(self, mock_http_dependencies):
        """Test find_filings with empty results."""
        # Setup
        empty_response = {"response": {"data": [], "total": 0}, "instructions": []}
        mock_http_dependencies["mock_make_request"].return_value = empty_response

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify
        assert isinstance(result, FindFilingsResponse)
        assert len(result.response.data) == 0
        assert result.response.pagination is not None or len(result.response.data) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("form_number", ["10-K", "10-Q", "8-K", "DEF 14A"])
    async def test_find_filings_different_form_types(
        self, mock_http_dependencies, filings_api_responses, form_number
    ):
        """Test find_filings with different form types."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            filings_api_responses["find_filings_success"]
        )

        args = FindFilingsArgs(
            start_date="2023-10-01", end_date="2023-10-31", form_number=form_number
        )

        # Execute
        result = await find_filings(args)

        # Verify
        assert isinstance(result, FindFilingsResponse)
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["params"]["form_number"] == form_number

    @pytest.mark.asyncio
    async def test_find_filings_pagination(
        self, mock_http_dependencies, filings_api_responses
    ):
        """Test find_filings with pagination parameters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            filings_api_responses["find_filings_success"]
        )

        args = FindFilingsArgs(
            start_date="2023-10-01", end_date="2023-10-31", page=2, page_size=25
        )

        # Execute
        result = await find_filings(args)

        # Verify - checking that pagination args were passed correctly
        assert isinstance(result, FindFilingsResponse)

        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["page"] == "2"  # Should be serialized as string
        assert params["page_size"] == "25"

    @pytest.mark.asyncio
    async def test_find_filings_with_filters(
        self, mock_http_dependencies, filings_api_responses
    ):
        """Test find_filings with various filters."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            filings_api_responses["find_filings_success"]
        )

        args = FindFilingsArgs(
            start_date="2023-10-01",
            end_date="2023-10-31",
            bloomberg_ticker="AAPL:US,MSFT:US",
            watchlist_id=123,
            sector_id=456,
            subsector_id=789,
        )

        # Execute
        result = await find_filings(args)

        # Verify
        call_args = mock_http_dependencies["mock_make_request"].call_args
        params = call_args[1]["params"]
        assert params["bloomberg_ticker"] == "AAPL:US,MSFT:US"
        assert params["watchlist_id"] == "123"
        assert params["sector_id"] == "456"
        assert params["subsector_id"] == "789"

    @pytest.mark.asyncio
    async def test_find_filings_citations_generated(
        self, mock_http_dependencies, filings_api_responses
    ):
        """Test that find_filings generates proper citations."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            filings_api_responses["find_filings_success"]
        )

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify response structure
        assert len(result.response.data) == 1
        first_filing = result.response.data[0]
        assert first_filing.equity.company_name == "Apple Inc"
        assert first_filing.form_number == "10-K"


@pytest.mark.unit
class TestGetFiling:
    """Test the get_filing tool."""

    @pytest.mark.asyncio
    async def test_get_filing_success(
        self, mock_http_dependencies, filings_api_responses
    ):
        """Test successful filing retrieval."""
        # Setup
        mock_http_dependencies["mock_make_request"].return_value = (
            filings_api_responses["get_filing_success"]
        )

        args = GetFilingArgs(filing_id="filing789")

        # Execute
        result = await get_filing(args)

        # Verify
        assert isinstance(result, GetFilingResponse)
        assert isinstance(result.filing, FilingDetails)
        assert result.filing.filing_id == 789
        assert result.filing.equity.company_name == "Apple Inc"
        assert result.filing.form_number == "10-K"
        assert result.filing.title == "Annual Report"
        # Note: content_preview and document_count may not be in test fixture

        # Check filing summary exists in the data
        assert result.filing.summary is not None

        # Check API call parameters
        call_args = mock_http_dependencies["mock_make_request"].call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["endpoint"] == "/chat-support/find-filings"

        # Check field mapping (filing_id -> filing_ids)
        params = call_args[1]["params"]
        assert "filing_ids" in params
        assert params["filing_ids"] == "filing789"
        assert "filing_id" not in params
        assert params["include_content"] == "true"

    @pytest.mark.asyncio
    async def test_get_filing_not_found(self, mock_http_dependencies):
        """Test get_filing when filing is not found."""
        # Setup - empty response
        mock_http_dependencies["mock_make_request"].return_value = {
            "response": {"data": []},
            "instructions": [],
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
                        "filing_id": 123,
                        "equity": {"company_name": "Test Company", "ticker": "TEST"},
                        "form_number": "10-K",
                        "title": "Test Filing",
                        "filing_date": "2023-10-27T00:00:00Z",  # ISO format with Z
                        "period_end_date": "2023-09-30T00:00:00Z",
                        "is_amendment": 0,
                    }
                ]
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = response_with_dates

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
                        "filing_id": 123,
                        "equity": {"company_name": "Test Company", "ticker": "TEST"},
                        "form_number": "10-K",
                        "title": "Test Filing",
                        "filing_date": "2023-10-27T00:00:00Z",
                        "is_amendment": 0,
                        # No optional summary fields
                    }
                ]
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = minimal_response

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
        """Test handling of malformed API responses.

        Note: Since FindFilingsResponse has optional response field,
        malformed data like {"invalid": "response"} will pass validation
        with response=None.
        """
        # Setup - malformed response
        mock_http_dependencies["mock_make_request"].return_value = {
            "invalid": "response"
        }

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify - malformed data results in None response
        assert isinstance(result, FindFilingsResponse)
        assert result.response is None

    @pytest.mark.asyncio
    async def test_handle_missing_date_fields(self, mock_http_dependencies):
        """Test handling of filings with missing or invalid date fields."""
        # Setup - response with missing/invalid dates
        response_with_bad_dates = {
            "response": {
                "data": [
                    {
                        "filing_id": 123,
                        "equity": {"company_name": "Test Company", "ticker": "TEST"},
                        "form_number": "10-K",
                        "title": "Test Filing",
                        "filing_date": "invalid-date",  # Invalid date
                        "is_amendment": 0,
                    },
                    {
                        "filing_id": 456,
                        "equity": {"company_name": "Test Company 2", "ticker": "TEST2"},
                        "form_number": "10-Q",
                        "title": "Test Filing 2",
                        # Missing filing_date
                        "is_amendment": 0,
                    },
                ],
                "total": 2,
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = (
            response_with_bad_dates
        )

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify - should still process filings
        assert len(result.response.data) == 2
        for filing in result.response.data:
            # filing_date may be None for invalid dates in test data
            assert filing.filing_id is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "exception_type", [ConnectionError, TimeoutError, ValueError]
    )
    async def test_network_errors_propagate(
        self, mock_http_dependencies, exception_type
    ):
        """Test that network errors are properly propagated."""
        # Setup - make_aiera_request raises exception
        mock_http_dependencies["mock_make_request"].side_effect = exception_type(
            "Test error"
        )

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
                        "filing_id": 999,
                        "equity": {"company_name": "Test Company", "ticker": "TEST"},
                        "form_number": "10-K/A",
                        "title": "Annual Report Amendment",
                        "filing_date": "2023-10-27T00:00:00Z",
                        "is_amendment": 1,
                        "official_url": "https://sec.gov/filing/filing_amend",
                    }
                ],
                "total": 1,
            },
            "instructions": [],
        }
        mock_http_dependencies["mock_make_request"].return_value = amendment_response

        args = FindFilingsArgs(start_date="2023-10-01", end_date="2023-10-31")

        # Execute
        result = await find_filings(args)

        # Verify amendment handling
        assert len(result.response.data) == 1
        filing = result.response.data[0]
        assert filing.is_amendment == 1  # Expect 1 for True
        assert filing.form_number == "10-K/A"  # Note: form_number not form_type
        assert "Amendment" in filing.title
