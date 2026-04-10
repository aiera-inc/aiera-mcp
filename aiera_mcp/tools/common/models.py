#!/usr/bin/env python3

"""Common base models for Aiera MCP tools."""

from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_serializer


class BaseAieraArgs(BaseModel):
    """Base class for all Aiera tool arguments."""

    pass


class CitationMetadata(BaseModel):
    """Metadata for citation information."""

    type: str = Field(
        description="The type of citation ('event', 'filing', 'company_doc', 'conference', 'company', 'research', or 'web_result')"
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
    filing_id: Optional[int] = Field(None, description="Filing identifier")
    content_id: Optional[int] = Field(None, description="Content identifier")
    company_doc_id: Optional[int] = Field(
        None, description="Company document identifier"
    )
    conference_id: Optional[int] = Field(None, description="Conference identifier")
    document_id: Optional[str] = Field(None, description="Document identifier")
    page: Optional[int] = Field(None, description="Page number within a document")


class CitationInfo(BaseModel):
    """Information for citing data sources."""

    title: Optional[str] = Field(None, description="Title or description of the source")
    url: Optional[str] = Field(None, description="URL to the source")
    metadata: Optional[CitationMetadata] = Field(
        None, description="Additional metadata about the citation"
    )


class BaseAieraResponse(BaseModel):
    """Base response model with common Aiera metadata."""

    instructions: List[str] = Field(
        default=[],
        description="Important instructions from the API",
    )

    error: Optional[str] = Field(None, description="Error message if request failed")


class PaginatedResponse(BaseAieraResponse):
    """Base for paginated list responses."""

    total: int = Field(..., description="Total number of items available")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")


# Common argument types used across multiple tools
class EmptyArgs(BaseAieraArgs):
    """Arguments model for tools that take no parameters."""

    pass


class SearchArgs(BaseAieraArgs):
    """Arguments model for search-based tools."""

    search: Optional[str] = Field(None, description="Search query")
    page: int = Field(1, description="Page number for pagination")
    page_size: int = Field(25, description="Number of items per page")


class GetGrammarTemplateArgs(BaseAieraArgs):
    """Retrieve a grammar template that contains output formatting instructions. Grammar templates define how you should structure, format, and present responses — including tone, style, and common language patterns.

    CRITICAL — CALL THIS TOOL BEFORE PRODUCING A RESPONSE:
    - You MUST call this tool at least once per session with `template_type='general'` to retrieve baseline formatting instructions before generating any response that uses Aiera data.

    TEMPLATE TYPES:
    - 'general': Baseline formatting instructions applicable to all Aiera data responses (default)
    """

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    template_type: str = Field(
        default="general",
        description="Template type to retrieve. Options: 'general' (broad guidance), 'topic' (topic-specific), 'provider' (provider-specific), 'sector' (sector-specific), 'subsector' (subsector-specific).",
    )

    template_subtype: Optional[str] = Field(
        default=None,
        description="Template subtype (e.g., sector name, provider name). Required for non-general template types.",
    )


class GetGrammarTemplateResponse(BaseAieraResponse):
    """Response for get_grammar_template tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetCoreInstructionsArgs(BaseAieraArgs):
    """Retrieve core instructions that define how to use Aiera tools and data effectively.

    WHEN TO USE:
    - Call this tool at least once per session to retrieve baseline instructions for working with Aiera data.
    - Core instructions provide guidance on tool selection, data interpretation, and response composition.
    """

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context, instruction generation, and to tailor responses appropriately. If the prompt is more than 500 characters, it can be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )


class GetCoreInstructionsResponse(BaseAieraResponse):
    """Response for get_core_instructions tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
