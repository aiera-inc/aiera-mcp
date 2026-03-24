#!/usr/bin/env python3

"""Search tools for Aiera MCP server."""

import logging
import asyncio

from ..base import get_http_client, make_aiera_request
from ..utils import correct_bloomberg_ticker
from ... import get_api_key
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchCompanyDocsArgs,
    SearchThirdbridgeArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResearchResponse,
    SearchCompanyDocsResponse,
    SearchThirdbridgeResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


def _build_filter_clause(
    must_clauses: list,
    must_not_clauses: list = None,
) -> dict | None:
    """Build a bool filter clause from must/must_not lists.

    Returns None if no clauses are provided, allowing callers
    to conditionally omit the filter entirely.
    """
    if not must_clauses and not must_not_clauses:
        return None

    bool_body = {}
    if must_clauses:
        bool_body["must"] = must_clauses
    if must_not_clauses:
        bool_body["must_not"] = must_not_clauses

    return {"bool": bool_body}


def _has_search_results(raw_response: dict) -> bool:
    """Check if a raw search API response contains results.

    The API may return results under either the 'result' or 'data' key
    within the 'response' object.
    """
    if not raw_response or "response" not in raw_response:
        return False
    resp = raw_response["response"]
    if not isinstance(resp, dict):
        return False
    return bool(resp.get("result")) or bool(resp.get("data"))


