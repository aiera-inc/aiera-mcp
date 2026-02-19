#!/usr/bin/env python3

"""Research tools for Aiera MCP."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    FindResearchArgs,
    GetResearchArgs,
    GetResearchProvidersArgs,
    FindResearchResponse,
    GetResearchResponse,
    GetResearchProvidersResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_research(args: FindResearchArgs) -> FindResearchResponse:
    """Find research reports using the find-research endpoint with filter-based discovery.

    Supports filtering by author, provider, ticker, date range, sector, index, watchlist, etc.
    """
    logger.info("tool called: find_research")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    # Map tool parameter names to API parameter names (comma-separated strings)
    if "author_ids" in params:
        params["author_person_ids"] = ",".join(params.pop("author_ids"))

    if "aiera_provider_ids" in params:
        params["provider_ids"] = ",".join(params.pop("aiera_provider_ids"))

    if "regions" in params:
        params["regions"] = ",".join(params.pop("regions"))

    if "countries" in params:
        params["countries"] = ",".join(params.pop("countries"))

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


async def get_research_providers(
    args: GetResearchProvidersArgs,
) -> GetResearchProvidersResponse:
    """Retrieve all available research providers."""
    logger.info("tool called: get_research_providers")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-research-providers",
        api_key=api_key,
        params=params,
    )

    response = GetResearchProvidersResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_research(args: GetResearchArgs) -> GetResearchResponse:
    """Retrieve a research report, including content, summary and other metadata."""
    logger.info("tool called: get_research")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research",
        api_key=api_key,
        params=params,
    )

    response = GetResearchResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
