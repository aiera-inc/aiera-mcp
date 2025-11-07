#!/usr/bin/env python3

"""Tool registry for Aiera MCP server."""

from typing import List, Tuple

# Import all tool functions
from .events import find_events, get_event, get_upcoming_events
from .filings import find_filings, get_filing
from .equities import find_equities, get_equity_summaries, get_available_watchlists, get_available_indexes, get_sectors_and_subsectors, get_index_constituents, get_watchlist_constituents
from .company_docs import find_company_docs, get_company_doc, get_company_doc_categories, get_company_doc_keywords
from .third_bridge import find_third_bridge_events, get_third_bridge_event
from .transcrippets import find_transcrippets, create_transcrippet, delete_transcrippet

# Import all parameter model classes
from .params import (
    FindEventsArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindFilingsArgs,
    GetFilingArgs,
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    EmptyArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    SearchArgs,
    FindThirdBridgeEventsArgs,
    GetThirdBridgeEventArgs,
    FindTranscrippetsArgs,
    CreateTranscrippetArgs,
    DeleteTranscrippetArgs,
)

TOOL_REGISTRY = {
    'find_events': {
        'display_name': 'Event Finder',
        'description': 'Find corporate events (earnings calls, conferences, meetings) filtered by date range and optionally by company identifiers, watchlists, indices, sectors, or event types. Returns events with metadata but no transcripts.',
        'input_schema': FindEventsArgs.model_json_schema(),
        'function': find_events,
        'args_model': FindEventsArgs,
        'category': 'events',
        'read_only': True,
        'destructive': False,
    },
    'get_event': {
        'display_name': 'Event Retriever',
        'description': 'Retrieve detailed information about a specific event including summary, transcript, and metadata. Optionally filter transcripts by section for earnings events.',
        'input_schema': GetEventArgs.model_json_schema(),
        'function': get_event,
        'args_model': GetEventArgs,
        'category': 'events',
        'read_only': True,
        'destructive': False,
    },
    'get_upcoming_events': {
        'display_name': 'Upcoming Events Finder',
        'description': 'Retrieve confirmed and estimated upcoming events within a date range, filtered by company identifiers, watchlists, indices, or sectors.',
        'input_schema': GetUpcomingEventsArgs.model_json_schema(),
        'function': get_upcoming_events,
        'args_model': GetUpcomingEventsArgs,
        'category': 'events',
        'read_only': True,
        'destructive': False,
    },
    'find_filings': {
        'display_name': 'Filing Finder',
        'description': 'Find SEC filings (10-K, 10-Q, 8-K, etc.) filtered by date range and optionally by company identifiers, watchlists, indices, sectors, or form types. Returns filing metadata and summaries.',
        'input_schema': FindFilingsArgs.model_json_schema(),
        'function': find_filings,
        'args_model': FindFilingsArgs,
        'category': 'filings',
        'read_only': True,
        'destructive': False,
    },
    'get_filing': {
        'display_name': 'Filing Retriever',
        'description': 'Retrieve detailed information about a specific SEC filing including content, metadata, and summaries.',
        'input_schema': GetFilingArgs.model_json_schema(),
        'function': get_filing,
        'args_model': GetFilingArgs,
        'category': 'filings',
        'read_only': True,
        'destructive': False,
    },
    'find_equities': {
        'display_name': 'Equity Finder',
        'description': 'Find companies and equities using various identifiers (Bloomberg tickers, ISIN, RIC, PermID) or search terms. Returns company and equity information.',
        'input_schema': FindEquitiesArgs.model_json_schema(),
        'function': find_equities,
        'args_model': FindEquitiesArgs,
        'category': 'equities',
        'read_only': True,
        'destructive': False,
    },
    'get_equity_summaries': {
        'display_name': 'Equity Summary Retriever',
        'description': 'Get comprehensive summary information for one or more equities including financial data, sector classification, and key metrics.',
        'input_schema': GetEquitySummariesArgs.model_json_schema(),
        'function': get_equity_summaries,
        'args_model': GetEquitySummariesArgs,
        'category': 'equities',
        'read_only': True,
        'destructive': False,
    },
    'get_available_watchlists': {
        'display_name': 'Watchlist Explorer',
        'description': 'Retrieve all available watchlists with their IDs, names, and descriptions. Used to find valid watchlist IDs for filtering other tools.',
        'input_schema': EmptyArgs.model_json_schema(),
        'function': get_available_watchlists,
        'args_model': EmptyArgs,
        'category': 'equities',
        'read_only': True,
        'destructive': False,
    },
    'get_available_indexes': {
        'display_name': 'Index Explorer',
        'description': 'Retrieve all available stock market indices with their IDs, names, and descriptions. Used to find valid index IDs for filtering other tools.',
        'input_schema': EmptyArgs.model_json_schema(),
        'function': get_available_indexes,
        'args_model': EmptyArgs,
        'category': 'equities',
        'read_only': True,
        'destructive': False,
    },
    'get_sectors_and_subsectors': {
        'display_name': 'Sector Explorer',
        'description': 'Retrieve all available sectors and subsectors with their IDs, names, and hierarchical relationships. Used to find valid sector/subsector IDs for filtering other tools.',
        'input_schema': SearchArgs.model_json_schema(),
        'function': get_sectors_and_subsectors,
        'args_model': SearchArgs,
        'category': 'equities',
        'read_only': True,
        'destructive': False,
    },
    'get_index_constituents': {
        'display_name': 'Index Constituent Finder',
        'description': 'Get all equities within a specific stock market index. Returns company information for index members.',
        'input_schema': GetIndexConstituentsArgs.model_json_schema(),
        'function': get_index_constituents,
        'args_model': GetIndexConstituentsArgs,
        'category': 'equities',
        'read_only': True,
        'destructive': False,
    },
    'get_watchlist_constituents': {
        'display_name': 'Watchlist Constituent Finder',
        'description': 'Get all equities within a specific watchlist. Returns company information for watchlist members.',
        'input_schema': GetWatchlistConstituentsArgs.model_json_schema(),
        'function': get_watchlist_constituents,
        'args_model': GetWatchlistConstituentsArgs,
        'category': 'equities',
        'read_only': True,
        'destructive': False,
    },
    'find_company_docs': {
        'display_name': 'Company Document Finder',
        'description': 'Find company-published documents (press releases, investor presentations, regulatory filings) filtered by date range and optionally by company identifiers, categories, or keywords.',
        'input_schema': FindCompanyDocsArgs.model_json_schema(),
        'function': find_company_docs,
        'args_model': FindCompanyDocsArgs,
        'category': 'company_docs',
        'read_only': True,
        'destructive': False,
    },
    'get_company_doc': {
        'display_name': 'Company Document Retriever',
        'description': 'Retrieve detailed information about a specific company document including content, metadata, and summaries.',
        'input_schema': GetCompanyDocArgs.model_json_schema(),
        'function': get_company_doc,
        'args_model': GetCompanyDocArgs,
        'category': 'company_docs',
        'read_only': True,
        'destructive': False,
    },
    'get_company_doc_categories': {
        'display_name': 'Document Category Explorer',
        'description': 'Retrieve all available document categories for filtering company documents. Used to find valid category values for find_company_docs.',
        'input_schema': SearchArgs.model_json_schema(),
        'function': get_company_doc_categories,
        'args_model': SearchArgs,
        'category': 'company_docs',
        'read_only': True,
        'destructive': False,
    },
    'get_company_doc_keywords': {
        'display_name': 'Document Keyword Explorer',
        'description': 'Retrieve all available keywords for filtering company documents. Used to find valid keyword values for find_company_docs.',
        'input_schema': SearchArgs.model_json_schema(),
        'function': get_company_doc_keywords,
        'args_model': SearchArgs,
        'category': 'company_docs',
        'read_only': True,
        'destructive': False,
    },
    'find_third_bridge_events': {
        'display_name': 'Third Bridge Event Finder',
        'description': 'Find expert insight events from Third Bridge filtered by date range and optionally by company identifiers, watchlists, indices, or sectors. Provides access to expert interviews and insights.',
        'input_schema': FindThirdBridgeEventsArgs.model_json_schema(),
        'function': find_third_bridge_events,
        'args_model': FindThirdBridgeEventsArgs,
        'category': 'third_bridge',
        'read_only': True,
        'destructive': False,
    },
    'get_third_bridge_event': {
        'display_name': 'Third Bridge Event Retriever',
        'description': 'Retrieve detailed information about a specific Third Bridge expert insight event including agenda, insights, transcript, and other metadata.',
        'input_schema': GetThirdBridgeEventArgs.model_json_schema(),
        'function': get_third_bridge_event,
        'args_model': GetThirdBridgeEventArgs,
        'category': 'third_bridge',
        'read_only': True,
        'destructive': False,
    },
    'find_transcrippets': {
        'display_name': 'Transcrippet Finder',
        'description': 'Find and retrieve Transcrippets™ (curated transcript segments) filtered by various identifiers and date ranges. Returns public URLs for sharing key insights.',
        'input_schema': FindTranscrippetsArgs.model_json_schema(),
        'function': find_transcrippets,
        'args_model': FindTranscrippetsArgs,
        'category': 'transcrippets',
        'read_only': True,
        'destructive': False,
    },
    'create_transcrippet': {
        'display_name': 'Transcrippet Creator',
        'description': 'Create a new Transcrippet™ from a specific segment of an event transcript. Requires precise positioning information to capture the exact text segment.',
        'input_schema': CreateTranscrippetArgs.model_json_schema(),
        'function': create_transcrippet,
        'args_model': CreateTranscrippetArgs,
        'category': 'transcrippets',
        'read_only': False,
        'destructive': False,
    },
    'delete_transcrippet': {
        'display_name': 'Transcrippet Deleter',
        'description': 'Delete a Transcrippet™ permanently by its ID. This operation cannot be undone.',
        'input_schema': DeleteTranscrippetArgs.model_json_schema(),
        'function': delete_transcrippet,
        'args_model': DeleteTranscrippetArgs,
        'category': 'transcrippets',
        'read_only': False,
        'destructive': True,
    },
}

