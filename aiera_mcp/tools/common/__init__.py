#!/usr/bin/env python3

"""Common base classes and utilities for Aiera MCP tools."""

from .models import (
    # Base classes
    BaseAieraArgs,
    BaseAieraResponse,
    PaginatedResponse,
    # Common models
    CitationInfo,
    # Response compaction
    CompactArgsMixin,
    CompactedResponseBody,
    is_compacted_response,
    # Common argument types
    EmptyArgs,
    SearchArgs,
    # Grammar template
    GetGrammarTemplateArgs,
    GetGrammarTemplateResponse,
    # Creation templates
    GetCreationTemplatesArgs,
    GetCreationTemplatesResponse,
    # Core instructions
    GetCoreInstructionsArgs,
    GetCoreInstructionsResponse,
    # Available tools
    AvailableToolsArgs,
    AvailableToolsResponse,
)
from .tools import (
    get_grammar_template,
    get_creation_templates,
    get_core_instructions,
    available_tools,
)

__all__ = [
    "BaseAieraArgs",
    "BaseAieraResponse",
    "PaginatedResponse",
    "CitationInfo",
    "CompactArgsMixin",
    "CompactedResponseBody",
    "is_compacted_response",
    "EmptyArgs",
    "SearchArgs",
    "GetGrammarTemplateArgs",
    "GetGrammarTemplateResponse",
    "get_grammar_template",
    "GetCreationTemplatesArgs",
    "GetCreationTemplatesResponse",
    "get_creation_templates",
    "GetCoreInstructionsArgs",
    "GetCoreInstructionsResponse",
    "get_core_instructions",
    "AvailableToolsArgs",
    "AvailableToolsResponse",
    "available_tools",
]
