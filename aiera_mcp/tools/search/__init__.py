#!/usr/bin/env python3

"""Search domain for Aiera MCP."""

from .tools import (
    search_transcripts,
    search_filings,
    search_research,
    search_sales_commentary,
    search_company_docs,
    search_thirdbridge,
)
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchSalesCommentaryArgs,
    SearchCompanyDocsArgs,
    SearchThirdbridgeArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResearchResponse,
    SearchSalesCommentaryResponse,
    SearchCompanyDocsResponse,
    SearchThirdbridgeResponse,
)

__all__ = [
    # Tools
    "search_transcripts",
    "search_filings",
    "search_research",
    "search_sales_commentary",
    "search_company_docs",
    "search_thirdbridge",
    # Parameter models
    "SearchTranscriptsArgs",
    "SearchFilingsArgs",
    "SearchResearchArgs",
    "SearchSalesCommentaryArgs",
    "SearchCompanyDocsArgs",
    "SearchThirdbridgeArgs",
    # Response models
    "SearchTranscriptsResponse",
    "SearchFilingsResponse",
    "SearchResearchResponse",
    "SearchSalesCommentaryResponse",
    "SearchCompanyDocsResponse",
    "SearchThirdbridgeResponse",
]
