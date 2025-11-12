#!/usr/bin/env python3

"""Global test configuration and fixtures for Aiera MCP tests."""

import os
import json
from typing import Dict, Any
from pathlib import Path

import pytest
import pytest_asyncio
import httpx
from unittest.mock import AsyncMock, MagicMock

from aiera_mcp.tools.base import get_http_client, get_api_key_from_context


# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "fixtures"
SAMPLE_API_RESPONSES_FILE = TEST_DATA_DIR / "api_responses.json"


@pytest_asyncio.fixture
async def mock_mcp_context():
    """Mock MCP context for testing tools."""
    mock_context = MagicMock()
    mock_context.meta = {"api_key": "test-api-key"}
    return mock_context


@pytest_asyncio.fixture
async def mock_http_client():
    """Mock HTTP client for unit tests."""
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest_asyncio.fixture
async def sample_api_responses():
    """Load sample API responses from fixtures."""
    if SAMPLE_API_RESPONSES_FILE.exists():
        with open(SAMPLE_API_RESPONSES_FILE, "r") as f:
            return json.load(f)
    return {}


@pytest.fixture
def api_key():
    """Get API key from environment or use test key."""
    return os.getenv("AIERA_API_KEY", "test-api-key")


@pytest_asyncio.fixture
async def integration_http_client():
    """Real HTTP client for integration tests."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client


@pytest.fixture
def integration_api_key():
    """API key for integration tests - skip test if not provided."""
    api_key = os.getenv("AIERA_API_KEY")
    if not api_key:
        pytest.skip(
            "AIERA_API_KEY environment variable not set - skipping integration test"
        )
    return api_key


# Test data generators
class APIResponseBuilder:
    """Helper class to build API responses for testing."""

    @staticmethod
    def build_events_response(events: list = None, total: int = None) -> Dict[str, Any]:
        """Build events API response."""
        events = events or [
            {
                "id": 12345,
                "title": "Apple Inc Q4 2023 Earnings Call",
                "event_type": "earnings",
                "event_date": "2023-10-26T21:00:00Z",
                "company_name": "Apple Inc",
                "ticker": "AAPL",
                "event_status": "confirmed",
                "description": "Q4 2023 earnings call for Apple Inc",
                "transcript_preview": "Welcome to the Apple Q4 2023 earnings call...",
                "audio_url": "https://example.com/audio/12345.mp3",
                "url": "https://aiera.com/event/12345",
            }
        ]

        return {
            "response": {"data": events, "total": total or len(events)},
            "instructions": ["Sample instructions from API"],
        }

    @staticmethod
    def build_filings_response(
        filings: list = None, total: int = None
    ) -> Dict[str, Any]:
        """Build filings API response."""
        filings = filings or [
            {
                "id": "54321",
                "company_name": "Apple Inc",
                "ticker": "AAPL",
                "form_type": "10-K",
                "title": "Annual Report",
                "filing_date": "2023-10-27T00:00:00Z",
                "period_end_date": "2023-09-30T00:00:00Z",
                "is_amendment": False,
                "official_url": "https://sec.gov/filing/54321",
                "summary": "Annual report summary",
                "key_points": ["Revenue increased", "Strong margins"],
                "financial_highlights": {"revenue": "$394.3B", "net_income": "$97.0B"},
                "content_preview": "This annual report contains...",
                "document_count": 1,
            }
        ]

        return {
            "response": {"data": filings, "total": total or len(filings)},
            "instructions": ["Sample filing instructions"],
        }

    @staticmethod
    def build_equities_response(
        equities: list = None, total: int = None
    ) -> Dict[str, Any]:
        """Build equities API response."""
        equities = equities or [
            {
                "id": "67890",
                "company_name": "Apple Inc",
                "ticker": "AAPL",
                "bloomberg_ticker": "AAPL:US",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "subsector": "Consumer Electronics",
                "country": "United States",
                "market_cap": 3000000000000,
                "identifiers": {"isin": "US0378331005", "cusip": "037833100"},
            }
        ]

        return {
            "response": {"data": equities, "total": total or len(equities)},
            "instructions": ["Sample equity instructions"],
        }


@pytest.fixture
def api_response_builder():
    """Fixture providing API response builder."""
    return APIResponseBuilder


# Mock patches for unit tests
@pytest.fixture
def mock_server_mcp(mock_mcp_context):
    """Mock the server mcp instance used by tools."""
    mock_mcp_server = MagicMock()
    mock_mcp_server.get_context.return_value = mock_mcp_context
    return mock_mcp_server


@pytest_asyncio.fixture
async def patch_get_http_client(mock_http_client):
    """Patch get_http_client function."""

    async def _get_http_client(ctx):
        return mock_http_client

    return _get_http_client


@pytest_asyncio.fixture
async def patch_get_api_key(api_key):
    """Patch get_api_key_from_context function."""

    async def _get_api_key(ctx):
        return api_key

    return _get_api_key


# Parametrized fixtures for comprehensive testing
@pytest.fixture(
    params=[
        "events",
        "filings",
        "equities",
        "company_docs",
        "third_bridge",
        "transcrippets",
    ]
)
def domain_name(request):
    """Parametrized fixture for testing all domains."""
    return request.param


@pytest.fixture(params=[200, 400, 401, 403, 404, 500])
def http_status_code(request):
    """Parametrized fixture for testing various HTTP status codes."""
    return request.param


@pytest.fixture(params=["GET", "POST", "PUT", "DELETE"])
def http_method(request):
    """Parametrized fixture for testing various HTTP methods."""
    return request.param
