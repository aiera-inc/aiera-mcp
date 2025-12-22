"""Aiera MCP Tools - Core financial data API tools for MCP servers."""

import os
from typing import Callable, Optional
import logging

try:
    from ._version import __version__
except ImportError:
    # Fallback for development/editable installs
    __version__ = "dev"

logger = logging.getLogger(__name__)

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

    Raises:
        ValueError: If provider is configured but fails to return an API key
    """
    # Try custom provider first
    if _api_key_provider:
        try:
            key = _api_key_provider()
            if key:
                logger.debug(f"Got API key from provider (length: {len(key)})")
                return key
            else:
                # Provider returned None - this is a configuration error
                logger.error(
                    "API key provider returned None. This indicates a configuration issue. "
                    "Falling back to environment variable."
                )
        except Exception as e:
            logger.error(f"API key provider failed with exception: {e}", exc_info=True)
            # Re-raise to surface the actual error instead of silently falling back
            raise ValueError(f"Failed to get API key from configured provider: {e}")

    # Fallback to environment variable only if no provider is configured
    env_key = os.getenv("AIERA_API_KEY")
    if env_key:
        logger.debug("Using API key from AIERA_API_KEY environment variable")
    else:
        logger.warning("No API key available from provider or environment variable")
    return env_key


def clear_api_key_provider() -> None:
    """Clear the configured API key provider (mainly for testing)."""
    global _api_key_provider
    _api_key_provider = None


# List of all available tool names for reference
AVAILABLE_TOOLS = [
    # Event Tools
    "find_events",
    "find_conferences",
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
    # Transcrippet Tools
    "find_transcrippets",
    "create_transcrippet",
    "delete_transcrippet",
    # Search Tools
    "search_transcripts",
    "search_filings",
]

# Convenience tool groups for common use cases
EVENT_TOOLS = ["find_events", "find_conferences", "get_event", "get_upcoming_events"]
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
EMBEDDING_SEARCH_PIPELINE = "embedding_pipeline"
HYBRID_SEARCH_PIPELINE = "hybrid_search_pipeline"

# Import tool functions from domain modules
from .tools.events import find_events, find_conferences, get_event, get_upcoming_events
from .tools.filings import find_filings, get_filing
from .tools.equities import (
    find_equities,
    get_equity_summaries,
    get_sectors_and_subsectors,
    get_available_indexes,
    get_index_constituents,
    get_available_watchlists,
    get_watchlist_constituents,
)
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
from .tools.search import search_transcripts, search_filings

# Import configuration
from .config import get_settings, reload_settings, AieraSettings

# Import context providers
from .context import (
    set_request_context_provider,
    get_request_context,
    clear_request_context_provider,
    set_error_handler,
    handle_api_error,
    clear_error_handler,
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
    # Version
    "__version__",
    # Tools
    "find_events",
    "find_conferences",
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
    "search_transcripts",
    "search_filings",
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
    # Context Providers
    "set_request_context_provider",
    "get_request_context",
    "clear_request_context_provider",
    "set_error_handler",
    "handle_api_error",
    "clear_error_handler",
    # Configuration
    "get_settings",
    "reload_settings",
    "AieraSettings",
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
