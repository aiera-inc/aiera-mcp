#!/usr/bin/env python3

"""Search tools for Aiera MCP server."""

import logging
import asyncio

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from aiera_mcp import EMBEDDING_SEARCH_PIPELINE, HYBRID_SEARCH_PIPELINE
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResponseData,
    SearchPaginationInfo,
    TranscriptSearchResponseData,
    TranscriptSearchItem,
    TranscriptSearchCitation,
    FilingSearchItem,
    FilingSearchCitation,
)
from .utils import correct_provided_ids, correct_provided_types, correct_event_type

# Setup logging
logger = logging.getLogger(__name__)


async def search_transcripts(args: SearchTranscriptsArgs) -> SearchTranscriptsResponse:
    """Smart transcript search with dual modes: semantic search or filtered browsing.

    Uses the post_filter approach to avoid "hybrid query must be a top level query" errors,
    similar to the opensearch-mcp-server-py implementation. This tool uses hybrid search
    with neural embedding-based semantic search and the ext.ml_inference.query_text pattern.
    """
    logger.info("tool called: search_transcripts")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    # Build filter clauses for post_filter approach
    filter_clauses = []

    # Add event filter as MUST clause - filters to specific events
    if args.event_ids:
        filter_clauses.append({"terms": {"transcript_event_id": args.event_ids}})

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
        filter_clauses.append(section_filter)

    # No longer need k_value since we're using match queries instead of neural queries

    # Build text-based search queries following opensearch-mcp pattern
    should_clauses = []

    # Add text search clauses if query_text is provided
    if args.query_text and args.query_text.strip():
        should_clauses.extend(
            [
                # Primary text search
                {"match": {"text": {"query": args.query_text, "boost": 2.0}}},
                # Title/multi-field search
                {
                    "multi_match": {
                        "query": args.query_text,
                        "fields": ["title^1.5", "speaker_name"],
                        "boost": 1.5,
                    }
                },
            ]
        )

    # Build main search query using bool structure with should clauses
    base_query = {
        "query": {
            "bool": {
                "should": should_clauses,
                "filter": filter_clauses,
                "minimum_should_match": 1 if should_clauses else 0,
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

    # ML query for embedding search using match_all + ext.ml_inference pattern (like filing tools)
    ml_query = {
        "query": {"match_all": {}},
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

    # Add filters to ML query using post_filter to avoid hybrid query wrapping issues
    if filter_clauses:
        if len(filter_clauses) == 1:
            ml_query["post_filter"] = filter_clauses[0]
        else:
            ml_query["post_filter"] = {"bool": {"must": filter_clauses}}
        logger.info(f"Using ML search with {len(filter_clauses)} post-filters")
    else:
        logger.info("Using ML search without filters")

    # Try searches in order: ML inference with pipeline -> standard search with pipeline -> direct search
    if args.query_text and args.query_text.strip():
        # Add ML inference extension for embedding search (like filing tools)
        ml_query["ext"] = {"ml_inference": {"query_text": args.query_text.strip()}}

        try:
            # Try ML inference search with hybrid pipeline
            logger.info(
                f"TranscriptSearch: Attempting ML inference search with pipeline='{HYBRID_SEARCH_PIPELINE}' (15s timeout)"
            )
            logger.info(
                f"TranscriptSearch: Using {len(filter_clauses)} filters for query='{args.query_text}'"
            )

            # Set a 15-second timeout for ML inference
            try:
                raw_response = await asyncio.wait_for(
                    make_aiera_request(
                        client=client,
                        method="POST",
                        endpoint="/chat-support/search/transcripts",
                        api_key=api_key,
                        params={"search_pipeline": HYBRID_SEARCH_PIPELINE},
                        data=ml_query,
                    ),
                    timeout=15.0,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "TranscriptSearch: ML inference timed out after 15s, falling back to standard search"
                )
                raise Exception("ML inference timeout")

            if (
                raw_response
                and "response" in raw_response
                and raw_response["response"].get("result")
            ):
                logger.info("TranscriptSearch ML inference successful")
                return SearchTranscriptsResponse.model_validate(raw_response)
            else:
                logger.info(
                    "TranscriptSearch: ML inference returned no results, trying standard search"
                )
                raise Exception("ML inference returned no results")

        except Exception as ml_error:
            logger.info(
                f"TranscriptSearch: ML inference failed ({str(ml_error)}), falling back to standard search"
            )
    else:
        logger.info(
            "TranscriptSearch: No query text provided, using standard filtered search"
        )

    # Fall back to standard text-based search with pipeline
    try:
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/transcripts",
            api_key=api_key,
            params={"search_pipeline": EMBEDDING_SEARCH_PIPELINE},
            data=base_query,
        )

        if raw_response and "response" in raw_response:
            logger.info("TranscriptSearch standard pipeline search successful")
            return SearchTranscriptsResponse.model_validate(raw_response)
        else:
            logger.warning(
                "TranscriptSearch: Standard pipeline returned no results, trying direct search"
            )
            raise Exception("Standard pipeline returned no results")

    except Exception as pipeline_error:
        logger.info(
            f"TranscriptSearch: Standard pipeline search failed: {str(pipeline_error)}, trying direct search"
        )

        try:
            # Final fallback: direct search without pipeline
            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={},
                data=base_query,
            )

            if raw_response and "response" in raw_response:
                logger.info("TranscriptSearch direct search successful")
                return SearchTranscriptsResponse.model_validate(raw_response)
            else:
                logger.error("TranscriptSearch: All search methods failed")
                return _get_empty_transcripts_response(args.max_results)

        except Exception as direct_error:
            logger.error(
                f"TranscriptSearch: Direct search also failed: {str(direct_error)}"
            )
            return _get_empty_transcripts_response(args.max_results)


async def search_filings(
    args: SearchFilingsArgs,
) -> SearchFilingsResponse:
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

    # Use post_filter approach to avoid "hybrid query must be a top level query" error
    # This applies filters after search without wrapping queries that might be hybrid internally
    # Particularly important for ML inference which may use hybrid search under the hood

    # Build the query dynamically based on provided parameters
    should_clauses = []

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

    # Add company search if company_name is provided
    company_query = None
    if args.company_name and args.company_name.strip():
        company_query = _build_filings_company_filter(args.company_name)

        # If we have text search, add company as post-filter
        if should_clauses:
            # Will be added to all_filters below for post_filter
            pass
        else:
            # If no text search, use company query as main query for scoring
            should_clauses.append(company_query)
            company_query = None  # Don't add to filters since it's in the main query

    # If no search clauses at all, use match_all as fallback
    if not should_clauses:
        should_clauses.append({"match_all": {}})

    # Collect all filter clauses for post_filter approach
    all_filters = []

    # Add company filter if it should be used as a filter (not in main query)
    if company_query is not None:
        all_filters.append(company_query)

    # Add date filter if provided
    if args.start_date or args.end_date:
        date_range = {}
        if args.start_date:
            date_range["gte"] = args.start_date
        if args.end_date:
            date_range["lte"] = args.end_date
        if date_range:
            all_filters.append({"range": {"date": date_range}})

    # Add filing type filter if provided
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
        all_filters.append(filing_type_filter)

    # Add filing IDs filter if provided
    if args.filing_ids:
        # Filter out empty strings and strip whitespace
        valid_filing_ids = [fid.strip() for fid in args.filing_ids if fid.strip()]
        if valid_filing_ids:
            filing_ids_filter = {
                "terms": {"filing_id": [int(fid) for fid in valid_filing_ids]}
            }
            all_filters.append(filing_ids_filter)

    # Add content IDs filter if provided
    if args.content_ids:
        # Filter out empty strings and strip whitespace
        valid_content_ids = [cid.strip() for cid in args.content_ids if cid.strip()]
        if valid_content_ids:
            content_ids_filter = {"terms": {"content_id": valid_content_ids}}
            all_filters.append(content_ids_filter)

    # Build base query structure using post_filter approach
    base_query = {
        "query": {"bool": {"should": should_clauses, "minimum_should_match": 1}},
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

    # Apply filters using post_filter to avoid hybrid query wrapping issues
    if all_filters:
        if len(all_filters) == 1:
            base_query["post_filter"] = all_filters[0]
        else:
            base_query["post_filter"] = {"bool": {"must": all_filters}}
        logger.info(f"Base query using post_filter with {len(all_filters)} filters")
    else:
        logger.info("Base query without filters")

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
    }

    # Use simplified filter logic for ML query (complex filters can slow down ML inference)
    # Only use essential filters that are ML-compatible
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

    # Add simple filing type filter (avoid complex boolean queries for ML)
    if args.filing_type and args.filing_type.strip():
        ml_filters.append({"term": {"filing_type": args.filing_type}})

    # Add simple company filter (avoid complex fuzzy/wildcard queries for ML)
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

    # Add filing IDs filter for ML (simple terms query)
    if args.filing_ids:
        valid_filing_ids = [fid.strip() for fid in args.filing_ids if fid.strip()]
        if valid_filing_ids:
            ml_filters.append(
                {"terms": {"filing_id": [int(fid) for fid in valid_filing_ids]}}
            )

    # Add content IDs filter for ML (simple terms query)
    if args.content_ids:
        valid_content_ids = [cid.strip() for cid in args.content_ids if cid.strip()]
        if valid_content_ids:
            ml_filters.append({"terms": {"content_id": valid_content_ids}})

    # Use match_all + ext.ml_inference approach for proper ML inference (like opensearch-mcp filing tools)
    ml_query["query"] = {"match_all": {}}

    # Apply ML filters using post_filter to avoid hybrid query wrapping issues
    if ml_filters:
        if len(ml_filters) == 1:
            ml_query["post_filter"] = ml_filters[0]
        else:
            ml_query["post_filter"] = {"bool": {"must": ml_filters}}

    # Filters are now integrated using post_filter approach
    if ml_filters:
        logger.info(f"ML query using post_filter with {len(ml_filters)} filters")
    else:
        logger.info("ML query without filters")

    # Try ML inference enhancement first if we have query text to embed
    # Pipeline usage pattern (consistent with opensearch-mcp-server-py):
    # 1. hybrid_search_pipeline - for ML inference (may use hybrid search internally)
    # 2. embedding_pipeline - for standard search fallback
    # 3. No pipeline - direct search as final fallback
    if args.query_text and args.query_text.strip():
        # Add ML inference extension for embedding search (like opensearch-mcp filing tools)
        ml_query["ext"] = {"ml_inference": {"query_text": args.query_text.strip()}}

        try:
            # Try with ML inference enhancement with timeout handling
            logger.info(
                f"FilingsSearch: Attempting ML inference search for company='{args.company_name}', query='{args.query_text}', pipeline='{HYBRID_SEARCH_PIPELINE}' (15s timeout)"
            )
            logger.info(
                f"FilingsSearch: Using {len(ml_filters)} simplified filters for ML (vs {len(all_filters)} complex filters for standard search)"
            )

            # Set a 15-second timeout for ML inference
            try:
                # Wrap in async timeout
                raw_response = await asyncio.wait_for(
                    make_aiera_request(
                        client=client,
                        method="POST",
                        endpoint="/chat-support/search/filing-chunks",
                        api_key=api_key,
                        params={"search_pipeline": HYBRID_SEARCH_PIPELINE},
                        data=ml_query,
                    ),
                    timeout=15.0,
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "FilingsSearch: ML inference timed out after 15s, falling back to standard search"
                )
                raise Exception("ML inference timeout")

            if (
                raw_response
                and "response" in raw_response
                and raw_response["response"].get("result")
            ):
                logger.info("FilingsSearch ML inference successful")
                return SearchFilingsResponse.model_validate(raw_response)
            else:
                logger.warning(
                    "FilingsSearch: ML inference returned no results, trying fallback"
                )
                raise Exception("ML inference returned no results")

        except Exception as ml_error:
            logger.warning(
                f"FilingsSearch: ML inference failed ({str(ml_error)}), falling back to standard search"
            )
    else:
        # No query text provided, skip ML inference and go directly to standard search
        logger.info(
            f"FilingsSearch: No query text provided, using standard filtered search for company='{args.company_name}'"
        )

    # If we don't have results from ML inference, try standard search with pipeline fallback
    try:
        # First fallback: Try with standard embedding pipeline
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/filing-chunks",
            api_key=api_key,
            params={"search_pipeline": EMBEDDING_SEARCH_PIPELINE},
            data=base_query,
        )

        if raw_response and "response" in raw_response:
            logger.info("FilingsSearch standard pipeline fallback successful")
            return SearchFilingsResponse.model_validate(raw_response)
        else:
            logger.warning(
                "FilingsSearch: Standard pipeline returned no results, trying direct search"
            )
            raise Exception("Standard pipeline returned no results")

    except Exception as pipeline_error:
        logger.warning(
            f"FilingsSearch: Standard pipeline search failed: {str(pipeline_error)}, trying direct search"
        )

        try:
            # Final fallback: Use direct search without pipeline
            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/filing-chunks",
                api_key=api_key,
                params={},
                data=base_query,
            )

            if raw_response and "response" in raw_response:
                logger.info("FilingsSearch direct search fallback successful")
                return SearchFilingsResponse.model_validate(raw_response)
            else:
                logger.error("FilingsSearch: All search methods failed")
                return _get_empty_filings_response(args.max_results)

        except Exception as direct_error:
            logger.error(
                f"FilingsSearch: Direct search also failed: {str(direct_error)}"
            )
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
            pagination=SearchPaginationInfo(
                total_count=0,
                current_page=1,
                page_size=max_results,
            ),
            result=[],
        ),
    )


def _get_empty_transcripts_response(max_results: int) -> SearchTranscriptsResponse:
    """Return empty response structure for transcript search."""
    return SearchTranscriptsResponse(
        instructions=[],
        response=TranscriptSearchResponseData(
            pagination=SearchPaginationInfo(
                total_count=0,
                current_page=1,
                page_size=max_results,
            ),
            result=[],
        ),
    )
