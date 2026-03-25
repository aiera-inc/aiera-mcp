#!/usr/bin/env python3

"""Equities domain models for Aiera MCP."""

from pydantic import BaseModel, Field, field_validator, field_serializer
from typing import Optional, Any, Union, Literal

from ..common.models import BaseAieraResponse


# Mixins for validation (extracted from original params.py)
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


# Parameter models (extracted from params.py)
class FindEquitiesArgs(BaseToolArgs, BloombergTickerMixin):
    """Find companies and equities using various identifiers or search. To find equities for multiple companies, provide a comma-separated list of bloomberg_tickers, isins, rics, or a search term. You do not need to make multiple calls."""

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

    bloomberg_ticker: Optional[str] = Field(
        default=None,
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces.",
    )

    isin: Optional[str] = Field(
        default=None,
        description="International Securities Identification Number (ISIN).",
    )

    ric: Optional[str] = Field(
        default=None, description="Reuters Instrument Code (RIC)."
    )

    permid: Optional[str] = Field(
        default=None, description="Refinitiv Permanent Identifier (PermID)."
    )

    search: Optional[str] = Field(
        default=None,
        description="Search term to filter results. Searches within company names or tickers.",
    )

    sector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific sector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    subsector_id: Optional[Union[int, str]] = Field(
        default=None,
        description="ID of a specific subsector. Use get_sectors_and_subsectors to find valid IDs.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25, ge=1, le=25, description="Number of items per page (1-25)."
    )


class GetEquitySummariesArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve detailed summary(s) about one or more equities, filtered by bloomberg_tickers (a comma-separated list).
    Summaries will include past and upcoming events, information about company leadership, recent financials, and within which indices the equity is included.
    To find summaries for multiple companies, provide a comma-separated list of bloomberg_tickers. You do not need to make multiple calls.
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

    bloomberg_ticker: str = Field(
        description="Bloomberg ticker(s) in format 'TICKER:COUNTRY' (e.g., 'AAPL:US'). For multiple tickers, use comma-separated list without spaces."
    )


class GetIndexConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific stock market index."""

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

    index: Union[str, int] = Field(
        description="Index identifier (index_id or short_name). Obtain valid values from get_available_indexes. Example: 1 or 'sp500'"
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25, ge=1, le=25, description="Number of items per page (1-25)."
    )


class GetWatchlistConstituentsArgs(BaseToolArgs):
    """Get all equities within a specific watchlist."""

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

    watchlist_id: Union[str, int] = Field(
        description="Watchlist identifier (watchlist_id). Obtain valid values from get_available_watchlists. Example: 42"
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25, ge=1, le=25, description="Number of items per page (1-25)."
    )


class GetAvailableWatchlistsArgs(BaseToolArgs):
    """Retrieve all available watchlists with their IDs, names, and descriptions. Used to find valid watchlist IDs for filtering other tools."""

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

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25, ge=1, le=25, description="Number of items per page (1-25)."
    )


class GetAvailableIndexesArgs(BaseToolArgs):
    """Retrieve all available stock market indices with their IDs, names, and descriptions. Used to find valid index IDs for filtering other tools."""

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


class GetSectorsAndSubsectorsArgs(BaseToolArgs):
    """Retrieve all available sectors and subsectors with their IDs, names, and hierarchical relationships. Used to find valid sector/subsector IDs for filtering other tools."""

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
        description="Search term to filter results. Searches within relevant text fields.",
    )

    page: Union[int, str] = Field(
        default=1, ge=1, description="Page number for pagination (1-based)."
    )

    page_size: Union[int, str] = Field(
        default=25, ge=1, le=25, description="Number of items per page (1-25)."
    )


class GetFinancialsArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve financial statement data for a company.

    Use this tool to get detailed financial metrics for a specific company and fiscal period.
    Available statement types:
    - Income Statement: Revenue, costs, operating income, net income, EPS
    - Balance Sheet: Assets, liabilities, equity, cash position, debt
    - Cash Flow Statement: Operating cash flow, CapEx, free cash flow, financing activities

    WORKFLOW: Use find_equities first to verify the bloomberg_ticker if needed.
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

    bloomberg_ticker: str = Field(
        description="Bloomberg ticker in format 'TICKER:COUNTRY' (e.g., 'AAPL:US')."
    )

    source: Literal["income-statement", "balance-sheet", "cash-flow-statement"] = Field(
        description="The type of financial statement to retrieve. Options: 'income-statement' (revenue, expenses, profit), 'balance-sheet' (assets, liabilities, equity), 'cash-flow-statement' (operating, investing, financing cash flows)."
    )

    source_type: Literal["as-reported", "standardized"] = Field(
        default="standardized",
        description="The format type of the financial data: 'as-reported' for original filings or 'standardized' for normalized data.",
    )

    period: Literal["annual", "quarterly", "semi-annual"] = Field(
        default="annual",
        description="The reporting period type. Options: 'annual' (full fiscal year), 'quarterly' (Q1-Q4, requires calendar_quarter), 'semi-annual' (half year).",
    )

    calendar_year: int = Field(description="The calendar year for the financial data.")

    calendar_quarter: Optional[int] = Field(
        default=None,
        description="The calendar quarter for the financial data (1-4). Required for quarterly periods.",
    )

    ratio_id: Optional[str] = Field(
        default=None,
        description="Specific ratio ID to filter.",
    )

    metric_id: Optional[str] = Field(
        default=None,
        description="Specific metric ID to filter.",
    )

    metric_type: Optional[str] = Field(
        default=None,
        description="Metric type filter.",
    )


class GetRatiosArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve financial ratios for a company.

    Use this tool to get ratio metrics for a specific company and fiscal period, including:
    - Profitability ratios (ROE, ROA, profit margins)
    - Liquidity ratios (current ratio, quick ratio)
    - Valuation ratios (P/E, P/B, EV/EBITDA)
    - Leverage ratios (debt-to-equity, interest coverage)

    WORKFLOW: Use find_equities first to verify the bloomberg_ticker if needed.
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

    bloomberg_ticker: str = Field(
        description="Bloomberg ticker in format 'TICKER:COUNTRY' (e.g., 'AAPL:US')."
    )

    period: Literal["annual", "quarterly", "semi-annual"] = Field(
        default="annual",
        description="The reporting period type. Options: 'annual' (full fiscal year), 'quarterly' (Q1-Q4, requires calendar_quarter), 'semi-annual' (half year).",
    )

    calendar_year: int = Field(description="The calendar year for the ratio data.")

    calendar_quarter: Optional[int] = Field(
        default=None,
        description="The calendar quarter for the ratio data (1-4). Required for quarterly periods.",
    )

    ratio_id: Optional[str] = Field(
        default=None,
        description="Specific ratio ID to filter.",
    )


class GetKpisAndSegmentsArgs(BaseToolArgs, BloombergTickerMixin):
    """Retrieve KPIs (Key Performance Indicators) and business segment data for a company.

    Use this tool to get company-specific operational metrics and segment breakdowns, including:
    - KPIs: Subscriber counts, unit sales, average selling prices, same-store sales, etc.
    - Segments: Revenue and metrics broken down by business unit, geography, or product line

    These metrics are company-specific and vary by industry. Not all companies report segment data.

    WORKFLOW: Use find_equities first to verify the bloomberg_ticker if needed.
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

    bloomberg_ticker: str = Field(
        description="Bloomberg ticker in format 'TICKER:COUNTRY' (e.g., 'AAPL:US')."
    )

    period: Literal["annual", "quarterly", "semi-annual"] = Field(
        default="annual",
        description="The reporting period type. Options: 'annual' (full fiscal year), 'quarterly' (Q1-Q4, requires calendar_quarter), 'semi-annual' (half year).",
    )

    calendar_year: int = Field(
        description="The calendar year for the KPI and segment data."
    )

    calendar_quarter: Optional[int] = Field(
        default=None,
        description="The calendar quarter for the KPI and segment data (1-4). Required for quarterly periods.",
    )

    metric_id: Optional[str] = Field(
        default=None,
        description="Specific metric ID to filter.",
    )

    metric_type: Optional[str] = Field(
        default=None,
        description="Metric type filter.",
    )


# Response models - pass through API response structure
class FindEquitiesResponse(BaseAieraResponse):
    """Response for find_equities tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetEquitySummariesResponse(BaseAieraResponse):
    """Response for get_equity_summaries tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetSectorsSubsectorsResponse(BaseAieraResponse):
    """Response for get_sectors_and_subsectors tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetAvailableIndexesResponse(BaseAieraResponse):
    """Response for get_available_indexes tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetIndexConstituentsResponse(BaseAieraResponse):
    """Response for get_index_constituents tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetAvailableWatchlistsResponse(BaseAieraResponse):
    """Response for get_available_watchlists tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetWatchlistConstituentsResponse(BaseAieraResponse):
    """Response for get_watchlist_constituents tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetFinancialsResponse(BaseAieraResponse):
    """Response for get_financials tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetRatiosResponse(BaseAieraResponse):
    """Response for get_ratios tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class GetKpisAndSegmentsResponse(BaseAieraResponse):
    """Response for get_kpis_and_segments tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
