#!/usr/bin/env python3

"""Unit test specific fixtures and configuration."""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from aiera_mcp.tools.base import make_aiera_request


@pytest_asyncio.fixture
async def mock_make_aiera_request():
    """Mock the make_aiera_request function for unit tests."""
    with patch('aiera_mcp.tools.base.make_aiera_request') as mock:
        yield mock


@pytest_asyncio.fixture
async def mock_server_import():
    """Mock the server import used by tools."""
    mock_mcp = MagicMock()
    mock_context = MagicMock()
    mock_context.meta = {"api_key": "test-api-key"}
    mock_mcp.get_context.return_value = mock_context

    with patch.dict('sys.modules', {
        'aiera_mcp.server': MagicMock(mcp=mock_mcp),
        'aiera_mcp.tools.server': MagicMock(mcp=mock_mcp)
    }):
        yield mock_mcp


@pytest_asyncio.fixture
async def mock_http_dependencies(mock_server_import, mock_make_aiera_request):
    """Mock all HTTP dependencies for tool testing."""

    # Mock get_http_client
    mock_client = AsyncMock(spec=httpx.AsyncClient)

    async def get_client_patch(ctx):
        return mock_client

    # Mock get_api_key_from_context
    async def get_api_key_patch(ctx):
        return "test-api-key"

    with patch('aiera_mcp.tools.base.get_http_client', side_effect=get_client_patch), \
         patch('aiera_mcp.tools.base.get_api_key_from_context', side_effect=get_api_key_patch), \
         patch('aiera_mcp.tools.transcrippets.tools.get_api_key_from_context', side_effect=get_api_key_patch), \
         patch('aiera_mcp.tools.transcrippets.tools.get_http_client', side_effect=get_client_patch), \
         patch('aiera_mcp.tools.transcrippets.tools.make_aiera_request', mock_make_aiera_request), \
         patch('aiera_mcp.tools.third_bridge.tools.get_api_key_from_context', side_effect=get_api_key_patch), \
         patch('aiera_mcp.tools.third_bridge.tools.get_http_client', side_effect=get_client_patch), \
         patch('aiera_mcp.tools.third_bridge.tools.make_aiera_request', mock_make_aiera_request), \
         patch('aiera_mcp.tools.filings.tools.get_api_key_from_context', side_effect=get_api_key_patch), \
         patch('aiera_mcp.tools.filings.tools.get_http_client', side_effect=get_client_patch), \
         patch('aiera_mcp.tools.filings.tools.make_aiera_request', mock_make_aiera_request), \
         patch('aiera_mcp.tools.equities.tools.get_api_key_from_context', side_effect=get_api_key_patch), \
         patch('aiera_mcp.tools.equities.tools.get_http_client', side_effect=get_client_patch), \
         patch('aiera_mcp.tools.equities.tools.make_aiera_request', mock_make_aiera_request), \
         patch('aiera_mcp.tools.events.tools.get_api_key_from_context', side_effect=get_api_key_patch), \
         patch('aiera_mcp.tools.events.tools.get_http_client', side_effect=get_client_patch), \
         patch('aiera_mcp.tools.events.tools.make_aiera_request', mock_make_aiera_request), \
         patch('aiera_mcp.tools.company_docs.tools.get_api_key_from_context', side_effect=get_api_key_patch), \
         patch('aiera_mcp.tools.company_docs.tools.get_http_client', side_effect=get_client_patch), \
         patch('aiera_mcp.tools.company_docs.tools.make_aiera_request', mock_make_aiera_request):

        yield {
            'mock_client': mock_client,
            'mock_make_request': mock_make_aiera_request,
            'mock_server': mock_server_import
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
def error_responses(sample_api_responses):
    """Error response fixtures."""
    return sample_api_responses.get("errors", {})