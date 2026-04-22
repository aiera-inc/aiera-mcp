#!/usr/bin/env python3

"""Third Bridge domain models for Aiera MCP."""

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer,
    model_validator,
)
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


# Parameter models (extracted from params.py)
class FindThirdBridgeEventsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find expert insight events from Third Bridge filtered by date range and optional filters.

    ABOUT THIRD BRIDGE: Third Bridge provides expert network insights - interviews and forums
    with industry experts, former executives, and specialists who provide unique perspectives
    on companies, industries, and market trends. These are NOT earnings calls but expert interviews.

    RETURNS METADATA AND SUMMARIES ONLY — NOT full transcripts. To retrieve full interview content, call get_third_bridge_event with the event_id from these results. For keyword-level search across many interviews, use search_thirdbridge instead.

    OPEN-ENDED QUERIES: For queries with no user-specified time period, OMIT start_date and end_date. Third Bridge content is valuable across its full historical corpus — only apply date filters when the user explicitly requests a specific time window.

    WHEN TO USE: Use this when you need expert/industry perspectives rather than official company communications.
    For official company events (earnings calls, presentations), use find_events instead.

    To find events for multiple companies, provide a comma-separated list of bloomberg_tickers in a single call.
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

    start_date: Optional[str] = Field(
        default=None,
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). For open-ended queries (no user-specified time period), OMIT this field to search the full historical corpus — do not default to a narrow window.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    end_date: Optional[str] = Field(
        default=None,
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). For open-ended queries (no user-specified time period), OMIT this field.",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter by title or description.",
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

    content_type: Optional[str] = Field(
        default=None,
        description="Filter by content type. Options: 'FORUM', 'PRIMER', 'COMMUNITY'.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetThirdBridgeEventArgs(BaseToolArgs):
    """Get detailed information about a specific Third Bridge expert insight event.

    ABOUT THIRD BRIDGE: Third Bridge provides expert network insights - interviews and forums
    with industry experts, former executives, and specialists who provide unique perspectives
    on companies, industries, and market trends.

    RESPONSE SIZE WARNING: This tool returns full transcript content from expert interviews,
    which can be extensive. The response includes agenda, key insights, and complete transcripts.

    WHEN TO USE:
    - Use this when you need complete expert interview content
    - Use this for full context on expert insights and analysis
    - For finding specific topics across multiple events, use find_third_bridge_events with filtering

    LIMITATIONS:
    - If you need multiple events, make separate sequential calls (one event_id per call)

    WORKFLOW: Use find_third_bridge_events first to obtain valid thirdbridge_event_ids.
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

    thirdbridge_event_id: Optional[str] = Field(
        default=None,
        serialization_alias="event_id",  # Serialize to API as "event_id"
        description="Unique identifier for the Third Bridge event. Obtain from find_third_bridge_events results (returned as 'event_id' in the response). Example: 'TB-12345'",
    )

    aiera_event_id: Optional[Union[int, str]] = Field(
        default=None,
        description="Aiera event ID (scheduled_audio_call_id) for the Third Bridge event. Obtain from search_thirdbridge results (returned as 'aiera_event_id').",
    )

    @model_validator(mode="after")
    def validate_at_least_one_id(self):
        if not self.thirdbridge_event_id and not self.aiera_event_id:
            raise ValueError(
                "At least one of 'thirdbridge_event_id' or 'aiera_event_id' must be provided."
            )
        return self


# Response models - pass through API response structure
class FindThirdBridgeEventsResponse(BaseAieraResponse):
    """Response for find_third_bridge_events tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetThirdBridgeEventResponse(BaseAieraResponse):
    """Response for get_third_bridge_event tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
