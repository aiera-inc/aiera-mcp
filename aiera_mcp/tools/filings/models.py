#!/usr/bin/env python3

"""Filings domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict, Union
from datetime import datetime

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


# Parameter models (extracted from params.py)
class FindFilingsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find SEC filings filtered by date range and optional filters. To find filings for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized; and if it is being truncated or summarized, please append a parenthetical saying so.",
    )

    include_base_instructions: Optional[bool] = Field(
        default=True,
        description="Whether or not to include initial critical instructions in the API response. This only needs to be done once per session.",
    )

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

    form_number: Optional[str] = Field(
        default=None,
        description="SEC form type to filter by (e.g., '10-K', '10-Q', '8-K').",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetFilingArgs(BaseToolArgs):
    """Get detailed information about a specific SEC filing."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized; and if it is being truncated or summarized, please append a parenthetical saying so.",
    )

    include_base_instructions: Optional[bool] = Field(
        default=True,
        description="Whether or not to include initial critical instructions in the API response. This only needs to be done once per session.",
    )

    filing_id: str = Field(
        description="Unique identifier for the SEC filing. Obtained from find_filings results."
    )


# Response models (extracted from responses.py)
class EquityInfo(BaseModel):
    """Company equity information embedded in filings."""

    equity_id: Optional[int] = Field(None, description="Equity identifier")
    company_id: Optional[int] = Field(None, description="Company identifier")
    name: Optional[str] = Field(None, description="Name of the company")
    bloomberg_ticker: Optional[str] = Field(None, description="Bloomberg ticker")
    sector_id: Optional[int] = Field(None, description="Sector identifier")
    subsector_id: Optional[int] = Field(None, description="Subsector identifier")


class FilingCitationMetadata(BaseModel):
    """Metadata for filing citation."""

    type: str = Field(
        description="The type of citation ('event', 'filing', 'company_doc', 'conference', or 'company')"
    )
    url_target: Optional[str] = Field(
        None, description="Whether the URL will be to Aiera or an external source"
    )
    company_id: Optional[int] = Field(None, description="Company identifier")
    content_id: Optional[int] = Field(None, description="Content identifier")
    filing_id: Optional[int] = Field(None, description="Filing identifier")


class FilingCitationInfo(BaseModel):
    """Citation information for filings."""

    title: Optional[str] = Field(None, description="Citation title")
    url: Optional[str] = Field(None, description="Citation URL")
    metadata: Optional[FilingCitationMetadata] = Field(
        None, description="Additional metadata about the citation"
    )


class FilingItem(BaseModel):
    """Individual filing item."""

    filing_id: int = Field(description="Unique filing identifier")
    title: str = Field(description="Filing title")
    filing_date: Optional[datetime] = Field(default=None, description="Filing date")
    period_end_date: Optional[datetime] = Field(
        default=None, description="Period end date"
    )
    is_amendment: int = Field(description="Whether this is an amendment (0/1)")
    equity: Optional[EquityInfo] = Field(None, description="Company equity information")
    form_number: Optional[str] = Field(None, description="SEC form number")
    form_name: Optional[str] = Field(None, description="SEC form name")
    filing_organization: Optional[str] = Field(None, description="Filing organization")
    filing_system: Optional[str] = Field(None, description="Filing system")
    release_date: Optional[datetime] = Field(None, description="Release date")
    arrival_date: Optional[datetime] = Field(None, description="Arrival date")
    pulled_date: Optional[datetime] = Field(None, description="Pulled date")
    json_synced: Optional[bool] = Field(None, description="JSON sync status")
    datafiles_synced: Optional[bool] = Field(None, description="Data files sync status")
    summary: Optional[List[str]] = Field(None, description="Filing summary as list")
    content_raw: Optional[str] = Field(None, description="Raw filing content")
    citation_information: Optional[FilingCitationInfo] = Field(
        None, description="Citation information"
    )

    @field_serializer(
        "filing_date", "period_end_date", "release_date", "arrival_date", "pulled_date"
    )
    def serialize_datetime_fields(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format string for JSON compatibility."""
        if value is None:
            return None
        return value.isoformat()


class FilingSummary(BaseModel):
    """Filing summary information."""

    summary: Optional[str] = Field(default=None, description="AI-generated summary")
    key_points: List[str] = Field(default=[], description="Key points from filing")
    financial_highlights: Dict[str, Any] = Field(
        default={}, description="Financial highlights"
    )


class FilingDetails(FilingItem):
    """Detailed filing information including content and summary."""

    summary: Optional[FilingSummary] = Field(default=None, description="Filing summary")
    content_preview: Optional[str] = Field(
        default=None, description="Preview of filing content"
    )
    document_count: int = Field(description="Number of documents in filing")


class ApiPaginationInfo(BaseModel):
    """Pagination information from API response."""

    total_count: Optional[int] = Field(None, description="Total number of items")
    current_page: Optional[int] = Field(None, description="Current page number")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    page_size: Optional[int] = Field(None, description="Items per page")


class ApiResponseData(BaseModel):
    """API response structure with data and pagination."""

    data: List[FilingItem] = Field(..., description="List of filings")
    pagination: Optional[ApiPaginationInfo] = Field(
        None, description="Pagination information"
    )


class FindFilingsResponse(BaseModel):
    """Response for find_filings tool - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[ApiResponseData] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if request failed")


class GetFilingResponse(BaseAieraResponse):
    """Response for get_filing tool."""

    filing: Optional[FilingDetails] = Field(
        default=None, description="Detailed filing information (None if not found)"
    )


# Import CitationInfo for backwards compatibility with existing tools.py
from ..common.models import CitationInfo

__all__ = [
    # Parameter models
    "FindFilingsArgs",
    "GetFilingArgs",
    # Response models
    "FindFilingsResponse",
    "GetFilingResponse",
    # Data models
    "FilingItem",
    "FilingDetails",
    "FilingSummary",
    "CitationInfo",
    # Mixins
    "BaseToolArgs",
    "BloombergTickerMixin",
]
