#!/usr/bin/env python3

"""Pydantic models for Aiera search tools."""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    field_serializer,
    model_validator,
    ValidationInfo,
)
from pydantic_core import PydanticCustomError

from ..common.models import BaseAieraArgs, BaseAieraResponse


class SearchTranscriptsArgs(BaseAieraArgs):
    """Semantic search within specific transcript events using embedding-based matching.

    Tool for extracting detailed transcript content from events identified
    in prior searches. Provides speaker attribution and contextual results.
    """

    query_text: str = Field(
        description="Search query for semantic matching within transcripts. Examples: 'earnings guidance', 'regulatory concerns', 'revenue growth'"
    )
    event_ids: List[int] = Field(
        description="List of specific event IDs to search within. Obtained from source identification using find_events."
    )
    equity_ids: List[int] = Field(
        description="List of specific equity IDs to filter search. Obtained from source identification using find_equities."
    )
    start_date: str = Field(
        default="",
        description="Start date for transcripts search in YYYY-MM-DD format. Example: '2024-01-01'.",
    )
    end_date: str = Field(
        default="",
        description="End date for transcripts search in YYYY-MM-DD format. Example: '2024-12-31'.",
    )
    transcript_section: str = Field(
        default="",
        description="Optional filter for specific transcript sections. Options: 'presentation' (prepared remarks), 'q_and_a' (Q&A session). If not provided, searches all sections.",
    )
    event_type: str = Field(
        default="earnings",
        description="Type of event to include within search. ONLY ONE type per call - to search multiple types, make separate calls. Options: 'earnings' (quarterly earnings calls with Q&A), 'presentation' (investor conferences, company presentations at events - use this for conferences), 'investor_meeting' (investor day events, one-on-one meetings - use this for investor meetings), 'shareholder_meeting' (annual/special shareholder meetings), 'special_situation' (M&A announcements, other corporate actions). Example: for 'conference calls AND meetings', make TWO calls: one with event_type='presentation' and one with event_type='investor_meeting'. Defaults to 'earnings'.",
    )
    max_results: int = Field(
        default=20,
        description="Maximum number of transcript segments to return across all events (10-50 recommended for optimal performance)",
    )


class SearchFilingsArgs(BaseAieraArgs):
    """Semantic search within SEC filing document chunks using embedding-based matching.

    Extracts relevant filing content chunks filtered by company, date, and filing type
    with high-quality semantic relevance scoring.
    """

    query_text: str = Field(
        description="Search query for semantic matching within filing chunks. Examples: 'revenue guidance', 'risk factors', 'acquisition strategy'. Optional if company_name or filing_type is provided.",
    )
    filing_ids: List[str] = Field(
        default_factory=list,
        description="Filter for specific filing IDs. Use to search chunks within specific filing documents. Examples: ['AAPL-10Q-2024-Q1', 'AAPL-10K-2023']. Optional.",
    )
    equity_ids: List[int] = Field(
        description="List of specific equity IDs to filter search. Obtained from source identification using find_equities."
    )
    start_date: str = Field(
        default="",
        description="Start date for filing chunks search in YYYY-MM-DD format. Example: '2024-01-01'. If not provided, defaults to 6 months ago.",
    )
    end_date: str = Field(
        default="",
        description="End date for filing chunks search in YYYY-MM-DD format. Example: '2024-12-31'. If not provided, defaults to today.",
    )
    filing_type: str = Field(
        default="",
        description="Filter for specific filing types. Examples: '10-K', '10-Q', '8-K', '4', 'DEF 14A'. Optional if query_text or company_name is provided.",
    )
    max_results: int = Field(
        default=20,
        description="Maximum number of filing chunks to return (10-50 recommended for optimal performance)",
    )


# Search result item models
class TranscriptSearchCitationMetadata(BaseModel):
    """Metadata for transcript search citation."""

    type: str = Field(description="Type of citation (e.g., 'event')")
    url_target: Optional[str] = Field(
        None, description="Target for URL (e.g., 'aiera')"
    )
    company_id: Optional[int] = Field(None, description="Company identifier")
    event_id: Optional[int] = Field(None, description="Event identifier")
    transcript_item_id: Optional[int] = Field(
        None, description="Transcript item identifier"
    )


class TranscriptSearchCitation(BaseModel):
    """Citation information for transcript search results."""

    title: str = Field(description="Title of the cited transcript")
    url: str = Field(description="URL to the specific transcript segment")
    metadata: Optional[TranscriptSearchCitationMetadata] = Field(
        None, description="Additional metadata about the citation"
    )


