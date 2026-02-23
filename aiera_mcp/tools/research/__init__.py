#!/usr/bin/env python3

"""Research domain for Aiera MCP."""

from .tools import (
    find_research,
    get_research,
    get_research_providers,
    find_research_authors,
)
from .models import (
    FindResearchArgs,
    GetResearchArgs,
    GetResearchProvidersArgs,
    FindResearchAuthorsArgs,
    FindResearchResponse,
    GetResearchResponse,
    GetResearchProvidersResponse,
    FindResearchAuthorsResponse,
)

__all__ = [
    # Tools
    "find_research",
    "get_research",
    "get_research_providers",
    "find_research_authors",
    # Parameter models
    "FindResearchArgs",
    "GetResearchArgs",
    "GetResearchProvidersArgs",
    "FindResearchAuthorsArgs",
    # Response models
    "FindResearchResponse",
    "GetResearchResponse",
    "GetResearchProvidersResponse",
    "FindResearchAuthorsResponse",
]
