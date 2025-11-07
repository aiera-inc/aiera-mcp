#!/usr/bin/env python3

"""Company document tools for Aiera MCP."""

import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .utils import correct_bloomberg_ticker, correct_categories, correct_keywords

# Setup logging
logger = logging.getLogger(__name__)

# Default pagination settings
DEFAULT_PAGE_SIZE = 50


async def find_company_docs(
    start_date: str,
    end_date: str,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
    categories: Optional[str] = None,
    keywords: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """Find documents that have been published by a company, filtered by a date range, and (optionally) by ticker(s), watchlist, index, sector, or subsector; or category(s) or keyword(s)."""
    logger.info("tool called: find_company_docs")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if watchlist_id:
        params["watchlist_id"] = str(watchlist_id)

    if index_id:
        params["index_id"] = str(index_id)

    if sector_id:
        params["sector_id"] = str(sector_id)

    if subsector_id:
        params["subsector_id"] = str(subsector_id)

    if categories:
        params["categories"] = correct_categories(categories)

    if keywords:
        params["keywords"] = correct_keywords(keywords)

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )


async def get_company_doc(company_doc_id: str) -> Dict[str, Any]:
    """Retrieve a company document, including a summary and other metadata."""
    logger.info("tool called: get_company_doc")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "company_doc_ids": str(company_doc_id),
        "include_content": "true",
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )


async def get_company_doc_categories(
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve a list of all categories associated with company documents."""
    logger.info("tool called: get_company_doc_categories")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {}

    if search:
        params["search"] = search

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-categories",
        api_key=api_key,
        params=params,
    )


async def get_company_doc_keywords(
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve a list of all keywords associated with company documents."""
    logger.info("tool called: get_company_doc_keywords")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {}

    if search:
        params["search"] = search

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-keywords",
        api_key=api_key,
        params=params,
    )


def register_company_docs_tools(mcp_server: FastMCP) -> None:
    """Register company document tools with FastMCP server."""

    @mcp_server.tool(
        name="find_company_docs",
        description="Finds company documents using search filters.",
        annotations={
            "title": "Find Company Documents",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def find_company_docs_tool(
        start_date: str,
        end_date: str,
        bloomberg_ticker: Optional[str] = None,
        watchlist_id: Optional[int] = None,
        index_id: Optional[int] = None,
        sector_id: Optional[int] = None,
        subsector_id: Optional[int] = None,
        categories: Optional[str] = None,
        keywords: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE
    ) -> Dict[str, Any]:
        return await find_company_docs(start_date, end_date, bloomberg_ticker, watchlist_id, index_id, sector_id, subsector_id, categories, keywords, page, page_size)

    @mcp_server.tool(
        name="get_company_doc",
        description="Returns the details of a company document given its identifier.",
        annotations={
            "title": "Get Company Document",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_company_doc_tool(company_doc_id: str) -> Dict[str, Any]:
        return await get_company_doc(company_doc_id)

    @mcp_server.tool(
        name="get_company_doc_categories",
        description="Returns the list of available categories for company documents.",
        annotations={
            "title": "Get Company Document Categories",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_company_doc_categories_tool(
        search: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        return await get_company_doc_categories(search, page, page_size)

    @mcp_server.tool(
        name="get_company_doc_keywords",
        description="Returns the list of available keywords for company documents.",
        annotations={
            "title": "Get Company Document Keywords",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def get_company_doc_keywords_tool(
        search: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        return await get_company_doc_keywords(search, page, page_size)