class TranscriptSearchItem(BaseModel):
    """Individual transcript search result item."""

    date: datetime = Field(description="Date and time of the transcript")
    primary_company_id: int = Field(description="Primary company identifier.")
    transcript_item_id: int = Field(
        validation_alias="content_id",
        description="Transcript item identifier (aliased from content_id)",
    )
    transcript_event_id: int = Field(description="Event identifier for the transcript")
    transcript_section: Optional[str] = Field(
        description="Section of transcript (e.g., 'q_and_a', 'presentation'). Can be null for some transcripts."
    )
    text: str = Field(description="The matching text content from the transcript")
    primary_equity_id: int = Field(
        description="Primary equity identifier. Can be found using the find_equities tool."
    )
    title: str = Field(description="Title of the event/transcript")
    citation_information: TranscriptSearchCitation = Field(
        description="Citation details for this result"
    )

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if isinstance(v, str):
            try:
                # Replace 'Z' with '+00:00' for ISO format compatibility
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return datetime.now()
        # If it's already a datetime object, return as is
        return v

    @field_serializer("date")
    def serialize_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class TranscriptSearchResult(BaseModel):
    """Container for transcript search results."""

    result: List[TranscriptSearchItem] = Field(
        description="List of transcript search results"
    )


# Search response pagination structure
class SearchTotalCount(BaseModel):
    """Total count structure from search API."""

    value: int = Field(description="Total count value")
    relation: str = Field(description="Relation type (e.g., 'eq')")


class SearchResponseData(BaseModel):
    """Search response data container."""

    result: Optional[List[Any]] = Field(description="Search results (can be null)")


class TranscriptSearchResponseData(BaseModel):
    """Transcript search response data container with typed results."""

    result: Optional[List[TranscriptSearchItem]] = Field(
        description="Transcript search results (can be null)"
    )


# Response models
class SearchTranscriptsResponse(BaseAieraResponse):
    """Response for search_transcripts tool - matches actual API structure."""

    response: Optional[TranscriptSearchResponseData] = Field(
        None, description="Response data container"
    )


class FilingSearchCitationMetadata(BaseModel):
    """Metadata for filing search citation."""

    type: str = Field(description="Type of citation (e.g., 'filing')")
    url_target: Optional[str] = Field(
        None, description="Target for URL (e.g., 'aiera')"
    )
    company_id: Optional[int] = Field(None, description="Company identifier")
    content_id: Optional[int] = Field(None, description="Content identifier")
    filing_id: Optional[int] = Field(None, description="Filing identifier")


class FilingSearchCitation(BaseModel):
    """Citation information for filing search results."""

    title: str = Field(description="Title of the cited filing")
    url: str = Field(description="URL to the specific filing segment")
    metadata: Optional[FilingSearchCitationMetadata] = Field(
        None, description="Additional metadata about the citation"
    )


class FilingSearchItem(BaseModel):
    """Individual filing chunk search result item."""

    date: datetime = Field(description="Date and time of the filing")
    primary_company_id: int = Field(description="Primary company identifier")
    content_id: str = Field(description="Filing chunk content identifier")
    filing_id: str = Field(description="Filing identifier")
    company_common_name: Optional[str] = Field(
        default=None, description="Company common name"
    )
    text: str = Field(description="The matching text content from the filing chunk")
    primary_equity_id: int = Field(
        description="Primary equity identifier. Can be found using the find_equities tool."
    )
    title: str = Field(description="Title of the filing")
    filing_type: Optional[str] = Field(
        default=None, description="Type of SEC filing (e.g., '10-K', '10-Q', '8-K')"
    )
    score: float = Field(
        validation_alias="_score",
        description="Search relevance score (aliased from _score)",
    )
    citation_information: FilingSearchCitation = Field(
        description="Citation details for this result"
    )

    @field_validator("date", mode="before")
    @classmethod
    def parse_date(cls, v):
        """Parse ISO format datetime strings to datetime objects."""
        if isinstance(v, str):
            try:
                # Replace 'Z' with '+00:00' for ISO format compatibility
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                return datetime.now()
        # If it's already a datetime object, return as is
        return v

    @field_serializer("date")
    def serialize_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class SearchFilingsResponse(BaseAieraResponse):
    """Response for search_filings tool - matches actual API structure."""

    response: Optional[SearchResponseData] = Field(
        None, description="Response data container"
    )
