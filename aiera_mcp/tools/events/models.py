#!/usr/bin/env python3

"""Events domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Union
from datetime import datetime
from enum import Enum

from ..common.models import BaseAieraArgs, BaseAieraResponse, PaginatedResponse


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


class EventTypeMixin(BaseModel):
    """Mixin for models with event_type field."""

    @field_validator("event_type", mode="before", check_fields=False)
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
    """Search for corporate events including earnings calls, investor presentations, shareholder meetings, and more. Search across all companies by date range, or filter by specific companies using bloomberg_tickers, watchlists, indexes, sectors, or subsectors.

    EVENT TYPE MAPPING - CRITICAL:
    - "earnings calls" or "earnings" → use event_type='earnings' (ONE call)
    - "conference calls" or "presentations" → use event_type='presentation' (ONE call)
    - "investor meetings" → use event_type='investor_meeting' (ONE call)
    - "shareholder meetings" → use event_type='shareholder_meeting' (ONE call)
    - "conference calls AND meetings" → make TWO separate calls: first with event_type='presentation', then with event_type='investor_meeting', and combine the results
    - "all events" or "any type of event" → make MULTIPLE calls for each event_type you want to include and combine results

    MULTIPLE EVENT TYPES: This tool only accepts ONE event_type per call. To search multiple event types, you MUST make separate calls for each event_type and combine the results yourself.

    MULTIPLE COMPANIES: To find events for multiple companies, provide a comma-separated list of bloomberg_tickers in a SINGLE call. You do NOT need multiple calls for multiple companies.

    This tool provides access to a comprehensive database of corporate events with transcripts and summaries.
    """

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
        description="Optional: Bloomberg ticker(s) to filter by specific companies in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces (e.g., 'AAPL:US,MSFT:US,GOOGL:US'). Defaults to ':US' if country code omitted. Leave empty to search across all companies.",
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
    event_type: str = Field(
        default="earnings",
        description="Type of event to search for. ONLY ONE type per call - to search multiple types, make separate calls. Options: 'earnings' (quarterly earnings calls with Q&A), 'presentation' (investor conferences, company presentations at events - use this for 'conference calls'), 'investor_meeting' (investor day events, one-on-one meetings - use this for 'investor meetings'), 'shareholder_meeting' (annual/special shareholder meetings), 'special_situation' (M&A announcements, other corporate actions). Example: for 'conference calls AND meetings', make TWO calls: one with event_type='presentation' and one with event_type='investor_meeting'. Defaults to 'earnings'.",
    )
    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )

    @field_validator("event_type")
    @classmethod
    def validate_event_type_values(cls, v):
        """Validate event_type against allowed values."""
        valid_types = [
            "earnings",
            "presentation",
            "shareholder_meeting",
            "investor_meeting",
            "special_situation",
        ]
        if v not in valid_types:
            raise ValueError(f"event_type must be one of: {', '.join(valid_types)}")
        return v


class GetEventArgs(BaseToolArgs):
    """Get detailed information about a specific event including transcripts. If you need to retrieve more than one event, make multiple sequential calls. Transcripts are not availble for future events."""

    event_id: str = Field(
        description="Unique identifier for the event. Obtained from find_events tool."
    )
    transcript_section: Optional[str] = Field(
        default=None,
        description="Filter transcripts by section. Only applicable for earnings events. Options: 'presentation', 'q_and_a'.",
    )

    @field_validator("transcript_section")
    @classmethod
    def validate_transcript_section(cls, v):
        if v is not None and v not in ["presentation", "q_and_a"]:
            raise ValueError(
                "transcript_section must be either 'presentation' or 'q_and_a'"
            )
        return v


class GetUpcomingEventsArgs(BaseToolArgs, BloombergTickerMixin):
    """Get confirmed and estimated upcoming events within a date range. Requires one of the following: bloomberg_tickers (a comma-separated list of tickers),
    a watchlist_id, an index_id, a sector_id, or a subsector_id.
    To find upcoming events for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls.
    """

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


class TranscriptItem(BaseModel):
    """Individual transcript item from an event."""

    transcript_item_id: int = Field(
        ..., description="Unique transcript item identifier"
    )
    transcript: str = Field(..., description="Transcript text content")
    timestamp: Optional[datetime] = Field(
        None, description="Timestamp of the transcript item"
    )
    start_ms: Optional[int] = Field(None, description="Start time in milliseconds")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    speaker: Optional[str] = Field(None, description="Speaker name")
    speaker_type: Optional[str] = Field(
        None, description="Speaker type (e.g., 'final', 'estimate')"
    )
    created: Optional[datetime] = Field(None, description="Creation timestamp")
    modified: Optional[datetime] = Field(None, description="Modification timestamp")
    transcript_section: Optional[str] = Field(
        None, description="Section of transcript (e.g., 'presentation', 'q_and_a')"
    )
    transcript_version: Optional[int] = Field(
        None, description="Version of the transcript"
    )
    citation_information: Optional[CitationInfo] = Field(
        None, description="Citation information for this transcript item"
    )

    @field_validator("timestamp", "created", "modified", mode="before")
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

    @field_serializer("timestamp", "created", "modified")
    def serialize_datetime_fields(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime fields to ISO format string for JSON compatibility."""
        if value is None:
            return None
        return value.isoformat()


