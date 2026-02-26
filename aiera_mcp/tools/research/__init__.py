#!/usr/bin/env python3

"""Research domain for Aiera MCP."""

from .tools import (
    find_research,
    get_research,
    get_research_providers,
    find_research_authors,
    find_research_asset_classes,
    find_research_asset_types,
)
from .models import (
    FindResearchArgs,
    GetResearchArgs,
    GetResearchProvidersArgs,
    FindResearchAuthorsArgs,
    FindResearchAssetClassesArgs,
    FindResearchAssetTypesArgs,
    FindResearchResponse,
    GetResearchResponse,
    GetResearchProvidersResponse,
    FindResearchAuthorsResponse,
    FindResearchAssetClassesResponse,
    FindResearchAssetTypesResponse,
)

__all__ = [
    # Tools
    "find_research",
    "get_research",
    "get_research_providers",
    "find_research_authors",
    "find_research_asset_classes",
    "find_research_asset_types",
    # Parameter models
    "FindResearchArgs",
    "GetResearchArgs",
    "GetResearchProvidersArgs",
    "FindResearchAuthorsArgs",
    "FindResearchAssetClassesArgs",
    "FindResearchAssetTypesArgs",
    # Response models
    "FindResearchResponse",
    "GetResearchResponse",
    "GetResearchProvidersResponse",
    "FindResearchAuthorsResponse",
    "FindResearchAssetClassesResponse",
    "FindResearchAssetTypesResponse",
]
