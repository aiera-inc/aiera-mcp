#!/usr/bin/env python3

"""Research tools for Aiera MCP."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    FindResearchArgs,
    GetResearchArgs,
    FindResearchResponse,
    GetResearchResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_research(args: FindResearchArgs) -> FindResearchResponse:
    """Find research reports filtered by optional search terms, authors, organizations, regions, and date range."""
    logger.info("tool called: find_research")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research",
        api_key=api_key,
        params=params,
    )

    response = FindResearchResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_research(args: GetResearchArgs) -> GetResearchResponse:
    """Retrieve a research report, including summary and other metadata."""
    logger.info("tool called: get_research")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-research",
        api_key=api_key,
        params=params,
    )

    response = GetResearchResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
