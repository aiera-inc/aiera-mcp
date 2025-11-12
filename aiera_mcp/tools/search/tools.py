#!/usr/bin/env python3

"""Search tools for Aiera MCP server."""

import logging

from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchFilingChunksArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchFilingChunksResponse,
    TranscriptSearchItem,
    TranscriptSearchCitation,
    FilingSearchItem,
    FilingSearchCitation,
    FilingChunkSearchItem,
)
from .utils import correct_provided_ids, correct_provided_types, correct_event_type

# Setup logging
logger = logging.getLogger(__name__)


async def search_transcripts(args: SearchTranscriptsArgs) -> SearchTranscriptsResponse:
    """Semantic search within specific transcript events using embedding-based matching.

    Tool for extracting detailed transcript content from events identified
    in prior searches. Provides speaker attribution and contextual results.
    """
    logger.info("tool called: search_transcripts")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    # Build the query for event-filtered search
    # Start with standard OpenSearch query, try ML inference as enhancement if available
    must_clauses = [
        # Event filter as MUST clause - gives baseline score > 0
        {"terms": {"transcript_event_id": [event_id for event_id in args.event_ids]}}
    ]

    # Add transcript section filter if provided with multiple field variations
    if args.transcript_section and args.transcript_section.strip():
        section_filter = {
            "bool": {
                "should": [
                    {"term": {"section.keyword": args.transcript_section}},
                    {"term": {"transcript_section.keyword": args.transcript_section}},
                    {"term": {"section": args.transcript_section}},
                    {"term": {"transcript_section": args.transcript_section}},
                ],
                "minimum_should_match": 1,
            }
        }
        must_clauses.append(section_filter)

    base_query = {
        "query": {
            "bool": {
                "must": must_clauses,
                "should": [
                    # Text search for BOOSTING on top of baseline score
                    {"match": {"text": {"query": args.query_text, "boost": 2.0}}},
                    # Multi-field search for broader boosting
                    {
                        "multi_match": {
                            "query": args.query_text,
                            "fields": ["text", "title", "speaker_name"],
                            "type": "best_fields",
                            "boost": 1.5,
                        }
                    },
                ],
                # NO minimum_should_match - should clauses are optional for boosting
            }
        },
        "size": args.max_results,
        "min_score": args.min_score,
        "_source": [
            "content_id",
            "text",
            "transcript_event_id",
            "title",
            "speaker_name",
            "speaker_title",
            "date",
            "section",
            "transcript_section",
        ],
        "sort": [{"_score": {"order": "desc"}}],
    }

    # ML query optimized for pipeline search - let ML do the semantic matching
    ml_query = {
        "query": {
            "bool": {"must": must_clauses}  # Use the same must clauses as base query
        },
        "size": args.max_results,
        "min_score": args.min_score,
        "_source": [
            "content_id",
            "text",
            "transcript_event_id",
            "title",
            "speaker_name",
            "speaker_title",
            "date",
            "section",
            "transcript_section",
        ],
        "sort": [{"_score": {"order": "desc"}}],
        "search_pipeline": "embedding_script_pipeline",
        "ext": {"ml_inference": {"query_text": args.query_text}},
    }

    # Try ML inference search first, fall back to standard search if it fails
    try:
        # Try with ML inference enhancement
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/transcripts",
            api_key=api_key,
            params={},
            data=ml_query,
        )
        logger.info("ML inference search succeeded")

        # Check if we got good results
        if (
            raw_response
            and "response" in raw_response
            and raw_response["response"].get("result")
        ):
            return SearchTranscriptsResponse.model_validate(raw_response)
        else:
            logger.info(
                "ML inference returned no results, falling back to standard search"
            )
            raise Exception("ML inference returned no results")

    except Exception as ml_error:
        logger.info(
            f"ML inference search failed: {str(ml_error)}, falling back to standard search"
        )

        try:
            # Fall back to standard search without ML inference
            base_query["search_pipeline"] = "embedding_script_pipeline"
            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={},
                data=base_query,
            )
            logger.info("Standard search with pipeline succeeded")
            return SearchTranscriptsResponse.model_validate(raw_response)

        except Exception as pipeline_error:
            logger.info(
                f"Pipeline search failed: {str(pipeline_error)}, trying direct search"
            )

            # Try direct search without pipeline as final fallback
            base_query.pop("search_pipeline", None)
            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={},
                data=base_query,
            )
            logger.info("Direct search succeeded")
            return SearchTranscriptsResponse.model_validate(raw_response)


