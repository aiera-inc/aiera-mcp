"""CORE-4557: available_tools must surface an upstream auth error rather than
silently returning a near-empty tool list."""

from unittest.mock import AsyncMock, patch

import pytest

from aiera_mcp.tools.common.models import AvailableToolsArgs
from aiera_mcp.tools.common.tools import available_tools


@pytest.mark.asyncio
async def test_upstream_auth_error_is_propagated():
    err = "The user is not properly authenticated with Aiera. Please instruct the user to re-authenticate."
    with patch("aiera_mcp.tools.common.tools.get_http_client", new=AsyncMock(return_value=object())), patch(
        "aiera_mcp.tools.common.tools.get_api_key", return_value="deadbeef"
    ), patch("aiera_mcp.tools.common.tools.make_aiera_request", new=AsyncMock(return_value={"error": err})):
        resp = await available_tools(AvailableToolsArgs())
    assert resp.error == err
    assert resp.available_tools == ["available_tools"]


@pytest.mark.asyncio
async def test_healthy_response_has_no_error():
    with patch("aiera_mcp.tools.common.tools.get_http_client", new=AsyncMock(return_value=object())), patch(
        "aiera_mcp.tools.common.tools.get_api_key", return_value="k"
    ), patch(
        "aiera_mcp.tools.common.tools.make_aiera_request",
        new=AsyncMock(return_value={"endpoints": ["/chat-support/find-events"]}),
    ):
        resp = await available_tools(AvailableToolsArgs())
    assert resp.error is None
    assert "find_events" in resp.available_tools
