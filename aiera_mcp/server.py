#!/usr/bin/env python3

import os
import httpx
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Callable, List, Set
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP

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

    ### Transcrippets API
    - find_transcrippets: Retrieve Transcrippets™, filtered by various identifiers such as transcrippet_id (comma-separated list), event_id (comma-separated list), equity_id (comma-separated list), speaker_id (comma-separated list), transcript_item_id (comma-separated list), and date ranges (created_start_date and created_end_date).
    -- Transcrippets™ are curated segments of event transcripts that capture key insights or memorable quotes.
    -- Date parameters should be in ISO format (YYYY-MM-DD).
    - create_transcrippet: Create a new Transcrippet™ from an event transcript segment. Requires event_id, transcript (the text content), transcript_item_id, transcript_item_offset, transcript_end_item_id, and transcript_end_item_offset. Optionally accepts company_id and equity_id.
    -- The event_id can be found using the find_events tool.
    -- Transcript item IDs and offsets define the precise boundaries of the transcript segment to capture.
    - delete_transcrippet: Delete a Transcrippet™ by its ID. This is a destructive operation that cannot be undone.
    -- The transcrippet_id can be found using the find_transcrippets tool.

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

    # Register all tools using the new modular structure
    from .tools import register_all_tools
    register_all_tools(mcp_server)


def run(transport: str = "stdio"):
    """Run the MCP server (for standalone usage)."""
    # Register all tools when running standalone
    register_aiera_tools(mcp)

    # Literal type fix for transport parameter
    from typing import Literal
    valid_transports = ["stdio", "sse", "streamable-http"]
    if transport not in valid_transports:
        raise ValueError(f"Invalid transport: {transport}. Must be one of {valid_transports}")

    # Cast to the expected literal type
    transport_literal: Literal["stdio", "sse", "streamable-http"] = transport  # type: ignore
    mcp.run(transport=transport_literal)