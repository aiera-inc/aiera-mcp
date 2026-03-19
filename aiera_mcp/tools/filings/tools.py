#!/usr/bin/env python3

"""SEC filing tools for Aiera MCP."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    FindFilingsArgs,
    GetFilingArgs,
    FindFilingsResponse,
    GetFilingResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_filings(args: FindFilingsArgs) -> FindFilingsResponse:
    """Find SEC filings, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector; and (optionally) by a form number.

    RECOMMENDED: It is highly recommended to include at least one parameter that identifies equity(s), such as bloomberg_ticker, watchlist_id, index_id, sector_id, or subsector_id.
    """
    logger.info("tool called: find_filings")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )

    response = FindFilingsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_filing(args: GetFilingArgs) -> GetFilingResponse:
    """Retrieve an SEC filing, including a summary and other metadata."""
    logger.info("tool called: get_filing")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    # Handle special field mapping: filing_id -> filing_ids
    if "filing_id" in params:
        params["filing_ids"] = str(params.pop("filing_id"))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )

    response = GetFilingResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
