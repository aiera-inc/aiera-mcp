#!/usr/bin/env python3

"""Common base models for Aiera MCP tools."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_serializer


class BaseAieraArgs(BaseModel):
    """Base class for all Aiera tool arguments."""

    pass


class CitationInfo(BaseModel):
    """Information for citing data sources."""

    title: str = Field(..., description="Title or description of the source")
    url: Optional[str] = Field(None, description="URL to the source (if available)")
    timestamp: Optional[datetime] = Field(
        None, description="When the data was created/published"
    )
    source: Optional[str] = Field(
        None, description="Source name (e.g., 'Aiera', 'SEC')"
    )

    @field_serializer("timestamp")
    def serialize_timestamp(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to ISO format string for JSON compatibility."""
        if value is None:
            return None
        return value.isoformat()


class BaseAieraResponse(BaseModel):
    """Base response model with common Aiera metadata."""

    instructions: List[str] = Field(
        default=[], description="Instructions or additional information from the API"
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
