#!/usr/bin/env python3

"""Instructions domain models for Aiera MCP."""

from pydantic import BaseModel, Field
from typing import Optional, List

from ..common.models import BaseAieraResponse


# Parameter models
class GetInstructionsArgs(BaseModel):
    """Retrieve instructions of a specific type for use with MCP/AI agents.

    This tool fetches instruction sets that guide AI behavior for specific tasks or contexts.
    Use this to get standardized instructions for processing events, filings, or other content types.
    """

    instruction_type: str = Field(
        description="The type of instructions to retrieve (citations, base, guidance). This determines which instruction set is returned."
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
