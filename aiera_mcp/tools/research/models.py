#!/usr/bin/env python3

"""Research domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import List, Optional, Any, Union

from ..common.models import BaseAieraArgs, BaseAieraResponse, CompactArgsMixin


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

    CURRENT RATING / PRICE TARGET QUESTIONS: Prefer get_current_ratings — it answers directly for one or more companies without a manual document workflow. Use find_research only as a fallback (an identifier get_current_ratings could not match, or when the user wants the underlying report): filter by equity identifier (`bloomberg_ticker` / `isin` / `ric`) with `sort_by_date=true` (plus any provider filter) to surface the newest covering document — INCLUDING multi-company sector/industry notes, where rating and price-target changes often land first and which a company-name text search will miss — then pass its document_id to get_research_metadata_ratings.

    RESOLVE PROVIDER AND AUTHOR NAMES FIRST: If the user names a specific provider (e.g., HSBC, Goldman Sachs, BofA) or analyst/team (e.g., "economics team", "Stan Shipley"), call get_research_providers or get_research_authors first to resolve the name into IDs, then pass them as aiera_provider_ids or author_ids. Never guess these IDs.

    DO NOT GUESS ENUMERATED FILTERS: For `asset_classes`, `asset_types`, `subjects`, `product_focuses`, `regions`, `countries`, call the corresponding lookup tool (e.g., get_research_asset_classes) first to discover valid values.

    MULTIPLE FILTERS: All filter parameters are optional. Combine them to narrow results.

    ANALYST RATINGS: Result items may include analyst rating fields — `security_ratings_primary`/`_secondary` (security-level, e.g. "Overweight", "Equal Weight", "Outperform"), `issuer_ratings_primary`/`_secondary`, and `sector_industry_ratings_primary`/`_secondary`. Values are the provider's own rating labels, passed through verbatim, so compare within a provider, not across.
    """

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
        description=(
            "Filter by one or more asset classes. Exactly four valid values: "
            "'Equity', 'FixedIncome', 'Currency', 'Commodity'. "
            "Reflects the ISSUER's asset class, not subject matter — credit-themed research "
            "covering an equity issuer is tagged 'Equity'. Do not use this filter to discover "
            "credit/fixed-income themes (use a text search instead). Common mistake: passing "
            "'Credit' / 'CorporateHighYieldCredit' here returns zero results — those are "
            "asset_types values, not asset_classes."
        ),
    )

    asset_types: Optional[List[str]] = Field(
        default=None,
        description=(
            "Filter by one or more asset types (e.g., 'Stock', 'Credit', "
            "'CorporateHighYieldCredit', 'InterestRates', 'USTreasuries'). "
            "Obtain valid values from get_research_asset_types. "
            "NOTE: Some providers (notably Deutsche) do not populate asset_types on their "
            "documents at all — adding ['Stock'] silently excludes their entire corpus. "
            "When the user just wants 'equity research', prefer a text search over this filter."
        ),
    )

    subjects: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more subjects. Obtain valid values from get_research_subjects. Example: ['Technology', 'Healthcare'].",
    )

    product_focuses: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more product focus values. Obtain valid values from get_research_product_focuses. Example: ['Equity Research', 'Credit Research'].",
    )

    search: Optional[str] = Field(
        default=None,
        description="Free-text search term. Matches against title, abstract, and description. Many providers do not tag documents with equity tickers, so text-based search is the most reliable way to find relevant reports. Typical values: a company name or ticker symbol (e.g., 'Netflix', 'NFLX').",
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

    sort_by_date: bool = Field(
        default=False,
        description=(
            "When true, results are sorted strictly by published_datetime (most recent first), "
            "ignoring text-search relevance. Use this when the user is explicitly asking for "
            "the LATEST / MOST RECENT / THIS WEEK / TODAY publications and freshness matters "
            "more than topical fit. Leave false (default) for general topic questions — the "
            "server already applies a recency decay to the relevance score, so you don't need "
            "this for ordinary 'current view' style queries."
        ),
    )


class GetResearchArgs(BaseAieraArgs, CompactArgsMixin):
    """Get detailed information about a specific research report including summary and content.

    RESPONSE SIZE WARNING: This tool returns full research content which can be extensive.
    Consider using search_research for targeted content extraction instead of reading full reports.

    WHEN TO USE:
    - Use this when you need the complete research report content and summary
    - Use this when you need full metadata for a specific research report
    - For finding specific topics across research, prefer search_research instead

    WORKFLOW: Use find_research first to obtain valid document_ids.

    EXTRACTION STATUS: The response includes ``prose_available`` (bool) and
    ``content_length`` (int) fields per document. Some research notes are chart-only
    or table-only and extract no meaningful prose — in that case ``prose_available``
    is ``false`` and ``content_length`` is small. When ``prose_available`` is false,
    do NOT attempt to summarize the document's content; the title/abstract/authors
    are still trustworthy for identification purposes, but the body itself is empty.
    """

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
        description=(
            "Unique identifier for the research report. Pass the document_id returned by "
            "find_research / search_research VERBATIM — do not strip suffixes (e.g., the "
            "trailing '_604' on Deutsche IDs is part of the canonical ID, not an optional "
            "chunk marker). A malformed or partial ID returns a misleading 'not entitled' error."
        ),
    )


