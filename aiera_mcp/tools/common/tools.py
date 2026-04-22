#!/usr/bin/env python3

"""Common utility tools for Aiera MCP."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    GetGrammarTemplateArgs,
    GetGrammarTemplateResponse,
    GetCoreInstructionsArgs,
    GetCoreInstructionsResponse,
    AvailableToolsArgs,
    AvailableToolsResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def get_grammar_template(
    args: GetGrammarTemplateArgs,
) -> GetGrammarTemplateResponse:
    """Retrieve a grammar template for tailored response guidance."""
    logger.info("tool called: get_grammar_template")

    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-grammar-template",
        api_key=api_key,
        params=params,
    )

    response = GetGrammarTemplateResponse.model_validate(raw_response)
    return response


async def get_core_instructions(
    args: GetCoreInstructionsArgs,
) -> GetCoreInstructionsResponse:
    """Retrieve core instructions for working with Aiera tools and data."""
    logger.info("tool called: get_core_instructions")

    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-core-instructions",
        api_key=api_key,
        params=params,
    )

    response = GetCoreInstructionsResponse.model_validate(raw_response)
    return response


# Mapping from API endpoint paths to tool names.
# Some endpoints map to multiple tools (e.g. get_event reuses the find-events endpoint).
ENDPOINT_TO_TOOLS = {
    "/chat-support/find-events": ["find_events", "get_event"],
    "/chat-support/find-conferences": ["find_conferences"],
    "/chat-support/estimated-and-upcoming-events": ["get_upcoming_events"],
    "/chat-support/find-filings": ["find_filings", "get_filing"],
    "/chat-support/find-equities": ["find_equities"],
    "/chat-support/equity-summaries": ["get_equity_summaries"],
    "/chat-support/available-watchlists": ["get_available_watchlists"],
    "/chat-support/available-indexes": ["get_available_indexes"],
    "/chat-support/get-sectors-and-subsectors": ["get_sectors_and_subsectors"],
    "/chat-support/index-constituents": ["get_index_constituents"],
    "/chat-support/watchlist-constituents": ["get_watchlist_constituents"],
    "/chat-support/get-financials": ["get_financials"],
    "/chat-support/get-ratios": ["get_ratios"],
    "/chat-support/get-segments-and-kpis": ["get_kpis_and_segments"],
    "/chat-support/find-company-docs": ["find_company_docs", "get_company_doc"],
    "/chat-support/get-company-doc-categories": ["get_company_doc_categories"],
    "/chat-support/get-company-doc-keywords": ["get_company_doc_keywords"],
    "/chat-support/find-third-bridge": [
        "find_third_bridge_events",
        "get_third_bridge_event",
    ],
    "/chat-support/find-research": ["find_research", "get_research"],
    "/chat-support/get-research-providers": ["get_research_providers"],
    "/chat-support/get-research-authors": ["get_research_authors"],
    "/chat-support/get-research-asset-classes": ["get_research_asset_classes"],
    "/chat-support/get-research-asset-types": ["get_research_asset_types"],
    "/chat-support/get-research-subjects": ["get_research_subjects"],
    "/chat-support/get-research-product-focuses": ["get_research_product_focuses"],
    "/chat-support/get-research-region-types": ["get_research_region_types"],
    "/chat-support/get-research-country-codes": ["get_research_country_codes"],
    "/chat-support/search/transcripts": ["search_transcripts"],
    "/chat-support/search/filings": ["search_filings"],
    "/chat-support/search/filing-chunks": ["search_filings"],
    "/chat-support/search/research": ["search_research"],
    "/chat-support/search/research-chunks": ["search_research"],
    "/chat-support/search/company-docs": ["search_company_docs"],
    "/chat-support/search/company-doc-chunks": ["search_company_docs"],
    "/chat-support/search/thirdbridge": ["search_thirdbridge"],
    "/chat-support/trusted-web": ["trusted_web_search"],
    "/chat-support/get-grammar-template": ["get_grammar_template"],
    "/chat-support/get-core-instructions": ["get_core_instructions"],
}


async def available_tools(
    args: AvailableToolsArgs,
) -> AvailableToolsResponse:
    """Retrieve the list of tools available to the current user."""
    logger.info("tool called: available_tools")

    client = await get_http_client(None)
    api_key = get_api_key()

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-endpoints",
        api_key=api_key,
        params={},
    )

    endpoints = raw_response.get("endpoints", [])

    tool_names = set()
    for endpoint in endpoints:
        tools = ENDPOINT_TO_TOOLS.get(endpoint, [])
        tool_names.update(tools)

    # Always include available_tools itself
    tool_names.add("available_tools")

    # Compute hidden tools as the difference from all registered tools
    from ..registry import TOOL_REGISTRY

    all_tools = set(TOOL_REGISTRY.keys())
    hidden_tools = all_tools - tool_names

    return AvailableToolsResponse(
        available_tools=sorted(tool_names),
        hidden_tools=sorted(hidden_tools),
    )
