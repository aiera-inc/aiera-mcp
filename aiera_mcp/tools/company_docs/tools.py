#!/usr/bin/env python3

"""Company document tools for Aiera MCP."""

import logging

from .models import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    GetCompanyDocCategoriesArgs,
    GetCompanyDocKeywordsArgs,
    FindCompanyDocsResponse,
    GetCompanyDocResponse,
    GetCompanyDocCategoriesResponse,
    GetCompanyDocKeywordsResponse,
)
from ..base import get_http_client, make_aiera_request
from ... import get_api_key

# Setup logging
logger = logging.getLogger(__name__)


async def find_company_docs(args: FindCompanyDocsArgs) -> FindCompanyDocsResponse:
    """Find company-published documents (press releases, annual reports, earnings releases, etc.) filtered by date range and optional company/document filters.

    IMPORTANT: When users request specific document types (e.g., 'press releases', 'annual reports'), ALWAYS use the 'categories' parameter to filter by document type.
    Example: 'Find all press releases from Apple in Q1 2024' should use categories='press_release' with bloomberg_ticker='AAPL:US'.

    RECOMMENDED: It is highly recommended to include at least one parameter that identifies equity(s), such as bloomberg_ticker, watchlist_id, index_id, sector_id, or subsector_id.
    """
    logger.info("tool called: find_company_docs")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )

    response = FindCompanyDocsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_company_doc(args: GetCompanyDocArgs) -> GetCompanyDocResponse:
    """Retrieve a company document, including a summary and other metadata."""
    logger.info("tool called: get_company_doc")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    # Handle special field mapping: company_doc_id -> company_doc_ids
    if "company_doc_id" in params:
        params["company_doc_ids"] = str(params.pop("company_doc_id"))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )

    response = GetCompanyDocResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_company_doc_categories(
    args: GetCompanyDocCategoriesArgs,
) -> GetCompanyDocCategoriesResponse:
    """Retrieve a list of all categories associated with company documents."""
    logger.info("tool called: get_company_doc_categories")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-categories",
        api_key=api_key,
        params=params,
    )

    response = GetCompanyDocCategoriesResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_company_doc_keywords(
    args: GetCompanyDocKeywordsArgs,
) -> GetCompanyDocKeywordsResponse:
    """Retrieve a list of all keywords associated with company documents."""
    logger.info("tool called: get_company_doc_keywords")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-keywords",
        api_key=api_key,
        params=params,
    )

    response = GetCompanyDocKeywordsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
