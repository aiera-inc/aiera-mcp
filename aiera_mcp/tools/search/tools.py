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
            return SearchTranscriptsResponse.model_validate(raw_response)

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
                return SearchTranscriptsResponse.model_validate(raw_response)

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
            return SearchFilingsResponse.model_validate(raw_response)

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
                return SearchFilingsResponse.model_validate(raw_response)

        except Exception as pipeline_error:
            logger.info(
                f"search_filings: Standard pipeline search failed: {str(pipeline_error)}"
            )

    # if failed, send empty response...
    return _get_empty_filings_response(args.max_results)


def _build_filings_company_filter(company_name: str) -> dict:
    """Build a comprehensive fuzzy company search filter for filing chunks index.

    Uses fuzzy matching against both company_common_name and company_legal_name fields
    to handle variations, typos, and different name formats effectively.

    Based on the opensearch-mcp-server-py implementation for optimal matching.
    """
    import re

    def _remove_special_characters(text: str) -> str:
        """Remove special characters from company names that might not be in filings."""
        clean_text = re.sub(r'[!@#$%^&*()_+\-=\[\]{}|\\:;"\',.<>?/]', "", text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        return clean_text

    def _escape_wildcard_special_chars(text: str) -> str:
        """Escape special characters in text for use in OpenSearch wildcard queries."""
        special_chars = ["*", "?", "[", "]", "{", "}", "\\", "!"]
        escaped_text = text
        for char in special_chars:
            escaped_text = escaped_text.replace(char, f"\\{char}")
        return escaped_text

    # Create variations with special characters handled
    company_clean = _remove_special_characters(company_name)

    # Build comprehensive filter with fuzzy matching as the primary approach
    should_clauses = [
        # Highest priority: exact matches for perfect accuracy
        {
            "term": {
                "company_common_name.keyword": {"value": company_name, "boost": 10.0}
            }
        },
        {
            "term": {
                "company_legal_name.keyword": {"value": company_name, "boost": 10.0}
            }
        },
        # High priority: fuzzy matching on both company name fields with different fuzziness levels
        {
            "fuzzy": {
                "company_common_name": {
                    "value": company_name,
                    "fuzziness": "AUTO",
                    "boost": 8.0,
                    "max_expansions": 50,
                }
            }
        },
        {
            "fuzzy": {
                "company_legal_name": {
                    "value": company_name,
                    "fuzziness": "AUTO",
                    "boost": 8.0,
                    "max_expansions": 50,
                }
            }
        },
        {
            "fuzzy": {
                "company_common_name": {
                    "value": company_clean,
                    "fuzziness": "AUTO",
                    "boost": 7.5,
                    "max_expansions": 50,
                }
            }
        },
        {
            "fuzzy": {
                "company_legal_name": {
                    "value": company_clean,
                    "fuzziness": "AUTO",
                    "boost": 7.5,
                    "max_expansions": 50,
                }
            }
        },
        # Medium-high priority: phrase matching for multi-word company names
        {
            "match_phrase": {
                "company_common_name": {"query": company_name, "boost": 6.0, "slop": 1}
            }
        },
        {
            "match_phrase": {
                "company_legal_name": {"query": company_name, "boost": 6.0, "slop": 1}
            }
        },
        {
            "match_phrase": {
                "company_common_name": {"query": company_clean, "boost": 5.5, "slop": 1}
            }
        },
        {
            "match_phrase": {
                "company_legal_name": {"query": company_clean, "boost": 5.5, "slop": 1}
            }
        },
        # Medium priority: word-based matching with fuzzy operator
        {
            "match": {
                "company_common_name": {
                    "query": company_name,
                    "boost": 5.0,
                    "operator": "and",
                    "fuzziness": "AUTO",
                }
            }
        },
        {
            "match": {
                "company_legal_name": {
                    "query": company_name,
                    "boost": 5.0,
                    "operator": "and",
                    "fuzziness": "AUTO",
                }
            }
        },
        {
            "match": {
                "company_common_name": {
                    "query": company_clean,
                    "boost": 4.5,
                    "operator": "and",
                    "fuzziness": "AUTO",
                }
            }
        },
        {
            "match": {
                "company_legal_name": {
                    "query": company_clean,
                    "boost": 4.5,
                    "operator": "and",
                    "fuzziness": "AUTO",
                }
            }
        },
        # Lower priority: title fuzzy matching for additional coverage
        {
            "fuzzy": {
                "title": {
                    "value": company_name,
                    "fuzziness": "AUTO",
                    "boost": 3.0,
                    "max_expansions": 25,
                }
            }
        },
        {
            "fuzzy": {
                "title": {
                    "value": company_clean,
                    "fuzziness": "AUTO",
                    "boost": 2.5,
                    "max_expansions": 25,
                }
            }
        },
    ]

    # Add selective wildcards for longer names to catch format variations
    if len(company_name) > 4:
        should_clauses.extend(
            [
                {
                    "wildcard": {
                        "company_common_name.keyword": {
                            "value": f"*{_escape_wildcard_special_chars(company_name)}*",
                            "boost": 2.0,
                        }
                    }
                },
                {
                    "wildcard": {
                        "company_legal_name.keyword": {
                            "value": f"*{_escape_wildcard_special_chars(company_name)}*",
                            "boost": 2.0,
                        }
                    }
                },
                {
                    "wildcard": {
                        "company_common_name.keyword": {
                            "value": f"*{_escape_wildcard_special_chars(company_clean)}*",
                            "boost": 1.8,
                        }
                    }
                },
                {
                    "wildcard": {
                        "company_legal_name.keyword": {
                            "value": f"*{_escape_wildcard_special_chars(company_clean)}*",
                            "boost": 1.8,
                        }
                    }
                },
            ]
        )

    company_filter = {"bool": {"should": should_clauses, "minimum_should_match": 1}}

    return company_filter


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