# Helper function to get tools by category
def get_tools_by_category(category: str) -> dict:
    """Get all tools in a specific category."""
    return {name: tool for name, tool in TOOL_REGISTRY.items() if tool['category'] == category}

# Helper function to get all categories
def get_categories() -> list:
    """Get all unique tool categories."""
    return list(set(tool['category'] for tool in TOOL_REGISTRY.values()))

# Helper function to get all tool names
def get_all_tool_names() -> list:
    """Get all available tool names."""
    return list(TOOL_REGISTRY.keys())

# Helper function to validate tool names
def validate_tool_names(tool_names: list) -> tuple[list, list]:
    """Validate a list of tool names.

    Returns:
        tuple: (valid_names, invalid_names)
    """
    available_tools = set(TOOL_REGISTRY.keys())
    provided_tools = set(tool_names)

    valid_names = list(provided_tools & available_tools)
    invalid_names = list(provided_tools - available_tools)

    return valid_names, invalid_names

# Helper function to suggest similar tool names
def suggest_similar_tools(invalid_name: str, max_suggestions: int = 3) -> list:
    """Suggest similar tool names for a given invalid name."""
    from difflib import get_close_matches
    available_tools = list(TOOL_REGISTRY.keys())
    return get_close_matches(invalid_name, available_tools, n=max_suggestions, cutoff=0.6)

# Helper function to get tools by read-only status
def get_tools_by_read_only(read_only: bool = True) -> dict:
    """Get all tools filtered by read-only status."""
    return {name: tool for name, tool in TOOL_REGISTRY.items() if tool['read_only'] == read_only}

# Helper function to get destructive tools
def get_destructive_tools() -> dict:
    """Get all tools that are marked as destructive."""
    return {name: tool for name, tool in TOOL_REGISTRY.items() if tool['destructive'] == True}