#!/usr/bin/env python3

"""Equities domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict
from datetime import datetime


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
class FindEquitiesArgs(BaseToolArgs, BloombergTickerMixin):
    """Find companies and equities using various identifiers or search. To find equities for multiple companies, provide a comma-separated list of bloomberg_tickers, isins, rics, or a search term. You do not need to make multiple calls."""

    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces.",
    )
    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number (ISIN).",
    )
    ric: Optional[str] = Field(
        default=None, description="Reuters Instrument Code (RIC)."
    )
    ticker: Optional[str] = Field(
        default=None, description="Stock ticker symbol (without country code)."
    )
    permid: Optional[str] = Field(
        default=None, description="Refinitiv Permanent Identifier (PermID)."
    )
    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within company names or tickers.",
    )
    page: int = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: int = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetEquitySummariesArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve detailed summary(s) about one or more equities, filtered by bloomberg_tickers (a comma-separated list).
    Summaries will include past and upcoming events, information about company leadership, recent financials, and within which indices the equity is included.
    To find summaries for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls.
    """

    bloomberg_ticker: str = Field(
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )


class GetIndexConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific stock market index."""

    index: str = Field(
        description="Index identifier. Use get_available_indexes to find valid values."
    )
    page: int = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: int = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetWatchlistConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific watchlist."""

    watchlist_id: str = Field(
        description="Watchlist identifier. Use get_available_watchlists to find valid values."
    )
    page: int = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: int = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetAvailableWatchlistsArgs(BaseToolArgs):
    """Retrieve all available watchlists with their IDs, names, and descriptions. Used to find valid watchlist IDs for filtering other tools."""

    pass


class GetAvailableIndexesArgs(BaseToolArgs):
    """Retrieve all available stock market indices with their IDs, names, and descriptions. Used to find valid index IDs for filtering other tools."""

    pass