async def search_transcripts(args: SearchTranscriptsArgs) -> SearchTranscriptsResponse:
    """Smart event transcript search with dual modes: semantic search or filtered browsing.

    Uses per-sub-query filters within the hybrid query for efficient pre-filtering.
    Neural queries use the filter parameter for kNN pre-filtering, and text queries
    are wrapped in a bool with a filter clause.
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

    # always exclude thirdbridge from transcript search
    must_not_clauses = [{"term": {"transcript_event_source": "thirdbridge"}}]

    filter_clause = _build_filter_clause(must_clauses, must_not_clauses)

    k_value = min(args.size * 2, 10000)

    # build neural sub-query with pre-filter
    neural_inner = {
        "query_text": args.query_text,
        "k": k_value,
    }
    if filter_clause:
        neural_inner["filter"] = filter_clause

    # build text sub-query with filter
    multi_match_query = {
        "multi_match": {
            "query": args.query_text,
            "fields": ["text^2", "title", "transcript_speaker_name"],
            "type": "best_fields",
            "boost": 1.5,
        }
    }
    if filter_clause:
        text_query = {
            "bool": {
                "must": [multi_match_query],
                "filter": [filter_clause],
            }
        }
    else:
        text_query = multi_match_query

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {"neural": {"embedding_384": neural_inner}},
                    text_query,
                ]
            }
        },
        "size": args.size,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
        "self_identification": args.self_identification,
    }

    if args.search_after is not None:
        query["search_after"] = args.search_after

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

        if _has_search_results(raw_response):
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
    if not _has_search_results(raw_response):
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
                                    "text": {
                                        "query": args.query_text,
                                        "boost": 2.0,
                                    }
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
                "size": args.size,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
                "self_identification": args.self_identification,
            }

            if args.search_after is not None:
                query["search_after"] = args.search_after

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
    return _get_empty_transcripts_response()


async def search_filings(args: SearchFilingsArgs) -> SearchFilingsResponse:
    """Semantic search within SEC filing document chunks using embedding-based matching.

    Uses per-sub-query filters within the hybrid query for efficient pre-filtering.
    Neural queries use the filter parameter for kNN pre-filtering, and text queries
    are wrapped in a bool with a filter clause.
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

    filter_clause = _build_filter_clause(must_clauses)

    k_value = min(args.size * 2, 10000)

    # build neural sub-query with pre-filter
    neural_inner = {
        "query_text": args.query_text,
        "k": k_value,
    }
    if filter_clause:
        neural_inner["filter"] = filter_clause

    # build text sub-query with filter
    multi_match_query = {
        "multi_match": {
            "query": args.query_text,
            "fields": ["text^2", "title", "transcript_speaker_name"],
            "type": "best_fields",
            "boost": 1.5,
        }
    }
    if filter_clause:
        text_query = {
            "bool": {
                "must": [multi_match_query],
                "filter": [filter_clause],
            }
        }
    else:
        text_query = multi_match_query

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {"neural": {"embedding_384": neural_inner}},
                    text_query,
                ]
            }
        },
        "size": args.size,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
        "self_identification": args.self_identification,
    }

    if args.search_after is not None:
        query["search_after"] = args.search_after

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

        if _has_search_results(raw_response):
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
    if not _has_search_results(raw_response):
        try:
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "should": [
                            {
                                "match": {
                                    "text": {
                                        "query": args.query_text,
                                        "boost": 2.0,
                                    }
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
                "size": args.size,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
                "self_identification": args.self_identification,
            }

            if args.search_after is not None:
                query["search_after"] = args.search_after

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/filing-chunks",
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
    return _get_empty_filings_response()


async def search_research(args: SearchResearchArgs) -> SearchResearchResponse:
    """Semantic search within research document chunks using embedding-based matching.

    Uses per-sub-query filters within the hybrid query for efficient pre-filtering.
    Neural queries use the filter parameter for kNN pre-filtering, and text queries
    are wrapped in a bool with a filter clause.
    """
    logger.info("tool called: search_research")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    must_clauses = []

    # add bloomberg ticker filter...
    if args.bloomberg_ticker:
        ticker = correct_bloomberg_ticker(args.bloomberg_ticker)
        must_clauses.append({"term": {"bloomberg_tickers": ticker}})

    # add document ID filter...
    if args.document_ids:
        must_clauses.append(
            {
                "terms": {
                    "parent_research_id": args.document_ids,
                }
            }
        )

    # add date range filter...
    if args.start_date:
        range = {"gte": args.start_date}
        if args.end_date:
            range["lte"] = args.end_date

        must_clauses.append({"range": {"published_datetime": range}})

    # add author filter...
    if args.author_ids:
        must_clauses.append({"terms": {"authors.person_id": args.author_ids}})

    # add aiera provider ID filter...
    if args.aiera_provider_ids:
        must_clauses.append({"terms": {"aiera_provider_id": args.aiera_provider_ids}})

    # add asset classes filter...
    if args.asset_classes:
        must_clauses.append({"terms": {"asset_classes": args.asset_classes}})

    # add asset types filter...
    if args.asset_types:
        must_clauses.append({"terms": {"asset_types": args.asset_types}})

    filter_clause = _build_filter_clause(must_clauses)

    k_value = min(args.size * 2, 10000)

    # build neural sub-query with pre-filter
    neural_inner = {
        "query_text": args.query_text,
        "k": k_value,
    }
    if filter_clause:
        neural_inner["filter"] = filter_clause

    # build text sub-query with filter
    multi_match_query = {
        "multi_match": {
            "query": args.query_text,
            "fields": ["text^2", "title"],
            "type": "best_fields",
            "boost": 1.5,
        }
    }
    if filter_clause:
        text_query = {
            "bool": {
                "must": [multi_match_query],
                "filter": [filter_clause],
            }
        }
    else:
        text_query = multi_match_query

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {"neural": {"passage_chunk.knn": neural_inner}},
                    text_query,
                ]
            }
        },
        "size": args.size,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
        "self_identification": args.self_identification,
    }

    if args.search_after is not None:
        query["search_after"] = args.search_after

    # Try ML-inference search...
    try:
        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/research-chunks",
                api_key=api_key,
                params={},
                data=query,
            ),
            timeout=15.0,
        )

        if _has_search_results(raw_response):
            logger.info("search_research ML inference successful")
            response = SearchResearchResponse.model_validate(raw_response)
            if args.exclude_instructions:
                response.instructions = []
            return response

    except asyncio.TimeoutError:
        logger.warning(
            "search_research: ML inference timed out, falling back to standard search"
        )
        raw_response = None

    # Fall back to standard text-based search with pipeline
    if not _has_search_results(raw_response):
        try:
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "should": [
                            {
                                "match": {
                                    "text": {
                                        "query": args.query_text,
                                        "boost": 2.0,
                                    }
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
                "size": args.size,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
                "self_identification": args.self_identification,
            }

            if args.search_after is not None:
                query["search_after"] = args.search_after

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/research-chunks",
                api_key=api_key,
                params={},
                data=query,
            )

            if raw_response and "response" in raw_response:
                logger.info("search_research standard pipeline search successful")
                response = SearchResearchResponse.model_validate(raw_response)
                if args.exclude_instructions:
                    response.instructions = []
                return response

        except Exception as pipeline_error:
            logger.info(
                f"search_research: Standard pipeline search failed: {str(pipeline_error)}"
            )

    # if failed, send empty response...
    return _get_empty_research_response()


async def search_company_docs(args: SearchCompanyDocsArgs) -> SearchCompanyDocsResponse:
    """Semantic search within company document chunks using embedding-based matching.

    Uses per-sub-query filters within the hybrid query for efficient pre-filtering.
    Neural queries use the filter parameter for kNN pre-filtering, and text queries
    are wrapped in a bool with a filter clause.
    """
    logger.info("tool called: search_company_docs")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    must_clauses = []

    # add company doc ID filter...
    if args.company_doc_ids:
        must_clauses.append(
            {
                "terms": {
                    "company_doc_id": args.company_doc_ids,
                }
            }
        )

    # add company ID filter...
    if args.company_ids:
        must_clauses.append(
            {
                "terms": {
                    "company_id": args.company_ids,
                }
            }
        )

    # add category filter...
    if args.categories:
        must_clauses.append({"terms": {"category.keyword": args.categories}})

    # add keywords filter...
    if args.keywords:
        must_clauses.append({"terms": {"keywords": args.keywords}})

    # add date range filter...
    if args.start_date:
        range = {"gte": args.start_date}
        if args.end_date:
            range["lte"] = args.end_date

        must_clauses.append({"range": {"publish_date": range}})

    filter_clause = _build_filter_clause(must_clauses)

    k_value = min(args.size * 2, 10000)

    # build neural sub-query with pre-filter
    neural_inner = {
        "query_text": args.query_text,
        "k": k_value,
    }
    if filter_clause:
        neural_inner["filter"] = filter_clause

    # build text sub-query with filter
    multi_match_query = {
        "multi_match": {
            "query": args.query_text,
            "fields": ["text^2", "title", "summary"],
            "type": "best_fields",
            "boost": 1.5,
        }
    }
    if filter_clause:
        text_query = {
            "bool": {
                "must": [multi_match_query],
                "filter": [filter_clause],
            }
        }
    else:
        text_query = multi_match_query

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {"neural": {"passage_chunk.knn": neural_inner}},
                    text_query,
                ]
            }
        },
        "size": args.size,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
        "self_identification": args.self_identification,
    }

    if args.search_after is not None:
        query["search_after"] = args.search_after

    # Try ML-inference search...
    try:
        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/company-doc-chunks",
                api_key=api_key,
                params={},
                data=query,
            ),
            timeout=15.0,
        )

        if _has_search_results(raw_response):
            logger.info("search_company_docs ML inference successful")
            response = SearchCompanyDocsResponse.model_validate(raw_response)
            if args.exclude_instructions:
                response.instructions = []
            return response

    except asyncio.TimeoutError:
        logger.warning(
            "search_company_docs: ML inference timed out, falling back to standard search"
        )
        raw_response = None

    # Fall back to standard text-based search with pipeline
    if not _has_search_results(raw_response):
        try:
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "should": [
                            {
                                "match": {
                                    "text": {
                                        "query": args.query_text,
                                        "boost": 2.0,
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": args.query_text,
                                    "fields": ["text", "title", "summary"],
                                    "type": "best_fields",
                                    "boost": 1.5,
                                }
                            },
                        ],
                    }
                },
                "size": args.size,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
                "self_identification": args.self_identification,
            }

            if args.search_after is not None:
                query["search_after"] = args.search_after

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/company-doc-chunks",
                api_key=api_key,
                params={},
                data=query,
            )

            if raw_response and "response" in raw_response:
                logger.info("search_company_docs standard pipeline search successful")
                response = SearchCompanyDocsResponse.model_validate(raw_response)
                if args.exclude_instructions:
                    response.instructions = []
                return response

        except Exception as pipeline_error:
            logger.info(
                f"search_company_docs: Standard pipeline search failed: {str(pipeline_error)}"
            )

    # if failed, send empty response...
    return _get_empty_company_docs_response()


