#!/usr/bin/env python3

import os
import httpx
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
    name="Aiera MCP",
    stateless_http=True,
    json_response=True,
    lifespan=app_lifespan
)

# Base configuration
AIERA_BASE_URL = "https://premium.aiera.com/api"
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Aiera-Public-MCP/1.0.0"
}


def correct_bloomberg_ticker(ticker: str) -> str:
    """Ensure bloomberg ticker is in the correct format (ticker:country_code)."""
    if ":" not in ticker and " " in ticker:
        ticker_parts = ticker.split()
        ticker = f"{ticker_parts[0]}:{ticker_parts[1]}"

    return ticker


async def make_aiera_request(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    api_key: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    return_type: str = "json",
) -> Dict[str, Any]:
    """Make a request to the Aiera REST API."""
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-KEY"] = api_key

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
        data = response.json()
        if type(data) == dict:
            return data

        else:
            return {"result": data}

    else:
        return {"result": response.text}


@mcp.tool()
async def find_events(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    event_type: Optional[str] = "earnings",
    modified_since: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve events, filtered by bloomberg ticker(s), date range, and (optionally) by event type."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "bloomberg_ticker": correct_bloomberg_ticker(bloomberg_ticker),
        "start_date": start_date,
        "end_date": end_date,
        "simplified": True,
    }

    if event_type:
        params["event_type"] = event_type

    if modified_since:
        params["modified_since"] = modified_since

    if from_index:
        params["from_index"] = from_index

    if size:
        params["size"] = size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/events-v2",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_event(event_id: str) -> Dict[str, Any]:
    """Retrieve a single event, including transcripts, summaries, and other metadata."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "linguistics": True,
        "pricing": True,
        "transcripts": True,
        "include_company_metadata": True,
        "include_connection_detail": True,
        "include_hierarchy": True,
        "include_estimated_docs": True,
        "include_tags": True,
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/events-v2/{event_id}",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_upcoming_events(
    bloomberg_ticker: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Retrieve confirmed and estimated upcoming events, filtered by bloomberg ticker(s) and a date range."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {}
    if bloomberg_ticker:
        params["bloomberg_ticker"] = correct_bloomberg_ticker(bloomberg_ticker)

    if start_date:
        params["start_date"] = start_date

    if end_date:
        params["end_date"] = end_date

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/estimated-and-upcoming-events",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def find_filings(
    bloomberg_ticker: str,
    start_date: str,
    end_date: str,
    form_number: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve SEC filings, filtered by bloomberg ticker(s) and a date range, and (optionally) by form number."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "bloomberg_ticker": correct_bloomberg_ticker(bloomberg_ticker),
        "start_date": start_date,
        "end_date": end_date
    }

    if form_number:
        params["form_number"] = form_number

    if from_index:
        params["from_index"] = from_index

    if size:
        params["size"] = size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/filings-v1",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_filing(filing_id: str) -> Dict[str, Any]:
    """Retrieve a single SEC filing."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/filings-v1/{filing_id}",
        api_key=api_key,
        params={},
    )


@mcp.tool()
async def get_filing_text(filing_id: str) -> Dict[str, Any]:
    """Retrieve the raw content for a single SEC filing."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/filings-v1/{filing_id}/text",
        api_key=api_key,
        params={},
        return_type="text",
    )


@mcp.tool()
async def find_equities(
    bloomberg_ticker: Optional[str] = None,
    isin: Optional[str] = None,
    ric: Optional[str] = None,
    ticker: Optional[str] = None,
    permid: Optional[str] = None,
    search: Optional[str] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve equities, filtered by various identifiers, such as bloomberg ticker(s) or RIC, or by a search term."""
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
        endpoint="/equities-v2",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_sectors_and_subsectors() -> Dict[str, Any]:
    """Retrieve a list of all sectors and subsectors that can be queried."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/equities-v2/sectors",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_equity_summaries(
    bloomberg_ticker: str,
    lookback: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve detailed summary information about one or more equities, filtered by bloomberg ticker(s)."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {
        "bloomberg_ticker": correct_bloomberg_ticker(bloomberg_ticker),
    }

    if lookback:
        params["lookback"] = lookback

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/equities-v2/summaries",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_available_indexes() -> Dict[str, Any]:
    """Retrieve the list of available indexes that can be queried."""
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


@mcp.tool()
async def get_index_constituents(
    index: str,
) -> Dict[str, Any]:
    """Retrieve the list of all equities within an index."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/index-constituents/{index}",
        api_key=api_key,
        params={},
    )


