#!/usr/bin/env python3

"""Unit tests for the get_creation_templates common tool."""

import pytest
from unittest.mock import AsyncMock, patch

from aiera_mcp.tools.common.tools import get_creation_templates
from aiera_mcp.tools.common.models import (
    GetCreationTemplatesArgs,
    GetCreationTemplatesResponse,
)


@pytest.mark.unit
class TestGetCreationTemplatesArgs:
    def test_all_fields_optional(self):
        # nothing is required; with no filters the API returns the full latest set
        assert GetCreationTemplatesArgs().model_dump(exclude_none=True) == {}

    def test_only_set_filters_are_sent(self):
        args = GetCreationTemplatesArgs(template_type="global")
        assert args.model_dump(exclude_none=True) == {"template_type": "global"}


@pytest.mark.unit
class TestGetCreationTemplates:
    @pytest.mark.asyncio
    async def test_hits_endpoint_and_returns_response(self):
        mock_request = AsyncMock(
            return_value={
                "instructions": [],
                "response": {"templates": [{"template_id": 1, "template_type": "global", "template": "x"}]},
            }
        )

        with patch("aiera_mcp.tools.common.tools.make_aiera_request", mock_request), patch(
            "aiera_mcp.tools.common.tools.get_http_client", AsyncMock(return_value=AsyncMock())
        ), patch("aiera_mcp.tools.common.tools.get_api_key", return_value="test-key"):
            result = await get_creation_templates(
                GetCreationTemplatesArgs(template_type="task", template_subtype="summary")
            )

        assert isinstance(result, GetCreationTemplatesResponse)
        assert result.response["templates"][0]["template_id"] == 1

        kwargs = mock_request.call_args.kwargs
        assert kwargs["method"] == "GET"
        assert kwargs["endpoint"] == "/chat-support/get-creation-templates"
        assert kwargs["params"] == {"template_type": "task", "template_subtype": "summary"}
