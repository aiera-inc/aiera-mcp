"""Aiera MCP Tools - Core financial data API tools for MCP servers."""

import os
from typing import Callable, Optional
import logging


logger = logging.getLogger(__name__)

__version__ = "0.1.0"

# API Key Provider Infrastructure
_api_key_provider: Optional[Callable[[], Optional[str]]] = None


def set_api_key_provider(provider: Callable[[], Optional[str]]) -> None:
    """Configure a custom API key provider function (e.g., for OAuth systems).

    Args:
        provider: A callable that returns an API key string or None

    Example:
        # For OAuth systems like aiera-public-mcp:
        from aiera_public_mcp.auth import get_current_api_key
        set_api_key_provider(get_current_api_key)
    """
    global _api_key_provider
    _api_key_provider = provider


def get_api_key() -> Optional[str]:
    """Get API key from configured provider or environment variable fallback.

    Returns:
        API key string or None if not available

    Priority order:
        1. Custom API key provider (if configured)
        2. AIERA_API_KEY environment variable
    """
    # Try custom provider first
    if _api_key_provider:
        try:
            if key := _api_key_provider():
                return key
        except Exception:
            logger.info(
                "Failed to get API key from provider, falling back to environment variable."
            )
            # Fallback to environment variable if provider fails
            pass

    # Fallback to environment variable
    return os.getenv("AIERA_API_KEY")


def clear_api_key_provider() -> None:
    """Clear the configured API key provider (mainly for testing)."""
    global _api_key_provider
    _api_key_provider = None


# List of all available tool names for reference with include/exclude
AVAILABLE_TOOLS = [
    # Event Tools
    "find_events",
    "get_event",
    "get_upcoming_events",
    # Filing Tools
    "find_filings",
    "get_filing",
    # Equity Tools
    "find_equities",
    "get_equity_summaries",
    "get_sectors_and_subsectors",
    # Index/Watchlist Tools
    "get_available_indexes",
    "get_index_constituents",
    "get_available_watchlists",
    "get_watchlist_constituents",
    # Company Document Tools
    "find_company_docs",
    "get_company_doc",
    "get_company_doc_categories",
    "get_company_doc_keywords",
    # Third Bridge Tools
    "find_third_bridge_events",
    "get_third_bridge_event",
]

# Convenience tool groups for common use cases
EVENT_TOOLS = ["find_events", "get_event", "get_upcoming_events"]
FILING_TOOLS = ["find_filings", "get_filing"]
EQUITY_TOOLS = ["find_equities", "get_equity_summaries", "get_sectors_and_subsectors"]
INDEX_WATCHLIST_TOOLS = [
    "get_available_indexes",
    "get_index_constituents",
    "get_available_watchlists",
    "get_watchlist_constituents",
]
COMPANY_DOC_TOOLS = [
    "find_company_docs",
    "get_company_doc",
    "get_company_doc_categories",
    "get_company_doc_keywords",
]
THIRD_BRIDGE_TOOLS = ["find_third_bridge_events", "get_third_bridge_event"]


from .tools.company_docs import (
    find_company_docs,
    get_company_doc,
    get_company_doc_categories,
    get_company_doc_keywords,
)
from .tools.third_bridge import find_third_bridge_events, get_third_bridge_event
from .tools.transcrippets import (
    find_transcrippets,
    create_transcrippet,
    delete_transcrippet,
)

# Import utilities
from .tools.base import make_aiera_request, AIERA_BASE_URL, CITATION_PROMPT
from .tools.utils import (
    correct_bloomberg_ticker,
    correct_keywords,
    correct_categories,
    correct_provided_ids,
    correct_event_type,
    correct_transcript_section,
)

# Import server functionality
from .server import register_aiera_tools, DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE

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
    "find_transcrippets",
    "create_transcrippet",
    "delete_transcrippet",
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
    # API Key Provider
    "set_api_key_provider",
    "get_api_key",
    "clear_api_key_provider",
    # Constants
    "DEFAULT_PAGE_SIZE",
    "DEFAULT_MAX_PAGE_SIZE",
    "AIERA_BASE_URL",
    "CITATION_PROMPT",
    "AVAILABLE_TOOLS",
    # Tool Groups
    "EVENT_TOOLS",
    "FILING_TOOLS",
    "EQUITY_TOOLS",
    "INDEX_WATCHLIST_TOOLS",
    "COMPANY_DOC_TOOLS",
    "THIRD_BRIDGE_TOOLS",
]
