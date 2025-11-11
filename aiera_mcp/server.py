#!/usr/bin/env python3

import os
import httpx
import logging
import contextvars
import json

from datetime import datetime
from typing import Any, Dict, Optional, Callable, List, Set
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Completion, CompletionArgument, CompletionContext
from mcp.types import PromptReference, ResourceTemplateReference

# Setup logging
logger = logging.getLogger(__name__)

# Import API key provider functions from package
try:
    from . import get_api_key
except ImportError:
    # Fallback for standalone usage
    def get_api_key() -> Optional[str]:
        return os.getenv("AIERA_API_KEY")

# Global HTTP client for Lambda environment with proper configuration
_lambda_http_client: Optional[httpx.AsyncClient] = None


async def cleanup_lambda_http_client():
    """Cleanup the global HTTP client."""
    global _lambda_http_client
    if _lambda_http_client is not None:
        await _lambda_http_client.aclose()
        _lambda_http_client = None


def get_lambda_http_client() -> httpx.AsyncClient:
    """Get or create a shared HTTP client for Lambda environment."""
    global _lambda_http_client
    if _lambda_http_client is None:
        # Configure client with connection pooling and timeouts
        _lambda_http_client = httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=30.0),
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    return _lambda_http_client


@asynccontextmanager
async def app_lifespan(_server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage application lifecycle with HTTP client."""
    # Always create client in lifespan to ensure proper FastMCP initialization
    # Even in Lambda, FastMCP requires the full lifespan cycle to initialize its task groups

    # In Lambda, we can use a shared client for efficiency
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME") or os.getenv("MCP_LAMBDA_MODE"):
        # For Lambda, yield the global client but still go through full lifespan
        client = get_lambda_http_client()
        yield {"http_client": client}
        # Don't close the global client on shutdown in Lambda

    else:
        # For non-Lambda environments, use context-managed client
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20, keepalive_expiry=30.0),
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        ) as client:
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

# Citation prompt for UI clients
CITATION_PROMPT = """IMPORTANT: when referencing this data in your response, ALWAYS include inline citations by using the information found in the `citation_information` block, along with an incrementing counter. Render these citations as markdown (padded with a leading space for readability), like this: [[1]](url "title")

Where possible, include inline citations for every fact, figure, or quote that was sourced, directly or indirectly, from a transcript by using transcript-level citations (as opposed to event-level citations).

If multiple citations are relevant, include them all. You can reference the same citation multiple times if needed.

However, if the user has requested a response as JSON, you do NOT need to include any citations."""


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


def correct_provided_ids(provided_ids: str) -> str:
    """Ensure provided ID lists have comma-separation."""
    if "," not in provided_ids and " " in provided_ids:
        provided_ids = ",".join(provided_ids.split())

    reid = []
    for provided_id in provided_ids.split(","):
        reid.append(int(provided_id.strip()))

    return reid


def correct_provided_types(provided_types: str) -> str:
    """Ensure provided type lists have comma-separation."""
    if "," not in provided_types and " " in provided_types:
        provided_types = ",".join(provided_types.split())

    retype = []
    for provided_type in provided_types.split(","):
        retype.append(str(provided_type.strip()))

    return retype


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


def correct_event_type(event_type: str) -> str:
    """Ensure event type is set correctly."""
    if event_type.strip() == "conference":
        event_type = "presentation"
    elif event_type.strip() == "m&a":
        event_type = "special_situation"

    if event_type.strip() not in ["earnings", "presentation", "shareholder_meeting", "investor_meeting", "special_situation"]:
        event_type = "earnings"

    return event_type.strip()


def correct_transcript_section(section: str) -> str:
    """Ensure the transcript section is set correctly."""
    if section.strip() == "qa":
        section = "q_and_a"

    return section.strip()


async def get_http_client(ctx) -> httpx.AsyncClient:
    """Get HTTP client from context."""
    # Try to get client from lifespan context first
    try:
        if hasattr(ctx, "request_context") and hasattr(ctx.request_context, "lifespan_context"):
            client = ctx.request_context.lifespan_context.get("http_client")
            if client:
                return client
    except (KeyError, AttributeError) as e:
        logger.debug(f"Could not get client from lifespan context: {e}")

    # Fall back to global client for Lambda or when lifespan context is not available
    return get_lambda_http_client()


async def get_api_key_from_context(ctx) -> str:
    """Extract API key from authenticated context with enhanced OAuth integration."""
    # Log context ID to verify isolation between concurrent requests
    context_id = id(contextvars.copy_context())
    logger.debug(f"Context ID: {context_id}")

    # Check if API key is already stored in context variable
    api_key = get_api_key()

    # If API key already set (e.g., from query parameter or OAuth), use it
    if api_key:
        logger.info(f"API key already set, using {api_key[:8]}...")
        return api_key

    # If no API key yet, try OAuth authentication
    try:
        # Try to import and use OAuth authentication
        try:
            from .auth import validate_auth_context, get_current_api_key
            await validate_auth_context(ctx)
            api_key = get_current_api_key()

            if not api_key:
                # This is the critical issue - if OAuth succeeds but no API key found,
                # we should NOT fall back to environment variables
                logger.error("OAuth authentication succeeded but no API key found in user claims")
                raise ValueError("No API key found in authenticated user claims")

        except ImportError:
            # OAuth not available, fall back to environment variable
            logger.debug("OAuth authentication not available, using environment variable")
            api_key = os.getenv("AIERA_API_KEY")

    except Exception as e:
        logger.error(f"Auth validation failed: {str(e)}")

        # Special handling for Lambda environment with direct API key
        # This should only be used as absolute last resort
        if os.getenv("AWS_LAMBDA_FUNCTION_NAME") and os.getenv("AIERA_API_KEY"):
            logger.warning("Using Lambda environment API key as emergency fallback")
            logger.warning("This should only happen during Lambda cold starts or system issues")

            api_key = os.getenv("AIERA_API_KEY")

        else:
            # Re-raise the original error
            raise

    if not api_key:
        raise ValueError("Failed to retrieve API key after all authentication attempts")

    return api_key


async def make_aiera_request(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    api_key: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    additional_instructions: Optional[str] = None,
    return_type: str = "json",
) -> Dict[str, Any]:
    """Make a request to the Aiera API with enhanced error handling and logging.

    Args:
        client: HTTP client instance
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        api_key: API key (required)
        params: Query parameters
        data: Request body data
        additional_instructions: Additional instructions for response formatting
        return_type: Response format type

    Returns:
        JSON response data with instructions
    """
    headers = DEFAULT_HEADERS.copy()
    headers["X-API-Key"] = api_key

    # Log API key info for debugging (without exposing the full key)
    logger.info(
        f"API request: {endpoint}\n"
        f"API key preview: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else '***'}\n"
        f"Params: {params}\n"
    )

    url = f"{AIERA_BASE_URL}{endpoint}"

    try:
        response = await client.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
            timeout=60.0,
        )

    except httpx.RequestError as e:
        logger.error(f"Request URL was: {url}")
        logger.error(f"Request headers were: {headers}")
        if params:
            logger.error(f"Request params were: {params}")

        raise Exception(f"Network error calling Aiera API: {str(e)}")

    if response.status_code != 200:
        logger.error(f"API error: {response.status_code} - {response.text}")
        logger.error(f"Request URL: {url}")
        logger.error(f"Request headers were: {headers}")
        if params:
            logger.error(f"Request params: {params}")

        # Check if this looks like an auth error
        if response.status_code in [401, 403]:
            raise Exception(
                f"Aiera API authentication failed (HTTP {response.status_code}). The API key may be invalid or expired."
            )
        else:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

    if return_type == "json":
        response_data = response.json()
    else:
        response_data = response.text

    # Prepare instructions for response formatting
    instructions = [
        "This data is provided for institutional finance professionals. Responses should be composed of accurate, concise, and well-structured financial insights.",
        CITATION_PROMPT,
    ]

    if additional_instructions:
        instructions.append(additional_instructions)

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
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Find events, filtered by a date range, and (optionally) ticker(s), watchlist, index, sector, or subsector; or event type(s)."""
    logger.info("tool called: find_events")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "include_transcripts": False,
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

    if event_type:
        params["event_type"] = correct_event_type(event_type)

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

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
    logger.info("tool called: get_event")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

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
    logger.info("tool called: get_upcoming_events")
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
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """Find SEC filings, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector; and (optionally) by a form number."""
    logger.info("tool called: find_filings")
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

    if form_number:
        params["form_number"] = form_number

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

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
    """Retrieve equities, filtered by various identifiers, such as ticker, ISIN, or RIC; or by search."""
    logger.info("tool called: find_equities")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "include_company_metadata": "true",
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
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

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
    logger.info("tool called: get_sectors_and_subsectors")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

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
    logger.info("tool called: get_equity_summaries")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "bloomberg_ticker": correct_bloomberg_ticker(bloomberg_ticker),
        "lookback": "90",
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
    logger.info("tool called: get_available_indexes")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

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
    logger.info("tool called: get_index_constituents")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {}

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

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
    logger.info("tool called: get_available_watchlists")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

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
    logger.info("tool called: get_watchlist_constituents")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {}

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

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
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE
) -> Dict[str, Any]:
    """Find documents that have been published by a company, filtered by a date range, and (optionally) by ticker(s), watchlist, index, sector, or subsector; or category(s) or keyword(s)."""
    logger.info("tool called: find_company_docs")
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
        "include_content": "true",
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-company-docs",
        api_key=api_key,
        params=params,
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
    logger.info("tool called: get_company_doc_categories")
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
    logger.info("tool called: get_company_doc_keywords")
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
    bloomberg_ticker: Optional[str] = None,
    watchlist_id: Optional[int] = None,
    index_id: Optional[int] = None,
    sector_id: Optional[int] = None,
    subsector_id: Optional[int] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Find expert insight events from Third Bridge, filtering by a date range and (optionally) by ticker, index, watchlist, sector, or subsector."""
    logger.info("tool called: find_third_bridge_events")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "start_date": start_date,
        "end_date": end_date,
        "include_transcripts": "false",
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

    if page:
        params["page"] = str(page)

    if page_size:
        params["page_size"] = str(page_size)

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
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
    """Retrieve an expert insight events from Third Bridge, including agenda, insights, transcript, and other metadata."""
    logger.info("tool called: get_third_bridge_event")
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {
        "event_ids": str(event_id),
        "include_transcripts": "true",
    }

    return await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-third-bridge",
        api_key=api_key,
        params=params,
    )


@mcp.tool(
    annotations={
        "title": "Search Transcripts",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def search_transcripts(
    search: str,
    event_ids: str = None,
    equity_ids: str = None,
    start_date: str = None,
    end_date: str = None,
    transcript_section: str = None,
    event_type: Optional[str] = "earnings",
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Perform a semantic search against all event transcripts."""
    logger.info("tool called: search_transcripts")

    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    must_clauses = []

    # add event ID filter...
    if event_ids:
        must_clauses.append({
            "terms": {
                "transcript_event_id": correct_provided_ids(event_ids),
            }
        })

    # add equity ID filter...
    if equity_ids:
        must_clauses.append({
            "terms": {
                "primary_equity_id": correct_provided_ids(equity_ids),
            }
        })

    # add date range filter...
    if start_date and end_date:
        must_clauses.append({
            "range": {
                "date": {
                    "gte": start_date,
                    "lte": end_date
                }
            }
        })

    # add event type filter...
    if event_type and event_type.strip():
        must_clauses.append({
            "term": {
                "transcript_event_type": correct_event_type(event_type)
            }
        })

    # add a section filter...
    if transcript_section and transcript_section.strip() in ["presentation", "q_and_a"]:
        must_clauses.append({
            "term": {
                "transcript_section": transcript_section.strip()
            }
        })

    # first, try ML-based search...
    query = {
        "query": {
            "bool": {
                "must": must_clauses,
            }
        },
        "from": (page - 1),
        "size": page_size,
        "min_score": 0.2,
        "_source": [
            "content_id",
            "transcript_event_id",
            "primary_equity_id",
            "title",
            "text",
            "speaker_name",
            "speaker_title",
            "date",
            "section",
            "transcript_section"
        ],
        "sort": [
            {
                "_score": {
                    "order": "desc"
                }
            }
        ],
        "ext": {
            "ml_inference": {
                "query_text": search
            }
        }
    }

    raw_results = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search/transcripts",
        api_key=api_key,
        params={},
        data=query,
    )

    # if not (or bad) results, fall back to traditional search...
    if not raw_results or "result" not in raw_results or not raw_results["result"]:
        query = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "should": [
                        {
                            "match": {
                                "text": {
                                    "query": search,
                                    "boost": 2.0
                                }
                            }
                        },
                        {
                            "multi_match": {
                                "query": search,
                                "fields": ["text", "title", "speaker_name"],
                                "type": "best_fields",
                                "boost": 1.5
                            }
                        }
                    ]
                }
            },
            "from": (page - 1),
            "size": page_size,
            "min_score": 0.2,
            "_source": [
                "content_id",
                "transcript_event_id",
                "primary_equity_id",
                "title",
                "text",
                "speaker_name",
                "speaker_title",
                "date",
                "section",
                "transcript_section"
            ],
            "sort": [
                {
                    "_score": {
                        "order": "desc"
                    }
                }
            ]
        }

        raw_results = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/transcripts",
            api_key=api_key,
            params={},
            data=query,
        )

    return raw_results


