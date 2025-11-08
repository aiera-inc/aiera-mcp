#!/usr/bin/env python3

"""Integration test specific fixtures and configuration."""

import os
import pytest
import pytest_asyncio
from unittest.mock import MagicMock

import httpx
from aiera_mcp.tools.base import get_http_client, get_api_key_from_context


@pytest.fixture
def real_api_key():
    """Get real API key for integration tests."""
    api_key = os.getenv("AIERA_API_KEY")
    if not api_key:
        pytest.skip("AIERA_API_KEY environment variable not set - skipping integration test")
    return api_key


@pytest_asyncio.fixture
async def real_http_client():
    """Real HTTP client for integration tests with extended timeout."""
    client = httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=10.0, read=60.0),
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
    )
    try:
        yield client
    finally:
        try:
            await client.aclose()
        except RuntimeError:
            # Event loop might be closed, ignore cleanup errors
            pass


@pytest.fixture
def integration_context(real_api_key):
    """Mock context with real API key for integration tests."""
    mock_context = MagicMock()
    mock_context.meta = {"api_key": real_api_key}

    # Ensure lifespan context returns None so get_http_client falls back to get_lambda_http_client
    mock_context.request_context.lifespan_context.get.return_value = None

    return mock_context


@pytest.fixture
def integration_mcp_server(integration_context):
    """Mock MCP server with real context for integration tests."""
    mock_mcp = MagicMock()
    mock_mcp.get_context.return_value = integration_context
    return mock_mcp


@pytest.fixture
def mock_get_http_client(real_http_client):
    """Mock get_http_client to return real HTTP client.

    Note: Due to pytest-asyncio event loop lifecycle issues, running multiple
    integration tests in the same session may cause event loop closure errors.
    Tests work fine when run individually.
    """
    async def _get_http_client(ctx):
        return real_http_client
    return _get_http_client


# Test data for integration tests
@pytest.fixture
def sample_tickers():
    """Sample tickers for testing that should have data."""
    return ["AAPL:US", "MSFT:US", "GOOGL:US", "TSLA:US", "AMZN:US"]


@pytest.fixture
def sample_date_ranges():
    """Sample date ranges for testing."""
    return [
        {"start_date": "2023-10-01", "end_date": "2023-10-31"},  # Q4 2023 earnings season
        {"start_date": "2023-07-01", "end_date": "2023-07-31"},  # Q3 2023 earnings season
        {"start_date": "2024-01-01", "end_date": "2024-01-31"},  # Q4 2023 earnings season
    ]


@pytest.fixture
def large_companies():
    """List of large companies that should have various document types."""
    return [
        {"ticker": "AAPL:US", "name": "Apple Inc"},
        {"ticker": "MSFT:US", "name": "Microsoft Corporation"},
        {"ticker": "GOOGL:US", "name": "Alphabet Inc"},
    ]


# Fixtures for skipping tests based on environment
@pytest.fixture
def skip_if_no_api_key():
    """Skip test if no API key available."""
    if not os.getenv("AIERA_API_KEY"):
        pytest.skip("Integration tests require AIERA_API_KEY environment variable")


@pytest.fixture
def skip_expensive_tests():
    """Skip expensive tests unless explicitly enabled."""
    if not os.getenv("RUN_EXPENSIVE_TESTS", "").lower() in ("1", "true", "yes"):
        pytest.skip("Expensive tests require RUN_EXPENSIVE_TESTS=1 environment variable")


# Rate limiting helpers
class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, calls_per_second: float = 2.0):
        self.calls_per_second = calls_per_second
        self.last_call_time = 0

    async def wait(self):
        """Wait if necessary to respect rate limits."""
        import asyncio
        import time

        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        min_interval = 1.0 / self.calls_per_second

        if time_since_last_call < min_interval:
            wait_time = min_interval - time_since_last_call
            await asyncio.sleep(wait_time)

        self.last_call_time = time.time()


@pytest.fixture
def api_rate_limiter():
    """Rate limiter for API calls to avoid hitting rate limits."""
    return RateLimiter(calls_per_second=1.0)  # Conservative 1 call per second