#!/usr/bin/env python3

"""Company docs domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict, Union

from ..common.models import BaseAieraResponse, PaginatedResponse


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
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized. If the prompt is being truncated or summarized, please explain that with a parenthetical.",
    )

    include_base_instructions: Optional[bool] = Field(
        default=True,
        description="Whether or not to include initial critical instructions in the API response. This only needs to be done once per session.",
    )

    start_date: str = Field(
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    end_date: str = Field(
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
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

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetCompanyDocArgs(BaseToolArgs):
    """Get detailed information about a specific company document including a summary and other metadata."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized. If the prompt is being truncated or summarized, please explain that with a parenthetical.",
    )

    include_base_instructions: Optional[bool] = Field(
        default=True,
        description="Whether or not to include initial critical instructions in the API response. This only needs to be done once per session.",
    )

    company_doc_ids: str = Field(
        description="Comma separated unique identifiers for the company documents. Obtained from find_company_docs results."
    )


class GetCompanyDocCategoriesArgs(BaseToolArgs):
    """Retrieve all available document categories for filtering company documents. Used to find valid category values for find_company_docs."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized. If the prompt is being truncated or summarized, please explain that with a parenthetical.",
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within relevant text fields.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetCompanyDocKeywordsArgs(BaseToolArgs):
    """Retrieve all available keywords for filtering company documents. Used to find valid keyword values for find_company_docs."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized. If the prompt is being truncated or summarized, please explain that with a parenthetical.",
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within relevant text fields.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


# Response models (extracted from responses.py)
class CompanyInfo(BaseModel):
    """Company information in document."""

    company_id: int = Field(description="Company identifier")
    name: str = Field(description="Company name")


class DocumentCitationMetadata(BaseModel):
    """Metadata for document citation."""

    type: str = Field(
        description="The type of citation ('event', 'filing', 'company_doc', 'conference', or 'company')"
    )
    url_target: Optional[str] = Field(
        None, description="Whether the URL will be to Aiera or an external source"
    )
    company_id: Optional[int] = Field(None, description="Company identifier")
    company_doc_id: Optional[int] = Field(
        None, description="Company document identifier"
    )


class DocumentCitationInfo(BaseModel):
    """Citation information for document."""

    title: Optional[str] = Field(
        None, description="Citation title (can be null if document title is null)"
    )
    url: str = Field(description="Citation URL")
    metadata: Optional[DocumentCitationMetadata] = Field(
        None, description="Additional metadata about the citation"
    )


class CompanyDocItem(BaseModel):
    """Individual company document item - matches actual API structure."""

    doc_id: int = Field(description="Document identifier")
    company: CompanyInfo = Field(description="Company information")
    publish_date: Optional[str] = Field(
        None, description="Publication date (can be null)"
    )
    category: Optional[str] = Field(None, description="Document category (can be null)")
    title: Optional[str] = Field(None, description="Document title (can be null)")
    source_url: str = Field(description="Original source URL")
    summary: Optional[List[str]] = Field(
        None, description="Document summary (can be null)"
    )
    keywords: Optional[List[str]] = Field(
        None, description="Document keywords (can be null)"
    )
    processed: Optional[str] = Field(None, description="Processing date")
    created: Optional[str] = Field(None, description="Creation date")
    modified: Optional[str] = Field(None, description="Modification date")
    content_raw: Optional[str] = Field(None, description="Raw document content")
    citation_information: Optional[DocumentCitationInfo] = Field(
        None, description="Citation information"
    )


class CompanyDocDetails(CompanyDocItem):
    """Detailed company document information."""

    # Don't override summary - inherit List[str] from CompanyDocItem
    # The API returns summary as a list for both find and get endpoints
    # content_raw is inherited from CompanyDocItem
    attachments: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Document attachments"
    )


class CategoryKeyword(BaseModel):
    """Category or keyword information."""

    name: str = Field(description="Category/keyword name")
    count: int = Field(description="Usage count")


# Response pagination structure
class CompanyDocPaginationInfo(BaseModel):
    """Pagination information from company docs API."""

    total_count: int = Field(description="Total number of documents")
    current_page: int = Field(description="Current page number")
    total_pages: int = Field(description="Total number of pages")
    page_size: int = Field(description="Number of documents per page")


class CompanyDocResponseData(BaseModel):
    """Company docs response data container."""

    pagination: CompanyDocPaginationInfo = Field(description="Pagination information")
    data: List[CompanyDocItem] = Field(description="List of company documents")


# Response classes
class FindCompanyDocsResponse(BaseAieraResponse):
    """Response for find_company_docs tool - matches actual API structure."""

    response: Optional[CompanyDocResponseData] = Field(
        None, description="Response data container"
    )


class GetCompanyDocResponse(BaseAieraResponse):
    """Response for get_company_doc tool."""

    document: Optional[CompanyDocDetails] = Field(
        default=None, description="Detailed document information (None if not found)"
    )


class GetCompanyDocCategoriesResponse(BaseAieraResponse):
    """Response for get_company_doc_categories tool - matches actual API structure."""

    pagination: CompanyDocPaginationInfo = Field(description="Pagination information")
    data: Dict[str, int] = Field(description="Dictionary of categories with counts")


class GetCompanyDocKeywordsResponse(BaseAieraResponse):
    """Response for get_company_doc_keywords tool - matches actual API structure."""

    pagination: CompanyDocPaginationInfo = Field(description="Pagination information")
    data: Dict[str, int] = Field(description="Dictionary of keywords with counts")
