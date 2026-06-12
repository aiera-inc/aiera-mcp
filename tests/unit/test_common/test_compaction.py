#!/usr/bin/env python3

"""Unit tests for compacted-response handling (models, detection helper, schema exposure)."""

import pytest

from aiera_mcp.tools.common.models import (
    CompactArgsMixin,
    CompactedResponseBody,
    is_compacted_response,
)
from aiera_mcp.tools.research.models import FindResearchArgs, FindResearchResponse
from aiera_mcp.tools.search.models import SearchTranscriptsArgs

COMPACTED_RAW_RESPONSE = {
    "instructions": ["be helpful"],
    "response": {
        "compacted": True,
        "compaction_note": "Lossy summary; re-call with compact=false for full data.",
        "summary": "## Digest\nNVDA margins expanded...",
        "preserved": {
            "ids": {"content_id": [111, 222]},
            "citations": [{"url": "https://a/1", "metadata": {"type": "research"}}],
            "pagination": {"total": 40, "next_search_after": [1, 2]},
        },
    },
}


@pytest.mark.unit
class TestIsCompactedResponse:
    def test_detects_compacted_envelope(self):
        assert is_compacted_response(COMPACTED_RAW_RESPONSE) is True

    def test_regular_response_not_compacted(self):
        assert is_compacted_response({"instructions": [], "response": {"data": [1]}}) is False

    def test_non_dict_inputs(self):
        assert is_compacted_response(None) is False
        assert is_compacted_response("text") is False
        assert is_compacted_response({"response": "text"}) is False

    def test_compacted_must_be_true(self):
        assert is_compacted_response({"response": {"compacted": False}}) is False


@pytest.mark.unit
class TestCompactedResponseBody:
    def test_validates_api_envelope(self):
        body = CompactedResponseBody.model_validate(COMPACTED_RAW_RESPONSE["response"])

        assert body.compacted is True
        assert body.summary.startswith("## Digest")
        assert body.preserved["ids"]["content_id"] == [111, 222]
        assert body.preserved["citations"][0]["url"] == "https://a/1"


@pytest.mark.unit
class TestCompactedEnvelopePassthrough:
    def test_domain_response_model_tolerates_compacted_envelope(self):
        """Domain response models use `response: Any` passthrough, so a compacted
        envelope must validate without error and survive round-tripping."""
        response = FindResearchResponse.model_validate(COMPACTED_RAW_RESPONSE)

        assert response.instructions == ["be helpful"]
        assert response.response["compacted"] is True
        assert response.response["preserved"]["pagination"]["total"] == 40

        # round-trips through model_dump (what server.py sends to the MCP client)
        dumped = response.model_dump()
        assert dumped["response"]["summary"].startswith("## Digest")


@pytest.mark.unit
class TestCompactArgsExposure:
    def test_compact_in_input_schema(self):
        for args_model in (FindResearchArgs, SearchTranscriptsArgs):
            schema = args_model.model_json_schema()
            assert "compact" in schema["properties"], args_model.__name__

    def test_unset_compact_excluded_from_params(self):
        args = FindResearchArgs()
        assert "compact" not in args.model_dump(exclude_none=True)

    def test_set_compact_included_in_params(self):
        args = FindResearchArgs(compact=True)
        assert args.model_dump(exclude_none=True)["compact"] is True

    def test_mixin_default_is_none(self):
        assert CompactArgsMixin().compact is None
