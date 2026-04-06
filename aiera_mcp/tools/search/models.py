#!/usr/bin/env python3

"""Pydantic models for Aiera search tools."""

from typing import List, Optional, Any
from pydantic import Field

from ..common.models import BaseAieraArgs, BaseAieraResponse


class SearchTranscriptsArgs(BaseAieraArgs):
    """Semantic search within event transcripts for specific topics, quotes, or discussions.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content (quotes, topics, discussions) within transcripts
    - Use find_events FIRST to identify relevant events by date/company, then use this tool to search within their transcript content
    - Use this for targeted content extraction rather than reading full transcripts

    RETURNS: Relevant transcript segments with speaker attribution, timestamps, and relevance scores.
    Results are individual chunks, not full transcripts. Use get_event for complete transcripts.

    WORKFLOW EXAMPLE:
    1. User asks: "What did Apple's CEO say about AI?"
    2. First call find_events with bloomberg_ticker='AAPL:US' to get recent event IDs
    3. Then call search_transcripts with query_text='AI artificial intelligence' and the event_ids

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within transcripts. Examples: 'earnings guidance', 'regulatory concerns', 'revenue growth'"
    )

    event_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific event IDs to search within. Obtain event_ids from find_events results. Example: [12345, 67890]",
    )

    equity_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific equity IDs to filter search. Obtain equity_ids from find_equities results. Example: [100, 200]",
    )

    start_date: str = Field(
        default="",
        description="Start date for transcripts search in YYYY-MM-DD format. Example: '2024-01-01'.",
    )

    end_date: str = Field(
        default="",
        description="End date for transcripts search in YYYY-MM-DD format. Example: '2024-12-31'.",
    )

    transcript_section: str = Field(
        default="",
        description="Optional filter for specific transcript sections. Options: 'presentation' (prepared remarks by management, typically first 15-30 min), 'q_and_a' (analyst questions and management answers). Leave empty to search all sections.",
    )

    event_type: str = Field(
        default="earnings",
        description="Type of event to include within search. ONLY ONE type per call - to search multiple types, make separate calls. Options: 'earnings' (quarterly earnings calls with Q&A), 'presentation' (investor conferences, company presentations at events - use this for conferences), 'investor_meeting' (investor day events, one-on-one meetings - use this for investor meetings), 'shareholder_meeting' (annual/special shareholder meetings), 'special_situation' (M&A announcements, other corporate actions). Example: for 'conference calls AND meetings', make TWO calls: one with event_type='presentation' and one with event_type='investor_meeting'. Defaults to 'earnings'.",
    )

    size: int = Field(
        default=25,
        description="Number of transcript segments to return per page (max 25, 10-25 recommended for optimal performance)",
    )

    search_after: Optional[List[Any]] = Field(
        default=None,
        description="Cursor for pagination. Pass the next_search_after value from a previous response to fetch the next page of results. Omit for the first page.",
    )


class SearchFilingsArgs(BaseAieraArgs):
    """Semantic search within SEC filing content for specific topics, disclosures, or risk factors.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content (risk factors, disclosures, financial discussions) within SEC filings
    - Use find_filings FIRST to identify relevant filings by date/company/form type, then use this tool to search within their content
    - Use this for targeted content extraction rather than reading full filings

    RETURNS: Relevant filing chunks with context, filing metadata, and relevance scores.
    Results are individual sections/chunks, not full filings. Use get_filing for complete filing content.

    WORKFLOW EXAMPLE:
    1. User asks: "What are Tesla's main risk factors?"
    2. First call find_filings with bloomberg_ticker='TSLA:US' and form_number='10-K' to get recent filing IDs
    3. Then call search_filings with query_text='risk factors' and the filing_ids

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within filing chunks. Examples: 'revenue guidance', 'risk factors', 'acquisition strategy'. Optional if company_name or filing_type is provided.",
    )

    filing_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific filing IDs to search within. Obtain filing_ids from find_filings results. Example: [12345, 67890]",
    )

    equity_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific equity IDs to filter search. Obtain equity_ids from find_equities results. Example: [100, 200]",
    )

    start_date: str = Field(
        default="",
        description="Start date for filing chunks search in YYYY-MM-DD format. Example: '2024-01-01'. If not provided, defaults to 6 months ago.",
    )

    end_date: str = Field(
        default="",
        description="End date for filing chunks search in YYYY-MM-DD format. Example: '2024-12-31'. If not provided, defaults to today.",
    )

    filing_type: str = Field(
        default="",
        description="Filter for specific filing types. Common values: '10-K' (annual report), '10-Q' (quarterly report), '8-K' (current report/material events), '4' (insider trading), 'DEF 14A' (proxy statement). Leave empty to search all filing types.",
    )

    size: int = Field(
        default=25,
        description="Number of filing chunks to return per page (max 25, 10-25 recommended for optimal performance)",
    )

    search_after: Optional[List[Any]] = Field(
        default=None,
        description="Cursor for pagination. Pass the next_search_after value from a previous response to fetch the next page of results. Omit for the first page.",
    )


