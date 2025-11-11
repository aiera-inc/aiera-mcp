#!/usr/bin/env python3

"""Search tools for Aiera MCP server."""

import logging
from typing import Dict, Any
from datetime import datetime

from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    TranscriptSearchItem,
    TranscriptSearchCitation,
    FilingSearchItem,
    FilingSearchCitation,
)
from .utils import correct_provided_ids, correct_provided_types, correct_event_type

# Setup logging
logger = logging.getLogger(__name__)


async def search_transcripts(args: SearchTranscriptsArgs) -> SearchTranscriptsResponse:
    """Perform a semantic search against all event transcripts."""
    logger.info("tool called: search_transcripts")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    must_clauses = []

    # Add event ID filter
    if args.event_ids:
        must_clauses.append({
            "terms": {
                "transcript_event_id": correct_provided_ids(args.event_ids),
            }
        })

    # Add equity ID filter
    if args.equity_ids:
        must_clauses.append({
            "terms": {
                "primary_equity_id": correct_provided_ids(args.equity_ids),
            }
        })

    # Add date range filter
    if args.start_date:
        date_range = {"gte": args.start_date}
        if args.end_date:
            date_range["lte"] = args.end_date

        must_clauses.append({
            "range": {
                "date": date_range
            }
        })

    # Add event type filter
    if args.event_type and args.event_type.strip():
        must_clauses.append({
            "term": {
                "transcript_event_type": correct_event_type(args.event_type)
            }
        })

    # Add section filter
    if args.transcript_section and args.transcript_section.strip() in ["presentation", "q_and_a"]:
        must_clauses.append({
            "term": {
                "transcript_section": args.transcript_section.strip()
            }
        })

    # First, try ML-based search
    query = {
        "query": {
            "bool": {
                "must": must_clauses,
            }
        },
        "from": (args.page - 1) * args.page_size,
        "size": args.page_size,
        "ext": {
            "ml_inference": {
                "query_text": args.search
            }
        }
    }

    raw_results = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search/transcripts",
        api_key=api_key,
        params={},
        data=query,
    )

    # If no results or bad results, fall back to traditional search
    if not raw_results or "result" not in raw_results or not raw_results["result"]:
        query = {
            "query": {
                "bool": {
                    "must": must_clauses,
                    "should": [
                        {
                            "match": {
                                "text": {
                                    "query": args.search,
                                    "boost": 2.0
                                }
                            }
                        },
                        {
                            "multi_match": {
                                "query": args.search,
                                "fields": ["text", "title", "speaker_name"],
                                "type": "best_fields",
                                "boost": 1.5
                            }
                        }
                    ]
                }
            },
            "from": (args.page - 1) * args.page_size,
            "size": args.page_size,
        }

        raw_results = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/transcripts",
            api_key=api_key,
            params={},
            data=query,
        )

    # Process raw results into structured format
    structured_results = []

    if raw_results and "result" in raw_results:
        result_data = raw_results["result"]
        if isinstance(result_data, list):
            for item in result_data:
                try:
                    # Parse the date string to datetime
                    date_str = item.get("date", "")
                    if date_str:
                        # Handle different possible date formats
                        if date_str.endswith('Z'):
                            # Replace Z with +00:00 for ISO format compatibility
                            date_str = date_str.replace('Z', '+00:00')
                        elif not date_str.endswith(('+00:00', '-00:00')) and 'T' in date_str:
                            # Add timezone if missing
                            date_str = date_str + '+00:00'
                        parsed_date = datetime.fromisoformat(date_str)
                    else:
                        parsed_date = datetime.now()

                    # Create citation information
                    citation_data = item.get("citation_information", {})
                    citation = TranscriptSearchCitation(
                        title=citation_data.get("title", ""),
                        url=citation_data.get("url", "")
                    )

                    # Create structured result item
                    search_item = TranscriptSearchItem(
                        date=parsed_date,
                        primary_company_id=item.get("primary_company_id", 0),
                        content_id=item.get("content_id", 0),  # This will be aliased to transcript_item_id
                        transcript_event_id=item.get("transcript_event_id", 0),
                        transcript_section=item.get("transcript_section", ""),
                        text=item.get("text", ""),
                        primary_equity_id=item.get("primary_equity_id", 0),
                        title=item.get("title", ""),
                        _score=item.get("_score", 0.0),  # This will be aliased to score
                        citation_information=citation
                    )

                    structured_results.append(search_item)

                except Exception as e:
                    logger.warning(f"Failed to parse search result item: {e}")
                    continue

    return SearchTranscriptsResponse(
        instrument_type="transcript_search",
        error_messages=[],
        error_count=0,
        result=structured_results,
        instructions=raw_results.get("instructions", []) if raw_results else [],
        citation_information=[]
    )


