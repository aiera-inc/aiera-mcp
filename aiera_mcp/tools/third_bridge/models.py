#!/usr/bin/env python3

"""Third Bridge domain models for Aiera MCP."""

from pydantic import AliasChoices, BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Union

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
class FindThirdBridgeEventsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find expert insight events from Third Bridge filtered by date range and optional filters. To find events for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls."""

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
    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )
    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class GetThirdBridgeEventArgs(BaseToolArgs):
    """Get detailed information about a specific Third Bridge expert insight event. If you need to retrieve more than one event, make multiple sequential calls."""

    thirdbridge_event_id: str = Field(
        serialization_alias="event_id",  # Serialize to API as "event_id"
        description="Unique identifier for the Third Bridge event. Obtained from find_third_bridge_events results.",
    )


# Search result item models
class ThirdBridgeCitationMetadata(BaseModel):
    """Metadata for third bridge citation."""

    type: str = Field(
        description="The type of citation ('event', 'filing', 'company_doc', 'conference', or 'company')"
    )
    url_target: Optional[str] = Field(
        None, description="Whether the URL will be to Aiera or an external source"
    )
    company_id: Optional[int] = Field(None, description="Company identifier")
    event_id: Optional[int] = Field(None, description="Event identifier")
    transcript_item_id: Optional[int] = Field(
        None, description="Transcript item identifier"
    )


# Citation models
class ThirdBridgeCitationInfo(BaseModel):
    """Citation information for Third Bridge events."""

    title: str = Field(description="Event title")
    url: str = Field(description="URL to the event")
    metadata: Optional[ThirdBridgeCitationMetadata] = Field(
        None, description="Additional metadata about the citation"
    )


# Response models (extracted from responses.py)
class ThirdBridgeEventItem(BaseModel):
    """Third Bridge event item."""

    thirdbridge_event_id: str = Field(
        validation_alias="event_id", description="Event identifier"
    )
    content_type: str = Field(description="Content type (e.g., FORUM, COMMUNITY)")
    call_date: Optional[str] = Field(
        default="", description="Event date and time as string"
    )
    title: str = Field(description="Event title")
    language: str = Field(description="Event language")
    agenda: List[str] = Field(description="Event agenda items")
    insights: Optional[List[str]] = Field(
        None, description="Key insights from the event (can be null)"
    )
    transcripts: Optional[List["ThirdBridgeTranscriptItem"]] = Field(
        None, description="Event transcripts (when included)"
    )
    citation_information: Optional[ThirdBridgeCitationInfo] = Field(
        None,
        description="Citation information",
        validation_alias=AliasChoices("citation_information", "citation_block"),
    )


class ThirdBridgeSpecialist(BaseModel):
    """Third Bridge specialist/expert information."""

    title: str = Field(description="Expert's job title")
    initials: str = Field(description="Expert's initials")


class ThirdBridgeModerator(BaseModel):
    """Third Bridge moderator information."""

    id: str = Field(description="Moderator identifier")
    initials: str = Field(description="Moderator's initials")


class ThirdBridgeTranscriptItem(BaseModel):
    """Third Bridge transcript item."""

    start_ms: Optional[int] = Field(None, description="Start time in milliseconds")
    duration_ms: Optional[int] = Field(None, description="Duration in milliseconds")
    transcript: Optional[str] = Field(None, description="Transcript text content")
    citation_information: Optional[ThirdBridgeCitationInfo] = Field(
        None, description="Citation information for this transcript item"
    )


class ThirdBridgeEventDetails(BaseModel):
    """Detailed Third Bridge event information."""

    thirdbridge_event_id: str = Field(
        validation_alias="event_id",  # Parse from API as "event_id"
        description="Event identifier",
    )
    content_type: str = Field(description="Content type (e.g., FORUM, COMMUNITY)")
    call_date: Optional[str] = Field(
        default="", description="Event date and time as string"
    )
    title: str = Field(description="Event title")
    language: str = Field(description="Event language")
    agenda: Optional[List[str]] = Field(None, description="Event agenda items")
    insights: Optional[List[str]] = Field(
        None, description="Key insights from the event"
    )
    citation_information: Optional[ThirdBridgeCitationInfo] = Field(
        None,
        description="Citation information",
        validation_alias=AliasChoices("citation_information", "citation_block"),
    )
    specialists: Optional[List[ThirdBridgeSpecialist]] = Field(
        None, description="Expert specialists participating in the event"
    )
    moderators: Optional[List[ThirdBridgeModerator]] = Field(
        None, description="Moderators of the event"
    )
    transcripts: Optional[List[ThirdBridgeTranscriptItem]] = Field(
        None, description="Full event transcripts"
    )


# Response classes
class ThirdBridgePaginationInfo(BaseModel):
    """Pagination information from Third Bridge API."""

    total_count: int = Field(description="Total number of events")
    current_page: int = Field(description="Current page number")
    total_pages: int = Field(description="Total number of pages")
    page_size: int = Field(description="Number of events per page")


class ThirdBridgeResponseData(BaseModel):
    """Third Bridge response data container."""

    pagination: ThirdBridgePaginationInfo = Field(description="Pagination information")
    data: List[ThirdBridgeEventItem] = Field(description="List of Third Bridge events")


class FindThirdBridgeEventsResponse(BaseAieraResponse):
    """Response for find_third_bridge_events tool - matches actual API structure."""

    response: Optional[ThirdBridgeResponseData] = Field(
        None, description="Response data container"
    )


class GetThirdBridgeEventResponse(BaseAieraResponse):
    """Response for get_third_bridge_event tool."""

    event: Optional[ThirdBridgeEventDetails] = Field(
        default=None, description="Detailed Third Bridge event (None if not found)"
    )
