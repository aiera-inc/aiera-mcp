#!/usr/bin/env python3

"""SEC filing tools for Aiera MCP."""

import logging
from typing import Any, Dict
from datetime import datetime, date

from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from .models import (
    FindFilingsArgs, GetFilingArgs,
    FindFilingsResponse, GetFilingResponse,
    FilingItem, FilingDetails, FilingSummary, CitationInfo
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_filings(args: FindFilingsArgs) -> FindFilingsResponse:
    """Find SEC filings, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector; and (optionally) by a form number."""
    logger.info("tool called: find_filings")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    api_data = raw_response.get("response", {})
    filings_data = api_data.get("data", [])

    filings = []
    citations = []

    for filing_data in filings_data:
        # Parse dates safely
        filing_date = None
        period_end_date = None

        try:
            if filing_data.get("filing_date"):
                filing_date = datetime.fromisoformat(filing_data["filing_date"].replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            pass

        try:
            if filing_data.get("period_end_date"):
                period_end_date = datetime.fromisoformat(filing_data["period_end_date"].replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            pass

        # Create filing item
        filing_item = FilingItem(
            filing_id=str(filing_data.get("id", "")),
            company_name=filing_data.get("company_name", ""),
            company_ticker=filing_data.get("ticker"),
            form_type=filing_data.get("form_type", ""),
            title=filing_data.get("title", ""),
            filing_date=filing_date or date.today(),
            period_end_date=period_end_date,
            is_amendment=filing_data.get("is_amendment", False),
            official_url=filing_data.get("official_url")
        )
        filings.append(filing_item)

        # Add citation if we have URL information
        if filing_data.get("official_url"):
            citations.append(CitationInfo(
                title=f"{filing_data.get('company_name', '')} {filing_data.get('form_type', '')} Filing",
                url=filing_data.get("official_url"),
                timestamp=datetime.combine(filing_date, datetime.min.time()) if filing_date else None
            ))

    return FindFilingsResponse(
        filings=filings,
        total=api_data.get("total", len(filings)),
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_filing(args: GetFilingArgs) -> GetFilingResponse:
    """Retrieve an SEC filing, including a summary and other metadata."""
    logger.info("tool called: get_filing")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    # Handle special field mapping: filing_id -> filing_ids
    if 'filing_id' in params:
        params['filing_ids'] = str(params.pop('filing_id'))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    api_data = raw_response.get("response", {})
    filings_data = api_data.get("data", [])

    if not filings_data:
        raise ValueError(f"Filing not found: {args.filing_id}")

    filing_data = filings_data[0]  # Get the first (and should be only) filing

    # Parse dates safely
    filing_date = None
    period_end_date = None

    try:
        if filing_data.get("filing_date"):
            filing_date = datetime.fromisoformat(filing_data["filing_date"].replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        pass

    try:
        if filing_data.get("period_end_date"):
            period_end_date = datetime.fromisoformat(filing_data["period_end_date"].replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        pass

    # Build filing summary
    summary = None
    if filing_data.get("summary") or filing_data.get("key_points") or filing_data.get("financial_highlights"):
        summary = FilingSummary(
            summary=filing_data.get("summary"),
            key_points=filing_data.get("key_points", []),
            financial_highlights=filing_data.get("financial_highlights", {})
        )

    # Build detailed filing
    filing_details = FilingDetails(
        filing_id=str(filing_data.get("id", "")),
        company_name=filing_data.get("company_name", ""),
        company_ticker=filing_data.get("ticker"),
        form_type=filing_data.get("form_type", ""),
        title=filing_data.get("title", ""),
        filing_date=filing_date or date.today(),
        period_end_date=period_end_date,
        is_amendment=filing_data.get("is_amendment", False),
        official_url=filing_data.get("official_url"),
        summary=summary,
        content_preview=filing_data.get("content_preview"),
        document_count=filing_data.get("document_count", 1)
    )

    # Build citation
    citations = []
    if filing_data.get("official_url"):
        citations.append(CitationInfo(
            title=f"{filing_data.get('company_name', '')} {filing_data.get('form_type', '')} Filing",
            url=filing_data.get("official_url"),
            timestamp=datetime.combine(filing_date, datetime.min.time()) if filing_date else None
        ))

    return GetFilingResponse(
        filing=filing_details,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


# Legacy registration functions removed - all tools now registered via registry