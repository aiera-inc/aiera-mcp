#!/usr/bin/env python3

"""Instructions domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, List, Any, Union

from ..common.models import BaseAieraResponse


# Mixins for validation
class BaseToolArgs(BaseModel):
    """Base class for all Aiera MCP tool arguments with common serializers."""

    @field_validator(
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


# Parameter models
class GetInstructionsArgs(BaseToolArgs):
    """Retrieve instructions of a specific type for use with MCP/AI agents.

    This tool fetches instruction sets that guide AI behavior for specific tasks or contexts.
    Use this to get standardized instructions for processing events, filings, or other content types.
    """

    instruction_type: str = Field(
        description="The type of instructions to retrieve. This determines which instruction set is returned."
    )

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

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter instructions. Searches within relevant text fields.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


# Response models
class InstructionsResponseData(BaseModel):
    """Instructions response data container."""

    instructions: List[str] = Field(
        default_factory=list, description="List of instruction strings"
    )


class GetInstructionsResponse(BaseAieraResponse):
    """Response for get_instructions tool - matches actual API structure."""

    response: Optional[InstructionsResponseData] = Field(
        None, description="Response data container with instructions"
    )
