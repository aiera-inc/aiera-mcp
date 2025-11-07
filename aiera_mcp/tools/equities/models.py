#!/usr/bin/env python3

"""Equities domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict
from datetime import datetime, date

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
class FindEquitiesArgs(BaseToolArgs, BloombergTickerMixin):
    """Find companies and equities using various identifiers or search."""
    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )
    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number (ISIN)."
    )
    ric: Optional[str] = Field(
        default=None,
        description="Reuters Instrument Code (RIC)."
    )
    ticker: Optional[str] = Field(
        default=None,
        description="Stock ticker symbol (without country code)."
    )
    permid: Optional[str] = Field(
        default=None,
        description="Refinitiv Permanent Identifier (PermID)."
    )
    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within company names, tickers, or relevant text fields."
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


class GetEquitySummariesArgs(BaseToolArgs, BloombergTickerMixin):
    """Get comprehensive summary information for one or more equities."""
    bloomberg_ticker: str = Field(
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )


class GetIndexConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific stock market index."""
    index: str = Field(
        description="Index identifier. Use get_available_indexes to find valid values."
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


class GetWatchlistConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific watchlist."""
    watchlist_id: str = Field(
        description="Watchlist identifier. Use get_available_watchlists to find valid values."
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


class EmptyArgs(BaseToolArgs):
    """Parameter model for tools that take no arguments."""
    pass


class SearchArgs(BaseToolArgs):
    """Parameter model for tools with optional search and pagination."""
    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within relevant text fields."
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


# Response models (extracted from responses.py)
class EquityItem(BaseModel):
    """Individual equity item."""
    equity_id: str = Field(description="Unique equity identifier")
    company_name: str = Field(description="Company name")
    ticker: str = Field(description="Primary ticker symbol")
    bloomberg_ticker: str = Field(description="Bloomberg ticker")
    exchange: Optional[str] = Field(description="Primary exchange")
    sector: Optional[str] = Field(description="GICS sector")
    subsector: Optional[str] = Field(description="GICS subsector")
    country: Optional[str] = Field(description="Country of incorporation")
    market_cap: Optional[float] = Field(description="Market capitalization")


class EquitySummary(BaseModel):
    """Equity summary information."""
    description: Optional[str] = Field(description="Company description")
    recent_events: List[Dict[str, Any]] = Field(default=[], description="Recent corporate events")
    key_metrics: Dict[str, Any] = Field(default={}, description="Key financial metrics")
    analyst_coverage: Dict[str, Any] = Field(default={}, description="Analyst coverage info")


class EquityDetails(EquityItem):
    """Detailed equity information."""
    summary: Optional[EquitySummary] = Field(description="Company summary")
    identifiers: Dict[str, str] = Field(default={}, description="Alternative identifiers")


class SectorSubsector(BaseModel):
    """Sector and subsector information."""
    sector_id: str = Field(description="Sector ID")
    sector_name: str = Field(description="Sector name")
    subsector_id: Optional[str] = Field(description="Subsector ID")
    subsector_name: Optional[str] = Field(description="Subsector name")


class IndexItem(BaseModel):
    """Index information."""
    index_id: str = Field(description="Index identifier")
    index_name: str = Field(description="Index name")
    symbol: str = Field(description="Index symbol")


class WatchlistItem(BaseModel):
    """Watchlist information."""
    watchlist_id: str = Field(description="Watchlist identifier")
    watchlist_name: str = Field(description="Watchlist name")
    description: Optional[str] = Field(description="Watchlist description")


# Response classes
class FindEquitiesResponse(PaginatedResponse):
    """Response for find_equities tool."""
    equities: List[EquityItem] = Field(description="List of equities")


class GetEquitySummariesResponse(BaseAieraResponse):
    """Response for get_equity_summaries tool."""
    summaries: List[EquityDetails] = Field(description="Detailed equity summaries")


class GetSectorsSubsectorsResponse(BaseAieraResponse):
    """Response for get_sectors_and_subsectors tool."""
    sectors: List[SectorSubsector] = Field(description="List of sectors and subsectors")


class GetAvailableIndexesResponse(BaseAieraResponse):
    """Response for get_available_indexes tool."""
    indexes: List[IndexItem] = Field(description="List of available indexes")


class GetIndexConstituentsResponse(PaginatedResponse):
    """Response for get_index_constituents tool."""
    index_name: str = Field(description="Index name")
    constituents: List[EquityItem] = Field(description="Index constituents")


class GetAvailableWatchlistsResponse(BaseAieraResponse):
    """Response for get_available_watchlists tool."""
    watchlists: List[WatchlistItem] = Field(description="List of available watchlists")


class GetWatchlistConstituentsResponse(PaginatedResponse):
    """Response for get_watchlist_constituents tool."""
    watchlist_name: str = Field(description="Watchlist name")
    constituents: List[EquityItem] = Field(description="Watchlist constituents")