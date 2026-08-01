#!/usr/bin/env python3

"""Unit tests for available_tools and the ENDPOINT_TO_TOOLS mapping.

These guard the invariant that every registered tool is reachable through the
available-endpoints translation, so a newly added tool can't silently end up
permanently reported as a hidden_tool.
"""

import pytest
from unittest.mock import AsyncMock, patch

from aiera_mcp.tools.common.tools import ENDPOINT_TO_TOOLS, available_tools
from aiera_mcp.tools.common.models import AvailableToolsArgs
from aiera_mcp.tools.registry import TOOL_REGISTRY

# Tools that are intentionally not backed by a permission endpoint. available_tools
# is always surfaced (a user who can call anything can enumerate their tools), so
# it has no entry in ENDPOINT_TO_TOOLS.
ENDPOINTLESS_TOOLS = {"available_tools"}


@pytest.mark.unit
class TestEndpointToToolsMapping:
    def test_mapped_tools_are_all_registered(self):
        mapped = {t for tools in ENDPOINT_TO_TOOLS.values() for t in tools}
        unknown = mapped - set(TOOL_REGISTRY.keys())
        assert not unknown, f"ENDPOINT_TO_TOOLS references unregistered tools: {sorted(unknown)}"

    def test_every_registered_tool_is_reachable(self):
        mapped = {t for tools in ENDPOINT_TO_TOOLS.values() for t in tools}
        unreachable = set(TOOL_REGISTRY.keys()) - mapped - ENDPOINTLESS_TOOLS
        assert not unreachable, (
            "these registered tools are not reachable via ENDPOINT_TO_TOOLS and would "
            f"always be reported as hidden_tools: {sorted(unreachable)}"
        )

    def test_research_metadata_endpoints_are_mapped(self):
        assert ENDPOINT_TO_TOOLS.get("/chat-support/get-research-metadata") == [
            "get_research_metadata"
        ]
        assert ENDPOINT_TO_TOOLS.get("/chat-support/get-research-metadata-fields") == [
            "get_research_metadata_fields"
        ]


@pytest.mark.unit
@pytest.mark.asyncio
class TestAvailableTools:
    async def test_translates_endpoints_and_computes_hidden(self):
        # User has permission to the two metadata endpoints only.
        raw = {
            "endpoints": [
                "/chat-support/get-research-metadata",
                "/chat-support/get-research-metadata-fields",
            ]
        }
        with patch(
            "aiera_mcp.tools.common.tools.make_aiera_request",
            new=AsyncMock(return_value=raw),
        ), patch(
            "aiera_mcp.tools.common.tools.get_api_key", return_value="k"
        ), patch(
            "aiera_mcp.tools.common.tools.get_http_client", new=AsyncMock(return_value=object())
        ):
            result = await available_tools(AvailableToolsArgs())

        # Both metadata tools are now surfaced (previously they'd be hidden).
        assert "get_research_metadata" in result.available_tools
        assert "get_research_metadata_fields" in result.available_tools
        assert "available_tools" in result.available_tools  # always included

        # And they must NOT appear in hidden_tools.
        assert "get_research_metadata" not in result.hidden_tools
        assert "get_research_metadata_fields" not in result.hidden_tools

        # hidden + available together cover every registered tool exactly once.
        assert set(result.available_tools) | set(result.hidden_tools) == set(
            TOOL_REGISTRY.keys()
        )
        assert not (set(result.available_tools) & set(result.hidden_tools))
