#!/usr/bin/env python3

"""Events domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum

from ..common.models import BaseAieraArgs, BaseAieraResponse, PaginatedResponse


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


class EventTypeMixin(BaseModel):
    """Mixin for models with event_type field."""

    @field_validator('event_type', mode='before', check_fields=False)
    @classmethod
    def validate_event_type_correction(cls, v):
        """Automatically correct event type format."""
        if v is None:
            return v
        from ..utils import correct_event_type
        return correct_event_type(v)


# Event types (from responses.py)
class EventType(str, Enum):
    """Event types supported by Aiera."""
    EARNINGS = "earnings"
    PRESENTATION = "presentation"
    SHAREHOLDER_MEETING = "shareholder_meeting"
    INVESTOR_MEETING = "investor_meeting"
    SPECIAL_SITUATION = "special_situation"


# Parameter models (extracted from params.py)
class FindEventsArgs(BaseToolArgs, BloombergTickerMixin, EventTypeMixin):
    """Find events filtered by date range and optional company/entity filters."""
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
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces (e.g., 'AAPL:US,MSFT:US,GOOGL:US'). Defaults to ':US' if country code omitted."
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
    event_type: str = Field(
        default="earnings",
        description="Type of event to search for. Options: 'earnings', 'presentation' (conferences), 'shareholder_meeting' (annual meetings), 'investor_meeting', 'special_situation' (M&A/corporate actions)."
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

    @field_validator('event_type')
    @classmethod
    def validate_event_type_values(cls, v):
        """Validate event_type against allowed values."""
        valid_types = ['earnings', 'presentation', 'shareholder_meeting', 'investor_meeting', 'special_situation']
        if v not in valid_types:
            raise ValueError(f"event_type must be one of: {', '.join(valid_types)}")
        return v


class GetEventArgs(BaseToolArgs):
    """Get detailed information about a specific event including transcripts."""
    event_id: str = Field(
        description="Unique identifier for the event. Obtained from find_events results."
    )
    transcript_section: Optional[str] = Field(
        default=None,
        description="Filter transcripts by section. Only applicable for earnings events. Options: 'presentation', 'q_and_a'."
    )

    @field_validator('transcript_section')
    @classmethod
    def validate_transcript_section(cls, v):
        if v is not None and v not in ['presentation', 'q_and_a']:
            raise ValueError("transcript_section must be either 'presentation' or 'q_and_a'")
        return v


class GetUpcomingEventsArgs(BaseToolArgs, BloombergTickerMixin):
    """Get confirmed and estimated upcoming events within a date range."""
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


# Response models (extracted from responses.py)
class EquityInfo(BaseModel):
    """Company equity information embedded in events."""
    equity_id: Optional[int] = Field(None, description="Equity ID")
    company_id: Optional[int] = Field(None, description="Company ID")
    name: Optional[str] = Field(None, description="Name of the company")
    bloomberg_ticker: Optional[str] = Field(None, description="Bloomberg ticker")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    subsector_id: Optional[int] = Field(None, description="Subsector ID")
    primary_equity: Optional[bool] = Field(None, description="Is primary equity")

class GroupingInfo(BaseModel):
    """Event grouping information."""
    grouping_id: Optional[int] = Field(None, description="Grouping ID")
    grouping_name: Optional[str] = Field(None, description="Grouping name")

class SummaryInfo(BaseModel):
    """Event summary information."""
    title: Optional[str] = Field(None, description="Summary title")
    summary: Optional[List[str]] = Field(None, description="Summary content as list")

class CitationInfo(BaseModel):
    """Citation information for events."""
    title: Optional[str] = Field(None, description="Citation title")
    url: Optional[str] = Field(None, description="Citation URL")

class EventItem(BaseModel):
    """Basic event information."""
    event_id: int = Field(..., description="Unique identifier for the event")
    title: str = Field(..., description="Event title")
    event_type: str = Field(..., description="Type of event")
    event_date: datetime = Field(..., description="Date and time of the event")
    equity: Optional[EquityInfo] = Field(None, description="Company equity information")
    event_category: Optional[str] = Field(None, description="Event category")
    expected_language: Optional[str] = Field(None, description="Expected language of the event")
    grouping: Optional[GroupingInfo] = Field(None, description="Event grouping information")
    summary: Optional[SummaryInfo] = Field(None, description="Event summary")
    citation_information: Optional[CitationInfo] = Field(None, description="Citation information")

    @field_serializer('event_date')
    def serialize_event_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class EventDetails(EventItem):
    """Detailed event information including transcripts and metadata."""
    description: Optional[str] = Field(None, description="Event description")
    transcript_preview: Optional[str] = Field(None, description="Preview of transcript content")
    audio_url: Optional[str] = Field(None, description="URL to event audio")


class ApiPaginationInfo(BaseModel):
    """Pagination information from API response."""
    total_count: Optional[int] = Field(None, description="Total number of items")
    current_page: Optional[int] = Field(None, description="Current page number")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    page_size: Optional[int] = Field(None, description="Items per page")

class ApiResponseData(BaseModel):
    """API response structure with data and pagination."""
    data: List[EventItem] = Field(..., description="List of events")
    pagination: Optional[ApiPaginationInfo] = Field(None, description="Pagination information")

class FindEventsResponse(BaseModel):
    """Response from finding events - matches actual API structure."""
    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: ApiResponseData = Field(..., description="Response data")


class GetEventResponse(BaseAieraResponse):
    """Response from getting a specific event."""
    event: EventDetails = Field(..., description="Detailed event information")


class UpcomingEventsData(BaseModel):
    """Upcoming events response structure with estimates and actuals."""
    estimates: Optional[List[EventItem]] = Field(None, description="Estimated events")
    actuals: Optional[List[EventItem]] = Field(None, description="Actual/confirmed events")

class GetUpcomingEventsResponse(BaseModel):
    """Response from getting upcoming events - matches actual API structure."""
    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: UpcomingEventsData = Field(..., description="Response data")