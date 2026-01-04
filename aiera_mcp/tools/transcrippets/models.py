#!/usr/bin/env python3

"""Transcrippets domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any

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


class ProvidedIdsMixin(BaseModel):
    """Mixin for models with ID fields that need correction."""

    @field_validator(
        "transcrippet_id",
        "event_id",
        "equity_id",
        "speaker_id",
        "transcript_item_id",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_provided_ids(cls, v):
        """Automatically correct provided ID formats."""
        if v is None:
            return v
        from ..utils import correct_provided_ids

        return correct_provided_ids(v)


# Parameter models (extracted from params.py)
class FindTranscrippetsArgs(BaseToolArgs, ProvidedIdsMixin):
    """Find saved Transcrippets™ (curated transcript highlights and audio clips).

    WHAT ARE TRANSCRIPPETS: Transcrippets are user-saved segments from event transcripts,
    useful for capturing and sharing:
    - Key quotes from executives
    - Important announcements and guidance
    - Notable Q&A exchanges
    - Memorable soundbites with synchronized audio

    WHEN TO USE:
    - Use this to retrieve previously saved transcript clips
    - Use this to check if clips exist for specific events, speakers, or companies
    - Use this to find clips created within a date range

    Each Transcrippet includes a public_url for sharing the clip with others.
    """

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    transcrippet_id: Optional[str] = Field(
        default=None,
        description="Filter by specific Transcrippet ID(s). For multiple IDs, use comma-separated list without spaces. Example: '123,456,789'",
    )

    event_id: Optional[str] = Field(
        default=None,
        description="Filter by event ID(s) to find Transcrippets from specific events. Obtain event_ids from find_events. For multiple IDs, use comma-separated list. Example: '12345,67890'",
    )

    equity_id: Optional[str] = Field(
        default=None,
        description="Filter by equity ID(s) to find Transcrippets for specific companies. Obtain equity_ids from find_equities. For multiple IDs, use comma-separated list. Example: '100,200'",
    )

    speaker_id: Optional[str] = Field(
        default=None,
        description="Filter by speaker ID(s) to find Transcrippets featuring specific speakers. For multiple IDs, use comma-separated list. Example: '555,666'",
    )

    transcript_item_id: Optional[str] = Field(
        default=None,
        description="Filter by transcript item ID(s). Obtain from get_event transcript results. For multiple IDs, use comma-separated list. Example: '11111,22222'",
    )

    created_start_date: Optional[str] = Field(
        default=None,
        description="Start date for transcrippet creation filter in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )

    created_end_date: Optional[str] = Field(
        default=None,
        description="End date for transcrippet creation filter in ISO format (YYYY-MM-DD).",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class CreateTranscrippetArgs(BaseToolArgs):
    """Create a new Transcrippet™ (saved transcript clip) from an event transcript segment.

    WHAT THIS DOES: Creates a shareable audio/text clip from a specific portion of an event
    transcript. The clip can be shared via a public URL.

    REQUIRED WORKFLOW:
    1. Use find_events to get the event_id for the event containing the quote
    2. Use get_event to retrieve the full transcript with transcript_item_ids
    3. Identify the start and end transcript items and character offsets for your clip
    4. Call this tool with the precise segment boundaries

    PARAMETERS EXPLAINED:
    - event_id: The event containing the transcript (from find_events)
    - transcript_item_id: Starting transcript item ID (from get_event transcripts)
    - transcript_item_offset: Character position within the starting item where clip begins
    - transcript_end_item_id: Ending transcript item ID
    - transcript_end_item_offset: Character position within the ending item where clip ends
    - transcript: The actual text content being clipped

    The created Transcrippet will include synchronized audio playback.
    """

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    event_id: int = Field(
        description="Event ID containing the transcript to clip. Obtain from find_events results. Example: 12345"
    )

    transcript: str = Field(
        description="The exact transcript text content to include in the Transcrippet. This should match the text between your start and end positions."
    )

    transcript_item_id: int = Field(
        description="ID of the starting transcript item for the segment. Obtain from get_event transcript results (each transcript item has a transcript_item_id). Example: 98765"
    )

    transcript_item_offset: int = Field(
        ge=0,
        description="Character offset (0-indexed) within the starting transcript item where the clip begins. Example: 0 for start of item, 50 to skip first 50 characters.",
    )

    transcript_end_item_id: int = Field(
        description="ID of the ending transcript item for the segment. Can be the same as transcript_item_id for clips within a single item. Example: 98766"
    )

    transcript_end_item_offset: int = Field(
        ge=0,
        description="Character offset (0-indexed) within the ending transcript item where the clip ends. Example: 150 to end after 150 characters.",
    )


class DeleteTranscrippetArgs(BaseToolArgs):
    """Delete a Transcrippet™ by its ID.

    WARNING: This is a DESTRUCTIVE operation that cannot be undone. The Transcrippet
    and its public sharing URL will be permanently deleted.

    WHEN TO USE:
    - Use this to remove Transcrippets that are no longer needed
    - Use this to clean up incorrectly created clips

    WORKFLOW: Use find_transcrippets first to obtain valid transcrippet_ids and verify
    you are deleting the correct clip.
    """

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    transcrippet_id: str = Field(
        description="Unique identifier for the transcrippet to delete. This operation cannot be undone."
    )


# Response models (extracted from responses.py)
class TranscrippetItem(BaseModel):
    """Individual transcrippet item - matches actual API structure."""

    transcrippet_id: int = Field(description="Transcrippet identifier")
    company_id: int = Field(description="Company identifier")
    equity_id: int = Field(description="Equity identifier")
    event_id: int = Field(description="Event identifier")
    transcript_item_id: int = Field(description="Transcript item identifier")
    user_id: int = Field(description="User identifier")
    audio_url: str = Field(description="Audio URL")
    company_logo_url: Optional[str] = Field(description="Company logo URL")
    company_name: str = Field(description="Company name")
    company_ticker: str = Field(description="Company ticker")
    created: str = Field(description="Creation date")
    end_ms: int = Field(description="End time in milliseconds")
    event_date: str = Field(description="Event date")
    event_title: str = Field(description="Event title")
    event_type: str = Field(description="Event type")
    modified: str = Field(description="Modification date")
    start_ms: int = Field(description="Start time in milliseconds")
    transcript: str = Field(description="Transcript text")
    transcrippet_guid: str = Field(description="Transcrippet GUID")
    transcription_audio_offset_seconds: int = Field(
        description="Audio offset in seconds"
    )
    trimmed_audio_url: str = Field(description="Trimmed audio URL")
    word_durations_ms: List[int] = Field(description="Word durations in milliseconds")
    speaker_name: Optional[str] = Field(default=None, description="Speaker name")
    speaker_title: Optional[str] = Field(default=None, description="Speaker title")
    public_url: Optional[str] = Field(
        default=None, description="Public URL for viewing the transcrippet"
    )


# Response classes
class FindTranscrippetsResponse(BaseAieraResponse):
    """Response for find_transcrippets tool - matches actual API structure."""

    response: Optional[List[TranscrippetItem]] = Field(
        None, description="List of transcrippets"
    )


class CreateTranscrippetResponse(BaseAieraResponse):
    """Response for create_transcrippet tool - matches actual API structure."""

    response: Optional[TranscrippetItem] = Field(
        None, description="Created transcrippet"
    )


class DeleteTranscrippetResponse(BaseAieraResponse):
    """Response for delete_transcrippet tool."""

    success: bool = Field(description="Whether deletion was successful")
    message: str = Field(description="Success or error message")