class EventItem(BaseModel):
    """Basic event information."""

    event_id: int = Field(..., description="Unique identifier for the event")
    title: str = Field(..., description="Event title")
    event_type: str = Field(..., description="Type of event")
    event_date: datetime = Field(..., description="Date and time of the event")
    equity: Optional[EquityInfo] = Field(None, description="Company equity information")
    event_category: Optional[str] = Field(None, description="Event category")
    expected_language: Optional[str] = Field(
        None, description="Expected language of the event"
    )
    grouping: Optional[GroupingInfo] = Field(
        None, description="Event grouping information"
    )
    summary: Optional[SummaryInfo] = Field(None, description="Event summary")
    citation_information: Optional[CitationInfo] = Field(
        None, description="Citation information"
    )
    transcripts: Optional[List[TranscriptItem]] = Field(
        None,
        description="List of transcript items (only populated when include_transcripts=true)",
    )

    @field_validator("event_date", mode="before")
    @classmethod
    def parse_event_date(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if isinstance(v, str):
            try:
                # Replace 'Z' with '+00:00' for ISO format compatibility
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                # If parsing fails, return current time as fallback
                return datetime.now()
        # If it's already a datetime object, return as is
        return v

    @field_serializer("event_date")
    def serialize_event_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class EventDetails(EventItem):
    """Detailed event information including transcripts and metadata."""

    description: Optional[str] = Field(None, description="Event description")
    transcript_preview: Optional[str] = Field(
        None, description="Preview of transcript content"
    )
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
    pagination: Optional[ApiPaginationInfo] = Field(
        None, description="Pagination information"
    )


class FindEventsResponse(BaseModel):
    """Response from finding events - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[ApiResponseData] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if request failed")


class GetEventResponse(BaseModel):
    """Response from getting a specific event - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[ApiResponseData] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if request failed")


class EstimateInfo(BaseModel):
    """Estimate information for future events."""

    call_type: Optional[str] = Field(None, description="Type of call/event")
    call_date: str = Field(..., description="Estimated date in ISO format")
    title: str = Field(..., description="Estimate title")


class ActualInfo(BaseModel):
    """Actual event information when available for an estimate."""

    scheduled_audio_call_id: int = Field(..., description="Scheduled audio call ID")
    call_type: Optional[str] = Field(None, description="Type of call")
    call_date: str = Field(..., description="Actual date in ISO format")
    title: str = Field(..., description="Actual event title")
    url: str = Field(..., description="URL to the event")


class EstimatedEventItem(BaseModel):
    """Individual estimated future event item."""

    estimate_id: int = Field(..., description="Unique identifier for the estimate")
    equity: Optional[EquityInfo] = Field(None, description="Company equity information")
    estimate: EstimateInfo = Field(..., description="Estimate information")
    actual: Optional[ActualInfo] = Field(
        None, description="Actual event info if confirmed"
    )
    citation_information: Optional[CitationInfo] = Field(
        None, description="Citation information"
    )


class UpcomingActualEventItem(BaseModel):
    """Individual upcoming confirmed event item."""

    event_id: int = Field(..., description="Unique identifier for the event")
    equity: Optional[EquityInfo] = Field(None, description="Company equity information")
    call_type: Optional[str] = Field(None, description="Type of call/event")
    call_date: str = Field(..., description="Event date in ISO format")
    title: str = Field(..., description="Event title")
    citation_information: Optional[CitationInfo] = Field(
        None, description="Citation information"
    )


class UpcomingEventsData(BaseModel):
    """Upcoming events response structure with estimates and actuals."""

    estimates: Optional[List[EstimatedEventItem]] = Field(
        None, description="Estimated future events"
    )
    actuals: Optional[List[UpcomingActualEventItem]] = Field(
        None, description="Confirmed upcoming events"
    )


class GetUpcomingEventsResponse(BaseModel):
    """Response from getting upcoming events - matches actual API structure."""

    instructions: Optional[List[str]] = Field(None, description="API instructions")
    response: Optional[UpcomingEventsData] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if request failed")
