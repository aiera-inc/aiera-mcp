#!/usr/bin/env python3

"""Third Bridge domain models for Aiera MCP."""

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


# Parameter models (extracted from params.py)
class FindThirdBridgeEventsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find expert insight events from Third Bridge filtered by date range and optional filters.

    ABOUT THIRD BRIDGE: Third Bridge provides expert network insights - interviews and forums
    with industry experts, former executives, and specialists who provide unique perspectives
    on companies, industries, and market trends. These are NOT earnings calls but expert interviews.

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

    start_date: str = Field(
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    end_date: str = Field(
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET).",
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
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
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

    thirdbridge_event_id: str = Field(
        serialization_alias="event_id",  # Serialize to API as "event_id"
        description="Unique identifier for the Third Bridge event. Obtain from find_third_bridge_events results (returned as 'event_id' in the response). Example: 'TB-12345'",
    )


# Response models - pass through API response structure
class FindThirdBridgeEventsResponse(BaseAieraResponse):
    """Response for find_third_bridge_events tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetThirdBridgeEventResponse(BaseAieraResponse):
    """Response for get_third_bridge_event tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
