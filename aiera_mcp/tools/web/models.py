#!/usr/bin/env python3

"""Web domain models for Aiera MCP."""

from pydantic import Field
from typing import Optional, Any

from ..common.models import BaseAieraArgs, BaseAieraResponse


class TrustedWebSearchArgs(BaseAieraArgs):
    """Search the web using only trusted/approved domains relevant to financial professionals.

    By default, searches across trusted sources will include cnbc.com, bloomberg.com, reuters.com, wsj.com,
    apnews.com, and other Aiera-approved domains. Optionally restrict or expand to specific domains.

    USE THIS TOOL WHEN THE USER ASKS FOR:
    - "news articles" / "news" / "headlines" / "latest news" / "recent news"
    - "media coverage" / "press coverage" / "what is being reported"
    - "articles about" a company, market, or financial topic
    - Current/breaking information that would only appear in news outlets
    - External commentary or analyst quotes outside of Aiera's research/transcripts/filings corpus

    DO NOT USE for company press releases or earnings releases — those are first-party documents and live in find_company_docs / get_company_doc (categories: press_release, earnings_release).

    DO NOT USE as a fallback for company-published content (use find_filings, find_events, find_research first). Per system policy, web search is reserved for genuine media-coverage queries OR when domain tools have been exhausted.

    NOTE: If no allowed_domains are provided, the search uses Aiera's curated list of trusted domains.
    """

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    include_base_instructions: Optional[bool] = Field(
        default=True,
        description="Whether or not to include initial critical instructions in the API response. This only needs to be done once per session.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    search: str = Field(
        description="The search query to find relevant news and articles from trusted financial sources.",
    )

    allowed_domains: Optional[str] = Field(
        default=None,
        description="Comma-separated list of allowed domains to restrict search results (e.g., 'cnbc.com,reuters.com'). If omitted, will use Aiera's curated list of trusted domains.",
    )


# Response models
class TrustedWebSearchResponse(BaseAieraResponse):
    """Response for trusted_web_search tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
