#!/usr/bin/env python3

"""Unit tests for the sales commentary tools (CORE-4827)."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.sales_commentary.tools import (
    find_sales_commentary,
    get_sales_commentary,
    report_sales_commentary_usage,
)
from aiera_mcp.tools.sales_commentary.models import (
    FindSalesCommentaryArgs,
    GetSalesCommentaryArgs,
    ReportSalesCommentaryUsageArgs,
    FindSalesCommentaryResponse,
    GetSalesCommentaryResponse,
    ReportSalesCommentaryUsageResponse,
)
from aiera_mcp.tools.search.tools import search_sales_commentary
from aiera_mcp.tools.search.models import SearchSalesCommentaryArgs, SearchSalesCommentaryResponse

EMAIL = {
    "document_id": "sc-1",
    "aiera_provider_id": "barclays",
    "title": "First Look: ACME 3Q",
    "series": "First Look",
    "thread_title": "ACME 3Q",
    "synopsis": "ACME beat.",
    "published_datetime": "2026-10-20T12:00:00",
    "authors": [{"name": "Ann Analyst", "author_id": "p1"}],
    "citation_information": {
        "title": "First Look: ACME 3Q",
        "url": None,
        "metadata": {"type": "sales_commentary", "url_target": "aiera", "document_id": "sc-1"},
    },
}

FIND_RESPONSE = {
    "instructions": ["This data is provided for institutional finance professionals..."],
    "response": {
        "pagination": {"total": 1, "page_size": 25, "has_next_page": False, "next_search_after": None},
        "data": [EMAIL],
    },
}

GET_RESPONSE = {
    "instructions": [],
    "response": {
        "result": [
            {
                **EMAIL,
                "content": [{"page": 1, "page_end": 1, "text": "ACME beat on margins."}],
                "content_length": 21,
                "prose_available": True,
            }
        ]
    },
}

SEARCH_RESPONSE = {
    "instructions": [],
    "response": {
        "pagination": {"total": 1, "page_size": 25, "has_next_page": False, "next_search_after": None},
        "data": [
            {
                "score": 0.9,
                "chunk_id": "chunk-9",
                "document_id": "sc-1",
                "text": "ACME beat on margins.",
                "page": 1,
                "title": "First Look: ACME 3Q",
                "series": "First Look",
                "citation_information": {
                    "title": "First Look: ACME 3Q",
                    "url": None,
                    "metadata": {"type": "sales_commentary", "url_target": "aiera", "document_id": "sc-1", "page": 1},
                },
            }
        ],
        "resolved_equities": [{"equity_id": 55, "bloomberg_ticker": "ACME:US", "common_name": "Acme"}],
    },
}


@pytest.mark.unit
class TestFindSalesCommentary:
    @pytest.mark.asyncio
    async def test_calls_find_endpoint_with_mapped_params(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = FIND_RESPONSE

        result = await find_sales_commentary(
            FindSalesCommentaryArgs(
                search="ACME:US",
                author_ids=["p1", "p2"],
                aiera_provider_ids=["barclays"],
                series=["First Look", "Daily"],
                subjects=["Earnings"],
                bloomberg_ticker="ACME US",
                search_after=["2026-10-20T12:00:00", 77],
                sort_by_date=True,
            )
        )

        assert isinstance(result, FindSalesCommentaryResponse)
        assert result.response["data"][0]["document_id"] == "sc-1"

        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "GET"
        assert call[1]["endpoint"] == "/chat-support/find-sales-commentary"
        params = call[1]["params"]
        # tool names -> API names, lists -> comma-separated, suffix stripped, ticker corrected
        assert params["author_person_ids"] == "p1,p2" and "author_ids" not in params
        assert params["provider_ids"] == "barclays" and "aiera_provider_ids" not in params
        assert params["series"] == "First Look,Daily"
        assert params["subjects"] == "Earnings"
        assert params["search"] == "ACME"
        assert params["bloomberg_ticker"] == "ACME:US"
        assert params["search_after"] == "2026-10-20T12:00:00,77"
        assert params["sort_by_date"] is True

    @pytest.mark.asyncio
    async def test_exclude_instructions_clears_them(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = FIND_RESPONSE
        result = await find_sales_commentary(FindSalesCommentaryArgs(exclude_instructions=True))
        assert result.instructions == []

    def test_unknown_arguments_are_rejected(self):
        with pytest.raises(ValidationError, match="Unknown argument"):
            FindSalesCommentaryArgs(regions=["EMEA"])

    def test_numeric_scope_ids_accept_strings(self):
        args = FindSalesCommentaryArgs(watchlist_id="12", page_size="10")
        dumped = args.model_dump(exclude_none=True)
        assert dumped["watchlist_id"] == "12" and dumped["page_size"] == "10"


@pytest.mark.unit
class TestGetSalesCommentary:
    @pytest.mark.asyncio
    async def test_fetches_by_document_id_with_content(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = GET_RESPONSE

        result = await get_sales_commentary(GetSalesCommentaryArgs(document_id="sc-1"))

        assert isinstance(result, GetSalesCommentaryResponse)
        assert result.response["result"][0]["prose_available"] is True
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["endpoint"] == "/chat-support/find-sales-commentary"
        assert call[1]["params"]["document_id"] == "sc-1"
        assert call[1]["params"]["include_content"] == "true"

    def test_document_id_is_required(self):
        with pytest.raises(ValidationError):
            GetSalesCommentaryArgs(document_id="")


@pytest.mark.unit
class TestReportSalesCommentaryUsage:
    @pytest.mark.asyncio
    async def test_posts_tagged_readership_items(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = {
            "instructions": [],
            "submitted": 2,
            "published": 2,
            "skipped": 0,
        }

        result = await report_sales_commentary_usage(
            ReportSalesCommentaryUsageArgs(document_ids="sc-1, sc-2,", self_identification="claude")
        )

        assert isinstance(result, ReportSalesCommentaryUsageResponse)
        assert (result.submitted, result.published, result.skipped) == (2, 2, 0)
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "POST"
        assert call[1]["endpoint"] == "/chat-support/report-readership"
        assert call[1]["params"] == {"self_identification": "claude"}
        # blanks dropped; every item tagged as sales commentary so the API looks it up on the right index
        assert call[1]["data"] == {
            "items": [
                {"research_id": "sc-1", "access_type": "summarize", "content_type": "sales_commentary"},
                {"research_id": "sc-2", "access_type": "summarize", "content_type": "sales_commentary"},
            ]
        }

    def test_document_ids_required(self):
        with pytest.raises(ValidationError):
            ReportSalesCommentaryUsageArgs()


@pytest.mark.unit
class TestSearchSalesCommentary:
    @pytest.mark.asyncio
    async def test_posts_only_set_fields_to_search_endpoint(self, mock_http_dependencies):
        mock_http_dependencies["mock_make_request"].return_value = SEARCH_RESPONSE

        result = await search_sales_commentary(
            SearchSalesCommentaryArgs(
                query_text="  reaction to the print ",
                bloomberg_ticker="ACME US",
                series=["First Look"],
                aiera_provider_ids=["barclays"],
                size=10,
            )
        )

        assert isinstance(result, SearchSalesCommentaryResponse)
        assert result.response["data"][0]["document_id"] == "sc-1"
        assert result.response["resolved_equities"][0]["bloomberg_ticker"] == "ACME:US"
        call = mock_http_dependencies["mock_make_request"].call_args
        assert call[1]["method"] == "POST"
        assert call[1]["endpoint"] == "/chat-support/search-sales-commentary"
        assert call[1]["data"] == {
            "query_text": "reaction to the print",
            "size": 10,
            "include_base_instructions": True,
            "bloomberg_ticker": "ACME:US",
            "aiera_provider_ids": ["barclays"],
            "series": ["First Look"],
        }

    def test_query_text_required_and_unknown_args_rejected(self):
        with pytest.raises(ValidationError):
            SearchSalesCommentaryArgs(query_text="   ")
        with pytest.raises(ValidationError, match="Unknown argument"):
            SearchSalesCommentaryArgs(query_text="x", asset_classes=["Equity"])
