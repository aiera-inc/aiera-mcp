#!/usr/bin/env python3

"""Search tools for Aiera MCP server."""

import logging
import asyncio
from typing import Optional

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from aiera_mcp import EMBEDDING_SEARCH_PIPELINE, HYBRID_SEARCH_PIPELINE
from .models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchFilingChunksArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchFilingChunksResponse,
    SearchResponseData,
    SearchPaginationInfo,
    TranscriptSearchResponseData,
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
    """Smart transcript search with dual modes: semantic search or filtered browsing.

    **Two Search Modes:**
    1. **Semantic Search Mode** (when query_text is provided): Uses neural embedding-based
       semantic search with hybrid queries and integrated filters within subqueries
    2. **Regular Filtered Search Mode** (when query_text is empty/not provided): Uses
       standard filtering without neural search for browsing transcripts by metadata

    This tool automatically selects the appropriate search mode based on whether
    query_text is provided.

    **Key Improvement**: Filters are now applied WITHIN each hybrid subquery (not post_filter),
    ensuring filters are applied DURING retrieval for better recall.
    """
    logger.info("tool called: search_transcripts")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    # Build filter clauses - will be integrated into subqueries, not used as post_filter
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

    # Check if query_text is provided for semantic search
    has_query_text = args.query_text and args.query_text.strip()

    if not has_query_text:
        # No query text provided - use regular filtered search
        logger.info(
            "TranscriptSearch: No query text provided, using regular filtered search"
        )
        return await _handle_regular_filtered_search_transcripts(
            args, filter_clauses, client, api_key
        )

    # Determine k parameter based on filtering
    # Higher k when filters are used to ensure good coverage after filtering
    k_value = args.max_results * 2
    if filter_clauses:
        k_value = min(args.max_results * 100, 10000)  # Cap at 10k for performance
        logger.info(
            f"TranscriptSearch: Using k={k_value} for filtered semantic search (max_results={args.max_results})"
        )
    else:
        logger.info(
            f"TranscriptSearch: Using k={k_value} for unfiltered semantic search (max_results={args.max_results})"
        )

    # Use modern neural search query with embedding_384 field
    neural_query = {
        "neural": {"embedding_384": {"query_text": args.query_text, "k": k_value}}
    }

    # Build lexical query for hybrid search
    lexical_query = {
        "multi_match": {
            "query": args.query_text,
            "fields": ["text^2", "title", "speaker_name"],
            "type": "best_fields",
            "boost": 1.5,
        }
    }

    # Build hybrid search query with filters INSIDE subqueries
    if filter_clauses:
        # Combine filters if multiple
        combined_filter = (
            {"bool": {"must": filter_clauses}}
            if len(filter_clauses) > 1
            else filter_clauses[0]
        )

        # Wrap each subquery with filters - key improvement for better recall
        hybrid_query = {
            "hybrid": {
                "queries": [
                    {
                        "bool": {
                            "must": [neural_query],
                            "filter": [combined_filter],
                        }
                    },
                    {
                        "bool": {
                            "must": [lexical_query],
                            "filter": [combined_filter],
                        }
                    },
                ]
            }
        }
        logger.info(
            f"TranscriptSearch: Using integrated filter approach with {len(filter_clauses)} filters inside subqueries"
        )
    else:
        # No filters - use simple hybrid query
        hybrid_query = {"hybrid": {"queries": [neural_query, lexical_query]}}
        logger.info("TranscriptSearch: Using hybrid search without filters")

    # Build the search request
    search_query = {
        "query": hybrid_query,
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
    }

    # Try hybrid search with pipeline
    try:
        logger.info(
            f"TranscriptSearch: Attempting hybrid search with pipeline='{HYBRID_SEARCH_PIPELINE}' for query='{args.query_text}'"
        )

        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={"search_pipeline": HYBRID_SEARCH_PIPELINE},
                data=search_query,
            ),
            timeout=15.0,
        )

        if raw_response and "response" in raw_response:
            logger.info("TranscriptSearch: Hybrid search successful")
            return SearchTranscriptsResponse.model_validate(raw_response)
        else:
            logger.warning(
                "TranscriptSearch: Hybrid search returned no results, trying fallback"
            )
            raise Exception("Hybrid search returned no results")

    except asyncio.TimeoutError:
        logger.warning(
            "TranscriptSearch: Hybrid search timed out after 15s, falling back"
        )
        raise Exception("Hybrid search timeout")

    except Exception as hybrid_error:
        logger.warning(
            f"TranscriptSearch: Hybrid search failed ({str(hybrid_error)}), falling back to text-based search"
        )

        # Fallback: Use text-based search with filters
        # Include both exact phrase matching and flexible text matching
        # to ensure exact matches are returned even if embedding search fails
        fallback_query = {
            "query": {
                "bool": {
                    "should": [
                        # Highest priority: exact phrase matches
                        {
                            "match_phrase": {
                                "text": {"query": args.query_text, "boost": 10.0}
                            }
                        },
                        {
                            "match_phrase": {
                                "title": {"query": args.query_text, "boost": 8.0}
                            }
                        },
                        {
                            "match_phrase": {
                                "speaker_name": {"query": args.query_text, "boost": 5.0}
                            }
                        },
                        # Lower priority: flexible text matching
                        {
                            "multi_match": {
                                "query": args.query_text,
                                "fields": ["text^2", "title", "speaker_name"],
                                "boost": 1.0,
                            }
                        },
                    ],
                    "filter": filter_clauses if filter_clauses else [],
                    "minimum_should_match": 1,
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
        }

        try:
            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/transcripts",
                api_key=api_key,
                params={},
                data=fallback_query,
            )

            if raw_response and "response" in raw_response:
                logger.info("TranscriptSearch: Fallback text search successful")
                return SearchTranscriptsResponse.model_validate(raw_response)
            else:
                logger.error("TranscriptSearch: All search methods failed")
                return _get_empty_transcripts_response(args.max_results)

        except Exception as fallback_error:
            logger.error(
                f"TranscriptSearch: Fallback search also failed: {str(fallback_error)}"
            )
            return _get_empty_transcripts_response(args.max_results)


async def search_filings(args: SearchFilingsArgs) -> SearchFilingsResponse:
    """SEC filing discovery tool designed to identify relevant filings for follow-up content analysis.

    Returns filing metadata (excluding full text/summary) optimized for:
    - Filing identification and validation
    - Metadata-based filtering (company, date, document type)
    - Integration with FilingChunkSearch for content extraction
    - Efficient discovery of relevant documents before detailed analysis

    Key features:
    1. Automatic company name discovery and variation matching
    2. Structured field-based search prioritizing filing metadata
    3. Result validation to ensure correct company matches
    4. Multiple fallback strategies for comprehensive discovery
    5. Optimized output format for filing discovery workflows
    """
    logger.info("tool called: search_filings")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    company_name = args.company_name.strip()
    logger.info(
        f"SearchFilings: enhanced search for '{company_name}' filings, start_date='{args.start_date}', end_date='{args.end_date}', document_types={args.document_types}"
    )

    # Build date filter only if dates are explicitly provided
    date_filter = None
    if args.start_date or args.end_date:
        date_range = {}
        if args.start_date:
            date_range["gte"] = args.start_date
        if args.end_date:
            date_range["lte"] = args.end_date
        if date_range:
            date_filter = {"range": {"date": date_range}}

    # Extract date boundaries for logging
    start_date_used = args.start_date if args.start_date else "all time"
    end_date_used = args.end_date if args.end_date else "all time"

    logger.info(
        f"SearchFilings: using date range {start_date_used} to {end_date_used}".strip()
    )

    # Build document type filter using match_phrase
    document_type_filter = None
    if args.document_types:
        doc_type_filters = []
        for doc_type in args.document_types:
            doc_type_upper = doc_type.upper()
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

    # STRATEGY 1: Try direct company name search first
    result = await _try_direct_company_search(
        args, company_name, date_filter, document_type_filter, client, api_key
    )

    # STRATEGY 2: If no results or poor quality, use automatic company discovery
    if not result or not _validate_search_results(
        result, company_name, args.document_types
    ):
        logger.info(
            f"Direct search failed/poor quality for '{company_name}', trying company discovery"
        )

        # Get company name variations
        try:
            discovered_variations = await _get_company_variations(company_name)

            # Try each discovered variation
            for variation in discovered_variations[:5]:  # Try top 5 variations
                logger.info(f"Trying discovered variation: '{variation}'")
                variation_result = await _try_direct_company_search(
                    args, variation, date_filter, document_type_filter, client, api_key
                )

                if variation_result and _validate_search_results(
                    variation_result, company_name, args.document_types
                ):
                    result = variation_result
                    break
        except Exception as discovery_error:
            logger.warning(f"Company discovery failed: {str(discovery_error)}")

    # STRATEGY 3: If still no results, try structured field search with company context
    if not result or not _validate_search_results(
        result, company_name, args.document_types
    ):
        logger.info(
            f"Discovery search failed for '{company_name}', trying company context variations"
        )

        # Get known company variations from CompanyContext
        context_variations = _get_company_context_variations(company_name)

        for variation in context_variations[:5]:
            logger.info(f"Trying context variation: '{variation}'")
            variation_result = await _try_direct_company_search(
                args, variation, date_filter, document_type_filter, client, api_key
            )

            if variation_result and _validate_search_results(
                variation_result, company_name, args.document_types
            ):
                result = variation_result
                break

    # STRATEGY 4: Final fallback - simplified broad search
    if not result or not _validate_search_results(
        result, company_name, args.document_types
    ):
        logger.info(
            f"All structured searches failed for '{company_name}', trying fallback search"
        )
        result = await _try_fallback_search(
            args, company_name, date_filter, document_type_filter, client, api_key
        )

    # Process and validate final results
    if result and isinstance(result, dict):
        # Handle Aiera API response structure
        if "response" in result and "result" in result["response"]:
            hits = result["response"]["result"]
            # Extract total_count, handling both integer and dict formats
            if (
                "pagination" in result["response"]
                and "total_count" in result["response"]["pagination"]
            ):
                tc = result["response"]["pagination"]["total_count"]
                total_count = tc["value"] if isinstance(tc, dict) else tc
            else:
                total_count = len(hits) if hits else 0

            # Validate and enhance results with stricter date checking
            validated_hits = []
            for hit in hits or []:
                if _validate_individual_result(
                    hit,
                    company_name,
                    args.document_types,
                    start_date_used,
                    end_date_used,
                    date_filter,
                ):
                    # Enhance hit with parsed data
                    _enhance_filing_result(hit)
                    validated_hits.append(hit)

            # Update result with validated hits
            result["response"]["result"] = validated_hits[: args.max_results]
            if "pagination" in result["response"]:
                result["response"]["pagination"]["total_count"] = {
                    "value": len(validated_hits),
                    "relation": "eq",
                }

            # Add search metadata
            if "_search_metadata" not in result:
                result["_search_metadata"] = {}

            result["_search_metadata"].update(
                {
                    "query": {
                        "company_name": company_name,
                        "document_types": args.document_types,
                        "start_date": args.start_date,
                        "end_date": args.end_date,
                        "fuzzy_matching": args.fuzzy_matching,
                        "sort_by": args.sort_by,
                    },
                    "search_info": {
                        "strategies_used": [
                            "direct_search",
                            "company_discovery",
                            "company_context",
                            "fallback",
                        ],
                        "validated_results": len(validated_hits),
                        "total_found": len(hits) if hits else 0,
                    },
                }
            )

            if validated_hits:
                logger.info(
                    f"SearchFilings completed: {len(validated_hits)} validated results for '{company_name}'"
                )
                return SearchFilingsResponse.model_validate(result)
            else:
                # No validated results found
                logger.warning(
                    f"SearchFilings: No validated {company_name} filings found"
                )
                return SearchFilingsResponse(
                    instructions=[
                        f"No validated {company_name} filings found",
                        "Suggestions: Expand time window or check company name variations",
                    ],
                    response=SearchResponseData(
                        pagination=SearchPaginationInfo(
                            total_count=0,
                            current_page=1,
                            page_size=args.max_results,
                        ),
                        result=[],
                    ),
                )

    # If we get here, no results found after all strategies
    logger.error(
        f"SearchFilings: No filing results found after trying all search strategies for '{company_name}'"
    )
    return SearchFilingsResponse(
        instructions=[
            f"No filing results found for '{company_name}' after trying all search strategies",
            "Suggestions: Verify company name or expand search criteria",
        ],
        response=SearchResponseData(
            pagination=SearchPaginationInfo(
                total_count=0,
                current_page=1,
                page_size=args.max_results,
            ),
            result=[],
        ),
    )


async def search_filing_chunks(
    args: SearchFilingChunksArgs,
) -> SearchFilingChunksResponse:
    """Semantic search within SEC filing document chunks using embedding-based matching.

    Smart filing chunk search with dual modes: semantic search or filtered browsing.

    **Two Search Modes:**
    1. **Semantic Search Mode** (when query_text is provided): Uses neural embedding-based
       semantic search with hybrid queries and integrated filters
    2. **Regular Filtered Search Mode** (when query_text is empty/not provided): Uses
       standard filtering without neural search for browsing filing chunks by metadata

    This tool automatically selects the appropriate search mode based on whether
    query_text is provided.
    """
    logger.info("tool called: search_filing_chunks")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    # Build filter clauses
    filter_clauses = []

    # Add company name filter if provided
    if args.company_name and args.company_name.strip():
        company_filter = _build_filing_chunks_company_filter(args.company_name)
        filter_clauses.append(company_filter)

    # Add date filter if provided
    if args.start_date or args.end_date:
        date_range = {}
        if args.start_date:
            date_range["gte"] = args.start_date
        if args.end_date:
            date_range["lte"] = args.end_date
        if date_range:
            filter_clauses.append({"range": {"date": date_range}})

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
        filter_clauses.append(filing_type_filter)

    # Add filing IDs filter if provided
    if args.filing_ids:
        # Filter out empty strings and strip whitespace
        valid_filing_ids = [fid.strip() for fid in args.filing_ids if fid.strip()]
        if valid_filing_ids:
            filing_ids_filter = {
                "terms": {"filing_id": [int(fid) for fid in valid_filing_ids]}
            }
            filter_clauses.append(filing_ids_filter)

    # Add content IDs filter if provided
    if args.content_ids:
        # Filter out empty strings and strip whitespace
        valid_content_ids = [cid.strip() for cid in args.content_ids if cid.strip()]
        if valid_content_ids:
            content_ids_filter = {"terms": {"content_id": valid_content_ids}}
            filter_clauses.append(content_ids_filter)

    # Check if query_text is provided for semantic search
    has_query_text = args.query_text and args.query_text.strip()

    if not has_query_text:
        # No query text provided - use regular filtered search
        logger.info(
            "FilingChunkSearch: No query text provided, using regular filtered search"
        )
        return await _handle_regular_filtered_search_filing_chunks(
            args, filter_clauses, client, api_key
        )

    # Determine k parameter based on filtering
    # Higher k when filters are used to ensure good coverage after filtering
    k_value = args.max_results * 2
    if filter_clauses:
        k_value = min(args.max_results * 100, 10000)  # Cap at 10k for performance
        logger.info(
            f"FilingChunkSearch: Using k={k_value} for filtered semantic search (max_results={args.max_results})"
        )
    else:
        logger.info(
            f"FilingChunkSearch: Using k={k_value} for unfiltered semantic search (max_results={args.max_results})"
        )

    # Use modern neural search query with embedding_384 field
    neural_query = {
        "neural": {"embedding_384": {"query_text": args.query_text, "k": k_value}}
    }

    # Build lexical query for hybrid search
    lexical_query = {
        "multi_match": {
            "query": args.query_text,
            "fields": ["text^2", "title", "company_common_name"],
            "type": "best_fields",
            "boost": 1.5,
        }
    }

    # Build hybrid search query with filters INSIDE subqueries
    if filter_clauses:
        # Combine filters if multiple
        combined_filter = (
            {"bool": {"must": filter_clauses}}
            if len(filter_clauses) > 1
            else filter_clauses[0]
        )

        # Wrap each subquery with filters - key improvement for better recall
        hybrid_query = {
            "hybrid": {
                "queries": [
                    {
                        "bool": {
                            "must": [neural_query],
                            "filter": [combined_filter],
                        }
                    },
                    {
                        "bool": {
                            "must": [lexical_query],
                            "filter": [combined_filter],
                        }
                    },
                ]
            }
        }
        logger.info(
            f"FilingChunkSearch: Using integrated filter approach with {len(filter_clauses)} filters inside subqueries"
        )
    else:
        # No filters - use simple hybrid query
        hybrid_query = {"hybrid": {"queries": [neural_query, lexical_query]}}
        logger.info("FilingChunkSearch: Using hybrid search without filters")

    # Build the search request
    search_query = {
        "query": hybrid_query,
        "size": args.max_results,
        "min_score": args.min_score,
        "_source": [
            "content_id",
            "text",
            "title",
            "company_common_name",
            "company_legal_name",
            "filing_id",
            "filing_form_id",
            "filing_type",
            "date",
            "chunk_id",
        ],
    }

    # Try hybrid search with pipeline
    try:
        logger.info(
            f"FilingChunkSearch: Attempting hybrid search with pipeline='{HYBRID_SEARCH_PIPELINE}' for query='{args.query_text}'"
        )

        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/filing-chunks",
                api_key=api_key,
                params={"search_pipeline": HYBRID_SEARCH_PIPELINE},
                data=search_query,
            ),
            timeout=15.0,
        )

        if raw_response and "response" in raw_response:
            logger.info("FilingChunkSearch: Hybrid search successful")
            return SearchFilingChunksResponse.model_validate(raw_response)
        else:
            logger.warning(
                "FilingChunkSearch: Hybrid search returned no results, trying fallback"
            )
            raise Exception("Hybrid search returned no results")

    except asyncio.TimeoutError:
        logger.warning(
            "FilingChunkSearch: Hybrid search timed out after 15s, falling back"
        )
        raise Exception("Hybrid search timeout")

    except Exception as hybrid_error:
        logger.warning(
            f"FilingChunkSearch: Hybrid search failed ({str(hybrid_error)}), falling back to text-based search"
        )

        # Fallback: Use text-based search with filters
        # Include both exact phrase matching and flexible text matching
        # to ensure exact matches are returned even if embedding search fails
        fallback_query = {
            "query": {
                "bool": {
                    "should": [
                        # Highest priority: exact phrase matches
                        {
                            "match_phrase": {
                                "text": {"query": args.query_text, "boost": 10.0}
                            }
                        },
                        {
                            "match_phrase": {
                                "title": {"query": args.query_text, "boost": 8.0}
                            }
                        },
                        {
                            "match_phrase": {
                                "company_common_name": {
                                    "query": args.query_text,
                                    "boost": 5.0,
                                }
                            }
                        },
                        # Lower priority: flexible text matching
                        {
                            "multi_match": {
                                "query": args.query_text,
                                "fields": ["text^2", "title", "company_common_name"],
                                "boost": 1.0,
                            }
                        },
                    ],
                    "filter": filter_clauses if filter_clauses else [],
                    "minimum_should_match": 1,
                }
            },
            "size": args.max_results,
            "min_score": args.min_score,
            "_source": [
                "content_id",
                "text",
                "title",
                "company_common_name",
                "company_legal_name",
                "filing_id",
                "filing_form_id",
                "filing_type",
                "date",
                "chunk_id",
            ],
        }

        try:
            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/filing-chunks",
                api_key=api_key,
                params={},
                data=fallback_query,
            )

            if raw_response and "response" in raw_response:
                logger.info("FilingChunkSearch: Fallback text search successful")
                return SearchFilingChunksResponse.model_validate(raw_response)
            else:
                logger.error("FilingChunkSearch: All search methods failed")
                return _get_empty_filing_chunks_response(args.max_results)

        except Exception as fallback_error:
            logger.error(
                f"FilingChunkSearch: Fallback search also failed: {str(fallback_error)}"
            )
            return _get_empty_filing_chunks_response(args.max_results)


