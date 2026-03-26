#!/usr/bin/env python3

"""Research domain for Aiera MCP."""

from .tools import (
    find_research,
    get_research,
    get_research_providers,
    get_research_authors,
    get_research_asset_classes,
    get_research_asset_types,
    get_research_subjects,
    get_research_product_focuses,
    get_research_region_types,
    get_research_country_codes,
)
from .models import (
    FindResearchArgs,
    GetResearchArgs,
    GetResearchProvidersArgs,
    GetResearchAuthorsArgs,
    GetResearchAssetClassesArgs,
    GetResearchAssetTypesArgs,
    GetResearchSubjectsArgs,
    GetResearchProductFocusesArgs,
    GetResearchRegionTypesArgs,
    GetResearchCountryCodesArgs,
    FindResearchResponse,
    GetResearchResponse,
    GetResearchProvidersResponse,
    GetResearchAuthorsResponse,
    GetResearchAssetClassesResponse,
    GetResearchAssetTypesResponse,
    GetResearchSubjectsResponse,
    GetResearchProductFocusesResponse,
    GetResearchRegionTypesResponse,
    GetResearchCountryCodesResponse,
)

__all__ = [
    # Tools
    "find_research",
    "get_research",
    "get_research_providers",
    "get_research_authors",
    "get_research_asset_classes",
    "get_research_asset_types",
    "get_research_subjects",
    "get_research_product_focuses",
    "get_research_region_types",
    "get_research_country_codes",
    # Parameter models
    "FindResearchArgs",
    "GetResearchArgs",
    "GetResearchProvidersArgs",
    "GetResearchAuthorsArgs",
    "GetResearchAssetClassesArgs",
    "GetResearchAssetTypesArgs",
    "GetResearchSubjectsArgs",
    "GetResearchProductFocusesArgs",
    "GetResearchRegionTypesArgs",
    "GetResearchCountryCodesArgs",
    # Response models
    "FindResearchResponse",
    "GetResearchResponse",
    "GetResearchProvidersResponse",
    "GetResearchAuthorsResponse",
    "GetResearchAssetClassesResponse",
    "GetResearchAssetTypesResponse",
    "GetResearchSubjectsResponse",
    "GetResearchProductFocusesResponse",
    "GetResearchRegionTypesResponse",
    "GetResearchCountryCodesResponse",
]