async def search_filings(args: SearchFilingsArgs) -> SearchFilingsResponse:
    """Perform a semantic search against all SEC filings."""
    logger.info("tool called: search_filings")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    must_clauses = []

    # Add filing ID filter
    if args.filing_ids:
        must_clauses.append({
            "terms": {
                "filing_id": correct_provided_ids(args.filing_ids),
            }
        })

    # Add equity ID filter
    if args.equity_ids:
        must_clauses.append({
            "terms": {
                "primary_equity_id": correct_provided_ids(args.equity_ids),
            }
        })

    # Add date range filter
    if args.start_date:
        date_range = {"gte": args.start_date}
        if args.end_date:
            date_range["lte"] = args.end_date

        must_clauses.append({
            "range": {
                "date": date_range
            }
        })

    # Add filing type filter
    if args.filing_types:
        must_clauses.append({
            "terms": {
                "filing_type": correct_provided_types(args.filing_types),
            }
        })

    query = {
        "query": {
            "bool": {
                "must": must_clauses,
                "should": [
                    {
                        "match": {
                            "text": {
                                "query": args.search,
                                "boost": 2.0
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": args.search,
                            "fields": ["text", "title"],
                            "type": "best_fields",
                            "boost": 1.5
                        }
                    }
                ]
            }
        },
        "from": (args.page - 1) * args.page_size,
        "size": args.page_size,
    }

    raw_results = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search/filings",
        api_key=api_key,
        params={},
        data=query,
    )

    # Process raw results into structured format
    structured_results = []

    if raw_results and "result" in raw_results:
        result_data = raw_results["result"]
        if isinstance(result_data, list):
            for item in result_data:
                try:
                    # Parse the date string to datetime
                    date_str = item.get("date", "")
                    if date_str:
                        # Handle different possible date formats
                        if date_str.endswith('Z'):
                            # Replace Z with +00:00 for ISO format compatibility
                            date_str = date_str.replace('Z', '+00:00')
                        elif not date_str.endswith(('+00:00', '-00:00')) and 'T' in date_str:
                            # Add timezone if missing
                            date_str = date_str + '+00:00'
                        parsed_date = datetime.fromisoformat(date_str)
                    else:
                        parsed_date = datetime.now()

                    # Create citation information
                    citation_data = item.get("citation_information", {})
                    citation = FilingSearchCitation(
                        title=citation_data.get("title", ""),
                        url=citation_data.get("url", "")
                    )

                    # Create structured result item
                    search_item = FilingSearchItem(
                        date=parsed_date,
                        primary_company_id=item.get("primary_company_id", 0),
                        content_id=item.get("content_id", 0),
                        filing_id=item.get("filing_id", 0),
                        text=item.get("text", ""),
                        primary_equity_id=item.get("primary_equity_id", 0),
                        title=item.get("title", ""),
                        filing_type=item.get("filing_type"),
                        _score=item.get("_score", 0.0),  # This will be aliased to score
                        citation_information=citation
                    )

                    structured_results.append(search_item)

                except Exception as e:
                    logger.warning(f"Failed to parse filing search result item: {e}")
                    continue

    return SearchFilingsResponse(
        instrument_type="filing_search",
        error_messages=[],
        error_count=0,
        result=structured_results,
        instructions=raw_results.get("instructions", []) if raw_results else [],
        citation_information=[]
    )