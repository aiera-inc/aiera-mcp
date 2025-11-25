#!/usr/bin/env python3

"""Pydantic models for Aiera search tools."""

from typing import List, Optional, Any, Union
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
        description="List of specific event IDs to search within. Obtained from source identification using CompanyEventsFinder."
    )
    max_results: int = Field(
        default=20,
        description="Maximum number of transcript segments to return across all events (10-50 recommended for optimal performance)",
    )
    index: str = Field(
        default="content_v1_transcript_processed",
        description="Transcript content index with processed segments, embeddings, and speaker attribution",
    )
    min_score: float = Field(
        default=0.2,
        description="Minimum relevance score threshold for returned segments (0.0-1.0). Lower values are more permissive and return more results. Default 0.2 balances relevance with coverage.",
    )
    transcript_section: str = Field(
        default="",
        description="Optional filter for specific transcript sections. Options: 'presentation' (prepared remarks), 'q_and_a' (Q&A session). If not provided, searches all sections.",
    )


class SearchFilingsArgs(BaseAieraArgs):
    """SEC filing discovery tool for identifying relevant filings before detailed content analysis.

    Returns filing metadata (excluding full text) optimized for filing identification and
    integration with FilingChunkSearch. Supports 60+ SEC document types with intelligent
    company name matching and comprehensive filtering capabilities.
    """

    company_name: str = Field(
        description="Company name to search filings for. Supports fuzzy matching for variations like 'Microsoft Corp', 'MSFT', 'Microsoft Corporation'. Examples: 'Apple', 'Tesla Inc', 'Amazon.com'"
    )
    start_date: str = Field(
        default="",
        description="Start date for filing search in YYYY-MM-DD format. Example: '2024-01-01'. If not provided, defaults to 6 months ago.",
    )
    end_date: str = Field(
        default="",
        description="End date for filing search in YYYY-MM-DD format. Example: '2024-12-31'. If not provided, defaults to today.",
    )
    document_types: List[str] = Field(
        default=[],
        description="Optional filter for specific SEC document types. Examples: ['10-K'], ['10-Q'], ['8-K'], ['4'], ['3', '4', '5'] (insider trading), ['SC 13D'], ['DEF 14A'], ['S-1'] (IPOs), ['20-F'] (foreign companies). Supports 60+ document types. Leave empty for all filing types.",
    )
    max_results: int = Field(
        default=5,
        description="Maximum number of filings to return (5-20 recommended for performance). Higher values may cause timeouts on large datasets.",
    )
    fuzzy_matching: bool = Field(
        default=True,
        description="Enable intelligent company name matching for subsidiaries, abbreviations, and name variations. Recommended for comprehensive results.",
    )
    sort_by: str = Field(
        default="desc",
        description="Sort order for results: 'desc' (newest first), 'asc' (oldest first), 'relevance' (best matches first)",
    )
    include_amendments: bool = Field(
        default=False,
        description="Include amended filings (like 10-K/A, 10-Q/A). False returns only original filings for cleaner results.",
    )


