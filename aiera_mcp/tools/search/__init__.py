#!/usr/bin/env python3

"""Search domain for Aiera MCP."""

from .tools import (
    search_transcripts,
    search_filings,
    search_research,
)
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResearchResponse,
)

__all__ = [
    # Tools
    "search_transcripts",
    "search_filings",
    "search_research",
    # Parameter models
    "SearchTranscriptsArgs",
    "SearchFilingsArgs",
    "SearchResearchArgs",
    # Response models
    "SearchTranscriptsResponse",
    "SearchFilingsResponse",
    "SearchResearchResponse",
]
