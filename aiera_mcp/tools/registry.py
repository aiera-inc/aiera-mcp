#!/usr/bin/env python3

"""Tool registry for Aiera MCP server."""


# Import all tool functions from domain modules
from .events import find_events, find_conferences, get_event, get_upcoming_events
from .filings import find_filings, get_filing
from .equities import (
    find_equities,
    get_equity_summaries,
    get_available_watchlists,
    get_available_indexes,
    get_sectors_and_subsectors,
    get_index_constituents,
    get_watchlist_constituents,
)
from .company_docs import (
    find_company_docs,
    get_company_doc,
    get_company_doc_categories,
    get_company_doc_keywords,
)
from .third_bridge import find_third_bridge_events, get_third_bridge_event
from .transcrippets import find_transcrippets, create_transcrippet, delete_transcrippet
from .search import search_transcripts, search_filings

# Import all parameter model classes from domain modules
from .events import (
    FindEventsArgs,
    FindConferencesArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
)
from .filings import FindFilingsArgs, GetFilingArgs
from .equities import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    GetAvailableWatchlistsArgs,
    GetAvailableIndexesArgs,
    GetSectorsAndSubsectorsArgs,
)
from .company_docs import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    GetCompanyDocCategoriesArgs,
    GetCompanyDocKeywordsArgs,
)
from .third_bridge import FindThirdBridgeEventsArgs, GetThirdBridgeEventArgs
from .transcrippets import (
    FindTranscrippetsArgs,
    CreateTranscrippetArgs,
    DeleteTranscrippetArgs,
)
from .search import SearchTranscriptsArgs, SearchFilingsArgs

