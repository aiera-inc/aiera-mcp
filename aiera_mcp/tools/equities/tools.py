#!/usr/bin/env python3

"""Equity and company metadata tools for Aiera MCP."""

import logging
from typing import Any, Dict
from datetime import datetime

from .models import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    EmptyArgs,
    SearchArgs,
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
    WatchlistItem
)
from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from ..common.models import CitationInfo

# Setup logging
logger = logging.getLogger(__name__)


async def find_equities(args: FindEquitiesArgs) -> FindEquitiesResponse:
    """Retrieve equities, filtered by various identifiers, such as ticker, ISIN, or RIC; or by search."""
    logger.info("tool called: find_equities")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)
    params["include_company_metadata"] = "true"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-equities",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        equities_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        equities_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(equities_data))

    equities = []
    citations = []

    for equity_data in equities_data:
        equity_item = EquityItem(
            equity_id=str(equity_data.get("id", "")),
            company_name=equity_data.get("company_name", ""),
            ticker=equity_data.get("ticker", ""),
            bloomberg_ticker=equity_data.get("bloomberg_ticker", ""),
            exchange=equity_data.get("exchange"),
            sector=equity_data.get("sector"),
            subsector=equity_data.get("subsector"),
            country=equity_data.get("country"),
            market_cap=equity_data.get("market_cap")
        )
        equities.append(equity_item)

        # Add citation if we have useful information
        if equity_data.get("company_name"):
            citations.append(CitationInfo(
                title=f"{equity_data.get('company_name')} ({equity_data.get('ticker', '')})",
                url=None,  # Equity data typically doesn't have URLs
                source="Aiera Equity Database"
            ))

    return FindEquitiesResponse(
        equities=equities,
        total=total_count,
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_sectors_and_subsectors(args: SearchArgs) -> GetSectorsSubsectorsResponse:
    """Retrieve a list of all sectors and subsectors."""
    logger.info("tool called: get_sectors_and_subsectors")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-sectors-and-subsectors",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        sectors_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        sectors_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(sectors_data))

    sectors = []
    for sector_data in sectors_data:
        sector_item = SectorSubsector(
            sector_id=str(sector_data.get("sector_id", "")),
            sector_name=sector_data.get("sector_name", ""),
            subsector_id=str(sector_data.get("subsector_id", "")) if sector_data.get("subsector_id") else None,
            subsector_name=sector_data.get("subsector_name")
        )
        sectors.append(sector_item)

    return GetSectorsSubsectorsResponse(
        sectors=sectors,
        instructions=raw_response.get("instructions", []),
        citation_information=[CitationInfo(title="GICS Sector Classification", source="Aiera")]
    )


async def get_equity_summaries(args: GetEquitySummariesArgs) -> GetEquitySummariesResponse:
    """Retrieve detailed summary information about one or more equities, filtered by ticker(s)."""
    logger.info("tool called: get_equity_summaries")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)
    params["lookback"] = "90"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/equity-summaries",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        summaries_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        summaries_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(summaries_data))

    summaries = []
    citations = []

    for summary_data in summaries_data:
        # Build equity summary
        equity_summary = None
        if (
            summary_data.get("description") or
            summary_data.get("recent_events") or
            summary_data.get("key_metrics") or
            summary_data.get("analyst_coverage")
        ):
            equity_summary = EquitySummary(
                description=summary_data.get("description"),
                recent_events=summary_data.get("recent_events", []),
                key_metrics=summary_data.get("key_metrics", {}),
                analyst_coverage=summary_data.get("analyst_coverage", {})
            )

        equity_details = EquityDetails(
            equity_id=str(summary_data.get("id", "")),
            company_name=summary_data.get("company_name", ""),
            ticker=summary_data.get("ticker", ""),
            bloomberg_ticker=summary_data.get("bloomberg_ticker", ""),
            exchange=summary_data.get("exchange"),
            sector=summary_data.get("sector"),
            subsector=summary_data.get("subsector"),
            country=summary_data.get("country"),
            market_cap=summary_data.get("market_cap"),
            summary=equity_summary,
            identifiers=summary_data.get("identifiers", {})
        )
        summaries.append(equity_details)

        # Add citation
        if summary_data.get("company_name"):
            citations.append(CitationInfo(
                title=f"{summary_data.get('company_name')} Company Summary",
                source="Aiera"
            ))

    return GetEquitySummariesResponse(
        summaries=summaries,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def get_available_indexes(args: EmptyArgs) -> GetAvailableIndexesResponse:
    """Retrieve the list of available indexes."""
    logger.info("tool called: get_available_indexes")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-indexes",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        indexes_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        indexes_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(indexes_data))

    indexes = []
    for index_data in indexes_data:
        index_item = IndexItem(
            index_id=str(index_data.get("id", index_data.get("symbol", ""))),
            index_name=index_data.get("name", ""),
            symbol=index_data.get("symbol", "")
        )
        indexes.append(index_item)

    return GetAvailableIndexesResponse(
        indexes=indexes,
        instructions=raw_response.get("instructions", []),
        citation_information=[CitationInfo(title="Available Market Indexes", source="Aiera")]
    )


async def get_index_constituents(args: GetIndexConstituentsArgs) -> GetIndexConstituentsResponse:
    """Retrieve the list of all equities within an index."""
    logger.info("tool called: get_index_constituents")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/index-constituents/{args.index}",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        constituents_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        constituents_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(constituents_data))

    constituents = []
    citations = []

    for constituent_data in constituents_data:
        equity_item = EquityItem(
            equity_id=str(constituent_data.get("id", "")),
            company_name=constituent_data.get("company_name", ""),
            ticker=constituent_data.get("ticker", ""),
            bloomberg_ticker=constituent_data.get("bloomberg_ticker", ""),
            exchange=constituent_data.get("exchange"),
            sector=constituent_data.get("sector"),
            subsector=constituent_data.get("subsector"),
            country=constituent_data.get("country"),
            market_cap=constituent_data.get("market_cap")
        )
        constituents.append(equity_item)

    return GetIndexConstituentsResponse(
        index_name=args.index,
        constituents=constituents,
        total=total_count,
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=[CitationInfo(title=f"{args.index} Index Constituents", source="Aiera")]
    )


async def get_available_watchlists(args: EmptyArgs) -> GetAvailableWatchlistsResponse:
    """Retrieve the list of available watchlists."""
    logger.info("tool called: get_available_watchlists")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-watchlists",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        watchlists_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        watchlists_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(watchlists_data))

    watchlists = []
    for watchlist_data in watchlists_data:
        watchlist_item = WatchlistItem(
            watchlist_id=str(watchlist_data.get("id", "")),
            watchlist_name=watchlist_data.get("name", ""),
            description=watchlist_data.get("description")
        )
        watchlists.append(watchlist_item)

    return GetAvailableWatchlistsResponse(
        watchlists=watchlists,
        instructions=raw_response.get("instructions", []),
        citation_information=[CitationInfo(title="Available Watchlists", source="Aiera")]
    )


async def get_watchlist_constituents(args: GetWatchlistConstituentsArgs) -> GetWatchlistConstituentsResponse:
    """Retrieve the list of all equities within a watchlist."""
    logger.info("tool called: get_watchlist_constituents")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/watchlist-constituents/{args.watchlist_id}",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        constituents_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        constituents_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(constituents_data))
    metadata = api_data.get("metadata", {})

    constituents = []
    for constituent_data in constituents_data:
        equity_item = EquityItem(
            equity_id=str(constituent_data.get("id", "")),
            company_name=constituent_data.get("company_name", ""),
            ticker=constituent_data.get("ticker", ""),
            bloomberg_ticker=constituent_data.get("bloomberg_ticker", ""),
            exchange=constituent_data.get("exchange"),
            sector=constituent_data.get("sector"),
            subsector=constituent_data.get("subsector"),
            country=constituent_data.get("country"),
            market_cap=constituent_data.get("market_cap")
        )
        constituents.append(equity_item)

    return GetWatchlistConstituentsResponse(
        watchlist_name=metadata.get("watchlist_name", f"Watchlist {args.watchlist_id}"),
        constituents=constituents,
        total=total_count,
        page=args.page,
        page_size=args.page_size,
        instructions=raw_response.get("instructions", []),
        citation_information=[CitationInfo(title=f"Watchlist {args.watchlist_id} Constituents", source="Aiera")]
    )


# Legacy registration functions removed - all tools now registered via registry
