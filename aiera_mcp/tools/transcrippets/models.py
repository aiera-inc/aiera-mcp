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
    """Find Transcrippets™ filtered by various identifiers and date ranges."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context and instruction generation, and to help tailor responses appropriately. If the prompt is long, it can be summarized or truncated.",
    )

    transcrippet_id: Optional[str] = Field(
        default=None,
        description="Transcrippet ID(s). For multiple IDs, use comma-separated list without spaces.",
    )

    event_id: Optional[str] = Field(
        default=None,
        description="Event ID(s) to filter by. For multiple IDs, use comma-separated list without spaces.",
    )

    equity_id: Optional[str] = Field(
        default=None,
        description="Equity ID(s) to filter by. For multiple IDs, use comma-separated list without spaces.",
    )

    speaker_id: Optional[str] = Field(
        default=None,
        description="Speaker ID(s) to filter by. For multiple IDs, use comma-separated list without spaces.",
    )

    transcript_item_id: Optional[str] = Field(
        default=None,
        description="Transcript item ID(s) to filter by. For multiple IDs, use comma-separated list without spaces.",
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
    """Create a new Transcrippet™ from an event transcript segment."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context and instruction generation, and to help tailor responses appropriately. If the prompt is long, it can be summarized or truncated.",
    )

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
        ge=0, description="Character offset within the starting transcript item."
    )

    transcript_end_item_id: int = Field(
        description="ID of the ending transcript item for the segment."
    )

    transcript_end_item_offset: int = Field(
        ge=0, description="Character offset within the ending transcript item."
    )


class DeleteTranscrippetArgs(BaseToolArgs):
    """Delete a Transcrippet™ by its ID."""

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context and instruction generation, and to help tailor responses appropriately. If the prompt is long, it can be summarized or truncated.",
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
