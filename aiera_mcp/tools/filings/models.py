#!/usr/bin/env python3

"""Filings domain models for Aiera MCP."""

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
class FindFilingsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find SEC filings filtered by date range and optional filters. To find filings for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls."""

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
        description="Search term to filter filings by title.",
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

    form_number: Optional[str] = Field(
        default=None,
        description="SEC form type to filter by. Common values: '10-K' (annual report), '10-Q' (quarterly report), '8-K' (current report/material events), '4' (insider trading), 'DEF 14A' (proxy statement), 'S-1' (IPO registration), '13F' (institutional holdings). Leave empty to include all form types.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetFilingArgs(BaseToolArgs):
    """Get detailed information about a specific SEC filing including summary and content.

    RESPONSE SIZE WARNING: This tool returns large text content. SEC filings (especially 10-K and 10-Q)
    can contain extensive text. Consider using search_filings for targeted content extraction
    instead of reading full filing content.

    WHEN TO USE:
    - Use this when you need the complete filing summary and metadata
    - Use this when you need full filing content for a specific document
    - For finding specific disclosures or risk factors, prefer search_filings instead

    WORKFLOW: Use find_filings first to obtain valid filing_ids.
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

    filing_id: Union[str, int] = Field(
        description="Unique identifier for the SEC filing. Obtain filing_id from find_filings or search_filings results. Example: '98765'"
    )

    @field_validator("filing_id", mode="before")
    @classmethod
    def coerce_filing_id_to_str(cls, v):
        """Accept both string and int filing IDs."""
        if v is not None:
            return str(v)
        return v


# Response models - pass through API response structure
class FindFilingsResponse(BaseAieraResponse):
    """Response for find_filings tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetFilingResponse(BaseAieraResponse):
    """Response for get_filing tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