@mcp.tool(
    annotations={
        "title": "Search Filings",
        "readOnlyHint": True,
        "destructiveHint": False,
    }
)
async def search_filings(
    search: str,
    filing_ids: str = None,
    equity_ids: str = None,
    filing_types: str = None,
    start_date: str = None,
    end_date: str = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    """Perform a semantic search against all SEC filings."""
    logger.info("tool called: search_filings")

    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    must_clauses = []

    # add event ID filter...
    if filing_ids:
        must_clauses.append({
            "terms": {
                "filing_id": correct_provided_ids(filing_ids),
            }
        })

    # add equity ID filter...
    if equity_ids:
        must_clauses.append({
            "terms": {
                "primary_equity_id": correct_provided_ids(equity_ids),
            }
        })

    # add date range filter...
    if start_date and end_date:
        must_clauses.append({
            "range": {
                "date": {
                    "gte": start_date,
                    "lte": end_date
                }
            }
        })

    # add filing type filter...
    if filing_types:
        must_clauses.append({
            "terms": {
                "filing_type": correct_provided_types(filing_types),
            }
        })

    query = {
        "query": {
            "bool": {
                "must": must_clauses,
                "should": [
                    {
                        "match": {
                            "text": {
                                "query": search,
                                "boost": 2.0
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": search,
                            "fields": ["text", "title"],
                            "type": "best_fields",
                            "boost": 1.5
                        }
                    }
                ]
            }
        },
        "from": (page - 1),
        "size": page_size,
        "min_score": 0.2,
        "_source": [
            "filing_id",
            "metadata",
            "primary_equity_id",
            "title",
            "text",
            "date",
            "filing_type"
        ],
        "sort": [
            {
                "_score": {
                    "order": "desc"
                }
            }
        ]
    }

    raw_results = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search/filings",
        api_key=api_key,
        params={},
        data=query,
    )

    return raw_results


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
    - find_third_bridge_events: Retrieve expert insight events from Third Bridge, filtered by start_date and end_date, and optionally by bloomberg_ticker (a comma-separated list of tickers), watchlist_id, index_id, sector_id, or subsector_id. This endpoint supports pagination.
    - get_third_bridge_event: Retrieve an expert insight event from Third Bridge, including an agenda, insights, the full transcript, filtered by event_id. 
    -- The event ID can be found using the tool find_third_bridge_events.
    -- If you need to retrieve more than one event, make multiple sequential calls.
    
    ### Search API
    - search_transcripts: Perform a semantic search against all event transcripts, filtered by event_ids (a comma-separated list of IDs), equity_ids (a comma-separated list of IDs), transcript_section, event_type, or a date range. This endpoint supports pagination.
    -- Transcript section must be one of the following: presentation, q_and_a
    -- Event type must be one of the following: earnings, presentation, shareholder_meeting, investor_meeting, special_situation
    -- Event IDs can be found using the find_events tool.
    -- Equity IDs can be found using the find_equities tool.
    - search_filings: Perform a semantic search against all SEC filings, filtered by filing_ids (a comma-separated list of IDs), equity_ids (a comma-separated list of IDs), filing_types (a comma-seperated list of types), or a date range. This endpoint supports pagination.
    -- Examples of filing types include: 10-K, 10-Q, and 8-K. There are other possibilities, but those 3 will be the most commonly used.
    -- Event IDs can be found using the find_events tool.
    -- Equity IDs can be found using the find_equities tool.
    
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
    - The current date is **{datetime.now().strftime("%Y-%m-%d")}**, and the current time is **{datetime.now().strftime("%I:%M %p")}**. Relative dates and times (e.g., "last 3 months" or "next 3 months" or "later today") should be calculated based on this date.
    """


def register_aiera_tools(
    mcp_server: FastMCP,
    api_key_provider: Optional[Callable[[], Optional[str]]] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> None:
    """Register Aiera tools with a FastMCP server instance with optional filtering.

    Args:
        mcp_server: FastMCP server instance to register tools with
        api_key_provider: Optional function that returns API key for OAuth systems
        include: Optional list of tool names to include (if specified, only these tools will be registered)
        exclude: Optional list of tool names to exclude (these tools will not be registered)

    Examples:
        # Basic usage with environment variable - registers all tools
        register_aiera_tools(mcp)

        # With OAuth provider - registers all tools
        from aiera_public_mcp.auth import get_current_api_key
        register_aiera_tools(mcp, get_current_api_key)

        # Register only event-related tools
        register_aiera_tools(mcp, include=["find_events", "get_event", "get_upcoming_events"])

        # Register all tools except Third Bridge
        register_aiera_tools(mcp, exclude=["find_third_bridge_events", "get_third_bridge_event"])

        # Combine OAuth with selective registration
        register_aiera_tools(mcp, get_current_api_key, include=["find_events", "find_filings"])
    """
    # Configure API key provider if provided
    if api_key_provider:
        from . import set_api_key_provider
        set_api_key_provider(api_key_provider)

    # Define all available tools
    available_tools = {
        "find_events": {
            "function": find_events,
            "description": "Finds company events using search filters including date, event type, company, sectors, and more."
        },
        "get_event": {
            "function": get_event,
            "description": "Returns the details of an event given its identifier."
        },
        "get_upcoming_events": {
            "function": get_upcoming_events,
            "description": "Returns upcoming events of a specific type that match provided filters."
        },
        "find_filings": {
            "function": find_filings,
            "description": "Finds SEC filings using search filters including company, date, form type, and more."
        },
        "get_filing": {
            "function": get_filing,
            "description": "Returns the details of a filing given its identifier."
        },
        "find_equities": {
            "function": find_equities,
            "description": "Finds companies/equities using search filters like company name, ticker, sector, and more."
        },
        "get_sectors_and_subsectors": {
            "function": get_sectors_and_subsectors,
            "description": "Returns the list of available sectors and their subsectors for filtering."
        },
        "get_equity_summaries": {
            "function": get_equity_summaries,
            "description": "Returns summary statistics for equities."
        },
        "get_available_indexes": {
            "function": get_available_indexes,
            "description": "Returns the list of available stock indexes."
        },
        "get_index_constituents": {
            "function": get_index_constituents,
            "description": "Returns the constituents of a stock index."
        },
        "get_available_watchlists": {
            "function": get_available_watchlists,
            "description": "Returns the list of available watchlists."
        },
        "get_watchlist_constituents": {
            "function": get_watchlist_constituents,
            "description": "Returns the constituents of a watchlist."
        },
        "find_company_docs": {
            "function": find_company_docs,
            "description": "Finds company documents using search filters."
        },
        "get_company_doc": {
            "function": get_company_doc,
            "description": "Returns the details of a company document given its identifier."
        },
        "get_company_doc_categories": {
            "function": get_company_doc_categories,
            "description": "Returns the list of available categories for company documents."
        },
        "get_company_doc_keywords": {
            "function": get_company_doc_keywords,
            "description": "Returns the list of available keywords for company documents."
        },
        "find_third_bridge_events": {
            "function": find_third_bridge_events,
            "description": "Finds Third Bridge events using search filters."
        },
        "get_third_bridge_event": {
            "function": get_third_bridge_event,
            "description": "Returns the details of a Third Bridge event given its identifier."
        },
    }

    # Validate include/exclude parameters
    if include is not None and exclude is not None:
        raise ValueError("Cannot specify both 'include' and 'exclude' parameters")

    if include is not None:
        # Validate that all included tools exist
        invalid_tools = set(include) - set(available_tools.keys())
        if invalid_tools:
            raise ValueError(f"Unknown tools specified in 'include': {sorted(invalid_tools)}")
        tools_to_register = set(include)
    elif exclude is not None:
        # Validate that all excluded tools exist
        invalid_tools = set(exclude) - set(available_tools.keys())
        if invalid_tools:
            raise ValueError(f"Unknown tools specified in 'exclude': {sorted(invalid_tools)}")
        tools_to_register = set(available_tools.keys()) - set(exclude)
    else:
        # Register all tools
        tools_to_register = set(available_tools.keys())

    # Register the selected tools
    for tool_name in sorted(tools_to_register):
        tool_info = available_tools[tool_name]
        mcp_server.tool(
            name=tool_name,
            description=tool_info["description"]
        )(tool_info["function"])


def run(transport: str = "streamable-http"):
    """Run the MCP server (for standalone usage)."""
    mcp.run(transport=transport)