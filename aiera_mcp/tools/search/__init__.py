#!/usr/bin/env python3

"""Search domain for Aiera MCP."""

from .tools import (
    search_transcripts,
    search_filings,
    search_filing_chunks,
)
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchFilingChunksArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchFilingChunksResponse,
)

__all__ = [
    # Tools
    "search_transcripts",
    "search_filings",
    "search_filing_chunks",
    # Parameter models
    "SearchTranscriptsArgs",
    "SearchFilingsArgs",
    "SearchFilingChunksArgs",
    # Response models
    "SearchTranscriptsResponse",
    "SearchFilingsResponse",
    "SearchFilingChunksResponse",
]