def _build_filing_chunks_company_filter(company_name: str) -> dict:
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


async def _handle_regular_filtered_search_transcripts(
    args: SearchTranscriptsArgs, filter_clauses: list, client, api_key: str
) -> SearchTranscriptsResponse:
    """Handle regular filtered search when no query text is provided.

    Uses standard filtering without semantic/neural search for browsing transcripts
    by metadata (event_ids, transcript_section, etc.).
    """
    # Build query with filters but no text search
    if filter_clauses:
        # Use filters as the main query
        if len(filter_clauses) == 1:
            query = filter_clauses[0]
        else:
            query = {"bool": {"must": filter_clauses}}
    else:
        # No filters either - return all results
        query = {"match_all": {}}

    search_query = {
        "query": query,
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
        "sort": [{"date": {"order": "desc"}}],  # Sort by date for browsing
    }

    try:
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/transcripts",
            api_key=api_key,
            params={},
            data=search_query,
        )

        if raw_response and "response" in raw_response:
            logger.info(
                f"TranscriptSearch: Regular filtered search successful ({len(filter_clauses)} filters)"
            )
            return SearchTranscriptsResponse.model_validate(raw_response)
        else:
            logger.warning("TranscriptSearch: Regular filtered search returned no data")
            return _get_empty_transcripts_response(args.max_results)

    except Exception as e:
        logger.error(f"TranscriptSearch: Regular filtered search failed: {str(e)}")
        return _get_empty_transcripts_response(args.max_results)