class GetResearchProvidersArgs(BaseToolArgs):
    """Retrieve all available research providers with their IDs, names, and descriptions. Used to find valid provider IDs for filtering research tools.

    ALWAYS CALL THIS when the user mentions a specific research provider or bank (e.g., HSBC, Goldman Sachs, Morgan Stanley, BofA, Evercore). Pass the provider name as the `search` parameter to resolve it into an aiera_provider_id, then pass that ID as `aiera_provider_ids` to find_research or search_research. Omitting the provider filter when a specific provider is named returns results from all providers — that is almost never what the user wants.

    BANK DISAMBIGUATION: When a bank or financial institution is named, default to treating it as a research provider (search for reports authored BY the bank) rather than as a company being researched. Only treat the bank as the research subject if the user explicitly asks about the bank's own financials, earnings, or business operations.
    """

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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

    page: Union[int, str] = Field(default=1, ge=1, description="Page number for pagination (1-based).")

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


class ReportResearchUsageArgs(BaseToolArgs):
    """Report research documents that informed your final answer. Call this tool exactly once after composing your response, passing the IDs of every research document whose content you used.

    Only report documents whose content meaningfully contributed to your answer; do not report documents that were retrieved and then discarded as off-topic, nor documents that only appeared in a listing without being read.

    Pass up to 100 research document IDs per call (the ``document_id`` values returned by ``find_research``, ``search_research``, or ``get_research``).
    """

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    research_ids: str = Field(
        ...,
        description="Comma-separated list of research document IDs (as returned by find_research, search_research, or get_research) that contributed to your final answer. Maximum 100 IDs per call.",
    )


class ReportResearchUsageResponse(BaseAieraResponse):
    """Response for report_research_usage tool."""

    submitted: Optional[int] = Field(
        default=None,
        description="Number of research IDs the tool submitted to the endpoint.",
    )

    published: Optional[int] = Field(
        default=None,
        description="Number of readership events successfully published.",
    )

    skipped: Optional[int] = Field(
        default=None,
        description="Number of IDs that were dropped (typically due to missing entitlement on the document).",
    )


class GetResearchMetadataArgs(BaseAieraArgs):
    """Retrieve the complete source metadata record for a research document.

    RETURNS: structured metadata including publication status and dates, publisher
    organization and author roles, covered issuers and securities,
    subject/sector/region/country classifications, product series, and file details.

    WHEN TO USE:
    - Use for complete or esoteric metadata needs — classifications, product series,
      publisher/author roles, coverage lists, or publication details not present in
      find_research / get_research results.
    - For ONLY the analyst rating or price target, use get_research_metadata_ratings instead: it
      returns a compact rating/target payload (a few hundred bytes) rather than this
      full metadata document.
    - For a targeted slice, pass ``fields`` with dot-paths (call
      get_research_metadata_fields first to discover valid paths).

    WORKFLOW: find_research or search_research -> document_id -> get_research_metadata.
    Repeated elements beyond ``max_list_items`` are truncated with a ``<key>__truncated``
    marker of shown/total counts.
    """

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
        description=(
            "Unique identifier for the research report. Pass the document_id returned by "
            "find_research / search_research VERBATIM — do not strip prefixes or suffixes."
        ),
    )

    fields: Optional[str] = Field(
        default=None,
        description=(
            "Comma-separated dot-paths to return (e.g. "
            "'Research.Product.Content,Research.Product.Context.ProductClassifications'). "
            "Discover valid paths with get_research_metadata_fields. Omit to receive the "
            "full metadata document."
        ),
    )

    max_list_items: Optional[int] = Field(
        default=None,
        ge=1,
        le=500,
        description=(
            "Truncate repeated elements beyond this count (default 50, max 500). Raise it "
            "when complete issuer/security coverage lists are needed."
        ),
    )


