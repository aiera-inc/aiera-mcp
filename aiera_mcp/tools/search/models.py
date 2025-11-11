#!/usr/bin/env python3

"""Pydantic models for Aiera search tools."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, field_serializer

from ..common.models import BaseAieraArgs, BaseAieraResponse


class SearchTranscriptsArgs(BaseAieraArgs):
    """Perform a semantic search against all event transcripts."""
    search: str = Field(description="Search query text for semantic search against transcripts")
    event_ids: Optional[str] = Field(
        default=None,
        description="Comma-separated list of event IDs to filter by. Use find_events to obtain valid event IDs."
    )
    equity_ids: Optional[str] = Field(
        default=None,
        description="Comma-separated list of equity IDs to filter by. Use find_equities to obtain valid equity IDs."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date for filtering in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET)."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date for filtering in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET)."
    )
    transcript_section: Optional[str] = Field(
        default=None,
        description="Filter by transcript section. Must be one of: 'presentation', 'q_and_a'."
    )
    event_type: Optional[str] = Field(
        default="earnings",
        description="Filter by event type. Options: 'earnings', 'presentation', 'shareholder_meeting', 'investor_meeting', 'special_situation'."
    )
    page: int = Field(default=1, description="Page number for pagination (1-based).", ge=1)
    page_size: int = Field(default=50, description="Number of items per page (1-100).", ge=1, le=100)


class SearchFilingsArgs(BaseAieraArgs):
    """Perform a semantic search against all SEC filings."""
    search: str = Field(description="Search query text for semantic search against SEC filings")
    filing_ids: Optional[str] = Field(
        default=None,
        description="Comma-separated list of filing IDs to filter by. Use find_filings to obtain valid filing IDs."
    )
    equity_ids: Optional[str] = Field(
        default=None,
        description="Comma-separated list of equity IDs to filter by. Use find_equities to obtain valid equity IDs."
    )
    filing_types: Optional[str] = Field(
        default=None,
        description="Comma-separated list of filing types to filter by (e.g., '10-K', '10-Q', '8-K')."
    )
    start_date: Optional[str] = Field(
        default=None,
        description="Start date for filtering in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET)."
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date for filtering in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET)."
    )
    page: int = Field(default=1, description="Page number for pagination (1-based).", ge=1)
    page_size: int = Field(default=50, description="Number of items per page (1-100).", ge=1, le=100)


# Search result item models
class TranscriptSearchCitation(BaseModel):
    """Citation information for transcript search results."""
    title: str = Field(description="Title of the cited transcript")
    url: str = Field(description="URL to the specific transcript segment")


class TranscriptSearchItem(BaseModel):
    """Individual transcript search result item."""
    date: datetime = Field(description="Date and time of the transcript")
    primary_company_id: int = Field(description="Primary company identifier")
    transcript_item_id: int = Field(alias="content_id", description="Transcript item identifier (aliased from content_id)")
    transcript_event_id: int = Field(description="Event identifier for the transcript")
    transcript_section: str = Field(description="Section of transcript (e.g., 'q_and_a', 'presentation')")
    text: str = Field(description="The matching text content from the transcript")
    primary_equity_id: int = Field(description="Primary equity identifier")
    title: str = Field(description="Title of the event/transcript")
    score: float = Field(alias="_score", description="Search relevance score (aliased from _score)")
    citation_information: TranscriptSearchCitation = Field(description="Citation details for this result")

    @field_serializer('date')
    def serialize_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class TranscriptSearchResult(BaseModel):
    """Container for transcript search results."""
    result: List[TranscriptSearchItem] = Field(description="List of transcript search results")


# Response models
class SearchTranscriptsResponse(BaseAieraResponse):
    """Response for search_transcripts tool."""
    instrument_type: str = Field(default="transcript_search", description="Type of instrument searched")
    error_messages: List[str] = Field(default=[], description="List of error messages if any")
    error_count: int = Field(default=0, description="Count of errors encountered")
    result: List[TranscriptSearchItem] = Field(description="List of transcript search results")


class FilingSearchCitation(BaseModel):
    """Citation information for filing search results."""
    title: str = Field(description="Title of the cited filing")
    url: str = Field(description="URL to the specific filing segment")


class FilingSearchItem(BaseModel):
    """Individual filing search result item."""
    date: datetime = Field(description="Date and time of the filing")
    primary_company_id: int = Field(description="Primary company identifier")
    content_id: int = Field(description="Filing content identifier")
    filing_id: int = Field(description="Filing identifier")
    text: str = Field(description="The matching text content from the filing")
    primary_equity_id: int = Field(description="Primary equity identifier")
    title: str = Field(description="Title of the filing")
    filing_type: Optional[str] = Field(default=None, description="Type of SEC filing (e.g., '10-K', '10-Q', '8-K')")
    score: float = Field(alias="_score", description="Search relevance score (aliased from _score)")
    citation_information: FilingSearchCitation = Field(description="Citation details for this result")

    @field_serializer('date')
    def serialize_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class SearchFilingsResponse(BaseAieraResponse):
    """Response for search_filings tool."""
    instrument_type: str = Field(default="filing_search", description="Type of instrument searched")
    error_messages: List[str] = Field(default=[], description="List of error messages if any")
    error_count: int = Field(default=0, description="Count of errors encountered")
    result: List[FilingSearchItem] = Field(description="List of filing search results")