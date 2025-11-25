#!/usr/bin/env python3

"""Equity and company metadata tools for Aiera MCP."""

import logging
from datetime import datetime

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
)
from ..base import get_http_client, make_aiera_request
from ... import get_api_key

# Setup logging
logger = logging.getLogger(__name__)


async def find_equities(args: FindEquitiesArgs) -> FindEquitiesResponse:
    """Retrieve equities, filtered by various identifiers, such as ticker, ISIN, or RIC; or by search."""
    logger.info("tool called: find_equities")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

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
                    created = datetime.fromisoformat(
                        equity_data["created"].replace("Z", "+00:00")
                    )
                except:
                    pass
            if equity_data.get("modified"):
                try:
                    modified = datetime.fromisoformat(
                        equity_data["modified"].replace("Z", "+00:00")
                    )
                except:
                    pass

            # Create new equity structure matching the actual response and new model
            parsed_equity = {
                "equity_id": equity_data.get("equity_id"),
                "company_id": equity_data.get("company_id"),
                "company_name": equity_data.get("name"),
                "name": equity_data.get("name"),
                "ticker": (
                    equity_data.get("bloomberg_ticker", "").split(":")[0]
                    if equity_data.get("bloomberg_ticker")
                    else None
                ),
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
                "modified": modified,
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
            instructions=[], response={"data": [], "pagination": None}
        )


async def get_sectors_and_subsectors(
    args: GetSectorsAndSubsectorsArgs,
) -> GetSectorsSubsectorsResponse:
    """Retrieve a list of all sectors and subsectors that can be queried."""
    logger.info("tool called: get_sectors_and_subsectors")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

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


async def get_equity_summaries(
    args: GetEquitySummariesArgs,
) -> GetEquitySummariesResponse:
    """Retrieve detailed summary information about one or more equities, filtered by ticker(s)."""
    logger.info("tool called: get_equity_summaries")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

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


async def get_available_indexes(
    args: GetAvailableIndexesArgs,
) -> GetAvailableIndexesResponse:
    """Retrieve the list of available indexes that can be queried."""
    logger.info("tool called: get_available_indexes")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-indexes",
        api_key=api_key,
        params=params,
    )

    return GetAvailableIndexesResponse.model_validate(raw_response)


async def get_index_constituents(
    args: GetIndexConstituentsArgs,
) -> GetIndexConstituentsResponse:
    """Retrieve the list of all equities within an index."""
    logger.info("tool called: get_index_constituents")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/index-constituents/{args.index}",
        api_key=api_key,
        params=params,
    )

    # Validate and return the response directly since it matches FindEquitiesResponse structure
    return GetIndexConstituentsResponse.model_validate(raw_response)


async def get_available_watchlists(
    args: GetAvailableWatchlistsArgs,
) -> GetAvailableWatchlistsResponse:
    """Retrieve the list of available watchlists that can be queried."""
    logger.info("tool called: get_available_watchlists")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/available-watchlists",
        api_key=api_key,
        params=params,
    )

    return GetAvailableWatchlistsResponse.model_validate(raw_response)


async def get_watchlist_constituents(
    args: GetWatchlistConstituentsArgs,
) -> GetWatchlistConstituentsResponse:
    """Retrieve the list of all equities within a watchlist."""
    logger.info("tool called: get_watchlist_constituents")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/watchlist-constituents/{args.watchlist_id}",
        api_key=api_key,
        params=params,
    )

    # Validate and return the response directly since it matches FindEquitiesResponse structure
    return GetWatchlistConstituentsResponse.model_validate(raw_response)


# Legacy registration functions removed - all tools now registered via registry
