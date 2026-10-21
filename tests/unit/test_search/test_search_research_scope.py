#!/usr/bin/env python3

"""search_research company scope: identifiers are declared, corrected and forwarded."""

import pytest

from aiera_mcp.tools.search.models import SearchResearchArgs
from aiera_mcp.tools.search.tools import search_research

EMPTY = {"instructions": [], "response": {"data": [], "pagination": {"total": 0}}}

IDENTS = {
    "bloomberg_ticker": "INTC:US",
    "isin": "US4581401001",
    "ric": "INTC.O",
    "permid": "4295906830",
}


@pytest.mark.unit
class TestSearchResearchIdentifierFields:
    def test_accepts_every_public_identifier(self):
        for ident, value in IDENTS.items():
            assert (
                getattr(SearchResearchArgs(query_text="q", **{ident: value}), ident)
                == value
            )

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("INTC US", "INTC:US"),
            ("INTC", "INTC:US"),
            ("INTC US,AMD US", "INTC:US,AMD:US"),
        ],
    )
    def test_bloomberg_ticker_is_corrected_like_find_tools(self, raw, expected):
        assert (
            SearchResearchArgs(query_text="q", bloomberg_ticker=raw).bloomberg_ticker
            == expected
        )

    def test_description_explains_unscoped_noise(self):
        assert "SCOPING TO A COMPANY" in SearchResearchArgs.__doc__
        assert "resolved_equities" in SearchResearchArgs.__doc__


@pytest.mark.unit
class TestSearchResearchIdentifierPayload:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("ident", sorted(IDENTS))
    async def test_identifier_is_forwarded(self, mock_http_dependencies, ident):
        mock_http_dependencies["mock_make_request"].return_value = EMPTY
        await search_research(
            SearchResearchArgs(
                query_text="3Q25 preview", size=10, **{ident: IDENTS[ident]}
            )
        )
        call = mock_http_dependencies["mock_make_request"].call_args[1]
        assert call["endpoint"] == "/chat-support/search-research"
        payload = call["data"]
        assert payload[ident] == IDENTS[ident]
        assert not any(other in payload for other in IDENTS if other != ident)

    @pytest.mark.asyncio
    async def test_no_identifier_no_scope_keys(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = EMPTY
        await search_research(SearchResearchArgs(query_text="rates outlook"))
        payload = mock_http_dependencies["mock_make_request"].call_args[1]["data"]
        assert not any(ident in payload for ident in IDENTS)