def _get_empty_filing_chunks_response(max_results: int) -> SearchFilingChunksResponse:
    """Return empty response structure for filing chunks search."""
    return SearchFilingChunksResponse(
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


async def _handle_regular_filtered_search_filing_chunks(
    args: SearchFilingChunksArgs, filter_clauses: list, client, api_key: str
) -> SearchFilingChunksResponse:
    """Handle regular filtered search when no query text is provided.

    Uses standard filtering without semantic/neural search for browsing filing chunks
    by metadata (company_name, filing_type, date, etc.).
    """
    # Build query with filters but no text search
    if filter_clauses:
        # Use filters as the main query
        if len(filter_clauses) == 1:
            query = filter_clauses[0]
        else:
            query = {"bool": {"must": filter_clauses}}
    else:
        # No filters either - return all results
        query = {"match_all": {}}

    search_query = {
        "query": query,
        "size": args.max_results,
        "min_score": args.min_score,
        "_source": [
            "content_id",
            "text",
            "title",
            "company_common_name",
            "company_legal_name",
            "filing_id",
            "filing_form_id",
            "filing_type",
            "date",
            "chunk_id",
        ],
        "sort": [{"date": {"order": "desc"}}],  # Sort by date for browsing
    }

    try:
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/filing-chunks",
            api_key=api_key,
            params={},
            data=search_query,
        )

        if raw_response and "response" in raw_response:
            logger.info(
                f"FilingChunkSearch: Regular filtered search successful ({len(filter_clauses)} filters)"
            )
            return SearchFilingChunksResponse.model_validate(raw_response)
        else:
            logger.warning(
                "FilingChunkSearch: Regular filtered search returned no data"
            )
            return _get_empty_filing_chunks_response(args.max_results)

    except Exception as e:
        logger.error(f"FilingChunkSearch: Regular filtered search failed: {str(e)}")
        return _get_empty_filing_chunks_response(args.max_results)


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


