#!/usr/bin/env python3

"""Third Bridge domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any
from datetime import datetime

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
class FindThirdBridgeEventsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find expert insight events from Third Bridge filtered by date range and optional filters."""
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


class GetThirdBridgeEventArgs(BaseToolArgs):
    """Get detailed information about a specific Third Bridge expert insight event."""
    event_id: str = Field(
        description="Unique identifier for the Third Bridge event. Obtained from find_third_bridge_events results."
    )


# Response models (extracted from responses.py)
class ThirdBridgeEventItem(BaseModel):
    """Third Bridge event item."""
    event_id: str = Field(description="Event identifier")
    title: str = Field(description="Event title")
    company_name: Optional[str] = Field(description="Associated company")
    event_date: datetime = Field(description="Event date and time")
    expert_name: Optional[str] = Field(description="Expert name")
    expert_title: Optional[str] = Field(description="Expert title/role")


class ThirdBridgeEventDetails(ThirdBridgeEventItem):
    """Detailed Third Bridge event information."""
    agenda: Optional[str] = Field(description="Event agenda")
    insights: Optional[str] = Field(description="Key insights")
    transcript: Optional[str] = Field(description="Event transcript")


# Response classes
class FindThirdBridgeEventsResponse(PaginatedResponse):
    """Response for find_third_bridge_events tool."""
    events: List[ThirdBridgeEventItem] = Field(description="List of Third Bridge events")


class GetThirdBridgeEventResponse(BaseAieraResponse):
    """Response for get_third_bridge_event tool."""
    event: ThirdBridgeEventDetails = Field(description="Detailed Third Bridge event")