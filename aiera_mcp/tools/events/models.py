#!/usr/bin/env python3

"""Events domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, Any, Union

from ..common.models import BaseAieraResponse


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

    start_date: str = Field(
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    end_date: str = Field(
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter events by title.",
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

    conference_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific conference. Use find_conferences to find valid IDs.",
    )

    event_type: str = Field(
        default="earnings",
        description="Type of event to search for. ONLY ONE type per call - to search multiple types, make separate calls. Options: 'earnings' (quarterly earnings calls with Q&A), 'presentation' (investor conferences, company presentations at events - use this for 'conference calls'), 'investor_meeting' (investor day events, one-on-one meetings - use this for 'investor meetings'), 'shareholder_meeting' (annual/special shareholder meetings), 'special_situation' (M&A announcements, other corporate actions). Example: for 'conference calls AND meetings', make TWO calls: one with event_type='presentation' and one with event_type='investor_meeting'. Defaults to 'earnings'.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25, ge=1, le=25, description="Number of items per page (1-25)."
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


# Parameter models (extracted from params.py)
class FindConferencesArgs(BaseToolArgs, BloombergTickerMixin, EventTypeMixin):
    """Search for conferences. Search across all conferences by date range.

    This tool provides access to a comprehensive database of upcoming and historical conferences.
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

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter conferences by title.",
    )

    start_date: str = Field(
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    end_date: str = Field(
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Required to define the search period.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25, ge=1, le=25, description="Number of items per page (1-25)."
    )


class GetEventArgs(BaseToolArgs):
    """Get detailed information about a specific event including the full transcript.

    RESPONSE SIZE WARNING: This tool returns large text content. The transcript field can contain
    thousands of words for earnings calls and presentations. Consider using search_transcripts
    for targeted content extraction instead of reading full transcripts.

    WHEN TO USE:
    - Use this when you need the complete transcript text
    - Use this when you need full event metadata and summary
    - For finding specific quotes or topics, prefer search_transcripts instead

    LIMITATIONS:
    - Transcripts are not available for future events
    - If you need multiple events, make separate sequential calls (one event_id per call)

    WORKFLOW: Use find_events first to obtain valid event_ids.
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

    event_id: str = Field(
        description="Unique identifier for the event. Obtain event_id from find_events or search_transcripts results. Example: '12345'"
    )


class GetUpcomingEventsArgs(BaseToolArgs, BloombergTickerMixin):
    """Get confirmed and estimated upcoming events within a date range. Requires one of the following: bloomberg_tickers (a comma-separated list of tickers),
    a watchlist_id, an index_id, a sector_id, or a subsector_id.
    To find upcoming events for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls.
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


# Response models - pass through API response structure
class FindEventsResponse(BaseAieraResponse):
    """Response for find_events tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class FindConferencesResponse(BaseAieraResponse):
    """Response for find_conferences tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetEventResponse(BaseAieraResponse):
    """Response for get_event tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetUpcomingEventsResponse(BaseAieraResponse):
    """Response for get_upcoming_events tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
