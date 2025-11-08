#!/usr/bin/env python3

"""Company document tools for Aiera MCP."""

import logging
from datetime import datetime, date

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
    CategoryKeyword
)
from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from ..common.models import CitationInfo

# Setup logging
logger = logging.getLogger(__name__)


async def find_company_docs(args: FindCompanyDocsArgs) -> FindCompanyDocsResponse:
    """Find documents that have been published by a company, filtered by a date range, and (optionally) by ticker(s), watchlist, index, sector, or subsector; or category(s) or keyword(s)."""
    logger.info("tool called: find_company_docs")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        docs_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        docs_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(docs_data))

    documents = []
    citations = []

    for doc_data in docs_data:
        # Parse publish date safely
        publish_date = None
        try:
            if doc_data.get("publish_date"):
                publish_date = datetime.fromisoformat(doc_data["publish_date"].replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            publish_date = date.today()

        doc_item = CompanyDocItem(
            doc_id=str(doc_data.get("id", "")),
            company_name=doc_data.get("company_name", ""),
            title=doc_data.get("title", ""),
            category=doc_data.get("category", ""),
            keywords=doc_data.get("keywords", []),
            publish_date=publish_date or date.today(),
            document_type=doc_data.get("document_type")
        )
        documents.append(doc_item)

        # Add citation if we have URL information
        if doc_data.get("url"):
            citations.append(CitationInfo(
                title=doc_data.get("title", ""),
                url=doc_data.get("url"),
                timestamp=datetime.combine(publish_date, datetime.min.time()) if publish_date else None
            ))

    return FindCompanyDocsResponse(
        documents=documents,
        total=total_count,
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_company_doc(args: GetCompanyDocArgs) -> GetCompanyDocResponse:
    """Retrieve a company document, including a summary and other metadata."""
    logger.info("tool called: get_company_doc")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    # Handle special field mapping: company_doc_id -> company_doc_ids
    if 'company_doc_id' in params:
        params['company_doc_ids'] = str(params.pop('company_doc_id'))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        docs_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        docs_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(docs_data))

    if not docs_data:
        raise ValueError(f"Document not found: {args.company_doc_id}")

    doc_data = docs_data[0]  # Get the first (and should be only) document

    # Parse publish date safely
    publish_date = None
    try:
        if doc_data.get("publish_date"):
            publish_date = datetime.fromisoformat(doc_data["publish_date"].replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        publish_date = date.today()

    # Build detailed document
    doc_details = CompanyDocDetails(
        doc_id=str(doc_data.get("id", "")),
        company_name=doc_data.get("company_name", ""),
        title=doc_data.get("title", ""),
        category=doc_data.get("category", ""),
        keywords=doc_data.get("keywords", []),
        publish_date=publish_date or date.today(),
        document_type=doc_data.get("document_type"),
        summary=doc_data.get("summary"),
        content_preview=doc_data.get("content_preview"),
        attachments=doc_data.get("attachments", [])
    )

    # Build citation
    citations = []
    if doc_data.get("url"):
        citations.append(CitationInfo(
            title=doc_data.get("title", ""),
            url=doc_data.get("url"),
            timestamp=datetime.combine(publish_date, datetime.min.time()) if publish_date else None
        ))

    return GetCompanyDocResponse(
        document=doc_details,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_company_doc_categories(args: SearchArgs) -> GetCompanyDocCategoriesResponse:
    """Retrieve a list of all categories associated with company documents."""
    logger.info("tool called: get_company_doc_categories")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-categories",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        categories_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        categories_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(categories_data))

    categories = []
    for category_data in categories_data:
        category_item = CategoryKeyword(
            name=category_data.get("name", category_data.get("category", "")),
            count=category_data.get("count", 0)
        )
        categories.append(category_item)

    # Default pagination values since this endpoint may not provide them
    page = getattr(args, 'page', 1)
    page_size = getattr(args, 'page_size', 50)

    return GetCompanyDocCategoriesResponse(
        categories=categories,
        total=total_count,
        page=page,
        page_size=page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=[CitationInfo(title="Company Document Categories", source="Aiera")]
    )


async def get_company_doc_keywords(args: SearchArgs) -> GetCompanyDocKeywordsResponse:
    """Retrieve a list of all keywords associated with company documents."""
    logger.info("tool called: get_company_doc_keywords")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-keywords",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        keywords_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        keywords_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(keywords_data))

    keywords = []
    for keyword_data in keywords_data:
        keyword_item = CategoryKeyword(
            name=keyword_data.get("name", keyword_data.get("keyword", "")),
            count=keyword_data.get("count", 0)
        )
        keywords.append(keyword_item)

    # Default pagination values since this endpoint may not provide them
    page = getattr(args, 'page', 1)
    page_size = getattr(args, 'page_size', 50)

    return GetCompanyDocKeywordsResponse(
        keywords=keywords,
        total=total_count,
        page=page,
        page_size=page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=[CitationInfo(title="Company Document Keywords", source="Aiera")]
    )


# Legacy registration functions removed - all tools now registered via registry