async def search_thirdbridge(args: SearchThirdbridgeArgs) -> SearchThirdbridgeResponse:
    """Semantic search within Third Bridge expert interview transcripts using embedding-based matching.

    Uses per-sub-query filters within the hybrid query for efficient pre-filtering.
    Neural queries use the filter parameter for kNN pre-filtering, and text queries
    are wrapped in a bool with a filter clause.
    """
    logger.info("tool called: search_thirdbridge")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    must_clauses = []

    # add company ID filter (matches primary or secondary company IDs)...
    if args.company_ids:
        must_clauses.append(
            {
                "bool": {
                    "should": [
                        {"terms": {"primary_company_ids": args.company_ids}},
                        {"terms": {"secondary_company_ids": args.company_ids}},
                    ],
                    "minimum_should_match": 1,
                }
            }
        )

    # add Third Bridge ID filter...
    if args.thirdbridge_ids:
        must_clauses.append(
            {
                "terms": {
                    "thirdbridge_id": args.thirdbridge_ids,
                }
            }
        )

    # add date range filter...
    if args.start_date:
        range = {"gte": args.start_date}
        if args.end_date:
            range["lte"] = args.end_date

        must_clauses.append({"range": {"event_date": range}})

    # add event content type filter...
    if args.event_content_type:
        must_clauses.append(
            {"term": {"event_content_type.keyword": args.event_content_type}}
        )

    filter_clause = _build_filter_clause(must_clauses)

    k_value = min(args.size * 2, 10000)

    # build neural sub-query with pre-filter
    neural_inner = {
        "query_text": args.query_text,
        "k": k_value,
    }
    if filter_clause:
        neural_inner["filter"] = filter_clause

    # build text sub-query with filter
    multi_match_query = {
        "multi_match": {
            "query": args.query_text,
            "fields": [
                "text^2",
                "event_title",
                "event_agenda",
                "event_insights",
            ],
            "type": "best_fields",
            "boost": 1.5,
        }
    }
    if filter_clause:
        text_query = {
            "bool": {
                "must": [multi_match_query],
                "filter": [filter_clause],
            }
        }
    else:
        text_query = multi_match_query

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {"neural": {"embedding_384": neural_inner}},
                    text_query,
                ]
            }
        },
        "size": args.size,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
        "self_identification": args.self_identification,
    }

    if args.search_after is not None:
        query["search_after"] = args.search_after

    # Try ML-inference search...
    try:
        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/thirdbridge",
                api_key=api_key,
                params={},
                data=query,
            ),
            timeout=15.0,
        )

        if _has_search_results(raw_response):
            logger.info("search_thirdbridge ML inference successful")
            response = SearchThirdbridgeResponse.model_validate(raw_response)
            if args.exclude_instructions:
                response.instructions = []
            return response

    except asyncio.TimeoutError:
        logger.warning(
            "search_thirdbridge: ML inference timed out, falling back to standard search"
        )
        raw_response = None

    # Fall back to standard text-based search with pipeline
    if not _has_search_results(raw_response):
        try:
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "should": [
                            {
                                "match": {
                                    "text": {
                                        "query": args.query_text,
                                        "boost": 2.0,
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": args.query_text,
                                    "fields": [
                                        "text",
                                        "event_title",
                                        "event_agenda",
                                        "event_insights",
                                    ],
                                    "type": "best_fields",
                                    "boost": 1.5,
                                }
                            },
                        ],
                    }
                },
                "size": args.size,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
                "self_identification": args.self_identification,
            }

            if args.search_after is not None:
                query["search_after"] = args.search_after

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/thirdbridge",
                api_key=api_key,
                params={},
                data=query,
            )

            if raw_response and "response" in raw_response:
                logger.info("search_thirdbridge standard pipeline search successful")
                response = SearchThirdbridgeResponse.model_validate(raw_response)
                if args.exclude_instructions:
                    response.instructions = []
                return response

        except Exception as pipeline_error:
            logger.info(
                f"search_thirdbridge: Standard pipeline search failed: {str(pipeline_error)}"
            )

    # if failed, send empty response...
    return _get_empty_thirdbridge_response()


def _get_empty_filings_response() -> SearchFilingsResponse:
    """Return empty response structure for filing chunks search."""
    return SearchFilingsResponse(
        instructions=[],
        response={"result": [], "pagination": None},
    )


def _get_empty_transcripts_response() -> SearchTranscriptsResponse:
    """Return empty response structure for transcript search."""
    return SearchTranscriptsResponse(
        instructions=[],
        response={"result": [], "pagination": None},
    )


def _get_empty_research_response() -> SearchResearchResponse:
    """Return empty response structure for research chunks search."""
    return SearchResearchResponse(
        instructions=[],
        response={"result": [], "pagination": None},
    )


def _get_empty_company_docs_response() -> SearchCompanyDocsResponse:
    """Return empty response structure for company doc chunks search."""
    return SearchCompanyDocsResponse(
        instructions=[],
        response={"result": [], "pagination": None},
    )


def _get_empty_thirdbridge_response() -> SearchThirdbridgeResponse:
    """Return empty response structure for Third Bridge search."""
    return SearchThirdbridgeResponse(
        instructions=[],
        response={"result": [], "pagination": None},
    )
