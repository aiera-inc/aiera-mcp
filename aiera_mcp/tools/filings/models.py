#!/usr/bin/env python3

"""Filings domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict
from datetime import datetime, date
from enum import Enum

from ..common.models import BaseAieraResponse, PaginatedResponse


# Mixins for validation (extracted from original params.py)
class BaseToolArgs(BaseModel):
    """Base class for all Aiera MCP tool arguments with common serializers."""

    @field_serializer('watchlist_id', 'index_id', 'sector_id', 'subsector_id', 'page', 'page_size', when_used='always', check_fields=False)
    def serialize_numeric_fields(self, value: Any) -> str:
        """Convert numeric fields to strings for API requests."""
        if value is None:
            return None
        return str(value)


class BloombergTickerMixin(BaseModel):
    """Mixin for models with bloomberg_ticker field."""

    @field_validator('bloomberg_ticker', mode='before', check_fields=False)
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
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    end_date: str = Field(
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET).",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )
    watchlist_id: Optional[int] = Field(
        default=None,
        description="ID of a specific watchlist. Use get_available_watchlists to find valid IDs."
    )
    index_id: Optional[int] = Field(
        default=None,
        description="ID of a specific index. Use get_available_indexes to find valid IDs."
    )
    sector_id: Optional[int] = Field(
        default=None,
        description="ID of a specific sector. Use get_sectors_and_subsectors to find valid IDs."
    )
    subsector_id: Optional[int] = Field(
        default=None,
        description="ID of a specific subsector. Use get_sectors_and_subsectors to find valid IDs."
    )
    form_number: Optional[str] = Field(
        default=None,
        description="SEC form type to filter by (e.g., '10-K', '10-Q', '8-K')."
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number for pagination (1-based)."
    )
    page_size: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Number of items per page (1-100)."
    )


class GetFilingArgs(BaseToolArgs):
    """Get detailed information about a specific SEC filing."""
    filing_id: str = Field(
        description="Unique identifier for the SEC filing. Obtained from find_filings results."
    )


# Response models (extracted from responses.py)
class FilingItem(BaseModel):
    """Individual filing item."""
    filing_id: str = Field(description="Unique filing identifier")
    company_name: str = Field(description="Company name")
    company_ticker: Optional[str] = Field(default=None, description="Company ticker")
    form_type: str = Field(description="SEC form type (e.g., 10-K, 10-Q)")
    title: str = Field(description="Filing title")
    filing_date: date = Field(description="Filing date")
    period_end_date: Optional[date] = Field(default=None, description="Period end date")
    is_amendment: bool = Field(description="Whether this is an amendment")
    official_url: Optional[str] = Field(default=None, description="Official SEC.gov URL")


class FilingSummary(BaseModel):
    """Filing summary information."""
    summary: Optional[str] = Field(default=None, description="AI-generated summary")
    key_points: List[str] = Field(default=[], description="Key points from filing")
    financial_highlights: Dict[str, Any] = Field(default={}, description="Financial highlights")


class FilingDetails(FilingItem):
    """Detailed filing information including content and summary."""
    summary: Optional[FilingSummary] = Field(default=None, description="Filing summary")
    content_preview: Optional[str] = Field(default=None, description="Preview of filing content")
    document_count: int = Field(description="Number of documents in filing")


class FindFilingsResponse(PaginatedResponse):
    """Response for find_filings tool."""
    filings: List[FilingItem] = Field(description="List of filings")


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