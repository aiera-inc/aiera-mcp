#!/usr/bin/env python3

"""Filings domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict
from datetime import datetime

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


# Parameter models (extracted from params.py)
class FindFilingsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find SEC filings filtered by date range and optional filters."""

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
    form_number: Optional[str] = Field(
        default=None,
        description="SEC form type to filter by (e.g., '10-K', '10-Q', '8-K').",
    )
    page: int = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: int = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetFilingArgs(BaseToolArgs):
    """Get detailed information about a specific SEC filing."""

    filing_id: str = Field(
        description="Unique identifier for the SEC filing. Obtained from find_filings results."
    )


# Response models (extracted from responses.py)
class EquityInfo(BaseModel):
    """Company equity information embedded in filings."""

    company_name: Optional[str] = Field(None, description="Name of the company")
    ticker: Optional[str] = Field(None, description="Company ticker symbol")


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
    citation_information: Optional[Dict[str, str]] = Field(
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
    response: ApiResponseData = Field(..., description="Response data")


class GetFilingResponse(BaseAieraResponse):
    """Response for get_filing tool."""

    filing: FilingDetails = Field(description="Detailed filing information")


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