class GetResearchMetadataFieldsArgs(BaseAieraArgs):
    """List every available metadata field path for get_research_metadata, with per-field
    coverage and typical size share.

    RETURNS: a catalog of dot-paths (elements and @attributes), each with docs_pct (how
    often the field is present across documents) and mean_size_pct (its typical share of
    document bytes), plus the node names hidden by default and usage notes for the
    ``fields`` and ``max_list_items`` parameters.

    WHEN TO USE: call once before using get_research_metadata's ``fields`` parameter to
    choose paths. Prefer high-coverage paths; avoid or cap large ones (e.g. issuer lists)
    unless the user needs them.
    """

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


class GetResearchMetadataResponse(BaseAieraResponse):
    """Response for get_research_metadata tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchMetadataFieldsResponse(BaseAieraResponse):
    """Response for get_research_metadata_fields tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetResearchMetadataRatingsArgs(BaseAieraArgs):
    """Get just the analyst ratings and price targets from a specific research report — a
    focused subset of get_research_metadata, and the fastest, most token-efficient way to
    answer "what is the rating / price target in this report?"

    RETURNS: per issuer and security: the Current (and Prior, when published) rating and
    target price with currency, security identifiers (RIC/Bloomberg/ISIN/CUSIP) for
    disambiguation, and rating/target-price actions when the publisher supplies them.
    Some publishers rate at the document level instead — that is returned as
    ``document_rating`` with its source noted. Sector reports may return many issuers,
    each with their own rating and target — match the requested company by name or
    security identifier in the response.

    WHEN TO USE:
    - Prefer this over get_research_metadata for ANY rating / price-target question — the
      response is a few hundred bytes instead of the full metadata document.
    - For other metadata (classifications, coverage lists, product series, publication
      details), use get_research_metadata instead.
    - An empty ``issuers`` list means the publisher did not include structured ratings
      in this document (common for macro/economics notes).
    - ``"target_price": null`` means the publisher omits target prices from this
      document's structured data — NOT that the report lacks one. Where possible the tool
      recovers the value from the document itself (returned with
      ``"source": "document_text"``); if it is still null, check the same document's full
      text via get_research before reporting the target as unavailable. Never substitute
      a target from an older document.

    WORKFLOW: find_research or search_research -> document_id -> get_research_metadata_ratings.
    For a company's CURRENT rating/target (not a specific report), use get_current_ratings
    instead — it answers directly without a manual document lookup.
    """

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
        description=(
            "Unique identifier for the research report. Pass the document_id returned by "
            "find_research / search_research VERBATIM — do not strip prefixes or suffixes."
        ),
    )


class GetResearchMetadataRatingsResponse(BaseAieraResponse):
    """Response for get_research_metadata_ratings tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetCurrentRatingsArgs(BaseAieraArgs):
    """Get the CURRENT analyst rating and price target for one or more companies — THE
    tool for "what is [provider]'s current rating / price target on [company]?", for any
    entitled provider.

    Answers from the provider's own frequently-updated coverage data where available and
    automatically falls back to the provider's newest covering research document
    (sector/industry notes included) otherwise — no manual document workflow needed.

    RETURNS: per requested identifier, the matching entries: company name, security
    identifiers, current rating, price target with currency, and the date the values
    last changed. Each entry carries a ``source``:
    - ``"coverage_feed"``: live provider coverage data; attribute in text with the
      per-provider ``as_of`` timestamp (e.g. "per Barclays coverage as of Aug 4").
      There is no citable document — do not fabricate a citation link.
    - ``"document"``: extracted from the provider's newest covering note
      (``document_id`` / ``document_title`` identify it). ALWAYS state the note's
      ``published_date`` with the value — it is as-of that note, not live.
    Identifiers with no match from any queried provider are listed under ``unmatched``.

    WHEN TO USE:
    - Any "current rating / price target" question, regardless of provider.
    - Batch companies into ONE call (up to 50 identifiers) instead of calling per company.
    - Omit provider_ids for every provider with a view; pass it when the user names firms.
    - Use get_research_metadata_ratings instead when the question is about a SPECIFIC
      report ("what rating is in this note?").

    WORKFLOW: get_current_ratings(identifiers=[...]) -> answer. The manual document
    workflow (find_research -> get_research_metadata_ratings) is only for unmatched
    identifiers, historical/prior values, or reading the underlying report.
    """

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

    identifiers: List[str] = Field(
        min_length=1,
        description=(
            "One or more companies to look up — ticker (any exchange format), ISIN, CUSIP, "
            "SEDOL, or company name. Batch all companies for the question into one call."
        ),
    )

    provider_ids: Optional[List[str]] = Field(
        default=None,
        description=(
            "Optional research provider IDs (resolve via get_research_providers) to restrict "
            "the lookup. Omit to query all providers the user is entitled to."
        ),
    )


class GetCurrentRatingsResponse(BaseAieraResponse):
    """Response for get_current_ratings tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
