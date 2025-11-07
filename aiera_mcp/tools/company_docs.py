#!/usr/bin/env python3

"""Company document tools for Aiera MCP."""

import logging
from typing import Any, Dict

from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .params import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    SearchArgs
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_company_docs(args: FindCompanyDocsArgs) -> Dict[str, Any]:
    """Find documents that have been published by a company, filtered by a date range, and (optionally) by ticker(s), watchlist, index, sector, or subsector; or category(s) or keyword(s)."""
    logger.info("tool called: find_company_docs")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )


async def get_company_doc(args: GetCompanyDocArgs) -> Dict[str, Any]:
    """Retrieve a company document, including a summary and other metadata."""
    logger.info("tool called: get_company_doc")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    # Handle special field mapping: company_doc_id -> company_doc_ids
    if 'company_doc_id' in params:
        params['company_doc_ids'] = str(params.pop('company_doc_id'))

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )


async def get_company_doc_categories(args: SearchArgs) -> Dict[str, Any]:
    """Retrieve a list of all categories associated with company documents."""
    logger.info("tool called: get_company_doc_categories")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-categories",
        api_key=api_key,
        params=params,
    )


async def get_company_doc_keywords(args: SearchArgs) -> Dict[str, Any]:
    """Retrieve a list of all keywords associated with company documents."""
    logger.info("tool called: get_company_doc_keywords")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-keywords",
        api_key=api_key,
        params=params,
    )


# Legacy registration functions removed - all tools now registered via registry
