#!/usr/bin/env python3

"""Common base models for Aiera MCP tools."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer


class BaseAieraArgs(BaseModel):
    """Base class for all Aiera tool arguments."""

    pass


class CitationMetadata(BaseModel):
    """Metadata for citation information."""

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
    filing_id: Optional[int] = Field(None, description="Filing identifier")
    content_id: Optional[int] = Field(None, description="Content identifier")
    company_doc_id: Optional[int] = Field(
        None, description="Company document identifier"
    )
    conference_id: Optional[int] = Field(None, description="Conference identifier")


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
    page_size: int = Field(50, description="Number of items per page")
