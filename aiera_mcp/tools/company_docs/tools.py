#!/usr/bin/env python3

"""Company document tools for Aiera MCP."""

import logging

from .models import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    SearchArgs,
    FindCompanyDocsResponse,
    GetCompanyDocResponse,
    GetCompanyDocCategoriesResponse,
    GetCompanyDocKeywordsResponse,
    CompanyDocItem,
    CompanyDocDetails,
    CategoryKeyword,
)
from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from ..common.models import CitationInfo

# Setup logging
logger = logging.getLogger(__name__)


async def find_company_docs(args: FindCompanyDocsArgs) -> FindCompanyDocsResponse:
    """Find documents that have been published by a company, filtered by a date range, and (optionally) by ticker(s), watchlist, index, sector, or subsector; or category(s) or keyword(s)."""
    logger.info("tool called: find_company_docs")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )

    # Return the structured response directly - no transformation needed
    # since FindCompanyDocsResponse model now matches the actual API format
    return FindCompanyDocsResponse.model_validate(raw_response)


async def get_company_doc(args: GetCompanyDocArgs) -> GetCompanyDocResponse:
    """Retrieve a company document, including a summary and other metadata."""
    logger.info("tool called: get_company_doc")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

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

    # Extract document from the nested response structure
    if "response" in raw_response and "document" in raw_response["response"]:
        doc_data = raw_response["response"]["document"]
    else:
        raise ValueError(f"Document not found: {args.company_doc_id}")

    # Create the response structure expected by GetCompanyDocResponse
    response_data = {
        "document": doc_data,
        "instructions": raw_response.get("instructions", []),
    }

    return GetCompanyDocResponse.model_validate(response_data)


async def get_company_doc_categories(
    args: SearchArgs,
) -> GetCompanyDocCategoriesResponse:
    """Retrieve a list of all categories associated with company documents."""
    logger.info("tool called: get_company_doc_categories")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-categories",
        api_key=api_key,
        params=params,
    )

    # Return the structured response directly - no transformation needed
    # since GetCompanyDocCategoriesResponse model now matches the actual API format
    return GetCompanyDocCategoriesResponse.model_validate(raw_response)


async def get_company_doc_keywords(args: SearchArgs) -> GetCompanyDocKeywordsResponse:
    """Retrieve a list of all keywords associated with company documents."""
    logger.info("tool called: get_company_doc_keywords")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-keywords",
        api_key=api_key,
        params=params,
    )

    # Return the structured response directly - no transformation needed
    # since GetCompanyDocKeywordsResponse model now matches the actual API format
    return GetCompanyDocKeywordsResponse.model_validate(raw_response)


# Legacy registration functions removed - all tools now registered via registry
