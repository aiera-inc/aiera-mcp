#!/usr/bin/env python3

"""Common base classes and utilities for Aiera MCP tools."""

from .models import (
    # Base classes
    BaseAieraArgs,
    BaseAieraResponse,
    PaginatedResponse,
    # Common models
    CitationInfo,
    # Common argument types
    EmptyArgs,
    SearchArgs,
    # Grammar template
    GetGrammarTemplateArgs,
    GetGrammarTemplateResponse,
    # Core instructions
    GetCoreInstructionsArgs,
    GetCoreInstructionsResponse,
)
from .tools import get_grammar_template, get_core_instructions

__all__ = [
    "BaseAieraArgs",
    "BaseAieraResponse",
    "PaginatedResponse",
    "CitationInfo",
    "EmptyArgs",
    "SearchArgs",
    "GetGrammarTemplateArgs",
    "GetGrammarTemplateResponse",
    "get_grammar_template",
    "GetCoreInstructionsArgs",
    "GetCoreInstructionsResponse",
    "get_core_instructions",
]
