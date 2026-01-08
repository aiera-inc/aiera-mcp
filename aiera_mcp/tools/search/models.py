#!/usr/bin/env python3

"""Pydantic models for Aiera search tools."""

from typing import List, Optional, Any
from datetime import datetime
from pydantic import (
    AliasChoices,
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
    """Semantic search within event transcripts for specific topics, quotes, or discussions.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content (quotes, topics, discussions) within transcripts
    - Use find_events FIRST to identify relevant events by date/company, then use this tool to search within their transcript content
    - Use this for targeted content extraction rather than reading full transcripts

    RETURNS: Relevant transcript segments with speaker attribution, timestamps, and relevance scores.
    Results are individual chunks, not full transcripts. Use get_event for complete transcripts.

    WORKFLOW EXAMPLE:
    1. User asks: "What did Apple's CEO say about AI?"
    2. First call find_events with bloomberg_ticker='AAPL:US' to get recent event IDs
    3. Then call search_transcripts with query_text='AI artificial intelligence' and the event_ids

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within transcripts. Examples: 'earnings guidance', 'regulatory concerns', 'revenue growth'"
    )

    event_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific event IDs to search within. Obtain event_ids from find_events results. Example: [12345, 67890]",
    )

    equity_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific equity IDs to filter search. Obtain equity_ids from find_equities results. Example: [100, 200]",
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
        description="Optional filter for specific transcript sections. Options: 'presentation' (prepared remarks by management, typically first 15-30 min), 'q_and_a' (analyst questions and management answers). Leave empty to search all sections.",
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
    """Semantic search within SEC filing content for specific topics, disclosures, or risk factors.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content (risk factors, disclosures, financial discussions) within SEC filings
    - Use find_filings FIRST to identify relevant filings by date/company/form type, then use this tool to search within their content
    - Use this for targeted content extraction rather than reading full filings

    RETURNS: Relevant filing chunks with context, filing metadata, and relevance scores.
    Results are individual sections/chunks, not full filings. Use get_filing for complete filing content.

    WORKFLOW EXAMPLE:
    1. User asks: "What are Tesla's main risk factors?"
    2. First call find_filings with bloomberg_ticker='TSLA:US' and form_number='10-K' to get recent filing IDs
    3. Then call search_filings with query_text='risk factors' and the filing_ids

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within filing chunks. Examples: 'revenue guidance', 'risk factors', 'acquisition strategy'. Optional if company_name or filing_type is provided.",
    )

    filing_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific filing IDs to search within. Obtain filing_ids from find_filings results. Example: [12345, 67890]",
    )

    equity_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific equity IDs to filter search. Obtain equity_ids from find_equities results. Example: [100, 200]",
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
        description="Filter for specific filing types. Common values: '10-K' (annual report), '10-Q' (quarterly report), '8-K' (current report/material events), '4' (insider trading), 'DEF 14A' (proxy statement). Leave empty to search all filing types.",
    )

    max_results: int = Field(
        default=20,
        description="Maximum number of filing chunks to return (10-50 recommended for optimal performance)",
    )


# Search result item models
class TranscriptSearchCitationMetadata(BaseModel):
    """Metadata for transcript search citation."""

    type: str = Field(
        description="The type of citation ('event', 'filing', 'company_doc', 'conference', or 'company')"
    )
    url_target: Optional[str] = Field(
        None,
        description="Whether the citation URL will go to Aiera or to an external source",
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

    score: float = Field(
        validation_alias=AliasChoices("_score", "score"),
        description="Search relevance score",
    )
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
    speaker_name: Optional[str] = Field(
        None, description="Name of the speaker. Can be null for some transcripts."
    )
    speaker_title: Optional[str] = Field(
        None, description="Title/role of the speaker. Can be null for some transcripts."
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

    type: str = Field(
        description="The type of citation ('event', 'filing', 'company_doc', 'conference', or 'company')"
    )
    url_target: Optional[str] = Field(
        None,
        description="Whether the citation URL will go to Aiera or to an external source",
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
        validation_alias=AliasChoices("_score", "score"),
        description="Search relevance score",
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


class SearchResearchArgs(BaseAieraArgs):
    """Semantic search within research content for specific topics, analyses, or insights.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content (analyses, insights, recommendations) within research documents
    - Use this for targeted content extraction from research reports

    RETURNS: Relevant research chunks with context, metadata, and relevance scores.
    Results are individual sections/chunks, not full research documents.

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within research chunks. Examples: 'revenue guidance', 'market outlook', 'analyst recommendations'.",
    )

    research_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific research IDs to search within. Example: [12345, 67890]",
    )

    equity_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific equity IDs to filter search. Obtain equity_ids from find_equities results. Example: [100, 200]",
    )

    start_date: str = Field(
        default="",
        description="Start date for research search in YYYY-MM-DD format. Example: '2024-01-01'. If not provided, defaults to 6 months ago.",
    )

    end_date: str = Field(
        default="",
        description="End date for research search in YYYY-MM-DD format. Example: '2024-12-31'. If not provided, defaults to today.",
    )

    max_results: int = Field(
        default=20,
        description="Maximum number of research chunks to return (10-50 recommended for optimal performance)",
    )


class SearchResearchResponse(BaseAieraResponse):
    """Response for search_research tool - matches actual API structure."""

    response: Optional[SearchResponseData] = Field(
        None, description="Response data container"
    )
