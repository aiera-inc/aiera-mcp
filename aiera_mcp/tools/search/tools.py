#!/usr/bin/env python3

"""Search tools for Aiera MCP server."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key

from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchCompanyDocsArgs,
    SearchThirdbridgeArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResearchResponse,
    SearchCompanyDocsResponse,
    SearchThirdbridgeResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def search_transcripts(args: SearchTranscriptsArgs) -> SearchTranscriptsResponse:
    """Hybrid semantic + keyword search over event transcripts.

    Finds the most relevant transcript segments for a query, with optional
    filtering by event, equity, date range, event type, or transcript section.
    Query construction and ranking are handled server-side; this tool forwards
    the caller's parameters and parses the response.
    """
    logger.info("tool called: search_transcripts")

    client = await get_http_client(None)
    api_key = get_api_key()

    payload = {
        "query_text": args.query_text,
        "size": args.size,
        "include_base_instructions": args.include_base_instructions,
    }

    if args.event_ids:
        payload["event_ids"] = args.event_ids

    if args.equity_ids:
        payload["equity_ids"] = args.equity_ids

    if args.start_date:
        payload["start_date"] = args.start_date

    if args.end_date:
        payload["end_date"] = args.end_date

    if args.event_type:
        payload["event_type"] = args.event_type

    if args.transcript_section:
        payload["transcript_section"] = args.transcript_section

    if args.search_after is not None:
        payload["search_after"] = args.search_after

    if args.originating_prompt:
        payload["originating_prompt"] = args.originating_prompt

    if args.self_identification:
        payload["self_identification"] = args.self_identification

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search-transcripts",
        api_key=api_key,
        params={},
        data=payload,
    )

    response = SearchTranscriptsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def search_filings(args: SearchFilingsArgs) -> SearchFilingsResponse:
    """Hybrid semantic + keyword search over SEC filing document chunks.

    Finds the most relevant filing passages for a query, with optional filtering
    by filing, equity, date range, or filing type. Query construction and ranking
    are handled server-side; this tool forwards the caller's parameters and parses
    the response.
    """
    logger.info("tool called: search_filings")

    client = await get_http_client(None)
    api_key = get_api_key()

    payload = {
        "query_text": args.query_text,
        "size": args.size,
        "include_base_instructions": args.include_base_instructions,
    }

    if args.filing_ids:
        payload["filing_ids"] = args.filing_ids

    if args.equity_ids:
        payload["equity_ids"] = args.equity_ids

    if args.start_date:
        payload["start_date"] = args.start_date

    if args.end_date:
        payload["end_date"] = args.end_date

    if args.filing_type:
        payload["filing_type"] = args.filing_type

    if args.search_after is not None:
        payload["search_after"] = args.search_after

    if args.originating_prompt:
        payload["originating_prompt"] = args.originating_prompt

    if args.self_identification:
        payload["self_identification"] = args.self_identification

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search-filings",
        api_key=api_key,
        params={},
        data=payload,
    )

    response = SearchFilingsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def search_research(args: SearchResearchArgs) -> SearchResearchResponse:
    """Semantic search within research documents.

    Finds the most relevant research passages for a query, with optional filtering
    by date range, author, provider, asset class/type, or specific documents. When
    no start date is given, results are limited to roughly the past year so broad
    queries return current rather than stale research.
    """
    logger.info("tool called: search_research")

    client = await get_http_client(None)
    api_key = get_api_key()

    # Only forward the parameters that were actually set; sensible defaults are
    # applied for anything omitted.
    payload = {
        "query_text": args.query_text,
        "size": args.size,
        "include_base_instructions": args.include_base_instructions,
    }

    if args.document_ids:
        payload["document_ids"] = args.document_ids

    if args.start_date:
        payload["start_date"] = args.start_date

    if args.end_date:
        payload["end_date"] = args.end_date

    if args.author_ids:
        payload["author_ids"] = args.author_ids

    if args.aiera_provider_ids:
        payload["aiera_provider_ids"] = args.aiera_provider_ids

    if args.asset_classes:
        payload["asset_classes"] = args.asset_classes

    if args.asset_types:
        payload["asset_types"] = args.asset_types

    if args.search_after is not None:
        payload["search_after"] = args.search_after

    if args.originating_prompt:
        payload["originating_prompt"] = args.originating_prompt

    if args.self_identification:
        payload["self_identification"] = args.self_identification

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search-research",
        api_key=api_key,
        params={},
        data=payload,
    )

    response = SearchResearchResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def search_company_docs(args: SearchCompanyDocsArgs) -> SearchCompanyDocsResponse:
    """Hybrid semantic + keyword search over company document chunks.

    Finds the most relevant company-document passages for a query, with optional
    filtering by document, company, category, keywords, or date range. Query
    construction and ranking are handled server-side; this tool forwards the
    caller's parameters and parses the response.
    """
    logger.info("tool called: search_company_docs")

    client = await get_http_client(None)
    api_key = get_api_key()

    payload = {
        "query_text": args.query_text,
        "size": args.size,
        "include_base_instructions": args.include_base_instructions,
    }

    if args.company_doc_ids:
        payload["company_doc_ids"] = args.company_doc_ids

    if args.company_ids:
        payload["company_ids"] = args.company_ids

    if args.categories:
        payload["categories"] = args.categories

    if args.keywords:
        payload["keywords"] = args.keywords

    if args.start_date:
        payload["start_date"] = args.start_date

    if args.end_date:
        payload["end_date"] = args.end_date

    if args.search_after is not None:
        payload["search_after"] = args.search_after

    if args.originating_prompt:
        payload["originating_prompt"] = args.originating_prompt

    if args.self_identification:
        payload["self_identification"] = args.self_identification

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search-company-docs",
        api_key=api_key,
        params={},
        data=payload,
    )

    response = SearchCompanyDocsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def search_thirdbridge(args: SearchThirdbridgeArgs) -> SearchThirdbridgeResponse:
    """Hybrid semantic + keyword search over Third Bridge expert interview transcripts.

    Finds the most relevant expert-interview passages for a query, with optional
    filtering by company, Third Bridge ID, Aiera event, date range, or content
    type. Query construction and ranking are handled server-side; this tool
    forwards the caller's parameters and parses the response.
    """
    logger.info("tool called: search_thirdbridge")

    client = await get_http_client(None)
    api_key = get_api_key()

    payload = {
        "query_text": args.query_text,
        "size": args.size,
        "include_base_instructions": args.include_base_instructions,
    }

    if args.company_ids:
        payload["company_ids"] = args.company_ids

    if args.thirdbridge_ids:
        payload["thirdbridge_ids"] = args.thirdbridge_ids

    if args.aiera_event_ids:
        payload["aiera_event_ids"] = args.aiera_event_ids

    if args.start_date:
        payload["start_date"] = args.start_date

    if args.end_date:
        payload["end_date"] = args.end_date

    if args.event_content_type:
        payload["event_content_type"] = args.event_content_type

    if args.search_after is not None:
        payload["search_after"] = args.search_after

    if args.originating_prompt:
        payload["originating_prompt"] = args.originating_prompt

    if args.self_identification:
        payload["self_identification"] = args.self_identification

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search-thirdbridge",
        api_key=api_key,
        params={},
        data=payload,
    )

    response = SearchThirdbridgeResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
