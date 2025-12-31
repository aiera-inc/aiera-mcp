#!/usr/bin/env python3

"""Search tools for Aiera MCP server."""

import logging
import asyncio

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResponseData,
    TranscriptSearchResponseData,
)

# Setup logging
logger = logging.getLogger(__name__)


async def search_transcripts(args: SearchTranscriptsArgs) -> SearchTranscriptsResponse:
    """Smart event transcript search with dual modes: semantic search or filtered browsing.

    Uses the post_filter approach to avoid "hybrid query must be a top level query" errors,
    similar to the opensearch-mcp-server-py implementation. This tool uses hybrid search
    with neural embedding-based semantic search and the ext.ml_inference.query_text pattern.
    """
    logger.info("tool called: search_transcripts")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    must_clauses = []

    # add event ID filter...
    if args.event_ids:
        must_clauses.append(
            {
                "terms": {
                    "transcript_event_id": args.event_ids,
                }
            }
        )

    # add equity ID filter...
    if args.equity_ids:
        must_clauses.append(
            {
                "terms": {
                    "primary_equity_id": args.equity_ids,
                }
            }
        )

    # add date range filter...
    if args.start_date:
        range = {"gte": args.start_date}
        if args.end_date:
            range["lte"] = args.end_date

        must_clauses.append({"range": {"date": range}})

    # add event type filter...
    if args.event_type and args.event_type in [
        "earnings",
        "presentation",
        "investor_meeting",
        "shareholder_meeting",
        "special_situation",
    ]:
        must_clauses.append({"term": {"transcript_event_type": args.event_type}})

    # add a section filter...
    if args.transcript_section and args.transcript_section in [
        "presentation",
        "q_and_a",
    ]:
        must_clauses.append({"term": {"transcript_section": args.transcript_section}})

    k_value = args.max_results * 2
    if must_clauses:
        k_value = args.max_results * 20  # Increased for filters

    if k_value > 10000:
        k_value = 10000

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {
                        "neural": {
                            "embedding_384": {
                                "query_text": args.query_text,
                                "k": k_value,
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": args.query_text,
                            "fields": ["text^2", "title", "transcript_speaker_name"],
                            "type": "best_fields",
                            "boost": 1.5,
                        }
                    },
                ]
            }
        },
        "post_filter": {
            "bool": {
                "must": must_clauses,
                "must_not": [{"term": {"transcript_event_source": "thirdbridge"}}],
            }
        },
        "size": args.max_results,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
    }

    # Try ML-inference search...
    try:
        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={},
                data=query,
            ),
            timeout=15.0,
        )

        if (
            raw_response
            and "response" in raw_response
            and raw_response["response"].get("result")
        ):
            logger.info("search_transcripts ML inference successful")
            response = SearchTranscriptsResponse.model_validate(raw_response)
            if args.exclude_instructions:
                response.instructions = []
            return response

    except asyncio.TimeoutError:
        logger.warning(
            "search_transcripts: ML inference timed out, falling back to standard search"
        )
        raw_response = None

    # Fall back to standard text-based search with pipeline
    if (
        not raw_response
        or "response" not in raw_response
        or not raw_response["response"].get("result")
    ):
        try:
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "must_not": [
                            {"term": {"transcript_event_source": "thirdbridge"}}
                        ],
                        "should": [
                            {
                                "match": {
                                    "text": {"query": args.query_text, "boost": 2.0}
                                }
                            },
                            {
                                "multi_match": {
                                    "query": args.query_text,
                                    "fields": [
                                        "text",
                                        "title",
                                        "transcript_speaker_name",
                                    ],
                                    "type": "best_fields",
                                    "boost": 1.5,
                                }
                            },
                        ],
                    }
                },
                "size": args.max_results,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
            }

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={},
                data=query,
            )

            if raw_response and "response" in raw_response:
                logger.info("search_transcripts standard pipeline search successful")
                response = SearchTranscriptsResponse.model_validate(raw_response)
                if args.exclude_instructions:
                    response.instructions = []
                return response

        except Exception as pipeline_error:
            logger.info(
                f"search_transcripts: Standard pipeline search failed: {str(pipeline_error)}"
            )

    # if failed, send empty response...
    return _get_empty_transcripts_response(args.max_results)


