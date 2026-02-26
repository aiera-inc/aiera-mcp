#!/usr/bin/env python3

"""Research domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import List, Optional, Any, Union

from ..common.models import BaseAieraArgs, BaseAieraResponse


# Mixins for validation (same pattern as events/filings domains)
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


class BloombergTickerMixin(BaseModel):
    """Mixin for models with bloomberg_ticker field."""

    @field_validator("bloomberg_ticker", mode="before", check_fields=False)
    @classmethod
    def validate_bloomberg_ticker(cls, v):
        """Automatically correct Bloomberg ticker format."""
        if v is None:
            return v
        from ..utils import correct_bloomberg_ticker

        return correct_bloomberg_ticker(v)


class FindResearchArgs(BaseToolArgs):
    """Find research reports filtered by optional search terms, author IDs, organizations, regions, and date range.

    WHEN TO USE:
    - Use this to browse and discover research reports
    - Use this to find research by specific author IDs, organizations, or regions
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

    start_date: Optional[str] = Field(
        default=None,
        description="Start date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Defaults to 52 weeks ago on the server.",
    )

    end_date: Optional[str] = Field(
        default=None,
        description="End date in ISO format (YYYY-MM-DD). All dates are in Eastern Time (ET). Defaults to now on the server.",
    )

    author_ids: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more author person IDs. Matches against the author's person_id field. Example: ['12345', '67890'].",
    )

    aiera_provider_ids: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more Aiera provider IDs. Obtain provider IDs from get_research_providers results. Example: ['krypton', 'krypton-test'].",
    )

    regions: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more regions. Example: ['Americas', 'EMEA'].",
    )

    countries: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more country codes. Example: ['US', 'GB'].",
    )

    search_after: Optional[List[Any]] = Field(
        default=None,
        description="Cursor for pagination. Pass the next_search_after value from a previous response to fetch the next page of results. Omit for the first page.",
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
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
        description="Unique identifier for the research report. Obtain research_id from find_research or search_research results."
    )


class GetResearchProvidersArgs(BaseAieraArgs):
    """Retrieve all available research providers with their IDs, names, and descriptions. Used to find valid provider IDs for filtering research tools."""

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


class FindResearchAuthorsArgs(BaseToolArgs):
    """Search for research authors by name or provider. Returns author IDs and display names. Used to find valid author_ids for filtering find_research and search_research tools.

    WHEN TO USE:
    - Use this to look up author IDs before filtering research by author
    - Use this to discover authors associated with a specific research provider

    WORKFLOW: Use this tool to obtain author_ids, then pass them to find_research or search_research.
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
        description="Search term to filter authors by display name.",
    )

    provider_id: Optional[str] = Field(
        default=None,
        description="Filter authors by Aiera provider ID. Obtain provider IDs from get_research_providers results.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class FindResearchAssetClassesArgs(BaseToolArgs):
    """Retrieve all available research asset classes with their names and document counts. Used to find valid asset class values for filtering research tools.

    WHEN TO USE:
    - Use this to discover available asset classes (e.g. "Equity", "Fixed Income") before filtering research
    - Use this to understand the distribution of research across asset classes

    WORKFLOW: Use this tool to obtain asset class names, then pass them to find_research or search_research.
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
        description="Search term to filter asset classes by name.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


class FindResearchAssetTypesArgs(BaseToolArgs):
    """Retrieve all available research asset types with their names and document counts. Used to find valid asset type values for filtering research tools.

    WHEN TO USE:
    - Use this to discover available asset types (e.g. "Common Stock", "Corporate Bond") before filtering research
    - Use this to understand the distribution of research across asset types

    WORKFLOW: Use this tool to obtain asset type names, then pass them to find_research or search_research.
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
        description="Search term to filter asset types by name.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=50, ge=1, le=100, description="Number of items per page (1-100)."
    )


# Response models
class FindResearchResponse(BaseAieraResponse):
    """Response for find_research tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchResponse(BaseAieraResponse):
    """Response for get_research tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchProvidersResponse(BaseAieraResponse):
    """Response for get_research_providers tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class FindResearchAuthorsResponse(BaseAieraResponse):
    """Response for find_research_authors tool - passes through the API response structure."""

    pagination: Optional[Any] = Field(
        None, description="Pagination metadata from the API"
    )
    data: Optional[Any] = Field(None, description="Response data from the API")


class FindResearchAssetClassesResponse(BaseAieraResponse):
    """Response for find_research_asset_classes tool - passes through the API response structure."""

    pagination: Optional[Any] = Field(
        None, description="Pagination metadata from the API"
    )
    data: Optional[Any] = Field(None, description="Response data from the API")


class FindResearchAssetTypesResponse(BaseAieraResponse):
    """Response for find_research_asset_types tool - passes through the API response structure."""

    pagination: Optional[Any] = Field(
        None, description="Pagination metadata from the API"
    )
    data: Optional[Any] = Field(None, description="Response data from the API")
