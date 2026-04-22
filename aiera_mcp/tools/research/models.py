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


class FindResearchArgs(BaseToolArgs):
    """Find research reports filtered by optional search terms, author IDs, organizations, regions, and date range.

    RETURNS METADATA AND SUMMARIES ONLY — NOT full report content. To retrieve the actual report, call get_research with the document_id from these results.

    NARROW VS BROAD SCOPE:
    - For narrow queries (≤5 relevant documents expected), use find_research → get_research to retrieve full content from each. Do NOT use search_research for narrow queries; it returns text chunks rather than complete documents.
    - For broad queries (many documents, thematic coverage), use search_research with a descriptive query_text and paginate as needed.

    ALWAYS PROVIDE A SEARCH TERM: Use the `search` parameter (ticker symbol or company name) whenever possible. Many research providers do not link their documents to equity tickers, so text-based search is the most reliable way to surface relevant reports across all providers.

    RESOLVE PROVIDER AND AUTHOR NAMES FIRST: If the user names a specific provider (e.g., HSBC, Goldman Sachs, BofA) or analyst/team (e.g., "economics team", "Stan Shipley"), call get_research_providers or get_research_authors first to resolve the name into IDs, then pass them as aiera_provider_ids or author_ids. Never guess these IDs.

    DO NOT GUESS ENUMERATED FILTERS: For `asset_classes`, `asset_types`, `subjects`, `product_focuses`, `regions`, `countries`, call the corresponding lookup tool (e.g., get_research_asset_classes) first to discover valid values.

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

    asset_classes: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more asset classes. Obtain valid values from get_research_asset_classes. Example: ['Equity', 'Fixed Income'].",
    )

    asset_types: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more asset types. Obtain valid values from get_research_asset_types. Example: ['Common Stock', 'Corporate Bond'].",
    )

    subjects: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more subjects. Obtain valid values from get_research_subjects. Example: ['Technology', 'Healthcare'].",
    )

    product_focuses: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more product focus values. Obtain valid values from get_research_product_focuses. Example: ['Equity Research', 'Credit Research'].",
    )

    discipline_types: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more discipline types. Example: ['Fundamental', 'Quantitative'].",
    )

    search: Optional[str] = Field(
        default=None,
        description="Free-text search term — STRONGLY RECOMMENDED. Matches against title, abstract, and description. Many providers do not tag documents with equity tickers, so text-based search is the most reliable way to find relevant reports. Typical values: a company name or ticker symbol (e.g., 'Netflix', 'NFLX').",
    )

    search_after: Optional[List[Any]] = Field(
        default=None,
        description="Cursor for pagination. Pass the next_search_after value from a previous response to fetch the next page of results. Omit for the first page.",
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchArgs(BaseAieraArgs):
    """Get detailed information about a specific research report including summary and content.

    RESPONSE SIZE WARNING: This tool returns full research content which can be extensive.
    Consider using search_research for targeted content extraction instead of reading full reports.

    WHEN TO USE:
    - Use this when you need the complete research report content and summary
    - Use this when you need full metadata for a specific research report
    - For finding specific topics across research, prefer search_research instead

    WORKFLOW: Use find_research first to obtain valid document_ids.
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

    document_id: str = Field(
        min_length=1,
        description="Unique identifier for the research report. Obtain document_id from find_research or search_research results.",
    )


class GetResearchProvidersArgs(BaseToolArgs):
    """Retrieve all available research providers with their IDs, names, and descriptions. Used to find valid provider IDs for filtering research tools.

    ALWAYS CALL THIS when the user mentions a specific research provider or bank (e.g., HSBC, Goldman Sachs, Morgan Stanley, BofA, Evercore). Pass the provider name as the `search` parameter to resolve it into an aiera_provider_id, then pass that ID as `aiera_provider_ids` to find_research or search_research. Omitting the provider filter when a specific provider is named returns results from all providers — that is almost never what the user wants.

    BANK DISAMBIGUATION: When a bank or financial institution is named, default to treating it as a research provider (search for reports authored BY the bank) rather than as a company being researched. Only treat the bank as the research subject if the user explicitly asks about the bank's own financials, earnings, or business operations.
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

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter providers by name.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchAuthorsArgs(BaseToolArgs):
    """Search for research authors by name or provider. Returns author IDs and display names. Used to find valid author_ids for filtering find_research and search_research tools.

    WHEN TO USE:
    - Use this to look up author IDs before filtering research by a specific analyst or team
    - Use this to discover authors associated with a specific research provider

    ALWAYS CALL THIS when the user mentions a specific analyst, team, or group (e.g., "economics team", "equity strategy", "Stan Shipley"). Pass `search` with the name and `provider_id` if known; then pass the resolved ID(s) as `author_ids` to find_research or search_research.

    TEAM NAME NORMALIZATION: Team names in the system often differ from how users refer to them colloquially. For example, the Evercore ISI economics team is stored as "EVRISI EcoTeam". This makes the lookup step essential — do not guess or pattern-match team names without resolving them here first. Team-authored publications are frequently published as standalone documents that would be missed if filtered only by provider.

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
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchAssetClassesArgs(BaseToolArgs):
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
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchAssetTypesArgs(BaseToolArgs):
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
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchSubjectsArgs(BaseToolArgs):
    """Retrieve all available research subjects with their names and document counts. Used to find valid subject values for filtering research tools.

    WHEN TO USE:
    - Use this to discover available research subjects before filtering research
    - Use this to understand the distribution of research across subjects

    WORKFLOW: Use this tool to obtain subject names, then pass them to find_research or search_research.
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
        description="Search term to filter subjects by name.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchProductFocusesArgs(BaseToolArgs):
    """Retrieve all available research product focus values with their names and document counts. Used to find valid product focus values for filtering research tools.

    WHEN TO USE:
    - Use this to discover available product focus values before filtering research
    - Use this to understand the distribution of research across product focuses

    WORKFLOW: Use this tool to obtain product focus names, then pass them to find_research or search_research.
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
        description="Search term to filter product focuses by name.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchRegionTypesArgs(BaseToolArgs):
    """Retrieve all available research region types with their names and document counts. Used to find valid region type values for filtering research tools.

    WHEN TO USE:
    - Use this to discover available region types before filtering research
    - Use this to understand the distribution of research across region types

    WORKFLOW: Use this tool to obtain region type names, then pass them to find_research or search_research.
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
        description="Search term to filter region types by name.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
    )


class GetResearchCountryCodesArgs(BaseToolArgs):
    """Retrieve all available research country codes with their names and document counts. Used to find valid country code values for filtering research tools.

    WHEN TO USE:
    - Use this to discover available country codes before filtering research
    - Use this to understand the distribution of research across country codes

    WORKFLOW: Use this tool to obtain country code names, then pass them to find_research or search_research.
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
        description="Search term to filter country codes by name.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25,
        ge=1,
        description="Number of items per page (max 25). Values above 25 are capped server-side.",
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


class GetResearchAuthorsResponse(BaseAieraResponse):
    """Response for get_research_authors tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchAssetClassesResponse(BaseAieraResponse):
    """Response for get_research_asset_classes tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchAssetTypesResponse(BaseAieraResponse):
    """Response for get_research_asset_types tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchSubjectsResponse(BaseAieraResponse):
    """Response for get_research_subjects tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchProductFocusesResponse(BaseAieraResponse):
    """Response for get_research_product_focuses tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchRegionTypesResponse(BaseAieraResponse):
    """Response for get_research_region_types tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchCountryCodesResponse(BaseAieraResponse):
    """Response for get_research_country_codes tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
