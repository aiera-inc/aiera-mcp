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

    # Return the structured response that matches the actual API format
    # Parse individual equities to match new model structure
    if "response" in raw_response and "data" in raw_response["response"]:
        equities_data = []
        for equity_data in raw_response["response"]["data"]:
            # Parse datetime fields
            created = None
            modified = None
            if equity_data.get("created"):
                try:
                    created = datetime.fromisoformat(equity_data["created"].replace("Z", "+00:00"))
                except:
                    pass
            if equity_data.get("modified"):
                try:
                    modified = datetime.fromisoformat(equity_data["modified"].replace("Z", "+00:00"))
                except:
                    pass

            # Create new equity structure matching the actual response and new model
            parsed_equity = {
                "equity_id": equity_data.get("equity_id"),
                "company_id": equity_data.get("company_id"),
                "company_name": equity_data.get("name"),
                "name": equity_data.get("name"),
                "ticker": equity_data.get("bloomberg_ticker", "").split(":")[0] if equity_data.get("bloomberg_ticker") else None,
                "bloomberg_ticker": equity_data.get("bloomberg_ticker", ""),
                "exchange": equity_data.get("exchange"),
                "sector": equity_data.get("sector"),
                "subsector": equity_data.get("subsector"),
                "sector_id": equity_data.get("sector_id"),
                "subsector_id": equity_data.get("subsector_id"),
                "country": equity_data.get("country"),
                "market_cap": equity_data.get("market_cap"),
                "primary_equity": equity_data.get("primary_equity"),
                "created": created,
                "modified": modified
            }
            equities_data.append(parsed_equity)

        raw_response["response"]["data"] = equities_data

    # Handle malformed responses gracefully
    try:
        return FindEquitiesResponse.model_validate(raw_response)
    except Exception as e:
        logger.warning(f"Failed to parse API response: {e}")
        # Return empty response for malformed data
        return FindEquitiesResponse(
            instructions=[],
            response={
                "data": [],
                "pagination": None
            }
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

    # Return the structured response directly - no transformation needed
    # since GetSectorsSubsectorsResponse model now matches the actual API format
    return GetSectorsSubsectorsResponse.model_validate(raw_response)


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

    # Return the structured response directly - no transformation needed
    # since GetEquitySummariesResponse model now matches the actual API format
    return GetEquitySummariesResponse.model_validate(raw_response)


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

    return GetAvailableIndexesResponse.model_validate(raw_response)


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
        # Handle equity_id - need to parse as int but handle empty strings
        equity_id = constituent_data.get("id") or constituent_data.get("equity_id")
        if isinstance(equity_id, str) and equity_id == "":
            equity_id = 0  # Default for empty string
        elif equity_id is None:
            equity_id = 0
        else:
            try:
                equity_id = int(equity_id)
            except (ValueError, TypeError):
                equity_id = 0

        equity_item = EquityItem(
            equity_id=equity_id,
            company_name=constituent_data.get("company_name", ""),
            name=constituent_data.get("name"),
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

    return GetAvailableWatchlistsResponse.model_validate(raw_response)


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
    metadata = api_data.get("metadata", {}) if "response" in raw_response else {}

    constituents = []
    for constituent_data in constituents_data:
        # Handle equity_id - need to parse as int but handle empty strings
        equity_id = constituent_data.get("id") or constituent_data.get("equity_id")
        if isinstance(equity_id, str) and equity_id == "":
            equity_id = 0  # Default for empty string
        elif equity_id is None:
            equity_id = 0
        else:
            try:
                equity_id = int(equity_id)
            except (ValueError, TypeError):
                equity_id = 0

        equity_item = EquityItem(
            equity_id=equity_id,
            company_name=constituent_data.get("company_name", ""),
            name=constituent_data.get("name"),
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
