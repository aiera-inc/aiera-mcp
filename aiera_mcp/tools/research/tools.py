#!/usr/bin/env python3

"""Research tools for Aiera MCP."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    FindResearchArgs,
    GetResearchArgs,
    GetResearchProvidersArgs,
    FindResearchAuthorsArgs,
    FindResearchAssetClassesArgs,
    FindResearchAssetTypesArgs,
    FindResearchSubjectsArgs,
    FindResearchProductFocusesArgs,
    FindResearchDisciplineTypesArgs,
    FindResearchRegionTypesArgs,
    FindResearchCountryCodesArgs,
    FindResearchResponse,
    GetResearchResponse,
    GetResearchProvidersResponse,
    FindResearchAuthorsResponse,
    FindResearchAssetClassesResponse,
    FindResearchAssetTypesResponse,
    FindResearchSubjectsResponse,
    FindResearchProductFocusesResponse,
    FindResearchDisciplineTypesResponse,
    FindResearchRegionTypesResponse,
    FindResearchCountryCodesResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_research(args: FindResearchArgs) -> FindResearchResponse:
    """Find research reports using the find-research endpoint with filter-based discovery.

    Supports filtering by author, provider, date range, region, and country.
    Uses cursor-based pagination via search_after.
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
        params["regions"] = ",".join(params["regions"])

    if "countries" in params:
        params["countries"] = ",".join(params["countries"])

    if "asset_classes" in params:
        params["asset_classes"] = ",".join(params["asset_classes"])

    if "asset_types" in params:
        params["asset_types"] = ",".join(params["asset_types"])

    if "subjects" in params:
        params["subjects"] = ",".join(params["subjects"])

    if "product_focuses" in params:
        params["product_focuses"] = ",".join(params["product_focuses"])

    if "discipline_types" in params:
        params["discipline_types"] = ",".join(params["discipline_types"])

    # Convert search_after array to comma-separated string for the GET endpoint
    if "search_after" in params:
        params["search_after"] = ",".join(str(v) for v in params["search_after"])

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


async def find_research_authors(
    args: FindResearchAuthorsArgs,
) -> FindResearchAuthorsResponse:
    """Search for research authors by name or provider. Returns author IDs and display names."""
    logger.info("tool called: find_research_authors")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-authors",
        api_key=api_key,
        params=params,
    )

    response = FindResearchAuthorsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def find_research_asset_classes(
    args: FindResearchAssetClassesArgs,
) -> FindResearchAssetClassesResponse:
    """Retrieve all available research asset classes."""
    logger.info("tool called: find_research_asset_classes")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-asset-classes",
        api_key=api_key,
        params=params,
    )

    response = FindResearchAssetClassesResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def find_research_asset_types(
    args: FindResearchAssetTypesArgs,
) -> FindResearchAssetTypesResponse:
    """Retrieve all available research asset types."""
    logger.info("tool called: find_research_asset_types")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-asset-types",
        api_key=api_key,
        params=params,
    )

    response = FindResearchAssetTypesResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def find_research_subjects(
    args: FindResearchSubjectsArgs,
) -> FindResearchSubjectsResponse:
    """Retrieve all available research subjects."""
    logger.info("tool called: find_research_subjects")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-subjects",
        api_key=api_key,
        params=params,
    )

    response = FindResearchSubjectsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def find_research_product_focuses(
    args: FindResearchProductFocusesArgs,
) -> FindResearchProductFocusesResponse:
    """Retrieve all available research product focus values."""
    logger.info("tool called: find_research_product_focuses")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-product-focuses",
        api_key=api_key,
        params=params,
    )

    response = FindResearchProductFocusesResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def find_research_discipline_types(
    args: FindResearchDisciplineTypesArgs,
) -> FindResearchDisciplineTypesResponse:
    """Retrieve all available research discipline types."""
    logger.info("tool called: find_research_discipline_types")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-discipline-types",
        api_key=api_key,
        params=params,
    )

    response = FindResearchDisciplineTypesResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def find_research_region_types(
    args: FindResearchRegionTypesArgs,
) -> FindResearchRegionTypesResponse:
    """Retrieve all available research region types."""
    logger.info("tool called: find_research_region_types")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-region-types",
        api_key=api_key,
        params=params,
    )

    response = FindResearchRegionTypesResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def find_research_country_codes(
    args: FindResearchCountryCodesArgs,
) -> FindResearchCountryCodesResponse:
    """Retrieve all available research country codes."""
    logger.info("tool called: find_research_country_codes")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-research-country-codes",
        api_key=api_key,
        params=params,
    )

    response = FindResearchCountryCodesResponse.model_validate(raw_response)
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
