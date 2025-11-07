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
class EventItem(BaseModel):
    """Basic event information."""
    event_id: str = Field(..., description="Unique identifier for the event")
    title: str = Field(..., description="Event title")
    event_type: EventType = Field(..., description="Type of event")
    event_date: datetime = Field(..., description="Date and time of the event")
    company_name: Optional[str] = Field(None, description="Name of the company")
    ticker: Optional[str] = Field(None, description="Company ticker symbol")
    event_status: Optional[str] = Field(None, description="Status of the event (confirmed, estimated, etc.)")


class EventDetails(EventItem):
    """Detailed event information including transcripts and metadata."""
    description: Optional[str] = Field(None, description="Event description")
    transcript_preview: Optional[str] = Field(None, description="Preview of transcript content")
    audio_url: Optional[str] = Field(None, description="URL to event audio")


class FindEventsResponse(PaginatedResponse):
    """Response from finding events."""
    events: List[EventItem] = Field(..., description="List of matching events")


class GetEventResponse(BaseAieraResponse):
    """Response from getting a specific event."""
    event: EventDetails = Field(..., description="Detailed event information")


class GetUpcomingEventsResponse(BaseAieraResponse):
    """Response from getting upcoming events."""
    events: List[EventItem] = Field(..., description="List of upcoming events")