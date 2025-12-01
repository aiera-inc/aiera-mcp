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
)
from .models import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    GetAvailableWatchlistsArgs,
    GetAvailableIndexesArgs,
    GetSectorsAndSubsectorsArgs,
    FindEquitiesResponse,
    GetEquitySummariesResponse,
    GetSectorsSubsectorsResponse,
    GetAvailableIndexesResponse,
    GetIndexConstituentsResponse,
    GetAvailableWatchlistsResponse,
    GetWatchlistConstituentsResponse,
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
    # Parameter models
    "FindEquitiesArgs",
    "GetEquitySummariesArgs",
    "GetIndexConstituentsArgs",
    "GetWatchlistConstituentsArgs",
    "GetAvailableWatchlistsArgs",
    "GetAvailableIndexesArgs",
    "GetSectorsAndSubsectorsArgs",
    # Response models
    "FindEquitiesResponse",
    "GetEquitySummariesResponse",
    "GetSectorsSubsectorsResponse",
    "GetAvailableIndexesResponse",
    "GetIndexConstituentsResponse",
    "GetAvailableWatchlistsResponse",
    "GetWatchlistConstituentsResponse",
    # Data models
    "EquityItem",
    "EquityDetails",
    "EquitySummary",
    "SectorSubsector",
    "IndexItem",
    "WatchlistItem",
]