# Filing-specific utility functions for multi-strategy search


def _escape_wildcard_special_chars(text: str) -> str:
    """Escape special characters in text for use in OpenSearch wildcard queries."""
    special_chars = ["*", "?", "[", "]", "{", "}", "\\", "!"]
    escaped_text = text
    for char in special_chars:
        escaped_text = escaped_text.replace(char, f"\\{char}")
    return escaped_text


def _remove_special_characters(text: str) -> str:
    """Remove special characters from company names that might not be in filings."""
    import re

    clean_text = re.sub(r'[!@#$%^&*()_+\-=\[\]{}|\\:;"\',.<>?/]', "", text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()
    return clean_text


def _generate_company_name_variations(company_name: str) -> list[str]:
    """Generate common variations of a company name for better matching.

    Handles cases like:
    - Netflix -> Netflix Inc, Netflix Inc., Netflix, Inc.
    - Apple -> Apple Inc, Apple Inc.
    - Johnson & Johnson -> Johnson and Johnson
    """
    variations = [company_name.strip()]
    base_name = company_name.strip()

    # Add version with special characters cleaned
    clean_name = _remove_special_characters(base_name)
    if clean_name != base_name and clean_name.strip():
        variations.append(clean_name)

    # Add corporate suffix variations
    suffixes_to_add = [
        "Inc",
        "Inc.",
        ", Inc",
        ", Inc.",
        "Corp",
        "Corp.",
        ", Corp",
        ", Corp.",
        "Corporation",
        "Company",
        "Co",
        "Co.",
        ", Co",
        ", Co.",
        "LLC",
        "L.L.C.",
    ]

    suffixes_to_remove = [
        "Inc",
        "Inc.",
        ", Inc",
        ", Inc.",
        "Corp",
        "Corp.",
        ", Corp",
        ", Corp.",
        "Corporation",
        "Company",
        "Co",
        "Co.",
        ", Co",
        ", Co.",
        "LLC",
        "L.L.C.",
    ]

    # If base name doesn't have corporate suffix, add common ones
    base_lower = base_name.lower()
    has_suffix = any(suffix.lower() in base_lower for suffix in suffixes_to_remove)

    if not has_suffix:
        for suffix in suffixes_to_add[:4]:  # Add most common suffixes
            variations.append(f"{base_name} {suffix}")
    else:
        # If it has a suffix, also try without suffix
        for suffix in suffixes_to_remove:
            if base_name.endswith(suffix):
                without_suffix = base_name[: -len(suffix)].strip()
                if without_suffix:
                    variations.append(without_suffix)
                    # Also add it with comma removed if present
                    if without_suffix.endswith(","):
                        variations.append(without_suffix[:-1].strip())

    # Add case variations
    variations.extend([base_name.upper(), base_name.lower(), base_name.title()])

    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for variation in variations:
        if variation and variation not in seen:
            seen.add(variation)
            unique_variations.append(variation)

    return unique_variations[:10]  # Limit to top 10 variations to avoid query bloat


def _get_company_context_variations(company_name: str) -> list[str]:
    """Get company variations from known context mappings."""
    # Known company mappings from the context tool
    known_mappings = {
        "Amazon": [
            "AMZN",
            "Amazon.com Inc",
            "Amazon Inc",
            "Amazon.com, Inc",
            "amazon",
        ],
        "Microsoft": [
            "MSFT",
            "Microsoft Corp",
            "Microsoft Corporation",
            "microsoft corp",
        ],
        "Apple": ["AAPL", "Apple Inc"],
        "Google": [
            "Alphabet Inc",
            "GOOGL",
            "GOOG",
            "Google Inc",
            "Alphabet",
        ],
        "Tesla": ["TSLA", "Tesla Inc", "Tesla Motors"],
        "Meta": ["META", "Meta Platforms Inc", "Facebook Inc", "Facebook"],
        "Netflix": ["NFLX", "Netflix Inc"],
        "Nvidia": ["NVDA", "NVIDIA Corp", "NVIDIA Corporation"],
    }

    # Check for exact matches first
    for key, variations in known_mappings.items():
        if company_name.lower() in [key.lower()] + [v.lower() for v in variations]:
            return [key] + variations

    # Return basic variations if no known mapping
    return [
        company_name,
        company_name.lower(),
        company_name.upper(),
        company_name.title(),
    ]


async def _get_company_variations(company_name: str) -> list[str]:
    """Get company name variations optimized for SEC filing title matching."""
    try:
        variations = [company_name]

        # Add version with special characters removed (CRITICAL for names like "Yum! Brands")
        clean_name = _remove_special_characters(company_name)
        if clean_name != company_name and clean_name.strip():
            variations.append(clean_name)
            logger.info(
                f"Added special-char-free variation: '{company_name}' -> '{clean_name}'"
            )

        # Add case variations
        variations.extend(
            [company_name.lower(), company_name.upper(), company_name.title()]
        )

        # Add case variations of the clean name too
        if clean_name != company_name and clean_name.strip():
            variations.extend(
                [clean_name.lower(), clean_name.upper(), clean_name.title()]
            )

        # Add corporate suffix variations
        for original, replacement in [
            ("Corp", "Corporation"),
            ("Corporation", "Corp"),
            ("Inc", "Incorporated"),
            ("Incorporated", "Inc"),
            ("Inc.", "Inc"),
            ("Inc", "Inc."),
            ("Co", "Company"),
            ("Company", "Co"),
            ("LLC", "L.L.C."),
            ("L.L.C.", "LLC"),
        ]:
            if original in company_name:
                variations.append(company_name.replace(original, replacement))

        # Special handling for known problem cases based on our data exploration
        company_lower = company_name.lower()

        # Apple variations
        if company_lower in ["apple", "aapl"]:
            variations.extend(
                [
                    "Apple",
                    "APPLE",
                    "Apple Inc",
                    "Apple Inc.",
                    "Apple Computer",
                    "Apple Computer Inc",
                ]
            )

        # Johnson & Johnson variations
        if "johnson" in company_lower:
            variations.extend(
                [
                    "Johnson & Johnson",
                    "JOHNSON & JOHNSON",
                    "Johnson and Johnson",
                    "JOHNSON AND JOHNSON",
                    "J&J",
                    "JNJ",
                    "Johnson & Johnson Inc",
                ]
            )

        # Add .com variations for tech companies
        if ".com" not in company_name.lower():
            variations.extend(
                [
                    f"{company_name}.com",
                    f"{company_name}.com Inc",
                    f"{company_name}.com Inc.",
                ]
            )

        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for variation in variations:
            if variation not in seen:
                seen.add(variation)
                unique_variations.append(variation)

        return unique_variations

    except Exception as e:
        logger.debug(f"Company variation discovery failed: {str(e)}")
        return [company_name]


def _validate_search_results(
    result: Optional[dict], target_company: str, document_types: Optional[list]
) -> bool:
    """Validate that search results actually match the target company and document types."""
    if not result or not isinstance(result, dict):
        return False

    # Handle Aiera API response structure
    if "response" in result and "result" in result["response"]:
        hits = result["response"]["result"]
    elif "hits" in result and "hits" in result["hits"]:
        hits = result["hits"]["hits"]
    else:
        return False

    if not hits:
        return False

    # Check if at least 30% of results match the target company
    matching_results = 0
    target_lower = target_company.lower()

    for hit in hits:
        # Handle both OpenSearch (_source) and Aiera API (direct fields) formats
        source = hit.get("_source", hit)
        title = source.get("title", "").lower()

        # Check for company name match in title or company fields
        company_match = (
            target_lower in title
            or target_lower in source.get("company_name", "").lower()
            or target_lower in source.get("issuer_name", "").lower()
        )

        if company_match:
            matching_results += 1

    match_ratio = matching_results / len(hits)
    return match_ratio >= 0.3  # At least 30% should match target company


def _validate_individual_result(
    hit: dict,
    target_company: str,
    document_types: Optional[list],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    date_filter: Optional[dict] = None,
) -> bool:
    """Validate individual search result for relevance and date compliance."""
    # Handle both OpenSearch (_source) and Aiera API (direct fields) formats
    source = hit.get("_source", hit)
    title = source.get("title", "").lower()
    target_lower = target_company.lower()

    # Must contain target company name
    company_match = (
        target_lower in title
        or target_lower in source.get("company_name", "").lower()
        or target_lower in source.get("issuer_name", "").lower()
        or target_lower in source.get("entity_name", "").lower()
    )

    if not company_match:
        return False

    # If document types specified, must match at least one
    if document_types:
        doc_type_match = False
        for doc_type in document_types:
            doc_type_upper = doc_type.upper()
            if (
                doc_type_upper in title.upper()
                or doc_type_upper in source.get("document_type", "").upper()
                or doc_type_upper in source.get("form_type", "").upper()
            ):
                doc_type_match = True
                break

        if not doc_type_match:
            return False

    # Enhanced date validation - strictly enforce date range if specified
    if date_filter and (start_date or end_date):
        filing_date = source.get("date") or source.get("filing_date")
        if filing_date:
            try:
                # Extract date components from the filter
                range_clause = date_filter.get("range", {})
                if range_clause:
                    date_field = list(range_clause.keys())[0]
                    date_constraints = range_clause[date_field]

                    start_date = date_constraints.get("gte")
                    end_date = date_constraints.get("lte")

                    # Convert filing_date to comparable format (YYYY-MM-DD)
                    if isinstance(filing_date, str):
                        # Handle different date formats
                        if len(filing_date) >= 10:  # At least YYYY-MM-DD
                            file_date_str = filing_date[:10]  # Take first 10 characters

                            # Check if filing date is within specified range
                            if start_date and file_date_str < start_date:
                                logger.debug(
                                    f"Rejecting result: filing date {file_date_str} before start {start_date}"
                                )
                                return False
                            if end_date and file_date_str > end_date:
                                logger.debug(
                                    f"Rejecting result: filing date {file_date_str} after end {end_date}"
                                )
                                return False
            except Exception as e:
                logger.debug(f"Date validation failed for result: {str(e)}")
                # Don't reject on date validation errors, but log them

    return True


async def _try_direct_company_search(
    args: SearchFilingsArgs,
    company_name: str,
    date_filter: Optional[dict],
    document_type_filter: Optional[dict],
    client,
    api_key: str,
) -> Optional[dict]:
    """Try direct search for a specific company name."""
    try:
        # Build query using flexible patterns
        escaped_company_name = _escape_wildcard_special_chars(company_name)

        # Generate company name variations for better matching
        company_variations = _generate_company_name_variations(company_name)

        # Use should clauses for flexible company matching
        company_search_clauses = []

        for variation in company_variations:
            company_search_clauses.extend(
                [
                    # Exact phrase matching (highest priority)
                    {"match_phrase": {"title": {"query": variation, "boost": 10.0}}},
                    # Fuzzy matching for typos and slight variations
                    {
                        "match": {
                            "title": {
                                "query": variation,
                                "fuzziness": "AUTO",
                                "boost": 8.0,
                            }
                        }
                    },
                    # Structured company fields with fuzzy matching
                    {
                        "match": {
                            "company_name": {
                                "query": variation,
                                "fuzziness": "AUTO",
                                "boost": 6.0,
                            }
                        }
                    },
                    {
                        "match": {
                            "issuer_name": {
                                "query": variation,
                                "fuzziness": "AUTO",
                                "boost": 6.0,
                            }
                        }
                    },
                    {
                        "match": {
                            "entity_name": {
                                "query": variation,
                                "fuzziness": "AUTO",
                                "boost": 6.0,
                            }
                        }
                    },
                    # Wildcard for partial matches (lower priority)
                    {
                        "wildcard": {
                            "title": {
                                "value": f"*{_escape_wildcard_special_chars(variation)}*",
                                "case_insensitive": True,
                                "boost": 4.0,
                            }
                        }
                    },
                ]
            )

        # Wrap all company matching in a single bool query
        must_clauses = [
            {
                "bool": {
                    "should": company_search_clauses,
                    "minimum_should_match": 1,
                }
            }
        ]

        # Add date filter to must clauses
        if date_filter:
            must_clauses.append(date_filter)
            logger.info(f"Applied date filter: {date_filter}")

        # Add document type filter to must clauses
        if document_type_filter:
            must_clauses.append(document_type_filter)

        # Build query
        query = {
            "size": args.max_results,
            "query": {"bool": {"must": must_clauses}},
            "_source": [
                "title",
                "date",
                "filing_form_id",
                "content_id",
                "filing_id",
                "source",
            ],
            "sort": [{"date": {"order": "desc"}}],
            "search_pipeline": HYBRID_SEARCH_PIPELINE,
        }

        # Make request to Aiera API
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/filings",
            api_key=api_key,
            params={},
            data=query,
        )

        return raw_response

    except Exception as e:
        logger.debug(f"Direct company search failed for '{company_name}': {str(e)}")
        return None


