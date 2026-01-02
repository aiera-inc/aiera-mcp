#!/usr/bin/env python3

"""Equities domain models for Aiera MCP."""

from pydantic import AliasChoices, BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Dict, Union, Literal
from datetime import datetime, date


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
class FindEquitiesArgs(BaseToolArgs, BloombergTickerMixin):
    """Find companies and equities using various identifiers or search. To find equities for multiple companies, provide a comma-separated list of bloomberg_tickers, isins, rics, or a search term. You do not need to make multiple calls."""

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

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetEquitySummariesArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve detailed summary(s) about one or more equities, filtered by bloomberg_tickers (a comma-separated list).
    Summaries will include past and upcoming events, information about company leadership, recent financials, and within which indices the equity is included.
    To find summaries for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls.
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

    bloomberg_ticker: str = Field(
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )


class GetIndexConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific stock market index."""

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

    index: Union[str, int] = Field(
        description="Index identifier. Use get_available_indexes to find valid values."
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetWatchlistConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific watchlist."""

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

    watchlist_id: Union[str, int] = Field(
        description="Watchlist identifier. Use get_available_watchlists to find valid values."
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetAvailableWatchlistsArgs(BaseToolArgs):
    """Retrieve all available watchlists with their IDs, names, and descriptions. Used to find valid watchlist IDs for filtering other tools."""

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


class GetAvailableIndexesArgs(BaseToolArgs):
    """Retrieve all available stock market indices with their IDs, names, and descriptions. Used to find valid index IDs for filtering other tools."""

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


class GetSectorsAndSubsectorsArgs(BaseToolArgs):
    """Retrieve all available sectors and subsectors with their IDs, names, and hierarchical relationships. Used to find valid sector/subsector IDs for filtering other tools."""

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

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


# Response models (extracted from responses.py)
class EquityItem(BaseModel):
    """Individual equity item."""

    equity_id: int = Field(description="Unique equity identifier")
    company_id: Optional[int] = Field(None, description="Company ID")
    name: Optional[str] = Field(None, description="Company name")
    bloomberg_ticker: str = Field(description="Bloomberg ticker")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    subsector_id: Optional[int] = Field(
        None,
        description="Subsector ID",
        validation_alias=AliasChoices("subsector_id", "sub_sector_id"),
    )
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


class ConfirmedEventCitationMetadata(BaseModel):
    """Metadata for confirmed event citation."""

    type: str = Field(
        description="The type of citation ('event', 'filing', 'company_doc', 'conference', or 'company')"
    )
    url_target: Optional[str] = Field(
        None,
        description="Whether the citation URL will go to Aiera or to an external source",
    )
    company_id: Optional[int] = Field(None, description="Company identifier")
    event_id: Optional[int] = Field(None, description="Event identifier")


class ConfirmedEventCitationInfo(BaseModel):
    """Citation information for confirmed events."""

    title: str = Field(description="Citation title")
    url: str = Field(description="Citation URL")
    metadata: Optional[ConfirmedEventCitationMetadata] = Field(
        None, description="Citation metadata"
    )


class EventSummary(BaseModel):
    """Summary information for a confirmed event."""

    title: Optional[str] = Field(None, description="Summary title")
    content: Optional[List[str]] = Field(None, description="Summary content paragraphs")


class ConfirmedEventItem(BaseModel):
    """A confirmed past or upcoming event."""

    event_id: int = Field(description="Event identifier")
    title: str = Field(description="Event title")
    event_type: str = Field(description="Type of event (e.g., 'earnings')")
    event_date: Optional[datetime] = Field(None, description="Event date")
    fiscal_quarter: Optional[int] = Field(None, description="Fiscal quarter")
    fiscal_year: Optional[int] = Field(None, description="Fiscal year")
    has_human_verified: Optional[bool] = Field(
        None, description="Whether event is human verified"
    )
    has_live_transcript: Optional[bool] = Field(
        None, description="Whether event has live transcript"
    )
    has_audio: Optional[bool] = Field(None, description="Whether event has audio")
    summary: Optional[EventSummary] = Field(None, description="Event summary")
    citation_information: Optional[ConfirmedEventCitationInfo] = Field(
        None, description="Citation information for this event"
    )

    @field_validator("event_date", mode="before")
    @classmethod
    def parse_event_date(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        return v

    @field_serializer("event_date")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat()


class ConfirmedEvents(BaseModel):
    """Confirmed events containing past and upcoming events."""

    past: Optional[List[ConfirmedEventItem]] = Field(
        default=None, description="Past confirmed events"
    )
    upcoming: Optional[List[ConfirmedEventItem]] = Field(
        default=None, description="Upcoming confirmed events"
    )


class EstimatedEventItem(BaseModel):
    """An estimated future event."""

    estimate_id: int = Field(description="Estimate identifier")
    estimate_date: Optional[datetime] = Field(None, description="Estimated event date")
    estimate_type: str = Field(description="Type of estimated event (e.g., 'earnings')")
    estimate_title: str = Field(description="Estimated event title")

    @field_validator("estimate_date", mode="before")
    @classmethod
    def parse_estimate_date(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        return v

    @field_serializer("estimate_date")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat()


class EquitySummaryItem(BaseModel):
    """Individual equity with full summary information."""

    equity_id: int = Field(description="Unique equity identifier")
    company_id: Optional[int] = Field(None, description="Company ID")
    name: Optional[str] = Field(None, description="Company name")
    bloomberg_ticker: str = Field(description="Bloomberg ticker")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    subsector_id: Optional[int] = Field(None, description="Subsector ID")
    description: Optional[str] = Field(None, description="Company description")
    country: Optional[str] = Field(None, description="Country")
    created: Optional[datetime] = Field(None, description="Creation date")
    modified: Optional[datetime] = Field(None, description="Modification date")
    status: Optional[str] = Field(None, description="Status (e.g., 'active')")
    leadership: Optional[List[LeadershipItem]] = Field(
        None, description="Leadership information"
    )
    indices: Optional[List[str]] = Field(
        None, description="List of indices the equity belongs to"
    )
    confirmed_events: Optional[ConfirmedEvents] = Field(
        None, description="Confirmed past and upcoming events"
    )
    estimated_events: Optional[List[EstimatedEventItem]] = Field(
        None, description="Estimated future events"
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
    short_name: Optional[str] = Field(None, description="Index short name/symbol")

    # Alias for backward compatibility
    @property
    def index_name(self) -> str:
        return self.name


class WatchlistItem(BaseModel):
    """Watchlist information."""

    watchlist_id: int = Field(description="Watchlist identifier")
    name: str = Field(description="Watchlist name")
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

    data: List[EquityItem] = Field(None, description="List of equities")
    pagination: Optional[ApiPaginationInfo] = Field(
        None, description="Pagination information"
    )


class FindEquitiesResponse(BaseModel):
    """Response for find_equities tool"""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[FindEquitiesApiResponseData] = Field(
        None, description="Response data"
    )
    error: Optional[str] = Field(None, description="Error message if request failed")


class GetEquitySummariesResponse(BaseModel):
    """Response for get_equity_summaries tool"""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[List[EquitySummaryItem]] = Field(
        None, description="List of equity summaries"
    )
    error: Optional[str] = Field(None, description="Error message if request failed")


class GetSectorsSubsectorsResponse(BaseModel):
    """Response for get_sectors_and_subsectors tool"""

    response: Optional[List[SectorSubsector]] = Field(
        None, description="List of sectors and subsectors"
    )


class GetAvailableIndexesResponse(BaseModel):
    """Response for get_available_indexes tool"""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[List[IndexItem]] = Field(
        None, description="List of available indexes"
    )
    error: Optional[str] = Field(None, description="Error message if request failed")


class GetIndexConstituentsResponse(BaseModel):
    """Response for get_index_constituents tool - matches actual API structure."""

    data: List[EquityItem] = Field(None, description="List of equities")
    pagination: Optional[ApiPaginationInfo] = Field(
        None, description="Pagination information"
    )


class GetAvailableWatchlistsResponse(BaseModel):
    """Response for get_available_watchlists tool - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[List[WatchlistItem]] = Field(
        None, description="List of available watchlists"
    )
    error: Optional[str] = Field(None, description="Error message if request failed")


class GetWatchlistConstituentsResponse(BaseModel):
    """Response for get_watchlist_constituents tool - matches actual API structure."""

    data: List[EquityItem] = Field(None, description="List of equities")
    pagination: Optional[ApiPaginationInfo] = Field(
        None, description="Pagination information"
    )


class GetFinancialsArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve financial data (income statements, balance sheets, cash flow statements) for a company.
    Use this tool to get detailed financial metrics for a specific company and fiscal period.
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

    bloomberg_ticker: str = Field(
        description="Bloomberg ticker in format 'TICKER:COUNTRY' (e.g., 'AAPL:US')."
    )

    source: Literal["income-statement", "balance-sheet", "cash-flow-statement"] = Field(
        description="The type of financial statement to retrieve."
    )

    source_type: Literal["as-reported", "standardized"] = Field(
        description="The format type of the financial data: 'as-reported' for original filings or 'standardized' for normalized data."
    )

    period: Literal["annual", "quarterly", "semi-annual", "ltm", "ytd", "latest"] = (
        Field(description="The reporting period type for the financial data.")
    )

    fiscal_year: int = Field(description="The fiscal year for the financial data.")

    fiscal_quarter: Optional[int] = Field(
        default=None,
        description="The fiscal quarter for the financial data (1-4). Required for quarterly periods.",
    )


class FinancialMetricInfo(BaseModel):
    """Metadata about a financial metric."""

    metric_name: str = Field(description="Name of the financial metric")
    metric_format: Optional[str] = Field(
        None, description="What the metric represents (e.g., number, ratio)"
    )
    is_point_in_time: Optional[bool] = Field(
        None, description="Whether the metric is a point-in-time value"
    )
    is_currency: Optional[bool] = Field(
        None, description="Whether the metric is a currency value"
    )
    is_per_share: Optional[bool] = Field(
        None, description="Whether the metric is a per-share value"
    )
    is_key_metric: Optional[bool] = Field(
        None, description="Whether the metric is a key/important metric"
    )
    is_total: Optional[bool] = Field(
        None, description="Whether the metric is a total/sum value"
    )
    headers: Optional[List[str]] = Field(
        None, description="Header hierarchy for the metric"
    )


class FinancialCitationMetadata(BaseModel):
    """Metadata for financial citation."""

    type: Optional[str] = Field(None, description="The type of citation")
    url_target: Optional[str] = Field(
        None,
        description="Whether the citation URL will go to Aiera or to an external source",
    )


class FinancialCitationInfo(BaseModel):
    """Citation information for financial metrics."""

    title: Optional[str] = Field(None, description="Citation title")
    url: Optional[str] = Field(None, description="Citation URL")
    metadata: Optional[FinancialCitationMetadata] = Field(
        None, description="Citation metadata"
    )


class FinancialMetricItem(BaseModel):
    """Individual financial metric with value and citation."""

    metric: FinancialMetricInfo = Field(description="Metric metadata")
    metric_value: Optional[Union[int, float]] = Field(
        None, description="The metric value"
    )
    metric_unit: Optional[str] = Field(
        None, description="Unit of the metric value (e.g. M, B)"
    )
    metric_currency: Optional[str] = Field(
        None, description="Currency of the metric value (e.g. USD, EUR)"
    )
    metric_is_calculated: Optional[bool] = Field(
        None, description="Whether the metric was calculated"
    )
    citation_information: Optional[FinancialCitationInfo] = Field(
        None, description="Citation information for this metric"
    )


class FinancialPeriodItem(BaseModel):
    """Financial data for a specific period."""

    period_type: Optional[str] = Field(
        None, description="Type of period (annual, quarterly, etc.)"
    )
    report_date: Optional[date] = Field(None, description="Report date")
    period_duration: Optional[str] = Field(None, description="Duration of the period")
    calendar_year: Optional[int] = Field(None, description="Calendar year")
    calendar_quarter: Optional[int] = Field(None, description="Calendar quarter")
    fiscal_year: Optional[int] = Field(None, description="Fiscal year")
    fiscal_quarter: Optional[int] = Field(None, description="Fiscal quarter")
    is_restated: Optional[bool] = Field(
        None, description="Whether the data was restated"
    )
    earnings_date: Optional[datetime] = Field(None, description="Earnings release date")
    filing_date: Optional[datetime] = Field(None, description="Filing date")
    metrics: Optional[List[FinancialMetricItem]] = Field(
        None, description="List of financial metrics"
    )

    @field_validator("report_date", mode="before")
    @classmethod
    def parse_report_date(cls, v):
        """Parse date strings to date objects."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return date.fromisoformat(v)
            except (ValueError, AttributeError):
                return None
        return v

    @field_validator("earnings_date", "filing_date", mode="before")
    @classmethod
    def parse_datetime_fields(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return None
        return v

    @field_serializer("report_date")
    def serialize_report_date(self, value: Optional[date]) -> Optional[str]:
        """Serialize date fields to ISO format string."""
        if value is None:
            return None
        return value.isoformat()

    @field_serializer("earnings_date", "filing_date")
    def serialize_datetime_fields(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format string."""
        if value is None:
            return None
        return value.isoformat()


class FinancialEquityInfo(BaseModel):
    """Equity information in financials response."""

    equity_id: Optional[int] = Field(None, description="Unique equity identifier")
    company_id: Optional[int] = Field(None, description="Company ID")
    name: Optional[str] = Field(None, description="Company name")
    bloomberg_ticker: Optional[str] = Field(None, description="Bloomberg ticker")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    subsector_id: Optional[int] = Field(None, description="Subsector ID")


class FinancialsResponseData(BaseModel):
    """Response data containing equity and financials."""

    equity: Optional[FinancialEquityInfo] = Field(
        None, description="Equity information"
    )
    financials: Optional[List[FinancialPeriodItem]] = Field(
        None, description="List of financial period data"
    )


class GetFinancialsResponse(BaseModel):
    """Response for get_financials tool."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[FinancialsResponseData] = Field(
        None, description="Response data with equity and financials"
    )
    error: Optional[str] = Field(None, description="Error message if request failed")
