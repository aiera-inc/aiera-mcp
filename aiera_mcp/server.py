#!/usr/bin/env python3

import os
import httpx

from datetime import datetime
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Completion, CompletionArgument, CompletionContext
from mcp.types import PromptReference, ResourceTemplateReference


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage application lifecycle with HTTP client."""
    async with httpx.AsyncClient() as client:
        yield {"http_client": client}


# Initialize FastMCP server
mcp = FastMCP(
    name="Aiera",
    stateless_http=True,
    json_response=True,
    lifespan=app_lifespan,
)

# Base configuration
DEFAULT_PAGE_SIZE = 50
DEFAULT_MAX_PAGE_SIZE = 100
AIERA_BASE_URL = "https://premium.aiera.com/api"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Aiera-MCP/1.0.0",
    "X-MCP-Origin": "local_mcp"
}


def correct_bloomberg_ticker(ticker: str) -> str:
    """Ensure bloomberg ticker is in the correct format (ticker:country_code)."""
    if "," in ticker:
        tickers = ticker.split(",")
        reticker = []
        for ticker in tickers:
            # if a space was substituted over colon...
            if ":" not in ticker and " " in ticker:
                ticker_parts = ticker.split()
                reticker.append(f"{ticker_parts[0]}:{ticker_parts[1]}")

            # default to US if ticker doesn't include country code...
            elif ":" not in ticker:
                reticker.append(f"{ticker}:US")

            else:
                reticker.append(ticker)

        return ",".join(reticker)

    # if a space was substituted over colon...
    elif ":" not in ticker and " " in ticker:
        ticker_parts = ticker.split()
        return f"{ticker_parts[0]}:{ticker_parts[1]}"

    # default to US if ticker doesn't include country code...
    elif ":" not in ticker:
        return f"{ticker}:US"

    return ticker


def correct_keywords(keywords: str) -> str:
    """Ensure keywords have comma-separation."""
    if "," not in keywords and " " in keywords and len(keywords.split()) > 3:
        return ",".join(keywords.split())

    return keywords


def correct_categories(categories: str) -> str:
    """Ensure categories have comma-separation."""
    if "," not in categories and " " in categories:
        return ",".join(categories.split())

    return categories


def correct_provided_ids(provided_ids: str) -> str:
    """Ensure provided ID lists have comma-separation."""
    if "," not in provided_ids and " " in provided_ids:
        corrected = []
        for provided_id in provided_ids.split(","):
            corrected.append(provided_id.strip())

        return ",".join(corrected)

    return provided_ids


def correct_event_type(event_type: str) -> str:
    """Ensure event type is set correctly."""
    if event_type.strip() == "conference":
        event_type = "presentation"
    elif event_type.strip() == "m&a":
        event_type = "special_situation"

    return event_type.strip()


def correct_transcript_section(section: str) -> str:
    """Ensure the transcript section is set correctly."""
    if section.strip() == "qa":
        section = "q_and_a"

    return section.strip()


async def make_aiera_request(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    api_key: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    return_type: str = "json",
    instructions: str = None,
) -> Dict[str, Any]:
    """Make a request to the Aiera REST API."""
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-Key"] = api_key

    url = f"{AIERA_BASE_URL}{endpoint}"

    response = await client.request(
        method=method,
        url=url,
        params=params,
        json=data,
        headers=headers,
        timeout=30.0
    )

    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code} - {response.text}")

    if return_type == "json":
        response_data = response.json()

    else:
        response_data = response.text

    if instructions:
        instructions = [
            "This data is provided for institutional finance professionals. Responses should be composed of accurate, concise, and well-structured financial insights.",
            instructions,
        ]

    return {
        "instructions": instructions,
        "response": response_data,
    }


@mcp.tool(
    annotations={
        "title": "Find Events",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def find_events(
    start_date: str,
    end_date: str,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
    event_type: Optional[str] = "earnings",
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Find events, filtered by a date range, and (optionally) ticker(s), watchlist, index, sector, or subsector; or event type(s) or search."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "include_transcripts": False,
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if watchlist_id:
        params["watchlist_id"] = watchlist_id

    if index_id:
        params["index_id"] = index_id

    if sector_id:
        params["sector_id"] = sector_id

    if subsector_id:
        params["subsector_id"] = subsector_id

    if event_type:
        params["event_type"] = correct_event_type(event_type)

    if search:
        params["search"] = search

    if page:
        params["page"] = page

    if page_size:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Event",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_event(
    event_id: str,
    transcript_section: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve an event, including the summary, transcript, and other metadata. Optionally, you filter the transcripts by section ('presentation' or 'q_and_a')."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "event_ids": str(event_id),
        "include_transcripts": True,
    }

    if transcript_section:
        params["transcript_section"] = transcript_section

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Upcoming Events",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_upcoming_events(
    start_date,
    end_date,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve confirmed and estimated upcoming events, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if watchlist_id:
        params["watchlist_id"] = watchlist_id

    if index_id:
        params["index_id"] = index_id

    if sector_id:
        params["sector_id"] = sector_id

    if subsector_id:
        params["subsector_id"] = subsector_id

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/estimated-and-upcoming-events",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Find Filings",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def find_filings(
    start_date: str,
    end_date: str,
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
    form_number: Optional[str] = None,
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """Find SEC filings, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector; and (optionally) by a form number or search."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if watchlist_id:
        params["watchlist_id"] = watchlist_id

    if index_id:
        params["index_id"] = index_id

    if sector_id:
        params["sector_id"] = sector_id

    if subsector_id:
        params["subsector_id"] = subsector_id

    if form_number:
        params["form_number"] = form_number

    if search:
        params["search"] = search

    if page:
        params["page"] = page

    if page_size:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Filing",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_filing(filing_id: str) -> Dict[str, Any]:
    """Retrieve an SEC filing, including a summary and other metadata."""
    logger.info("tool called: get_filing")

    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "filing_ids": str(filing_id),
        "include_content": True,
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
        instructions=CITATION_PROMPT if FROM_UI_CLIENT else None,
    )