class GetSectorsAndSubsectorsArgs(BaseToolArgs):
    """Retrieve all available sectors and subsectors with their IDs, names, and hierarchical relationships. Used to find valid sector/subsector IDs for filtering other tools."""

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
class EquityItem(BaseModel):
    """Individual equity item."""

    equity_id: int = Field(description="Unique equity identifier")
    company_id: Optional[int] = Field(None, description="Company ID")
    company_name: Optional[str] = Field(None, description="Company name")
    name: Optional[str] = Field(None, description="Company name (alias)")
    ticker: Optional[str] = Field(None, description="Stock ticker")
    bloomberg_ticker: str = Field(description="Bloomberg ticker")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    sector: Optional[str] = Field(None, description="Sector name")
    subsector: Optional[str] = Field(None, description="Subsector name")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    subsector_id: Optional[int] = Field(None, description="Subsector ID")
    country: Optional[str] = Field(default=None, description="Country of incorporation")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    primary_equity: Optional[bool] = Field(None, description="Is primary equity")
    created: Optional[datetime] = Field(None, description="Creation date")
    modified: Optional[datetime] = Field(None, description="Modification date")

    @field_validator("created", "modified", mode="before")
    @classmethod
    def parse_datetime_fields(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # Replace 'Z' with '+00:00' for ISO format compatibility
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        # If it's already a datetime object, return as is
        return v

    @field_serializer("created", "modified")
    def serialize_datetime_fields(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format string for JSON compatibility."""
        if value is None:
            return None
        return value.isoformat()


class LeadershipItem(BaseModel):
    """Leadership information for equity summaries."""

    name: str = Field(description="Person name")
    title: str = Field(description="Job title")
    event_count: Optional[int] = Field(None, description="Number of events")
    last_event_date: Optional[datetime] = Field(None, description="Last event date")

    @field_validator("last_event_date", mode="before")
    @classmethod
    def parse_last_event_date(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # Replace 'Z' with '+00:00' for ISO format compatibility
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        # If it's already a datetime object, return as is
        return v

    @field_serializer("last_event_date")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat()


class EquitySummaryItem(BaseModel):
    """Individual equity with full summary information."""

    equity_id: int = Field(description="Unique equity identifier")
    company_id: Optional[int] = Field(None, description="Company ID")
    company_name: Optional[str] = Field(None, description="Company name")
    name: Optional[str] = Field(None, description="Company name (alias)")
    ticker: Optional[str] = Field(None, description="Stock ticker")
    bloomberg_ticker: str = Field(description="Bloomberg ticker")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    sector: Optional[str] = Field(None, description="Sector name")
    subsector: Optional[str] = Field(None, description="Subsector name")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    subsector_id: Optional[int] = Field(None, description="Subsector ID")
    description: Optional[str] = Field(None, description="Company description")
    country: Optional[str] = Field(None, description="Country")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    created: Optional[datetime] = Field(None, description="Creation date")
    modified: Optional[datetime] = Field(None, description="Modification date")
    status: Optional[str] = Field(None, description="Status")
    leadership: Optional[List[LeadershipItem]] = Field(
        None, description="Leadership information"
    )

    @field_validator("created", "modified", mode="before")
    @classmethod
    def parse_datetime_fields(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                # Replace 'Z' with '+00:00' for ISO format compatibility
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        # If it's already a datetime object, return as is
        return v

    @field_serializer("created", "modified")
    def serialize_datetime_fields(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat()


class EquitySummary(BaseModel):
    """Equity summary information."""

    description: Optional[str] = Field(default=None, description="Company description")
    recent_events: List[str] = Field(default=[], description="Recent corporate events")
    key_metrics: Dict[str, Any] = Field(default={}, description="Key financial metrics")
    analyst_coverage: Dict[str, Any] = Field(
        default={}, description="Analyst coverage info"
    )


class EquityDetails(EquityItem):
    """Detailed equity information."""

    summary: Optional[EquitySummary] = Field(
        default=None, description="Company summary"
    )
    identifiers: Dict[str, str] = Field(
        default={}, description="Alternative identifiers"
    )


class SubsectorInfo(BaseModel):
    """Subsector information."""

    subsector_id: int = Field(description="Subsector ID")
    name: str = Field(description="Subsector name")
    gics_code: Optional[str] = Field(None, description="GICS subsector code")
    gics_industry_code: Optional[str] = Field(None, description="GICS industry code")


class SectorSubsector(BaseModel):
    """Sector and subsector information."""

    sector_id: int = Field(description="Sector ID")
    name: str = Field(description="Sector name")
    gics_code: Optional[str] = Field(None, description="GICS sector code")
    subsectors: Optional[List[SubsectorInfo]] = Field(
        None, description="List of subsectors"
    )

    # Backward compatibility properties
    @property
    def sector_name(self) -> str:
        return self.name

    # For single subsector access (legacy compatibility)
    @property
    def subsector_id(self) -> Optional[int]:
        if self.subsectors and len(self.subsectors) > 0:
            return self.subsectors[0].subsector_id
        return None

    @property
    def subsector_name(self) -> Optional[str]:
        if self.subsectors and len(self.subsectors) > 0:
            return self.subsectors[0].name
        return None


class IndexItem(BaseModel):
    """Index information."""

    index_id: int = Field(description="Index identifier")
    name: str = Field(description="Index name")
    symbol: Optional[str] = Field(None, description="Index symbol")
    short_name: Optional[str] = Field(None, description="Index short name/symbol")

    # Alias for backward compatibility
    @property
    def index_name(self) -> str:
        return self.name


class WatchlistItem(BaseModel):
    """Watchlist information."""

    watchlist_id: int = Field(description="Watchlist identifier")
    name: str = Field(description="Watchlist name")
    description: Optional[str] = Field(None, description="Watchlist description")
    type: Optional[str] = Field(None, description="Watchlist type")

    # Alias for backward compatibility
    @property
    def watchlist_name(self) -> str:
        return self.name


# Response classes
class ApiPaginationInfo(BaseModel):
    """Pagination information from API response."""

    total_count: Optional[int] = Field(None, description="Total number of items")
    current_page: Optional[int] = Field(None, description="Current page number")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    page_size: Optional[int] = Field(None, description="Items per page")


class FindEquitiesApiResponseData(BaseModel):
    """API response structure with data and pagination for find_equities."""

    data: List[EquityItem] = Field(..., description="List of equities")
    pagination: Optional[ApiPaginationInfo] = Field(
        None, description="Pagination information"
    )


class FindEquitiesResponse(BaseModel):
    """Response for find_equities tool"""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: FindEquitiesApiResponseData = Field(..., description="Response data")


class GetEquitySummariesResponse(BaseModel):
    """Response for get_equity_summaries tool"""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: List[EquitySummaryItem] = Field(
        ..., description="List of equity summaries"
    )


class GetSectorsSubsectorsResponse(BaseModel):
    """Response for get_sectors_and_subsectors tool"""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: List[SectorSubsector] = Field(
        ..., description="List of sectors and subsectors"
    )


class GetAvailableIndexesResponse(BaseModel):
    """Response for get_available_indexes tool"""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: List[IndexItem] = Field(..., description="List of available indexes")


class GetIndexConstituentsResponse(BaseModel):
    """Response for get_index_constituents tool - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: FindEquitiesApiResponseData = Field(..., description="Response data")


class GetAvailableWatchlistsResponse(BaseModel):
    """Response for get_available_watchlists tool - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: List[WatchlistItem] = Field(
        ..., description="List of available watchlists"
    )


class GetWatchlistConstituentsResponse(BaseModel):
    """Response for get_watchlist_constituents tool - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: FindEquitiesApiResponseData = Field(..., description="Response data")