class SearchResearchArgs(BaseAieraArgs):
    """Semantic search within research content for specific topics, analyses, or insights.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content (analyses, insights, recommendations) within research documents
    - Use this for targeted content extraction from research reports

    RETURNS: Relevant research chunks with context, metadata, and relevance scores.
    Results are individual sections/chunks, not full research documents.

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within research chunks. Examples: 'earnings outlook', 'competitive analysis', 'market trends'.",
    )

    document_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of specific document IDs to search within. Obtain document_ids from find_research or search_research results. Example: ['doc123', 'doc456']",
    )

    start_date: str = Field(
        default="",
        description="Start date for research chunks search in YYYY-MM-DD format. Example: '2024-01-01'.",
    )

    end_date: str = Field(
        default="",
        description="End date for research chunks search in YYYY-MM-DD format. Example: '2024-12-31'.",
    )

    author_ids: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more author person IDs. Matches against the author's person_id field. Example: ['12345', '67890'].",
    )

    aiera_provider_ids: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more Aiera provider IDs. Obtain provider IDs from get_research_providers results. Example: ['krypton', 'krypton-test'].",
    )

    asset_classes: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more asset classes. Obtain valid values from get_research_asset_classes. Example: ['Equity', 'Fixed Income'].",
    )

    asset_types: Optional[List[str]] = Field(
        default=None,
        description="Filter by one or more asset types. Obtain valid values from get_research_asset_types. Example: ['Common Stock', 'Corporate Bond'].",
    )

    size: int = Field(
        default=25,
        description="Number of research chunks to return per page (max 25, 10-25 recommended for optimal performance)",
    )

    search_after: Optional[List[Any]] = Field(
        default=None,
        description="Cursor for pagination. Pass the next_search_after value from a previous response to fetch the next page of results. Omit for the first page.",
    )


class SearchCompanyDocsArgs(BaseAieraArgs):
    """Semantic search within company document chunks for specific content, disclosures, or topics.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content within company documents (presentations, press releases, investor materials, etc.)
    - Use find_company_docs FIRST to identify relevant documents by date/company/category, then use this tool to search within their content
    - Use this for targeted content extraction rather than reading full documents

    RETURNS: Relevant company document chunks with context, metadata, and relevance scores.
    Results are individual sections/chunks, not full documents. Use get_company_doc for complete document content.

    WORKFLOW EXAMPLE:
    1. User asks: "What did Apple say about sustainability in their investor presentations?"
    2. First call find_company_docs with company_id to get relevant document IDs
    3. Then call search_company_docs with query_text='sustainability' and the company_doc_ids

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within company document chunks. Examples: 'sustainability initiatives', 'capital allocation', 'product roadmap'.",
    )

    company_doc_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of specific company document IDs to search within. Obtain company_doc_ids from find_company_docs results. Example: [12345, 67890]",
    )

    company_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of company IDs to filter search. Obtain company_ids from find_equities results. Example: [1, 2]",
    )

    categories: Optional[List[str]] = Field(
        default=None,
        description="Optional list of document categories to filter by. Obtain valid values from get_company_doc_categories. Example: ['Investor Presentation', 'Press Release'].",
    )

    keywords: Optional[List[str]] = Field(
        default=None,
        description="Optional list of keywords to filter by. Obtain valid values from get_company_doc_keywords. Example: ['earnings', 'guidance'].",
    )

    start_date: str = Field(
        default="",
        description="Start date for company document chunks search in YYYY-MM-DD format. Filters on publish_date. Example: '2024-01-01'.",
    )

    end_date: str = Field(
        default="",
        description="End date for company document chunks search in YYYY-MM-DD format. Filters on publish_date. Example: '2024-12-31'.",
    )

    size: int = Field(
        default=25,
        description="Number of company document chunks to return per page (max 25, 10-25 recommended for optimal performance)",
    )

    search_after: Optional[List[Any]] = Field(
        default=None,
        description="Cursor for pagination. Pass the next_search_after value from a previous response to fetch the next page of results. Omit for the first page.",
    )