class SearchFilingChunksArgs(BaseAieraArgs):
    """Semantic search within SEC filing document chunks using embedding-based matching.

    Extracts relevant filing content chunks filtered by company, date, and filing type
    with high-quality semantic relevance scoring.
    """

    query_text: str = Field(
        default="",
        description="Search query for semantic matching within filing chunks. Examples: 'revenue guidance', 'risk factors', 'acquisition strategy'. Optional if company_name or filing_type is provided.",
    )
    company_name: str = Field(
        default="",
        description="Company name to filter filing chunks. Uses fuzzy search across company_name and company_legal_name fields. Supports variations like 'Apple Inc', 'AAPL', 'Apple Corporation'. Optional if query_text or filing_type is provided.",
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
    filing_ids: List[str] = Field(
        default_factory=list,
        description="Filter for specific filing IDs. Use to search chunks within specific filing documents. Examples: ['AAPL-10Q-2024-Q1', 'AAPL-10K-2023']. Optional.",
    )
    content_ids: List[str] = Field(
        default_factory=list,
        description="Filter for specific content_ids. Use to search within specific content pieces/chunks. Examples: ['25003532', '24964901']. Provides precise targeting of individual document chunks. Optional.",
    )
    max_results: int = Field(
        default=20,
        description="Maximum number of filing chunks to return (10-50 recommended for optimal performance)",
    )
    index: str = Field(
        default="content_v1_filing_chunks",
        description="Filing chunks index with processed segments, embeddings, and company attribution",
    )
    min_score: float = Field(
        default=0.2,
        description="Minimum relevance score threshold for returned chunks (0.0-1.0). Lower values are more permissive and return more results.",
    )

    @field_validator(
        "query_text", "company_name", "filing_type", "filing_ids", "content_ids"
    )
    @classmethod
    def validate_at_least_one_search_param(cls, v, info):
        """Ensure at least one of query_text, company_name, filing_type, filing_ids, or content_ids is provided."""
        # Get all field values at validation time
        if info.context and "all_fields" in info.context:
            all_fields = info.context["all_fields"]
        else:
            # During individual field validation, we can't check other fields yet
            return v

        query_text = all_fields.get("query_text", "").strip()
        company_name = all_fields.get("company_name", "").strip()
        filing_type = all_fields.get("filing_type", "").strip()
        filing_ids = all_fields.get("filing_ids", [])
        content_ids = all_fields.get("content_ids", [])

        if not any([query_text, company_name, filing_type, filing_ids, content_ids]):
            raise ValueError(
                "At least one of 'query_text', 'company_name', 'filing_type', 'filing_ids', or 'content_ids' must be provided"
            )
        return v

    @model_validator(mode="after")
    def validate_search_parameters(self):
        """Ensure at least one search parameter is provided."""
        if not any(
            [
                self.query_text.strip(),
                self.company_name.strip(),
                self.filing_type.strip(),
                self.filing_ids,
                self.content_ids,
            ]
        ):
            raise ValueError(
                "At least one of 'query_text', 'company_name', 'filing_type', 'filing_ids', or 'content_ids' must be provided"
            )
        return self


# Search result item models
class TranscriptSearchCitation(BaseModel):
    """Citation information for transcript search results."""

    title: str = Field(description="Title of the cited transcript")
    url: str = Field(description="URL to the specific transcript segment")


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


class SearchPaginationInfo(BaseModel):
    """Pagination information from search API."""

    total_count: Union[SearchTotalCount, int] = Field(
        description="Total count information - can be object or integer"
    )
    current_page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")

    @field_validator("total_count", mode="before")
    @classmethod
    def validate_total_count(cls, v):
        """Handle both object and integer formats for total_count."""
        if isinstance(v, int):
            # Convert integer to expected object format
            return SearchTotalCount(value=v, relation="eq")
        elif isinstance(v, dict):
            # Already in object format, let Pydantic handle validation
            return v
        else:
            # Let Pydantic handle other cases
            return v


class SearchResponseData(BaseModel):
    """Search response data container."""

    pagination: SearchPaginationInfo = Field(description="Pagination information")
    result: Optional[List[Any]] = Field(description="Search results (can be null)")


class TranscriptSearchResponseData(BaseModel):
    """Transcript search response data container with typed results."""

    pagination: SearchPaginationInfo = Field(description="Pagination information")
    result: Optional[List[TranscriptSearchItem]] = Field(
        description="Transcript search results (can be null)"
    )


# Response models
class SearchTranscriptsResponse(BaseAieraResponse):
    """Response for search_transcripts tool - matches actual API structure."""

    response: TranscriptSearchResponseData = Field(
        description="Response data container"
    )


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

    @field_serializer("date")
    def serialize_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class SearchFilingsResponse(BaseAieraResponse):
    """Response for search_filings tool - matches actual API structure."""

    response: SearchResponseData = Field(description="Response data container")


class FilingChunkSearchItem(BaseModel):
    """Individual filing chunk search result item."""

    date: datetime = Field(description="Date and time of the filing")
    primary_company_id: int = Field(description="Primary company identifier")
    content_id: str = Field(description="Filing chunk content identifier")
    filing_id: str = Field(description="Filing identifier")
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

    @field_serializer("date")
    def serialize_date(self, value: datetime) -> str:
        """Serialize datetime to ISO format string for JSON compatibility."""
        return value.isoformat()


class SearchFilingChunksResponse(BaseAieraResponse):
    """Response for search_filing_chunks tool - matches actual API structure."""

    response: SearchResponseData = Field(description="Response data container")