async def _try_fallback_search(
    args: SearchFilingsArgs,
    company_name: str,
    date_filter: Optional[dict],
    document_type_filter: Optional[dict],
    client,
    api_key: str,
) -> Optional[dict]:
    """Final fallback search with broader matching."""
    try:
        # Very broad search as last resort
        should_clauses = [
            {
                "wildcard": {
                    "title": {
                        "value": f"*{company_name}*",
                        "case_insensitive": True,
                        "boost": 5.0,
                    }
                }
            },
            {
                "match": {
                    "title": {
                        "query": company_name,
                        "minimum_should_match": "75%",
                        "boost": 3.0,
                    }
                }
            },
            {
                "match": {
                    "company_name": {
                        "query": company_name,
                        "minimum_should_match": "50%",
                        "boost": 2.0,
                    }
                }
            },
            {
                "match": {
                    "issuer_name": {
                        "query": company_name,
                        "minimum_should_match": "50%",
                        "boost": 2.0,
                    }
                }
            },
        ]

        filter_clauses = []
        if date_filter:
            filter_clauses.append(date_filter)
        if document_type_filter:
            filter_clauses.append(document_type_filter)

        query = {
            "size": min(args.max_results * 3, 30),
            "query": {
                "bool": {
                    "should": should_clauses,
                    "filter": filter_clauses,
                    "minimum_should_match": 1,
                }
            },
            "_source": ["content_id", "title", "company_name", "date", "filing_id"],
            "sort": [{"_score": {"order": "desc"}}, {"date": {"order": "desc"}}],
            "timeout": "10s",
            "search_pipeline": HYBRID_SEARCH_PIPELINE,
        }

        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/chat-support/search/filings",
            api_key=api_key,
            params={},
            data=query,
        )

        return raw_response

    except Exception as e:
        logger.debug(f"Fallback search failed for '{company_name}': {str(e)}")
        return None


def _enhance_filing_result(hit: dict):
    """Enhance filing result with parsed company name and document type."""
    # Handle both OpenSearch (_source) and Aiera API (direct fields) formats
    source = hit.get("_source", hit)
    title = source.get("title", "")

    # Extract company name from title if not in structured field
    if not source.get("company_name"):
        if " - " in title:
            company = title.split(" - ")[0].strip()
            source["_parsed_company_name"] = company

    # Extract document type from title if not in structured field
    if not source.get("document_type"):
        import re

        type_match = re.search(
            r"\b(10-K|10-Q|8-K|S-\d+|DEF\s+14A|20-F|\d+(?:/A)?)\b",
            title,
            re.IGNORECASE,
        )
        if type_match:
            source["_parsed_document_type"] = type_match.group(1).upper()
        else:
            source["_parsed_document_type"] = "SEC Filing"
