#!/usr/bin/env python3

"""Company docs domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, Any, Union

from ..common.models import BaseAieraResponse


# Mixins for validation (extracted from original params.py)
class BaseToolArgs(BaseModel):
    """Base class for all Aiera MCP tool arguments with common serializers."""

    @field_validator(
        "watchlist_id",
        "index_id",
        "sector_id",
        "subsector_id",
        "page",
        "page_size",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_numeric_fields(cls, v):
        """Accept both integers and string representations of integers."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError(f"Cannot convert '{v}' to integer")
        return v

    @field_serializer(
        "watchlist_id",
        "index_id",
        "sector_id",
        "subsector_id",
        "page",
        "page_size",
        when_used="always",
        check_fields=False,
    )
    def serialize_numeric_fields(self, value: Any) -> str:
        """Convert numeric fields to strings for API requests."""
        if value is None:
            return None
        return str(value)


class BloombergTickerMixin(BaseModel):
    """Mixin for models with bloomberg_ticker field."""

    @field_validator("bloomberg_ticker", mode="before", check_fields=False)
    @classmethod
    def validate_bloomberg_ticker(cls, v):
        """Automatically correct Bloomberg ticker format."""
        if v is None:
            return v
        from ..utils import correct_bloomberg_ticker

        return correct_bloomberg_ticker(v)


class CategoriesKeywordsMixin(BaseModel):
    """Mixin for models with categories and keywords fields."""

    @field_validator("categories", mode="before", check_fields=False)
    @classmethod
    def validate_categories(cls, v):
        """Automatically correct categories format."""
        if v is None:
            return v
        from ..utils import correct_categories

        return correct_categories(v)

    @field_validator("keywords", mode="before", check_fields=False)
    @classmethod
    def validate_keywords(cls, v):
        """Automatically correct keywords format."""
        if v is None:
            return v
        from ..utils import correct_keywords

        return correct_keywords(v)


# Parameter models (extracted from params.py)
class FindCompanyDocsArgs(BaseToolArgs, BloombergTickerMixin, CategoriesKeywordsMixin):
    """Find company-published documents (press releases, annual reports, earnings releases, etc.) filtered by date range and optional filters.

    RETURNS METADATA AND SUMMARIES ONLY — NOT full document text. To retrieve the actual document content, call get_company_doc with the company_doc_id from these results. For keyword-level search across many documents, use search_company_docs instead.

    DOCUMENT TYPE MAPPING - CRITICAL:
    When users request specific document types, ALWAYS use the 'categories' parameter:
    - "press releases" → use categories='press_release'
    - "annual reports" → use categories='annual_report'
    - "earnings releases" → use categories='earnings_release'
    - "slide presentations" or "investor decks" → use categories='slide_presentation'
    - "compliance documents" → use categories='compliance'
    - "disclosure documents" → use categories='disclosure'
    - "press releases and annual reports" → use categories='press_release,annual_report'

    MULTIPLE DOCUMENT TYPES: For multiple document types, provide comma-separated categories without spaces (e.g., 'press_release,earnings_release').

    MULTIPLE COMPANIES: To find documents for multiple companies, provide a comma-separated list of bloomberg_tickers in a SINGLE call. You do NOT need multiple calls for multiple companies.

    This tool provides access to company-published documents with summaries and metadata.
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

    start_date: str = Field(
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    end_date: str = Field(
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter docs by title or category.",
    )

    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Optional: Bloomberg ticker(s) to filter by specific companies in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces (e.g., 'AAPL:US,MSFT:US'). Defaults to ':US' if country code omitted. Leave empty to search across all companies.",
    )

    watchlist_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific watchlist. Use get_available_watchlists to find valid IDs.",
    )

    index_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific index. Use get_available_indexes to find valid IDs.",
    )

    sector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific sector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    subsector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific subsector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    categories: Optional[str] = Field(
        default=None,
        description="CRITICAL: Filter by document type/category. Common categories: 'press_release' (press releases/news), 'annual_report' (annual reports), 'earnings_release' (earnings releases), 'slide_presentation' (investor presentations/decks), 'compliance' (compliance filings), 'disclosure' (disclosure documents). Use get_company_doc_categories to see all valid categories. Multiple categories should be comma-separated without spaces (e.g., 'press_release,earnings_release'). Example: For 'Find all press releases from Apple in Q1 2024', use categories='press_release'.",
    )

    keywords: Optional[str] = Field(
        default=None,
        description="Optional: Filter by keywords/topics (e.g., 'ESG', 'diversity', 'risk management', 'sustainability'). Use get_company_doc_keywords to see all valid keywords. Multiple keywords should be comma-separated without spaces.",
    )

    exclude_categories: Optional[str] = Field(
        default=None,
        description="Comma-separated category names to exclude from results.",
    )

    exclude_keywords: Optional[str] = Field(
        default=None,
        description="Comma-separated keywords to exclude from results.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetCompanyDocArgs(BaseToolArgs):
    """Get detailed information about specific company documents including summary, content, and metadata.

    RESPONSE SIZE WARNING: This tool returns full document content which can be extensive,
    especially for annual reports and detailed press releases.

    WHEN TO USE:
    - Use this when you need complete document content and summary
    - Use this when you need full metadata for specific documents
    - For browsing documents by type/date, use find_company_docs instead

    WORKFLOW: Use find_company_docs first to obtain valid company_doc_ids.
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

    company_doc_id: str = Field(
        description="Unique identifier for the company document. Obtain company_doc_id from find_company_docs results. Example: '12345'"
    )


class GetCompanyDocCategoriesArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve all available document categories for filtering company documents. Requires at least one company filter (bloomberg_ticker, isin, ric, permid, sector_id, or subsector_id). Used to find valid category values for find_company_docs."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within relevant text fields.",
    )

    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). At least one company filter is required.",
    )

    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number (ISIN).",
    )

    ric: Optional[str] = Field(
        default=None,
        description="Reuters Instrument Code (RIC).",
    )

    permid: Optional[str] = Field(
        default=None,
        description="Refinitiv Permanent Identifier (PermID).",
    )

    sector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific sector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    subsector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific subsector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetCompanyDocKeywordsArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve all available keywords for filtering company documents. Requires at least one company filter (bloomberg_ticker, isin, ric, permid, sector_id, or subsector_id). Used to find valid keyword values for find_company_docs."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within relevant text fields.",
    )

    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). At least one company filter is required.",
    )

    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number (ISIN).",
    )

    ric: Optional[str] = Field(
        default=None,
        description="Reuters Instrument Code (RIC).",
    )

    permid: Optional[str] = Field(
        default=None,
        description="Refinitiv Permanent Identifier (PermID).",
    )

    sector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific sector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    subsector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific subsector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


# Response models - pass through API response structure
class FindCompanyDocsResponse(BaseAieraResponse):
    """Response for find_company_docs tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetCompanyDocResponse(BaseAieraResponse):
    """Response for get_company_doc tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetCompanyDocCategoriesResponse(BaseAieraResponse):
    """Response for get_company_doc_categories tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetCompanyDocKeywordsResponse(BaseAieraResponse):
    """Response for get_company_doc_keywords tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