async def search_filings(args: SearchFilingsArgs) -> SearchFilingsResponse:
    """Semantic search within SEC filing document chunks using embedding-based matching.

    Uses the post_filter approach to avoid "hybrid query must be a top level query" errors,
    similar to the opensearch-mcp-server-py implementation. This tool uses the
    ext.ml_inference.query_text pattern to automatically generate embeddings
    from the query text using the configured embedding pipeline.
    """
    logger.info("tool called: search_filings")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    must_clauses = []

    # add event ID filter...
    if args.filing_ids:
        must_clauses.append(
            {
                "terms": {
                    "filing_id": args.filing_ids,
                }
            }
        )

    # add equity ID filter...
    if args.equity_ids:
        must_clauses.append(
            {
                "terms": {
                    "primary_equity_id": args.equity_ids,
                }
            }
        )

    # add date range filter...
    if args.start_date:
        range = {"gte": args.start_date}
        if args.end_date:
            range["lte"] = args.end_date

        must_clauses.append({"range": {"date": range}})

    # add filing type filter...
    if args.filing_type:
        must_clauses.append(
            {
                "term": {
                    "filing_type": args.filing_type,
                }
            }
        )

    k_value = args.max_results * 2
    if must_clauses:
        k_value = args.max_results * 20  # Increased for filters

    if k_value > 10000:
        k_value = 10000

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {
                        "neural": {
                            "embedding_384": {
                                "query_text": args.query_text,
                                "k": k_value,
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": args.query_text,
                            "fields": ["text^2", "title", "transcript_speaker_name"],
                            "type": "best_fields",
                            "boost": 1.5,
                        }
                    },
                ]
            }
        },
        "post_filter": {
            "bool": {
                "must": must_clauses,
            }
        },
        "size": args.max_results,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
    }

    # Try ML-inference search...
    try:
        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/filing-chunks",
                api_key=api_key,
                params={},
                data=query,
            ),
            timeout=15.0,
        )

        if (
            raw_response
            and "response" in raw_response
            and raw_response["response"].get("result")
        ):
            logger.info("search_filings ML inference successful")
            response = SearchFilingsResponse.model_validate(raw_response)
            if args.exclude_instructions:
                response.instructions = []
            return response

    except asyncio.TimeoutError:
        logger.warning(
            "search_filings: ML inference timed out, falling back to standard search"
        )
        raw_response = None

    # Fall back to standard text-based search with pipeline
    if (
        not raw_response
        or "response" not in raw_response
        or not raw_response["response"].get("result")
    ):
        try:
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "should": [
                            {
                                "match": {
                                    "text": {"query": args.query_text, "boost": 2.0}
                                }
                            },
                            {
                                "multi_match": {
                                    "query": args.query_text,
                                    "fields": ["text", "title"],
                                    "type": "best_fields",
                                    "boost": 1.5,
                                }
                            },
                        ],
                    }
                },
                "size": args.max_results,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
            }

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={},
                data=query,
            )

            if raw_response and "response" in raw_response:
                logger.info("search_filings standard pipeline search successful")
                response = SearchFilingsResponse.model_validate(raw_response)
                if args.exclude_instructions:
                    response.instructions = []
                return response

        except Exception as pipeline_error:
            logger.info(
                f"search_filings: Standard pipeline search failed: {str(pipeline_error)}"
            )

    # if failed, send empty response...
    return _get_empty_filings_response(args.max_results)


def _get_empty_filings_response(max_results: int) -> SearchFilingsResponse:
    """Return empty response structure for filing chunks search."""
    return SearchFilingsResponse(
        instructions=[],
        response=SearchResponseData(
            result=[],
        ),
    )


def _get_empty_transcripts_response(max_results: int) -> SearchTranscriptsResponse:
    """Return empty response structure for transcript search."""
    return SearchTranscriptsResponse(
        instructions=[],
        response=TranscriptSearchResponseData(
            result=[],
        ),
    )
