#!/usr/bin/env python3

"""Equities domain for Aiera MCP."""

from .tools import (
    find_equities,
    get_sectors_and_subsectors,
    get_equity_summaries,
    get_available_indexes,
    get_index_constituents,
    get_available_watchlists,
    get_watchlist_constituents,
    get_financials,
)
from .models import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    GetAvailableWatchlistsArgs,
    GetAvailableIndexesArgs,
    GetSectorsAndSubsectorsArgs,
    GetFinancialsArgs,
    FindEquitiesResponse,
    GetEquitySummariesResponse,
    GetSectorsSubsectorsResponse,
    GetAvailableIndexesResponse,
    GetIndexConstituentsResponse,
    GetAvailableWatchlistsResponse,
    GetWatchlistConstituentsResponse,
    GetFinancialsResponse,
    EquityItem,
    EquityDetails,
    EquitySummary,
    SectorSubsector,
    IndexItem,
    WatchlistItem,
)

__all__ = [
    # Tools
    "find_equities",
    "get_sectors_and_subsectors",
    "get_equity_summaries",
    "get_available_indexes",
    "get_index_constituents",
    "get_available_watchlists",
    "get_watchlist_constituents",
    "get_financials",
    # Parameter models
    "FindEquitiesArgs",
    "GetEquitySummariesArgs",
    "GetIndexConstituentsArgs",
    "GetWatchlistConstituentsArgs",
    "GetAvailableWatchlistsArgs",
    "GetAvailableIndexesArgs",
    "GetSectorsAndSubsectorsArgs",
    "GetFinancialsArgs",
    # Response models
    "FindEquitiesResponse",
    "GetEquitySummariesResponse",
    "GetSectorsSubsectorsResponse",
    "GetAvailableIndexesResponse",
    "GetIndexConstituentsResponse",
    "GetAvailableWatchlistsResponse",
    "GetWatchlistConstituentsResponse",
    "GetFinancialsResponse",
    # Data models
    "EquityItem",
    "EquityDetails",
    "EquitySummary",
    "SectorSubsector",
    "IndexItem",
    "WatchlistItem",
]
