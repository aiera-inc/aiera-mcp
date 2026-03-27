#!/usr/bin/env python3

"""SEC filing tools for Aiera MCP."""

import json
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

# Maximum response size in bytes (conservative limit under payload cap)
MAX_RESPONSE_SIZE = 4 * 1024 * 1024  # 4MB


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

    # Check if the requested filing was found
    response_data = response.response or {}
    data = response_data.get("data", []) if isinstance(response_data, dict) else []
    if not data:
        response.error = f"Filing not found for filing_id '{args.filing_id}'. The filing may not exist or the ID may be invalid. Use find_filings or search_filings to discover valid filing IDs."

    # Truncate oversized content to prevent 502 errors from payload limits
    if data:
        try:
            response_size = len(json.dumps(raw_response))
            if response_size > MAX_RESPONSE_SIZE:
                for filing in data:
                    content = filing.get("content_raw", "") or ""
                    if len(content) > MAX_RESPONSE_SIZE:
                        truncated = content[:MAX_RESPONSE_SIZE]

                        # Trim to last complete paragraph
                        last_break = truncated.rfind("\n\n")
                        if last_break > MAX_RESPONSE_SIZE // 2:
                            truncated = truncated[:last_break]

                        filing["content_raw"] = (
                            truncated
                            + "\n\n[Content truncated due to size. "
                            + "Use search_filings for targeted content extraction.]"
                        )

                        logger.info(
                            f"get_filing: truncated content_raw from {len(content)} "
                            f"to {len(filing['content_raw'])} chars for filing_id {args.filing_id}"
                        )

        except Exception as e:
            logger.warning(f"get_filing: error during content truncation: {e}")

    if args.exclude_instructions:
        response.instructions = []
    return response
