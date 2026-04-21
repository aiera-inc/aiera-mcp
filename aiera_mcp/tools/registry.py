#!/usr/bin/env python3

"""Tool registry for Aiera MCP server."""

import functools
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)

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
    get_financials,
    get_ratios,
    get_kpis_and_segments,
)
from .company_docs import (
    find_company_docs,
    get_company_doc,
    get_company_doc_categories,
    get_company_doc_keywords,
)
from .third_bridge import find_third_bridge_events, get_third_bridge_event
from .research import (
    find_research,
    get_research,
    get_research_providers,
    get_research_authors,
    get_research_asset_classes,
    get_research_asset_types,
    get_research_subjects,
    get_research_product_focuses,
    get_research_region_types,
    get_research_country_codes,
)
from .web import trusted_web_search
from .common import get_grammar_template, get_core_instructions, available_tools
from .search import (
    search_transcripts,
    search_filings,
    search_research,
    search_company_docs,
    search_thirdbridge,
)

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
    GetFinancialsArgs,
    GetRatiosArgs,
    GetKpisAndSegmentsArgs,
)
from .company_docs import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    GetCompanyDocCategoriesArgs,
    GetCompanyDocKeywordsArgs,
)
from .third_bridge import FindThirdBridgeEventsArgs, GetThirdBridgeEventArgs
from .research import (
    FindResearchArgs,
    GetResearchArgs,
    GetResearchProvidersArgs,
    GetResearchAuthorsArgs,
    GetResearchAssetClassesArgs,
    GetResearchAssetTypesArgs,
    GetResearchSubjectsArgs,
    GetResearchProductFocusesArgs,
    GetResearchRegionTypesArgs,
    GetResearchCountryCodesArgs,
)
from .web import TrustedWebSearchArgs
from .common import GetGrammarTemplateArgs, GetCoreInstructionsArgs, AvailableToolsArgs
from .search import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchCompanyDocsArgs,
    SearchThirdbridgeArgs,
)

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
    "get_financials": {
        "display_name": "Get Financials",
        "input_schema": GetFinancialsArgs.model_json_schema(),
        "function": get_financials,
        "args_model": GetFinancialsArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_ratios": {
        "display_name": "Get Ratios",
        "input_schema": GetRatiosArgs.model_json_schema(),
        "function": get_ratios,
        "args_model": GetRatiosArgs,
        "category": "equities",
        "read_only": True,
        "destructive": False,
    },
    "get_kpis_and_segments": {
        "display_name": "Get KPIs and Segments",
        "input_schema": GetKpisAndSegmentsArgs.model_json_schema(),
        "function": get_kpis_and_segments,
        "args_model": GetKpisAndSegmentsArgs,
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
    "find_research": {
        "display_name": "Find Research",
        "input_schema": FindResearchArgs.model_json_schema(),
        "function": find_research,
        "args_model": FindResearchArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research": {
        "display_name": "Get Research",
        "input_schema": GetResearchArgs.model_json_schema(),
        "function": get_research,
        "args_model": GetResearchArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_providers": {
        "display_name": "Get Research Providers",
        "input_schema": GetResearchProvidersArgs.model_json_schema(),
        "function": get_research_providers,
        "args_model": GetResearchProvidersArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_authors": {
        "display_name": "Get Research Authors",
        "input_schema": GetResearchAuthorsArgs.model_json_schema(),
        "function": get_research_authors,
        "args_model": GetResearchAuthorsArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_asset_classes": {
        "display_name": "Get Research Asset Classes",
        "input_schema": GetResearchAssetClassesArgs.model_json_schema(),
        "function": get_research_asset_classes,
        "args_model": GetResearchAssetClassesArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_asset_types": {
        "display_name": "Get Research Asset Types",
        "input_schema": GetResearchAssetTypesArgs.model_json_schema(),
        "function": get_research_asset_types,
        "args_model": GetResearchAssetTypesArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_subjects": {
        "display_name": "Get Research Subjects",
        "input_schema": GetResearchSubjectsArgs.model_json_schema(),
        "function": get_research_subjects,
        "args_model": GetResearchSubjectsArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_product_focuses": {
        "display_name": "Get Research Product Focuses",
        "input_schema": GetResearchProductFocusesArgs.model_json_schema(),
        "function": get_research_product_focuses,
        "args_model": GetResearchProductFocusesArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_region_types": {
        "display_name": "Get Research Region Types",
        "input_schema": GetResearchRegionTypesArgs.model_json_schema(),
        "function": get_research_region_types,
        "args_model": GetResearchRegionTypesArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
    },
    "get_research_country_codes": {
        "display_name": "Get Research Country Codes",
        "input_schema": GetResearchCountryCodesArgs.model_json_schema(),
        "function": get_research_country_codes,
        "args_model": GetResearchCountryCodesArgs,
        "category": "research",
        "read_only": True,
        "destructive": False,
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
    "search_research": {
        "display_name": "Search Research",
        "input_schema": SearchResearchArgs.model_json_schema(),
        "function": search_research,
        "args_model": SearchResearchArgs,
        "category": "search",
        "read_only": True,
        "destructive": False,
    },
    "search_company_docs": {
        "display_name": "Search Company Documents",
        "input_schema": SearchCompanyDocsArgs.model_json_schema(),
        "function": search_company_docs,
        "args_model": SearchCompanyDocsArgs,
        "category": "search",
        "read_only": True,
        "destructive": False,
    },
    "search_thirdbridge": {
        "display_name": "Search Third Bridge",
        "input_schema": SearchThirdbridgeArgs.model_json_schema(),
        "function": search_thirdbridge,
        "args_model": SearchThirdbridgeArgs,
        "category": "search",
        "read_only": True,
        "destructive": False,
    },
    "trusted_web_search": {
        "display_name": "Trusted Web Search",
        "input_schema": TrustedWebSearchArgs.model_json_schema(),
        "function": trusted_web_search,
        "args_model": TrustedWebSearchArgs,
        "category": "web",
        "read_only": True,
        "destructive": False,
    },
    "get_grammar_template": {
        "display_name": "Get Grammar Template",
        "input_schema": GetGrammarTemplateArgs.model_json_schema(),
        "function": get_grammar_template,
        "args_model": GetGrammarTemplateArgs,
        "category": "common",
        "read_only": True,
        "destructive": False,
    },
    "get_core_instructions": {
        "display_name": "Get Core Instructions",
        "input_schema": GetCoreInstructionsArgs.model_json_schema(),
        "function": get_core_instructions,
        "args_model": GetCoreInstructionsArgs,
        "category": "common",
        "read_only": True,
        "destructive": False,
    },
    "available_tools": {
        "display_name": "Available Tools",
        "input_schema": AvailableToolsArgs.model_json_schema(),
        "function": available_tools,
        "args_model": AvailableToolsArgs,
        "category": "common",
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


def _wrap_with_logging(func: Any, tool_name: str) -> Any:
    """Wrap a tool function to fire-and-forget a log after each invocation."""
    from .base import send_tool_log

    @functools.wraps(func)
    async def wrapper(args: Any) -> Any:
        is_error = False
        result = None
        start = time.perf_counter()
        try:
            result = await func(args)
            return result
        except Exception:
            is_error = True
            raise
        finally:
            duration_ms = int((time.perf_counter() - start) * 1000)
            try:
                params = args.model_dump() if hasattr(args, "model_dump") else None
                resp = None
                if result is not None:
                    resp = (
                        result.model_dump() if hasattr(result, "model_dump") else result
                    )
                send_tool_log(
                    tool_name, params, resp, is_error=is_error, duration_ms=duration_ms
                )
            except Exception:
                logger.debug(
                    "Failed to schedule MCP tool log for %s", tool_name, exc_info=True
                )

    return wrapper


# Wrap all tool functions with logging
for _tool_name, _tool_config in TOOL_REGISTRY.items():
    _tool_config["function"] = _wrap_with_logging(_tool_config["function"], _tool_name)


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
