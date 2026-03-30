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
)
from .tools import get_grammar_template

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
]
