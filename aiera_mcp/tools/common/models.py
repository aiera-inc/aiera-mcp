#!/usr/bin/env python3

"""Common base models for Aiera MCP tools."""

from typing import Any, Dict, List, Optional
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


class CompactArgsMixin(BaseModel):
    """Mixin adding the opt-in LLM response-compaction argument to a tool."""

    # Runtime default is None (not False) on purpose: make_aiera_request applies
    # the server-wide COMPACT_RESPONSES default only when `compact` is ABSENT from
    # the params, and an explicit per-call value must override it. A None default
    # means model_dump(exclude_none=True) omits the field when the caller didn't
    # set it, preserving that contract. The model-facing default ("off") is
    # advertised to the LLM via json_schema_extra so the schema still reads
    # default=false without forcing the field onto every request.
    compact: Optional[bool] = Field(
        default=None,
        json_schema_extra={"default": False},
        description=(
            "Defaults to no compaction. If true, the API compacts the response body with an LLM into a short summary plus "
            "verbatim 'preserved' fields (citations, pagination cursors, and ids). The summary is "
            "LOSSY — re-call with compact=false when you need the complete data."
        ),
    )


class CompactedResponseBody(BaseModel):
    """Shape of the `response` field when the API compacted it (compact=true).

    The `summary` is a lossy LLM digest of the full payload. Everything under
    `preserved` (citations, pagination cursors, ids) is verbatim from the full
    response and is authoritative for tool chaining.
    """

    compacted: bool = Field(description="Always true for compacted responses")
    compaction_note: Optional[str] = Field(
        None, description="Guidance from the API about the compacted payload"
    )
    summary: Optional[str] = Field(
        None, description="Lossy LLM digest of the full response (markdown)"
    )
    preserved: Optional[Dict[str, Any]] = Field(
        None,
        description="Verbatim machine-critical fields: citations, pagination, next_search_after, ids",
    )


def is_compacted_response(raw_response: Any) -> bool:
    """True when an aiera-api reply carries a compacted body in its `response` field."""
    if not isinstance(raw_response, dict):
        return False

    body = raw_response.get("response")
    return isinstance(body, dict) and body.get("compacted") is True


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


class GetCreationTemplatesArgs(BaseAieraArgs):
    """Retrieve content creation templates prior to writing first-party research content.

    IMPORTANT: this is distinct from the grammar templates used for formatting standard chat responses.
    Creation templates provide guidance on how to structure and compose first-party research content in
    the tone and style of an institutional analyst.

    These templates are not designed for general-purpose chat or summarization tasks.

    TEMPLATE TYPES:
    - 'global': Baseline creation guidance applied to all creation workflows
    - 'style': Style/tone template only (extracted from the global template)
    - 'task': Task-specific templates (keyed by template_subtype, which can be pulled from the global template)
    - 'analyst': Analyst-specific templates (requires entitlement)
    """

    originating_prompt: Optional[str] = Field(
        default=None,
        description="The original user prompt that led to this API call. Used for context and analytics. If more than 500 characters, it may be truncated or summarized.",
    )

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    template_type: Optional[str] = Field(
        default=None,
        description="Optional filter by template type: 'global', 'task', 'style', or 'analyst'. Default is 'global' if not specified. ",
    )

    template_subtype: Optional[str] = Field(
        default=None,
        description="Optional filter by template subtype (e.g. a specific task or analyst).",
    )


class GetCreationTemplatesResponse(BaseAieraResponse):
    """Response for get_creation_templates tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetCoreInstructionsArgs(BaseAieraArgs):
    """Retrieve core instructions that define how to use Aiera tools and data effectively.

    CRITICAL — CALL THIS TOOL FIRST BEFORE ANY OTHER TOOLS ARE CALLED:
    - You MUST call this tool at the beginning of each session to retrieve baseline instructions for working with Aiera data, and guidance on tool selection, data interpretation, and response composition.
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


class AvailableToolsArgs(BaseAieraArgs):
    """Retrieve the list of tools available to the current user based on their permissions.

    WHEN TO USE:
    - Call this tool to discover which tools the current user has access to.
    - Use this to check permissions before calling other tools.
    """

    pass


class AvailableToolsResponse(BaseAieraResponse):
    """Response for available_tools tool."""

    available_tools: List[str] = Field(
        default=[],
        description="List of tool names available to the current user",
    )

    hidden_tools: List[str] = Field(
        default=[],
        description="List of tool names the current user does not have access to",
    )