@mcp.tool()
async def find_company_docs(
    start_date: str,
    end_date: str,
    bloomberg_ticker: Optional[str] = None,
    categories: Optional[str] = None,
    keywords: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None
) -> Dict[str, Any]:
    """Retrieve documents that have been published on company IR websites, filtered by a date range, and (optionally) by bloomberg ticker(s), categories or keywords."""
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

    if categories:
        params["categories"] = categories

    if keywords:
        params["keywords"] = keywords

    if from_index:
        params["from_index"] = from_index

    if size:
        params["size"] = size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/company-docs-v1",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_company_doc_text(
    company_doc_id: str,
) -> Dict[str, Any]:
    """Retrieve raw text from a specific company document."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/company-docs-v1/{company_doc_id}/text",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_company_doc_categories(
    search: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve a list of all categories associated with company documents (and the number of documents associated with each category)."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {}

    if search:
        params["search"] = search

    if from_index:
        params["from_index"] = from_index

    if size:
        params["size"] = size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/company-docs-v1/categories",
        api_key=api_key,
        params=params,
    )


@mcp.tool()
async def get_company_doc_keywords(
    search: Optional[str] = None,
    from_index: Optional[int] = None,
    size: Optional[int] = None,
) -> Dict[str, Any]:
    """Retrieve a list of all keywords associated with company documents (and the number of documents associated with each keyword)."""
    ctx = mcp.get_context()
    client = ctx.request_context.lifespan_context["http_client"]
    api_key = os.getenv("AIERA_API_KEY")

    if not api_key:
        raise ValueError("AIERA_API_KEY environment variable is required")

    params = {}

    if search:
        params["search"] = search

    if from_index:
        params["from_index"] = from_index

    if size:
        params["size"] = size

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/company-docs-v1/keywords",
        api_key=api_key,
        params=params,
    )


@mcp.resource("aiera://api/docs")
def get_api_documentation() -> str:
    """Provide documentation for the Aiera API."""
    return """
    # Aiera Financial Data API

    This MCP server provides access to Aiera's comprehensive financial data API.

    ## Available Tools:

    ### Events API
    - find_events: Retrieve events, filtered by bloomberg ticker(s), date range, and (optionally) by event type. This endpoint supports pagination.
    -- Event types include: earnings, presentation, shareholder_meeting, investor_meeting, and special_situation.
    -- Conferences are labeled as presentation.
    -- Annual meetings are labeled as shareholder_meeting.
    -- Mergers & acquisitions, spinoffs, and other corporate actions are labeled as special_situation.
    - get_event: Retrieve a single event, including transcripts, summaries, and other metadata. Event IDs can be found using the find_events tool.
    - get_upcoming_events: Retrieve confirmed and estimated upcoming events, filtered by bloomberg ticker(s) and a date range.

    ### Filings API
    - find_filings: Retrieve SEC filings, filtered by bloomberg ticker(s) and a date range, and (optionally) by form number. This endpoint supports pagination.
    -- Examples of form numbers include: 10-K, 10-Q, and 8-K. There are other possibilities, but those 3 are typically the most relevant.
    - get_filing: Retrieve a single SEC filing. Filing IDs can be found with the tool find_filings.
    - get_filing_text: Retrieve the raw content for a single SEC filing. Filings IDs can be found with the tool find_filings.

    ### Equity API
    - find_equities: Retrieve equities, filtered by various identifiers, such as bloomberg ticker(s) or RIC, or by a search term.
    - get_sectors_and_subsectors: Retrieve a list of all sectors and subsectors that can be queried.
    - get_equity_summaries: Retrieve detailed summary information about one or more equities, filtered by bloomberg ticker(s). Results include past and upcoming events, company leadership, recent financials, and index membership.
    - get_available_indexes: Retrieve the list of available indexes that can be queried.
    - get_index_constituents: Retrieve the list of all equities within an index.

    ### Company Docs API
    - find_company_docs: Retrieve documents that have been published on company IR websites, filtered by a date range, and (optionally) by bloomberg ticker(s), categories (comma-separated list) or keywords (comma-separated list). This endpoint supports pagination.
    -- Examples of a category include: annual_report, compliance, disclosure, earnings_release, slide_presentation, press_release. There are hundreds of other possibilities. The full list of possible categories can be found using the tool get_company_doc_categories.
    -- Examples of a keyword include: ESG, diversity, risk management. There are hundreds of other possibilities. The full list of possible keywords can be found using the tool get_company_doc_keywords.
    - get_company_doc_categories: Retrieve a list of all categories associated with company documents (and the number of documents associated with each category). This endpoint supports pagination, and can be filtered by a search term.
    - get_company_doc_keywords: Retrieve a list of all keywords associated with company documents (and the number of documents associated with each keyword). This endpoint supports pagination, and can be filtered by a search term.
    - get_company_doc_text: Retrieve the raw content for a single company document. Document IDs can be found using the tool find_company_docs.
    
    ## Authentication:
    All endpoints require the AIERA_API_KEY environment variable to be set.

    ## Parameter Notes:
    - Endpoints that support pagination use 'size' and 'from_index' parameters.
    - Date parameters should be in ISO format (YYYY-MM-DD).
    - Bloomberg tickers should be composed of a ticker and a country code joined by a colon (e.g., "AAPL:US").
    - Boolean parameters accept true/false values.

    ## Other Notes:
    - All dates and times are in eastern time (ET) unless specifically stated otherwise.
    - The term "publication" or "document" is likely referring to either an SEC filing or a company document.
    """


def run(transport="streamable-http"):
    mcp.run(transport=transport)