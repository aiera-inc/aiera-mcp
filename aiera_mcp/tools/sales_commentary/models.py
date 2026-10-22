#!/usr/bin/env python3

"""Sales commentary domain models for Aiera MCP (CORE-4827).

Sales commentary is a provider's sales-desk email flow ("First Look", morning notes,
desk colour, follow-ups) that summarises and reacts to published research. One
document per email; section chunks power search_sales_commentary. The tools mirror
the research family (find / get / search / usage) without the helper tools: provider
ids come from get_research_providers, author ids from find / search results.
"""

from pydantic import Field, field_validator
from typing import List, Optional, Any, Union

from ..common.models import BaseAieraArgs, BaseAieraResponse, CompactArgsMixin, StrictArgsMixin
from ..research.models import BaseToolArgs
from ..utils import correct_bloomberg_ticker


class FindSalesCommentaryArgs(StrictArgsMixin, BaseToolArgs):
    """Find sales commentary emails (a provider's sales-desk notes: "First Look", morning notes, desk colour, follow-ups) filtered by company identifier, search terms, author IDs, providers, series, subjects, and date range.

    RETURNS METADATA AND SYNOPSES ONLY — NOT the email body. To read an email, call get_sales_commentary with the document_id from these results.

    WHAT AN EMAIL CARRIES: `title` is the subject line, `thread_title` the subject with RE:/FW: stripped, `series` the subject prefix it belongs to (e.g. "First Look"), `synopsis` an LLM summary, and `referenced_research` the research reports the email discusses (title, issuer, rating / target-price actions). Sales commentary REACTS to research: when the user wants the underlying analysis, follow the reference into find_research / get_research rather than presenting the desk's paraphrase as the analyst's conclusion.

    NARROW VS BROAD SCOPE: For narrow queries (a provider, a company, a week), use find_sales_commentary → get_sales_commentary. For broad thematic questions ("what is the desk saying about ...") use search_sales_commentary, which returns email sections across the corpus.

    SCOPING TO A COMPANY: Pass `bloomberg_ticker` (or `isin` / `ric` / `permid`); it is resolved server-side and matches emails tagged with the company and emails carrying the publisher's own security identifiers. An unknown identifier returns an explicit error, never an unfiltered result.

    RESOLVE PROVIDER NAMES FIRST: provider ids are the same registry as research — call get_research_providers to resolve a bank or firm name into an id, then pass it as aiera_provider_ids. Never guess ids.

    RECENCY: commentary is time-sensitive. For "latest" / "this week" / "what is the desk saying now" set `sort_by_date=true` and a tight `start_date`.
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

    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description=(
            "PREFERRED way to scope results to a company. Bloomberg ticker in 'TICKER:COUNTRY' "
            "format (e.g. 'INTC:US'); comma-separate several (e.g. 'INTC:US,AMD:US'). Resolved "
            "server-side, so you never need an internal id. An unknown ticker returns an explicit "
            "error rather than unfiltered results. Only one identifier type per call "
            "(bloomberg_ticker OR isin OR ric OR permid)."
        ),
    )

    isin: Optional[str] = Field(
        default=None,
        description="ISIN to scope results to one company (alternative to bloomberg_ticker).",
    )

    ric: Optional[str] = Field(
        default=None,
        description="Reuters Instrument Code to scope results to one company (alternative to bloomberg_ticker).",
    )

    permid: Optional[str] = Field(
        default=None,
        description="Refinitiv PermID to scope results to one company (alternative to bloomberg_ticker).",
    )

    @field_validator("bloomberg_ticker", mode="before")
    @classmethod
    def validate_bloomberg_ticker(cls, v):
        """Same Bloomberg ticker correction as the other find_* tools ('INTC US' / 'intc'
        -> 'INTC:US'), so a format slip is fixed client-side."""
        if v is None:
            return v
        return correct_bloomberg_ticker(v)

    sector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific GICS sector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    subsector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific GICS subsector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    index_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific market index. Use get_available_indexes to find valid IDs.",
    )

    watchlist_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific user watchlist. Use get_available_watchlists to find valid IDs.",
    )

    author_ids: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more author person IDs, as returned on find / search results. Example: ['12345', '67890'].",
    )

    aiera_provider_ids: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more Aiera provider IDs. Obtain provider IDs from get_research_providers results (the same registry as research). Example: ['barclays'].",
    )

    series: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more series: the subject prefix an email belongs to, e.g. ['First Look']. Use it when the user names a series or wants a particular daily product.",
    )

    subjects: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more subject tags carried on the emails.",
    )

    search: Optional[str] = Field(
        default=None,
        description="Free-text search term matched against the subject line, thread subject, quoted-reply subject and synopsis (not the email body — use search_sales_commentary for that). Typical values: a company name or ticker symbol (e.g., 'Netflix', 'NFLX').",
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
            "ignoring text-search relevance. Use this for LATEST / MOST RECENT / THIS WEEK / TODAY "
            "questions, where freshness matters more than topical fit."
        ),
    )


class GetSalesCommentaryArgs(BaseAieraArgs, CompactArgsMixin):
    """Get a sales commentary email in full: metadata, synopsis, referenced research and the email body as ordered sections.

    WORKFLOW: Use find_sales_commentary or search_sales_commentary first to obtain valid document_ids.

    EXTRACTION STATUS: The response includes ``prose_available`` (bool) and ``content_length`` (int). When ``prose_available`` is false the body extracted no meaningful prose — do NOT summarize the content; the subject, synopsis and authors are still trustworthy for identification.
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
        description="Unique identifier for the sales commentary email. Pass the document_id returned by find_sales_commentary / search_sales_commentary VERBATIM.",
    )


class ReportSalesCommentaryUsageArgs(BaseToolArgs):
    """Report sales commentary emails that informed your final answer. Call this tool exactly once after composing your response, passing the IDs of every email whose content you used.

    Only report emails whose content meaningfully contributed to your answer; do not report emails that were retrieved and then discarded as off-topic, nor emails that only appeared in a listing without being read.

    Pass up to 100 document IDs per call (the ``document_id`` values returned by ``find_sales_commentary``, ``search_sales_commentary`` or ``get_sales_commentary``).
    """

    self_identification: Optional[str] = Field(
        default=None,
        description="Optional self-identification string for the user/session making the request. Used for tracking and analytics purposes.",
    )

    exclude_instructions: Optional[bool] = Field(
        default=False,
        description="Whether to exclude all instructions from the tool response.",
    )

    document_ids: str = Field(
        ...,
        description="Comma-separated list of sales commentary document IDs (as returned by find_sales_commentary, search_sales_commentary or get_sales_commentary) that contributed to your final answer. Maximum 100 IDs per call.",
    )


class FindSalesCommentaryResponse(BaseAieraResponse):
    """Response for find_sales_commentary tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetSalesCommentaryResponse(BaseAieraResponse):
    """Response for get_sales_commentary tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class ReportSalesCommentaryUsageResponse(BaseAieraResponse):
    """Response for report_sales_commentary_usage tool."""

    submitted: Optional[int] = Field(default=None, description="Number of document IDs submitted to the endpoint.")
    published: Optional[int] = Field(default=None, description="Number of readership events successfully published.")
    skipped: Optional[int] = Field(
        default=None,
        description="Number of IDs that were dropped (typically due to missing entitlement on the document).",
    )