class SearchThirdbridgeArgs(BaseAieraArgs):
    """Semantic search within Third Bridge expert interview transcripts for specific topics, insights, or discussions.

    WHEN TO USE THIS TOOL:
    - Use this when you need to find specific content (expert opinions, industry insights, competitive analysis) within Third Bridge interviews
    - Use find_third_bridge_events FIRST to identify relevant interviews by date/company, then use this tool to search within their content
    - Use this for targeted content extraction rather than reading full transcripts

    RETURNS: Relevant Third Bridge transcript segments with speaker attribution, event metadata, and relevance scores.
    Results are individual paragraphs/chunks, not full transcripts. Use get_third_bridge_event for complete transcripts.

    WORKFLOW EXAMPLE:
    1. User asks: "What do experts say about semiconductor supply chains?"
    2. First call find_third_bridge_events to get relevant event IDs
    3. Then call search_thirdbridge with query_text='semiconductor supply chain'

    NOTE: This tool uses hybrid semantic + keyword search for high-quality results.
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

    query_text: str = Field(
        description="Search query for semantic matching within Third Bridge transcripts. Examples: 'competitive landscape', 'pricing trends', 'market share dynamics'.",
    )

    company_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of company IDs to filter search. Matches against both primary_company_ids and secondary_company_ids. Obtain company_ids from find_equities results. Example: [1, 2]",
    )

    thirdbridge_ids: Optional[List[str]] = Field(
        default=None,
        description="Optional list of Third Bridge IDs to search within. Obtain from find_third_bridge_events results. Example: ['TB-12345', 'TB-67890']",
    )

    aiera_event_ids: Optional[List[int]] = Field(
        default=None,
        description="Optional list of Aiera event IDs to search within. Obtain from find_third_bridge_events or search_thirdbridge results. Example: [12345, 67890]",
    )

    start_date: str = Field(
        default="",
        description="Start date for Third Bridge transcript search in YYYY-MM-DD format. Filters on event_date. Example: '2024-01-01'.",
    )

    end_date: str = Field(
        default="",
        description="End date for Third Bridge transcript search in YYYY-MM-DD format. Filters on event_date. Example: '2024-12-31'.",
    )

    event_content_type: str = Field(
        default="",
        description="Optional filter for Third Bridge content type. Example: 'FORUM'. Leave empty to search all content types.",
    )

    size: int = Field(
        default=25,
        description="Number of Third Bridge transcript segments to return per page (max 25, 10-25 recommended for optimal performance)",
    )

    search_after: Optional[List[Any]] = Field(
        default=None,
        description="Cursor for pagination. Pass the next_search_after value from a previous response to fetch the next page of results. Omit for the first page.",
    )


# Response models - pass through API response structure
class SearchTranscriptsResponse(BaseAieraResponse):
    """Response for search_transcripts tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class SearchFilingsResponse(BaseAieraResponse):
    """Response for search_filings tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class SearchResearchResponse(BaseAieraResponse):
    """Response for search_research tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class SearchCompanyDocsResponse(BaseAieraResponse):
    """Response for search_company_docs tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")


class SearchThirdbridgeResponse(BaseAieraResponse):
    """Response for search_thirdbridge tool - passes through the API response structure."""

    response: Optional[Any] = Field(None, description="Response data from the API")
