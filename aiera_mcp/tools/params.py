#!/usr/bin/env python3

"""Pydantic parameter models for Aiera MCP tools."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any
from datetime import datetime, timedelta


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
        from .utils import correct_bloomberg_ticker
        return correct_bloomberg_ticker(v)


class CategoriesKeywordsMixin(BaseModel):
    """Mixin for models with categories and keywords fields."""

    @field_validator('categories', mode='before', check_fields=False)
    @classmethod
    def validate_categories(cls, v):
        """Automatically correct categories format."""
        if v is None:
            return v
        from .utils import correct_categories
        return correct_categories(v)

    @field_validator('keywords', mode='before', check_fields=False)
    @classmethod
    def validate_keywords(cls, v):
        """Automatically correct keywords format."""
        if v is None:
            return v
        from .utils import correct_keywords
        return correct_keywords(v)


class EventTypeMixin(BaseModel):
    """Mixin for models with event_type field."""

    @field_validator('event_type', mode='before', check_fields=False)
    @classmethod
    def validate_event_type_correction(cls, v):
        """Automatically correct event type format."""
        if v is None:
            return v
        from .utils import correct_event_type
        return correct_event_type(v)


class ProvidedIdsMixin(BaseModel):
    """Mixin for models with ID fields that need correction."""

    @field_validator('transcrippet_id', 'event_id', 'equity_id', 'speaker_id', 'transcript_item_id', mode='before', check_fields=False)
    @classmethod
    def validate_provided_ids(cls, v):
        """Automatically correct provided ID formats."""
        if v is None:
            return v
        from .utils import correct_provided_ids
        return correct_provided_ids(v)


# Event-related parameter models
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


# Filing-related parameter models
class FindFilingsArgs(BaseToolArgs, BloombergTickerMixin):
    """Find SEC filings filtered by date range and optional filters."""
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
    form_number: Optional[str] = Field(
        default=None,
        description="SEC form type to filter by (e.g., '10-K', '10-Q', '8-K')."
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


class GetFilingArgs(BaseToolArgs):
    """Get detailed information about a specific SEC filing."""
    filing_id: str = Field(
        description="Unique identifier for the SEC filing. Obtained from find_filings results."
    )


# Equity-related parameter models
class FindEquitiesArgs(BaseToolArgs, BloombergTickerMixin):
    """Find companies and equities using various identifiers or search."""
    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )
    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number (ISIN)."
    )
    ric: Optional[str] = Field(
        default=None,
        description="Reuters Instrument Code (RIC)."
    )
    ticker: Optional[str] = Field(
        default=None,
        description="Stock ticker symbol (without country code)."
    )
    permid: Optional[str] = Field(
        default=None,
        description="Refinitiv Permanent Identifier (PermID)."
    )
    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within company names, tickers, or relevant text fields."
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


class GetEquitySummariesArgs(BaseToolArgs, BloombergTickerMixin):
    """Get comprehensive summary information for one or more equities."""
    bloomberg_ticker: str = Field(
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )


class EmptyArgs(BaseToolArgs):
    """Parameter model for tools that take no arguments."""
    pass


class GetIndexConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific stock market index."""
    index: str = Field(
        description="Index identifier. Use get_available_indexes to find valid values."
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


class GetWatchlistConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific watchlist."""
    watchlist_id: str = Field(
        description="Watchlist identifier. Use get_available_watchlists to find valid values."
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


# Company documents parameter models
class FindCompanyDocsArgs(BaseToolArgs, BloombergTickerMixin, CategoriesKeywordsMixin):
    """Find company-published documents filtered by date range and optional filters."""
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
    categories: Optional[str] = Field(
        default=None,
        description="Document categories to filter by (e.g., 'annual_report,earnings_release'). Use get_company_doc_categories to find valid values. Multiple categories should be comma-separated without spaces."
    )
    keywords: Optional[str] = Field(
        default=None,
        description="Keywords to filter by (e.g., 'ESG,diversity'). Use get_company_doc_keywords to find valid values. Multiple keywords should be comma-separated without spaces."
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


class GetCompanyDocArgs(BaseToolArgs):
    """Get detailed information about a specific company document."""
    company_doc_id: str = Field(
        description="Unique identifier for the company document. Obtained from find_company_docs results."
    )


class SearchArgs(BaseToolArgs):
    """Parameter model for tools with optional search and pagination."""
    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within relevant text fields."
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


# Third Bridge parameter models
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


# Transcrippet parameter models
class FindTranscrippetsArgs(BaseToolArgs, ProvidedIdsMixin):
    """Find Transcrippets™ filtered by various identifiers and date ranges."""
    transcrippet_id: Optional[str] = Field(
        default=None,
        description="Transcrippet ID(s). For multiple IDs, use comma-separated list without spaces."
    )
    event_id: Optional[str] = Field(
        default=None,
        description="Event ID(s) to filter by. For multiple IDs, use comma-separated list without spaces."
    )
    equity_id: Optional[str] = Field(
        default=None,
        description="Equity ID(s) to filter by. For multiple IDs, use comma-separated list without spaces."
    )
    speaker_id: Optional[str] = Field(
        default=None,
        description="Speaker ID(s) to filter by. For multiple IDs, use comma-separated list without spaces."
    )
    transcript_item_id: Optional[str] = Field(
        default=None,
        description="Transcript item ID(s) to filter by. For multiple IDs, use comma-separated list without spaces."
    )
    created_start_date: Optional[str] = Field(
        default=None,
        description="Start date for transcrippet creation filter in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    created_end_date: Optional[str] = Field(
        default=None,
        description="End date for transcrippet creation filter in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )


class CreateTranscrippetArgs(BaseToolArgs):
    """Create a new Transcrippet™ from an event transcript segment."""
    event_id: int = Field(
        description="Event ID from which to create the transcrippet. Use find_events to obtain valid event IDs."
    )
    transcript: str = Field(
        description="The transcript text content to include in the transcrippet."
    )
    transcript_item_id: int = Field(
        description="ID of the starting transcript item for the segment."
    )
    transcript_item_offset: int = Field(
        ge=0,
        description="Character offset within the starting transcript item."
    )
    transcript_end_item_id: int = Field(
        description="ID of the ending transcript item for the segment."
    )
    transcript_end_item_offset: int = Field(
        ge=0,
        description="Character offset within the ending transcript item."
    )
    company_id: Optional[int] = Field(
        default=None,
        description="Optional company ID to associate with the transcrippet."
    )
    equity_id: Optional[int] = Field(
        default=None,
        description="Optional equity ID to associate with the transcrippet."
    )


class DeleteTranscrippetArgs(BaseToolArgs):
    """Delete a Transcrippet™ by its ID."""
    transcrippet_id: str = Field(
        description="Unique identifier for the transcrippet to delete. This operation cannot be undone."
    )