TOOL_REGISTRY = {
    "find_events": {
        "display_name": "Find Events",
        "input_schema": FindEventsArgs.model_json_schema(),
        "function": find_events,
        "args_model": FindEventsArgs,
        "category": "events",
        "read_only": True,
        "destructive": False,
    },
    "find_conferences": {
        "display_name": "Find Conferences",
        "input_schema": FindConferencesArgs.model_json_schema(),
        "function": find_conferences,
        "args_model": FindConferencesArgs,
        "category": "events",
        "read_only": True,
        "destructive": False,
    },
    "get_event": {
        "display_name": "Get Event",
        "input_schema": GetEventArgs.model_json_schema(),
        "function": get_event,
        "args_model": GetEventArgs,
        "category": "events",
        "read_only": True,
        "destructive": False,
    },
    "get_upcoming_events": {
        "display_name": "Get Upcoming Events",
        "input_schema": GetUpcomingEventsArgs.model_json_schema(),
        "function": get_upcoming_events,
        "args_model": GetUpcomingEventsArgs,
        "category": "events",
        "read_only": True,
        "destructive": False,
    },
    "find_filings": {
        "display_name": "Find Filings",
        "input_schema": FindFilingsArgs.model_json_schema(),
        "function": find_filings,
        "args_model": FindFilingsArgs,
        "category": "filings",
        "read_only": True,
        "destructive": False,
    },
    "get_filing": {
        "display_name": "Get Filing",
        "input_schema": GetFilingArgs.model_json_schema(),
        "function": get_filing,
        "args_model": GetFilingArgs,
        "category": "filings",
        "read_only": True,
        "destructive": False,
    },
    "find_equities": {
        "display_name": "Find Equities",
        "input_schema": FindEquitiesArgs.model_json_schema(),
        "function": find_equities,
        "args_model": FindEquitiesArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_equity_summaries": {
        "display_name": "Get Equity Summaries",
        "input_schema": GetEquitySummariesArgs.model_json_schema(),
        "function": get_equity_summaries,
        "args_model": GetEquitySummariesArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_available_watchlists": {
        "display_name": "Get Available Watchlists",
        "input_schema": GetAvailableWatchlistsArgs.model_json_schema(),
        "function": get_available_watchlists,
        "args_model": GetAvailableWatchlistsArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_available_indexes": {
        "display_name": "Get Available Indexes",
        "input_schema": GetAvailableIndexesArgs.model_json_schema(),
        "function": get_available_indexes,
        "args_model": GetAvailableIndexesArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_sectors_and_subsectors": {
        "display_name": "Get Sectors and Subsectors",
        "input_schema": GetSectorsAndSubsectorsArgs.model_json_schema(),
        "function": get_sectors_and_subsectors,
        "args_model": GetSectorsAndSubsectorsArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_index_constituents": {
        "display_name": "Get Index Constituents",
        "input_schema": GetIndexConstituentsArgs.model_json_schema(),
        "function": get_index_constituents,
        "args_model": GetIndexConstituentsArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_watchlist_constituents": {
        "display_name": "Get Watchlist Constituents",
        "input_schema": GetWatchlistConstituentsArgs.model_json_schema(),
        "function": get_watchlist_constituents,
        "args_model": GetWatchlistConstituentsArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "find_company_docs": {
        "display_name": "Find Company Documents",
        "input_schema": FindCompanyDocsArgs.model_json_schema(),
        "function": find_company_docs,
        "args_model": FindCompanyDocsArgs,
        "category": "company_docs",
        "read_only": True,
        "destructive": False,
    },
    "get_company_doc": {
        "display_name": "Get Company Document",
        "input_schema": GetCompanyDocArgs.model_json_schema(),
        "function": get_company_doc,
        "args_model": GetCompanyDocArgs,
        "category": "company_docs",
        "read_only": True,
        "destructive": False,
    },
    "get_company_doc_categories": {
        "display_name": "Get Company Document Categories",
        "input_schema": GetCompanyDocCategoriesArgs.model_json_schema(),
        "function": get_company_doc_categories,
        "args_model": GetCompanyDocCategoriesArgs,
        "category": "company_docs",
        "read_only": True,
        "destructive": False,
    },
    "get_company_doc_keywords": {
        "display_name": "Get Company Document Keywords",
        "input_schema": GetCompanyDocKeywordsArgs.model_json_schema(),
        "function": get_company_doc_keywords,
        "args_model": GetCompanyDocKeywordsArgs,
        "category": "company_docs",
        "read_only": True,
        "destructive": False,
    },
    "find_third_bridge_events": {
        "display_name": "Find Third Bridge Events",
        "input_schema": FindThirdBridgeEventsArgs.model_json_schema(),
        "function": find_third_bridge_events,
        "args_model": FindThirdBridgeEventsArgs,
        "category": "third_bridge",
        "read_only": True,
        "destructive": False,
    },
    "get_third_bridge_event": {
        "display_name": "Get Third Bridge Event",
        "input_schema": GetThirdBridgeEventArgs.model_json_schema(),
        "function": get_third_bridge_event,
        "args_model": GetThirdBridgeEventArgs,
        "category": "third_bridge",
        "read_only": True,
        "destructive": False,
    },
    "find_transcrippets": {
        "display_name": "Find Transcrippets",
        "input_schema": FindTranscrippetsArgs.model_json_schema(),
        "function": find_transcrippets,
        "args_model": FindTranscrippetsArgs,
        "category": "transcrippets",
        "read_only": True,
        "destructive": False,
    },
    "create_transcrippet": {
        "display_name": "Create Transcrippet",
        "input_schema": CreateTranscrippetArgs.model_json_schema(),
        "function": create_transcrippet,
        "args_model": CreateTranscrippetArgs,
        "category": "transcrippets",
        "read_only": False,
        "destructive": False,
    },
    "delete_transcrippet": {
        "display_name": "Delete Transcrippet",
        "input_schema": DeleteTranscrippetArgs.model_json_schema(),
        "function": delete_transcrippet,
        "args_model": DeleteTranscrippetArgs,
        "category": "transcrippets",
        "read_only": False,
        "destructive": True,
    },
    "search_transcripts": {
        "display_name": "Search Transcripts",
        "input_schema": SearchTranscriptsArgs.model_json_schema(),
        "function": search_transcripts,
        "args_model": SearchTranscriptsArgs,
        "category": "search",
        "read_only": True,
        "destructive": False,
    },
    "search_filings": {
        "display_name": "Search Filings",
        "input_schema": SearchFilingsArgs.model_json_schema(),
        "function": search_filings,
        "args_model": SearchFilingsArgs,
        "category": "search",
        "read_only": True,
        "destructive": False,
    },
}


# Automatically populate descriptions from Args model docstrings
for tool_name, tool_config in TOOL_REGISTRY.items():
    args_model = tool_config.get("args_model")
    if args_model and args_model.__doc__:
        # Extract and clean the docstring
        description = args_model.__doc__.strip()
        tool_config["description"] = description


# Helper function to get tools by category
def get_tools_by_category(category: str) -> dict:
    """Get all tools in a specific category."""
    return {
        name: tool
        for name, tool in TOOL_REGISTRY.items()
        if tool["category"] == category
    }


# Helper function to get all categories
def get_categories() -> list:
    """Get all unique tool categories."""
    return list(set(tool["category"] for tool in TOOL_REGISTRY.values()))


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
    return get_close_matches(
        invalid_name, available_tools, n=max_suggestions, cutoff=0.6
    )


# Helper function to get tools by read-only status
def get_tools_by_read_only(read_only: bool = True) -> dict:
    """Get all tools filtered by read-only status."""
    return {
        name: tool
        for name, tool in TOOL_REGISTRY.items()
        if tool["read_only"] == read_only
    }


# Helper function to get destructive tools
def get_destructive_tools() -> dict:
    """Get all tools that are marked as destructive."""
    return {
        name: tool
        for name, tool in TOOL_REGISTRY.items()
        if tool["destructive"] == True
    }
