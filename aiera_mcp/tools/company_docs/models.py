#!/usr/bin/env python3

"""Company docs domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict

from ..common.models import BaseAieraResponse, PaginatedResponse


# Mixins for validation (extracted from original params.py)
class BaseToolArgs(BaseModel):
    """Base class for all Aiera MCP tool arguments with common serializers."""

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
    """Find company-published documents filtered by date range and optional filters."""

    start_date: str = Field(
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces.",
    )
    watchlist_id: Optional[int] = Field(
        default=None,
        description="ID of a specific watchlist. Use get_available_watchlists to find valid IDs.",
    )
    index_id: Optional[int] = Field(
        default=None,
        description="ID of a specific index. Use get_available_indexes to find valid IDs.",
    )
    sector_id: Optional[int] = Field(
        default=None,
        description="ID of a specific sector. Use get_sectors_and_subsectors to find valid IDs.",
    )
    subsector_id: Optional[int] = Field(
        default=None,
        description="ID of a specific subsector. Use get_sectors_and_subsectors to find valid IDs.",
    )
    categories: Optional[str] = Field(
        default=None,
        description="Document categories to filter by (e.g., 'annual_report,earnings_release'). Use get_company_doc_categories to find valid values. Multiple categories should be comma-separated without spaces.",
    )
    keywords: Optional[str] = Field(
        default=None,
        description="Keywords to filter by (e.g., 'ESG,diversity'). Use get_company_doc_keywords to find valid values. Multiple keywords should be comma-separated without spaces.",
    )
    page: int = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: int = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetCompanyDocArgs(BaseToolArgs):
    """Get detailed information about a specific company document."""

    company_doc_id: str = Field(
        description="Unique identifier for the company document. Obtained from find_company_docs results."
    )


class SearchArgs(BaseToolArgs):
    """Parameter model for tools with optional search and pagination."""

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within relevant text fields.",
    )
    page: int = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: int = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


# Response models (extracted from responses.py)
class CompanyInfo(BaseModel):
    """Company information in document."""

    company_id: int = Field(description="Company identifier")
    name: str = Field(description="Company name")


class DocumentCitationInfo(BaseModel):
    """Citation information for document."""

    title: str = Field(description="Citation title")
    url: str = Field(description="Citation URL")


class CompanyDocItem(BaseModel):
    """Individual company document item - matches actual API structure."""

    doc_id: int = Field(description="Document identifier")
    company: CompanyInfo = Field(description="Company information")
    publish_date: str = Field(description="Publication date as string")
    category: str = Field(description="Document category")
    title: str = Field(description="Document title")
    source_url: str = Field(description="Source URL")
    summary: List[str] = Field(description="Document summary as list of strings")
    keywords: List[str] = Field(default=[], description="Document keywords")
    processed: Optional[str] = Field(None, description="Processing date")
    created: Optional[str] = Field(None, description="Creation date")
    modified: Optional[str] = Field(None, description="Modification date")
    citation_information: Optional[DocumentCitationInfo] = Field(
        None, description="Citation information"
    )


class CompanyDocDetails(CompanyDocItem):
    """Detailed company document information."""

    summary: Optional[str] = Field(description="Document summary")
    content_preview: Optional[str] = Field(description="Content preview")
    attachments: List[Dict[str, Any]] = Field(
        default=[], description="Document attachments"
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

    response: CompanyDocResponseData = Field(description="Response data container")


class GetCompanyDocResponse(BaseAieraResponse):
    """Response for get_company_doc tool."""

    document: CompanyDocDetails = Field(description="Detailed document information")


# Categories and Keywords response structures
class CategoriesKeywordsResponseData(BaseModel):
    """Categories/Keywords response data container."""

    pagination: CompanyDocPaginationInfo = Field(description="Pagination information")
    data: Dict[str, int] = Field(
        description="Dictionary of categories/keywords with counts"
    )


class GetCompanyDocCategoriesResponse(BaseAieraResponse):
    """Response for get_company_doc_categories tool - matches actual API structure."""

    response: CategoriesKeywordsResponseData = Field(
        description="Response data container"
    )


class GetCompanyDocKeywordsResponse(BaseAieraResponse):
    """Response for get_company_doc_keywords tool - matches actual API structure."""

    response: CategoriesKeywordsResponseData = Field(
        description="Response data container"
    )
