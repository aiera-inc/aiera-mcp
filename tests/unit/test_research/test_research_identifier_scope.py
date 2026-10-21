#!/usr/bin/env python3

"""find_research company scope: identifiers are declared, corrected and forwarded."""

import pytest

from aiera_mcp.tools.research.models import FindResearchArgs
from aiera_mcp.tools.research.tools import find_research

EMPTY = {
    "instructions": [],
    "response": {
        "result": [],
        "pagination": {
            "total": 0,
            "page_size": 25,
            "has_next_page": False,
            "next_search_after": None,
        },
    },
}

IDENTS = {
    "bloomberg_ticker": "INTC:US",
    "isin": "US4581401001",
    "ric": "INTC.O",
    "permid": "4295906830",
}


@pytest.mark.unit
class TestFindResearchIdentifierFields:
    def test_accepts_every_public_identifier(self):
        for ident, value in IDENTS.items():
            assert getattr(FindResearchArgs(**{ident: value}), ident) == value

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("INTC US", "INTC:US"),
            ("INTC", "INTC:US"),
            ("INTC:US,AMD:US", "INTC:US,AMD:US"),
            ("INTC US,AMD US", "INTC:US,AMD:US"),
        ],
    )
    def test_bloomberg_ticker_is_corrected_like_other_finders(self, raw, expected):
        assert FindResearchArgs(bloomberg_ticker=raw).bloomberg_ticker == expected

    def test_group_filters_serialize_as_strings(self):
        args = FindResearchArgs(
            sector_id=45, subsector_id="4510", index_id=7, watchlist_id="12"
        )
        dumped = args.model_dump(exclude_none=True)
        assert dumped["sector_id"] == "45" and dumped["subsector_id"] == "4510"
        assert dumped["index_id"] == "7" and dumped["watchlist_id"] == "12"

    def test_description_steers_the_model_to_the_identifier(self):
        desc = FindResearchArgs.model_fields["bloomberg_ticker"].description
        assert "PREFERRED" in desc and "explicit error" in desc
        assert "SCOPING TO A COMPANY" in FindResearchArgs.__doc__


@pytest.mark.unit
class TestFindResearchIdentifierPayload:
    """The identifier reaches the GET params unchanged; unset ones are omitted."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("ident", sorted(IDENTS))
    async def test_identifier_is_forwarded(self, mock_http_dependencies, ident):
        mock_http_dependencies["mock_make_request"].return_value = EMPTY
        await find_research(
            FindResearchArgs(
                **{ident: IDENTS[ident]}, start_date="2025-10-01", end_date="2025-10-31"
            )
        )
        call = mock_http_dependencies["mock_make_request"].call_args[1]
        assert call["endpoint"] == "/chat-support/find-research"
        assert call["params"][ident] == IDENTS[ident]
        assert not any(other in call["params"] for other in IDENTS if other != ident)

    @pytest.mark.asyncio
    async def test_identifier_combines_with_text_search(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = EMPTY
        await find_research(
            FindResearchArgs(
                bloomberg_ticker="INTC:US", search="3Q25 preview", sort_by_date=True
            )
        )
        params = mock_http_dependencies["mock_make_request"].call_args[1]["params"]
        assert params["bloomberg_ticker"] == "INTC:US"
        assert params["search"] == "3Q25 preview"
        assert params["sort_by_date"] is True
