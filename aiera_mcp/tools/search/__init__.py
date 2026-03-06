#!/usr/bin/env python3

"""Search domain for Aiera MCP."""

from .tools import (
    search_transcripts,
    search_filings,
    search_research,
    search_company_docs,
    search_thirdbridge,
)
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchCompanyDocsArgs,
    SearchThirdbridgeArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResearchResponse,
    SearchCompanyDocsResponse,
    SearchThirdbridgeResponse,
)

__all__ = [
    # Tools
    "search_transcripts",
    "search_filings",
    "search_research",
    "search_company_docs",
    "search_thirdbridge",
    # Parameter models
    "SearchTranscriptsArgs",
    "SearchFilingsArgs",
    "SearchResearchArgs",
    "SearchCompanyDocsArgs",
    "SearchThirdbridgeArgs",
    # Response models
    "SearchTranscriptsResponse",
    "SearchFilingsResponse",
    "SearchResearchResponse",
    "SearchCompanyDocsResponse",
    "SearchThirdbridgeResponse",
]
