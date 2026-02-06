#!/usr/bin/env python3

"""Research domain models for Aiera MCP."""

from pydantic import BaseModel, Field
from typing import Optional, Any

from ..common.models import BaseAieraArgs, BaseAieraResponse


class FindResearchArgs(BaseAieraArgs):
    """Find research reports filtered by optional search terms, authors, organizations, regions, and date range.

    WHEN TO USE:
    - Use this to browse and discover research reports
    - Use this to find research by specific authors, organizations, or regions
    - Use this to find research within a date range

    MULTIPLE FILTERS: All filter parameters are optional. Combine them to narrow results.
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

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter research reports. Searches within relevant text fields.",
    )

    author_person_ids: Optional[str] = Field(
        default=None,
        description="Comma-separated list of author person IDs to filter by specific authors. Example: '123,456'.",
    )

    organization_names: Optional[str] = Field(
        default=None,
        description="Comma-separated list of organization names to filter by. Example: 'Goldman Sachs,Morgan Stanley'.",
    )

    region_types: Optional[str] = Field(
        default=None,
        description="Comma-separated list of region types to filter by. Example: 'North America,Europe'.",
    )

    start_date: Optional[str] = Field(
        default=None,
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET).",
    )

    end_date: Optional[str] = Field(
        default=None,
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET).",
    )


class GetResearchArgs(BaseAieraArgs):
    """Get detailed information about a specific research report including summary and content.

    RESPONSE SIZE WARNING: This tool returns full research content which can be extensive.
    Consider using search_research for targeted content extraction instead of reading full reports.

    WHEN TO USE:
    - Use this when you need the complete research report content and summary
    - Use this when you need full metadata for a specific research report
    - For finding specific topics across research, prefer search_research instead

    WORKFLOW: Use find_research first to obtain valid research_ids.
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

    research_id: str = Field(
        description="Unique identifier for the research report. Obtain research_id from find_research results. Example: '98765'"
    )


# Response models
class FindResearchResponse(BaseAieraResponse):
    """Response for find_research tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchResponse(BaseAieraResponse):
    """Response for get_research tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
