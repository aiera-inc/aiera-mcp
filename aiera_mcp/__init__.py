"""Aiera MCP Tools - Core financial data API tools for MCP servers."""

__version__ = "0.1.0"

from .server import (
    # Tools
    find_events,
    get_event,
    get_upcoming_events,
    find_filings,
    get_filing,
    find_equities,
    get_equity_summaries,
    get_sectors_and_subsectors,
    get_available_indexes,
    get_index_constituents,
    get_available_watchlists,
    get_watchlist_constituents,
    find_company_docs,
    get_company_doc,
    get_company_doc_categories,
    get_company_doc_keywords,
    find_third_bridge_events,
    get_third_bridge_event,

    # Utilities
    make_aiera_request,
    correct_bloomberg_ticker,
    correct_keywords,
    correct_categories,
    correct_provided_ids,
    correct_event_type,
    correct_transcript_section,

    # Tool registration
    register_aiera_tools,

    # Constants
    DEFAULT_PAGE_SIZE,
    DEFAULT_MAX_PAGE_SIZE,
    AIERA_BASE_URL,
    CITATION_PROMPT,
)

__all__ = [
    # Tools
    "find_events",
    "get_event",
    "get_upcoming_events",
    "find_filings",
    "get_filing",
    "find_equities",
    "get_equity_summaries",
    "get_sectors_and_subsectors",
    "get_available_indexes",
    "get_index_constituents",
    "get_available_watchlists",
    "get_watchlist_constituents",
    "find_company_docs",
    "get_company_doc",
    "get_company_doc_categories",
    "get_company_doc_keywords",
    "find_third_bridge_events",
    "get_third_bridge_event",

    # Utilities
    "make_aiera_request",
    "correct_bloomberg_ticker",
    "correct_keywords",
    "correct_categories",
    "correct_provided_ids",
    "correct_event_type",
    "correct_transcript_section",

    # Tool registration
    "register_aiera_tools",

    # Constants
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_MAX_PAGE_SIZE",
    "AIERA_BASE_URL",
    "CITATION_PROMPT",
]