@mcp.tool(
    annotations={
        "title": "Find Equities",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def find_equities(
    bloomberg_ticker: Optional[str] = None,
    isin: Optional[str] = None,
    ric: Optional[str] = None,
    ticker: Optional[str] = None,
    permid: Optional[str] = None,
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve equities, filtered by various identifiers, such as ticker, ISIN, or RIC; or by a search term."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "include_company_metadata": True,
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if isin:
        params["isin"] = isin

    if ric:
        params["ric"] = ric

    if ticker:
        params["ticker"] = ticker

    if permid:
        params["permid"] = permid

    if search:
        params["search"] = search

    if page:
        params["page"] = page

    if page_size:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-equities",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Sectors and Subsectors",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_sectors_and_subsectors() -> Dict[str, Any]:
    """Retrieve a list of all sectors and subsectors."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-sectors-and-subsectors",
        api_key=api_key,
        params={},
    )


@mcp.tool(
    annotations={
        "title": "Get Equity Summaries",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_equity_summaries(bloomberg_ticker: str) -> Dict[str, Any]:
    """Retrieve detailed summary information about one or more equities, filtered by ticker(s)."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "bloomberg_ticker": correct_bloomberg_ticker(bloomberg_ticker),
        "lookback": 90,
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/equity-summaries",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Available Indexes",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_available_indexes() -> Dict[str, Any]:
    """Retrieve the list of available indexes."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-indexes",
        api_key=api_key,
        params={},
    )


@mcp.tool(
    annotations={
        "title": "Get Index Constituents",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_index_constituents(
    index: str,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve the list of all equities within an index."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {}

    if page:
        params["page"] = page

    if page:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/index-constituents/{index}",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Available Watchlists",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_available_watchlists() -> Dict[str, Any]:
    """Retrieve the list of available watchlists."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-watchlists",
        api_key=api_key,
        params={},
    )


@mcp.tool(
    annotations={
        "title": "Get Watchlist Constituents",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_watchlist_constituents(
    watchlist_id: str,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve the list of all equities within a watchlist."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {}

    if page:
        params["page"] = page

    if page:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/watchlist-constituents/{watchlist_id}",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Find Company Documents",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
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
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """Find documents that have been published by a company, filtered by a date range, and (optionally) by ticker(s), watchlist, index, sector, or subsector; or category(s) or keyword(s) or search."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "start_date": start_date,
        "end_date": end_date,
    }

    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if watchlist_id:
        params["watchlist_id"] = watchlist_id

    if index_id:
        params["index_id"] = index_id

    if sector_id:
        params["sector_id"] = sector_id

    if subsector_id:
        params["subsector_id"] = subsector_id

    if categories:
        params["categories"] = correct_categories(categories)

    if keywords:
        params["keywords"] = correct_keywords(keywords)

    if search:
        params["search"] = search

    if page:
        params["page"] = page

    if page_size:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Company Document",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_company_doc(company_doc_id: str) -> Dict[str, Any]:
    """Retrieve a company document, including a summary and other metadata."""
    logger.info("tool called: get_company_doc")

    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "company_doc_ids": str(company_doc_id),
        "include_content": True,
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
        instructions=CITATION_PROMPT if FROM_UI_CLIENT else None,
    )


@mcp.tool(
    annotations={
        "title": "Get Company Document Categories",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_company_doc_categories(
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve a list of all categories associated with company documents."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {}

    if search:
        params["search"] = search

    if page:
        params["page"] = page

    if page_size:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-categories",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Company Document Keywords",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_company_doc_keywords(
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Retrieve a list of all keywords associated with company documents."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {}

    if search:
        params["search"] = search

    if page:
        params["page"] = page

    if page_size:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-company-doc-keywords",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Find Third Bridge Events",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def find_third_bridge_events(
    start_date: str,
    end_date: str,
    search: Optional[str] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Find expert insight events from Third Bridge, filtering by a date range and (optionally) by search."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "event_category": "thirdbridge",
        "include_transcripts": False,
    }

    if search:
        params["search"] = search

    if page:
        params["page"] = page

    if page_size:
        params["page_size"] = page_size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Get Third Bridge Event",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def get_third_bridge_event(event_id: str) -> Dict[str, Any]:
    """Retrieve an expert insight events from Third Bridge, including transcripts, summaries, and other metadata."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "event_ids": str(event_id),
        "event_category": "thirdbridge",
        "include_transcripts": True,
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-events",
        api_key=api_key,
        params=params,
    )


@mcp.resource(uri="aiera://api/docs")
def get_api_documentation() -> str:
    """Provide documentation for the Aiera API."""
    return f"""
    # Aiera Financial Data API

    This MCP server provides access to Aiera's comprehensive financial data API.

    ## Available Tools:

    ### Equity API
    - find_equities: Retrieve equities, filtered by various identifiers, such as bloomberg_ticker (a comma-separated list of tickers) or ric (a comma-separated list of RICs), or by a search term. This endpoint supports pagination.
    -- Search will only look for matches within the company name or ticker.
    - get_equity_summaries: Retrieve detailed summary(s) about one or more equities, filtered by bloomberg_ticker (a comma-separated list). Summaries will include past and upcoming events, information about company leadership, recent financials, and within which indices the equity is included.
    - get_sectors_and_subsectors: Retrieve a list of all sectors and subsectors that can be queried.
    - get_available_indexes: Retrieve the list of available indexes that can be queried.
    - get_index_constituents: Retrieve the list of all equities within an index. This endpoint supports pagination.
    - get_available_watchlists: Retrieve the list of watchlists that can be queried.
    - get_watchlist_constituents: Retrieve the list of all equities within a watchlist. This endpoint supports pagination.

    ### Events API
    - find_events: Retrieve events, filtered by start_date and end_date, and optionally by bloomberg_ticker (a comma-separated list of tickers), watchlist_id, index_id, sector_id, or subsector_id; or event_type (a comma-separated list of event types). This endpoint supports pagination.
    -- Event type must be one of the following: earnings, presentation, shareholder_meeting, investor_meeting, special_situation
    -- Some common associations of event_type:
    --- Conferences will often be a reference to the event type: presentation
    --- Annual meetings will often be a reference to the event type: shareholder_meeting
    --- Mergers, acquisitions, spinoffs, and other corporate actions will often be a reference to the event type: special_situation
    -- watchlist_id can be found using the tool get_available_watchlists.
    -- index_id can be found using the tool get_available_indexes.
    -- sector_id and subsector_id can be found using the tool get_sectors_and_subsectors.
    - get_event: Retrieve an event, including a summary, the transcript, and other metadata. Optionally, you can also filter the included transcript by transcript_section ("presentation" or "q_and_a").
    -- The event ID can be found using the find_events tool.
    -- If you need to retrieve more than one event, make multiple sequential calls.
    -- transcript_section is only applicable with the earnings event_type, and must be one of the following: presentation, q_and_a
    - get_upcoming_events: Retrieve confirmed and estimated upcoming events, filtered by start_date and end_date, and one of the following: bloomberg_ticker (a comma-separated list of tickers), watchlist_id, index_id, sector_id, or subsector_id.
    -- watchlist_id can be found using the tool get_available_watchlists.
    -- index_id can be found using the tool get_available_indexes.
    -- sector_id and subsector_id can be found using the tool get_sectors_and_subsectors.

    ### Filings API
    - find_filings: Retrieve SEC filings, filtered by start_date and end_date, and one of the following: bloomberg_ticker (a comma-separated list of tickers), watchlist_id, index_id, sector_id, or subsector_id; and optionally by form_number. This endpoint supports pagination.
    -- Examples of form numbers include: 10-K, 10-Q, and 8-K. There are other possibilities, but those 3 will be the most commonly used.
    -- watchlist_id can be found using the tool get_available_watchlists.
    -- index_id can be found using the tool get_available_indexes.
    -- sector_id and subsector_id can be found using the tool get_sectors_and_subsectors.
    - get_filing: Retrieve an SEC filing, including a summary, document contents, and other metadata, filtered by filing_id.
    -- The filing ID can be found with the tool find_filings.
    -- If you need to retrieve more than one filing, make multiple sequential calls.

    ### Company Docs API
    - find_company_docs: Retrieve documents that have been published on company IR websites, filtered by a date range, and optionally by bloomberg_ticker (a comma-separated list), watchlist_id, index_id, sector_id, or subsector_id; or categories (a comma-separated list), keywords (a comma-separated list). This endpoint supports pagination.
    -- Examples of a category include: annual_report, compliance, disclosure, earnings_release, slide_presentation, press_release. There are hundreds of other possibilities. The full list of possible categories can be found using the tool get_company_doc_categories.
    -- Examples of a keyword include: ESG, diversity, risk management. There are hundreds of other possibilities. The full list of possible keywords can be found using the tool get_company_doc_keywords.
    -- watchlist_id can be found using the tool get_available_watchlists.
    -- index_id can be found using the tool get_available_indexes.
    -- sector_id and subsector_id can be found using the tool get_sectors_and_subsectors.
    - get_company_doc: Retrieve a company document, including a summary and other metadata, filtered by company_doc_id. 
    -- The document ID can be found using the tool find_company_docs.
    -- If you need to retrieve more than one company document, make multiple sequential calls.
    - get_company_doc_categories: Retrieve a list of all categories associated with company documents (and the number of documents associated with each category). This endpoint supports pagination, and can be filtered by a search term.
    - get_company_doc_keywords: Retrieve a list of all keywords associated with company documents (and the number of documents associated with each keyword). This endpoint supports pagination, and can be filtered by a search term.

    ### Third Bridge API
    - find_third_bridge_events: Retrieve expert insight events from Third Bridge, filtered by start_date and end_date. This endpoint supports pagination.
    - get_third_bridge_event: Retrieve an expert insight event from Third Bridge, including a summary, the full transcript, and other metadata, filtered by event_id. 
    -- The event ID can be found using the tool find_third_bridge_events.
    -- If you need to retrieve more than one event, make multiple sequential calls.
    
    ## Authentication:
    All endpoints require the AIERA_API_KEY environment variable to be set.
    Some endpoints may require specific permissions based on a subscription plan. If access is denied, the user should talk to their Aiera representative about gaining access.

    ## Parameter Notes:
    - Tools that support pagination use 'page' and 'page_size' parameters. By default, page is set to 1 and page_size is set to {DEFAULT_PAGE_SIZE}. The default maximum page_size is {DEFAULT_MAX_PAGE_SIZE}.
    - Date parameters should be in ISO format (YYYY-MM-DD).
    - Bloomberg tickers are composed of a ticker and a country code joined by a colon (e.g., "AAPL:US").
    -- If information from multiple bloomberg tickers is needed, they should be represented as a comma-separated list (e.g., "AAPL:US,MSFT:US,GOOGL:US").
    - Comma-separated lists should not contain spaces (e.g., "keyword1,keyword2,keyword3").
    - Boolean parameters accept true/false values.
    
    ## Usage Hints:
    - Questions about guidance will always require the transcript from at least one earnings event, and often will require multiple earnings transcripts from the last year in order to provide sufficient context.
    -- Answers to guidance questions should focus on management commentary, and avoid analyst commentary unless specifically asked for.
    
    ## Other Notes:
    - All dates and times are in eastern time (ET) unless specifically stated otherwise.
    - The term "publication" or "document" is likely referring to either an SEC filing or a company document.
    - The current date is {datetime.now().strftime("%Y-%m-%d")}. Relative dates (e.g., "last 3 months" or "next 3 months") should be calculated based on this date.
    """


def run(transport="streamable-http"):
    mcp.run(transport=transport)