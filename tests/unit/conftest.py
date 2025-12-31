#!/usr/bin/env python3

"""Unit test specific fixtures and configuration."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import ExitStack

import httpx

from aiera_mcp.tools.base import make_aiera_request


@pytest_asyncio.fixture
async def mock_make_aiera_request():
    """Mock the make_aiera_request function for unit tests."""
    with patch("aiera_mcp.tools.base.make_aiera_request") as mock:
        yield mock


@pytest_asyncio.fixture
async def mock_server_import():
    """Mock the server import used by tools."""
    mock_mcp = MagicMock()
    mock_context = MagicMock()
    mock_context.meta = {"api_key": "test-api-key"}
    mock_mcp.get_context.return_value = mock_context

    with patch.dict(
        "sys.modules",
        {
            "aiera_mcp.server": MagicMock(mcp=mock_mcp),
            "aiera_mcp.tools.server": MagicMock(mcp=mock_mcp),
        },
    ):
        yield mock_mcp


@pytest_asyncio.fixture
async def mock_http_dependencies(mock_server_import, mock_make_aiera_request):
    """Mock all HTTP dependencies for tool testing."""

    # Mock get_http_client
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    async def get_client_patch(ctx):
        return mock_client

    # Mock get_api_key
    def get_api_key_patch():
        return "test-api-key"

    # Use ExitStack to manage many context managers
    with ExitStack() as stack:
        # Base patches
        stack.enter_context(
            patch("aiera_mcp.tools.base.get_http_client", side_effect=get_client_patch)
        )
        stack.enter_context(
            patch("aiera_mcp.get_api_key", side_effect=get_api_key_patch)
        )

        # Tool-specific patches - organized by domain
        tool_modules = [
            "aiera_mcp.tools.transcrippets.tools",
            "aiera_mcp.tools.third_bridge.tools",
            "aiera_mcp.tools.filings.tools",
            "aiera_mcp.tools.equities.tools",
            "aiera_mcp.tools.events.tools",
            "aiera_mcp.tools.company_docs.tools",
            "aiera_mcp.tools.search.tools",
        ]

        for module in tool_modules:
            stack.enter_context(
                patch(f"{module}.get_api_key", return_value="test-api-key")
            )
            stack.enter_context(
                patch(f"{module}.get_http_client", side_effect=get_client_patch)
            )
            stack.enter_context(
                patch(f"{module}.make_aiera_request", mock_make_aiera_request)
            )

        yield {
            "mock_client": mock_client,
            "mock_make_request": mock_make_aiera_request,
            "mock_server": mock_server_import,
        }


# Domain-specific response fixtures
@pytest.fixture
def events_api_responses(sample_api_responses):
    """Events API response fixtures."""
    return sample_api_responses.get("events", {})


@pytest.fixture
def filings_api_responses(sample_api_responses):
    """Filings API response fixtures."""
    return sample_api_responses.get("filings", {})


@pytest.fixture
def equities_api_responses(sample_api_responses):
    """Equities API response fixtures."""
    return sample_api_responses.get("equities", {})


@pytest.fixture
def company_docs_api_responses(sample_api_responses):
    """Company docs API response fixtures."""
    return sample_api_responses.get("company_docs", {})


@pytest.fixture
def third_bridge_api_responses(sample_api_responses):
    """Third Bridge API response fixtures."""
    return sample_api_responses.get("third_bridge", {})


@pytest.fixture
def transcrippets_api_responses(sample_api_responses):
    """Transcrippets API response fixtures."""
    return sample_api_responses.get("transcrippets", {})


@pytest.fixture
def search_api_responses(sample_api_responses):
    """Search API response fixtures."""
    return sample_api_responses.get("search", {})


@pytest.fixture
def error_responses(sample_api_responses):
    """Error response fixtures."""
    return sample_api_responses.get("errors", {})