async def search_filings(args: SearchFilingsArgs) -> SearchFilingsResponse:
    """SEC filing discovery tool for identifying relevant filings before detailed content analysis.

    Returns filing metadata (excluding full text) optimized for filing identification and
    integration with FilingChunkSearch. Supports 60+ SEC document types with intelligent
    company name matching and comprehensive filtering capabilities.
    """
    logger.info("tool called: search_filings")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    company_name = args.company_name.strip()
    logger.info(
        f"SearchFilings: enhanced search for '{company_name}' filings, start_date='{args.start_date}', end_date='{args.end_date}', document_types={args.document_types}"
    )

    # Build flexible company name search using multiple strategies
    should_clauses = [
        # Primary: match_phrase (works well for exact company names)
        {"match_phrase": {"title": {"query": company_name, "boost": 15.0}}},
        # Secondary: flexible wildcard matching
        {
            "wildcard": {
                "title": {
                    "value": f"*{company_name}*",
                    "case_insensitive": True,
                    "boost": 8.0,
                }
            }
        },
        # For compound names, try individual words
        *[
            {
                "wildcard": {
                    "title": {
                        "value": f"*{word.strip()}*",
                        "case_insensitive": True,
                        "boost": 6.0,
                    }
                }
            }
            for word in company_name.replace("&", " ").replace("  ", " ").split()
            if len(word.strip()) > 2
        ],  # Skip short words like "&"
        # Structured company field matches (fallback since these are often empty)
        {"term": {"company_name.keyword": company_name}},
        {"term": {"issuer_name.keyword": company_name}},
        {"term": {"entity_name.keyword": company_name}},
        {"term": {"filer_name.keyword": company_name}},
    ]

    # Add document type filter using match_phrase since wildcard queries don't work reliably
    filter_clauses = []
    if args.document_types:
        doc_type_filters = []
        for doc_type in args.document_types:
            doc_type_upper = doc_type.upper()
            # Use match_phrase for document type matching
            doc_type_filters.extend(
                [
                    # Primary: exact phrase match for the document type
                    {
                        "match_phrase": {
                            "title": {"query": doc_type_upper, "boost": 10.0}
                        }
                    },
                    {
                        "match_phrase": {
                            "title": {"query": doc_type.lower(), "boost": 8.0}
                        }
                    },
                    # Structured field matching as fallback
                    {"term": {"document_type.keyword": doc_type_upper}},
                    {"term": {"form_type.keyword": doc_type_upper}},
                    {"term": {"filing_type.keyword": doc_type_upper}},
                ]
            )

        if doc_type_filters:
            document_type_filter = {
                "bool": {"should": doc_type_filters, "minimum_should_match": 1}
            }
            filter_clauses.append(document_type_filter)

    # Build date filter
    if args.start_date or args.end_date:
        date_range = {}
        if args.start_date:
            date_range["gte"] = args.start_date
        if args.end_date:
            date_range["lte"] = args.end_date
        if date_range:
            filter_clauses.append({"range": {"date": date_range}})

    # Add amendments filter
    if not args.include_amendments:
        filter_clauses.append(
            {"bool": {"must_not": {"regexp": {"filing_type": ".*[/]A"}}}}
        )

    # Add filing type boosting if no specific document types are requested
    if not args.document_types:
        logger.info(
            f"No document types specified for '{company_name}', adding filing type boosting for important SEC forms"
        )
        # Define filing type priorities with boost scores
        priority_filings = {
            # Core periodic reports (highest priority)
            "10-K": 15.0,  # Annual report - most comprehensive
            "10-Q": 12.0,  # Quarterly report - regular updates
            "8-K": 10.0,  # Current report - material events
            # International and specialized forms (medium-high priority)
            "20-F": 8.0,  # Annual report for foreign companies
            "DEF 14A": 7.0,  # Proxy statement
            "S-1": 6.0,  # Registration statement for IPOs
            "S-3": 5.0,  # Registration statement for seasoned companies
        }

        filing_boosting_clauses = []
        # Add boosting for each priority filing type
        for filing_type, boost_score in priority_filings.items():
            # Boost in title patterns (common SEC filing title formats)
            filing_boosting_clauses.extend(
                [
                    {
                        "wildcard": {
                            "title": {
                                "value": f"*- {filing_type}",
                                "case_insensitive": True,
                                "boost": boost_score * 0.8,
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "title": {
                                "value": f"* - {filing_type}",
                                "case_insensitive": True,
                                "boost": boost_score * 0.8,
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "title": {
                                "value": f"*{filing_type}*",
                                "case_insensitive": True,
                                "boost": boost_score * 0.6,
                            }
                        }
                    },
                ]
            )

        should_clauses.extend(filing_boosting_clauses)

    # Build sort clause
    sort_clause = []
    if args.sort_by == "desc":
        sort_clause = [{"date": {"order": "desc"}}, {"_score": {"order": "desc"}}]
    elif args.sort_by == "asc":
        sort_clause = [{"date": {"order": "asc"}}, {"_score": {"order": "desc"}}]
    elif args.sort_by == "relevance":
        sort_clause = [{"_score": {"order": "desc"}}, {"date": {"order": "desc"}}]

    # Build query - ensure filters are strictly enforced in the filter clause
    query = {
        "size": args.max_results,
        "query": {
            "bool": {
                "should": should_clauses,
                "filter": filter_clauses,
                "minimum_should_match": 1,
            }
        },
        "_source": [
            "content_id",
            "title",
            "company_name",
            "issuer_name",
            "entity_name",
            "document_type",
            "form_type",
            "filing_type",
            "date",
            "filing_date",
            "filing_id",
        ],
        "sort": sort_clause,
        "timeout": "15s",
        "search_pipeline": "embedding_script_pipeline",
    }

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/chat-support/search/filings",
        api_key=api_key,
        params={},
        data=query,
    )

    return SearchFilingsResponse.model_validate(raw_response)


async def search_filing_chunks(
    args: SearchFilingChunksArgs,
) -> SearchFilingChunksResponse:
    """Semantic search within SEC filing document chunks using embedding-based matching.

    Extracts relevant filing content chunks filtered by company, date, and filing type
    with high-quality semantic relevance scoring.
    """
    logger.info("tool called: search_filing_chunks")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = await get_api_key_from_context(None)

    # Build the query dynamically based on provided parameters
    should_clauses = []
    must_filters = []

    # Add text search clauses if query_text is provided
    if args.query_text and args.query_text.strip():
        should_clauses.extend(
            [
                # Primary text search
                {"match": {"text": {"query": args.query_text, "boost": 2.0}}},
                # Title/summary search
                {
                    "multi_match": {
                        "query": args.query_text,
                        "fields": ["title^1.5", "summary"],
                        "boost": 1.5,
                    }
                },
            ]
        )

    # Add company search if company_name is provided using precise filtering
    if args.company_name and args.company_name.strip():
        company_filter = {
            "bool": {
                "should": [
                    # High priority: exact matches and close variations
                    {
                        "term": {
                            "company_common_name.keyword": {
                                "value": args.company_name,
                                "boost": 5.0,
                            }
                        }
                    },
                    {
                        "term": {
                            "company_legal_name.keyword": {
                                "value": args.company_name,
                                "boost": 5.0,
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "company_common_name": {
                                "query": args.company_name,
                                "boost": 4.0,
                            }
                        }
                    },
                    {
                        "match_phrase": {
                            "company_legal_name": {
                                "query": args.company_name,
                                "boost": 4.0,
                            }
                        }
                    },
                    # Medium priority: word-based matching (more precise than wildcards)
                    {
                        "match": {
                            "company_common_name": {
                                "query": args.company_name,
                                "boost": 3.0,
                                "operator": "and",
                            }
                        }
                    },
                    {
                        "match": {
                            "company_legal_name": {
                                "query": args.company_name,
                                "boost": 3.0,
                                "operator": "and",
                            }
                        }
                    },
                    # Lower priority: fuzzy matching for typos (limited fuzziness)
                    {
                        "fuzzy": {
                            "company_common_name": {
                                "value": args.company_name,
                                "fuzziness": 1,
                                "boost": 2.0,
                            }
                        }
                    },
                    {
                        "fuzzy": {
                            "company_legal_name": {
                                "value": args.company_name,
                                "fuzziness": 1,
                                "boost": 2.0,
                            }
                        }
                    },
                    # Title matching with phrase search
                    {
                        "match_phrase": {
                            "title": {"query": args.company_name, "boost": 2.5}
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        }

        # If we have text search, add company as filter
        if should_clauses:
            must_filters.append(company_filter)
        else:
            # If no text search, use company query as main query for scoring
            should_clauses.append(company_filter)

    # If no search clauses at all, use match_all as fallback
    if not should_clauses:
        should_clauses.append({"match_all": {}})

    # Add date filter
    if args.start_date or args.end_date:
        date_range = {}
        if args.start_date:
            date_range["gte"] = args.start_date
        if args.end_date:
            date_range["lte"] = args.end_date
        if date_range:
            must_filters.append({"range": {"date": date_range}})

    # Add filing type filter
    if args.filing_type and args.filing_type.strip():
        filing_type_filter = {
            "bool": {
                "should": [
                    {"term": {"filing_type": args.filing_type}},
                    {"wildcard": {"title": f"*{args.filing_type.upper()}*"}},
                ],
                "minimum_should_match": 1,
            }
        }
        must_filters.append(filing_type_filter)

    # Add filing IDs filter
    if args.filing_ids:
        # Filter out empty strings and strip whitespace
        valid_filing_ids = [fid.strip() for fid in args.filing_ids if fid.strip()]
        if valid_filing_ids:
            filing_ids_filter = {
                "terms": {"filing_id": [int(fid) for fid in valid_filing_ids]}
            }
            must_filters.append(filing_ids_filter)

    # Add content IDs filter
    if args.content_ids:
        # Filter out empty strings and strip whitespace
        valid_content_ids = [cid.strip() for cid in args.content_ids if cid.strip()]
        if valid_content_ids:
            content_ids_filter = {"terms": {"content_id": valid_content_ids}}
            must_filters.append(content_ids_filter)

    # Build base query structure
    base_query = {
        "query": {
            "bool": {
                "should": should_clauses,
                "filter": must_filters,
                "minimum_should_match": 1,
            }
        },
        "size": args.max_results,
        "min_score": args.min_score,
        "timeout": "10s",
        "_source": [
            "content_id",
            "text",
            "title",
            "company_common_name",
            "filing_id",
            "filing_form_id",
            "date",
            "chunk_id",
        ],
    }

    # ML-enhanced query for embedding search
    ml_query = {
        "size": args.max_results,
        "min_score": args.min_score,
        "timeout": "15s",
        "_source": [
            "content_id",
            "text",
            "title",
            "company_common_name",
            "filing_id",
            "filing_form_id",
            "date",
            "chunk_id",
        ],
        "search_pipeline": "embedding_script_pipeline",
    }

    # Use simplified filter logic for ML query (complex filters can slow down ML inference)
    ml_filters = []

    # Add date filter (simple and effective)
    if args.start_date or args.end_date:
        date_range = {}
        if args.start_date:
            date_range["gte"] = args.start_date
        if args.end_date:
            date_range["lte"] = args.end_date
        if date_range:
            ml_filters.append({"range": {"date": date_range}})

    # Add simple filing type filter
    if args.filing_type and args.filing_type.strip():
        ml_filters.append({"term": {"filing_type": args.filing_type}})

    # Add simple company filter
    if args.company_name and args.company_name.strip():
        ml_filters.append(
            {
                "match": {
                    "company_common_name": {
                        "query": args.company_name,
                        "operator": "and",
                    }
                }
            }
        )

    # Add filing IDs filter for ML
    if args.filing_ids:
        valid_filing_ids = [fid.strip() for fid in args.filing_ids if fid.strip()]
        if valid_filing_ids:
            ml_filters.append(
                {"terms": {"filing_id": [int(fid) for fid in valid_filing_ids]}}
            )

    # Add content IDs filter for ML
    if args.content_ids:
        valid_content_ids = [cid.strip() for cid in args.content_ids if cid.strip()]
        if valid_content_ids:
            ml_filters.append({"terms": {"content_id": valid_content_ids}})

    ml_query["query"] = {"bool": {"filter": ml_filters}}

    # Try ML inference enhancement first if we have query text to embed
    if args.query_text and args.query_text.strip():
        # Add ML inference extension for embedding search
        ml_query["ext"] = {"ml_inference": {"query_text": args.query_text.strip()}}

        try:
            # Try with ML inference enhancement
            logger.info(
                f"FilingChunkSearch: Attempting ML inference search for company='{args.company_name}', query='{args.query_text}'"
            )

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/filing-chunks",
                api_key=api_key,
                params={},
                data=ml_query,
            )

            if (
                raw_response
                and "response" in raw_response
                and raw_response["response"].get("result")
            ):
                logger.info("FilingChunkSearch ML inference successful")
                return SearchFilingChunksResponse.model_validate(raw_response)
            else:
                logger.warning(
                    "FilingChunkSearch: ML inference returned no results, trying fallback"
                )
                raise Exception("ML inference returned no results")

        except Exception as ml_error:
            logger.warning(
                f"FilingChunkSearch: ML inference failed ({str(ml_error)}), falling back to standard search"
            )
    else:
        # No query text provided, skip ML inference
        logger.info(
            f"FilingChunkSearch: No query text provided, using standard filtered search for company='{args.company_name}'"
        )

    # Fall back to standard search without ML inference
    try:
        base_query["search_pipeline"] = "embedding_script_pipeline"
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/filing-chunks",
            api_key=api_key,
            params={},
            data=base_query,
        )

        if raw_response and "response" in raw_response:
            logger.info("FilingChunkSearch fallback successful")
            return SearchFilingChunksResponse.model_validate(raw_response)
        else:
            logger.error("FilingChunkSearch: Both ML and fallback search failed")
            # Return empty response structure
            return SearchFilingChunksResponse(
                instructions=[],
                response={
                    "pagination": {
                        "total_count": 0,
                        "current_page": 1,
                        "page_size": args.max_results,
                    },
                    "result": [],
                },
            )

    except Exception as fallback_error:
        logger.error(
            f"FilingChunkSearch: Fallback search also failed: {str(fallback_error)}"
        )
        # Return empty response structure
        return SearchFilingChunksResponse(
            instructions=[],
            response={
                "pagination": {
                    "total_count": 0,
                    "current_page": 1,
                    "page_size": args.max_results,
                },
                "result": [],
            },
        )
