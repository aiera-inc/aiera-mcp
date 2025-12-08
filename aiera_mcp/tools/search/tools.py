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
        fallback_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": args.query_text,
                                "fields": ["text^2", "title", "speaker_name"],
                            }
                        }
                    ],
                    "filter": filter_clauses if filter_clauses else [],
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
    """SEC filing discovery tool for identifying relevant filings before detailed content analysis.

    Returns filing metadata (excluding full text) optimized for filing identification and
    integration with FilingChunkSearch. Supports 60+ SEC document types with intelligent
    company name matching and comprehensive filtering capabilities.
    """
    logger.info("tool called: search_filings")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

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

    return SearchFilingsResponse.model_validate(raw_response)


async def search_filing_chunks(
    args: SearchFilingChunksArgs,
) -> SearchFilingChunksResponse:
    """Semantic search within SEC filing document chunks using embedding-based matching.

    Uses the post_filter approach to avoid "hybrid query must be a top level query" errors,
    similar to the opensearch-mcp-server-py implementation. This tool uses the
    ext.ml_inference.query_text pattern to automatically generate embeddings
    from the query text using the configured embedding pipeline.
    """
    logger.info("tool called: search_filing_chunks")

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
        company_query = _build_filing_chunks_company_filter(args.company_name)

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
                f"FilingChunkSearch: Attempting ML inference search for company='{args.company_name}', query='{args.query_text}', pipeline='{HYBRID_SEARCH_PIPELINE}' (15s timeout)"
            )
            logger.info(
                f"FilingChunkSearch: Using {len(ml_filters)} simplified filters for ML (vs {len(all_filters)} complex filters for standard search)"
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
                    "FilingChunkSearch: ML inference timed out after 15s, falling back to standard search"
                )
                raise Exception("ML inference timeout")

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
        # No query text provided, skip ML inference and go directly to standard search
        logger.info(
            f"FilingChunkSearch: No query text provided, using standard filtered search for company='{args.company_name}'"
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
            logger.info("FilingChunkSearch standard pipeline fallback successful")
            return SearchFilingChunksResponse.model_validate(raw_response)
        else:
            logger.warning(
                "FilingChunkSearch: Standard pipeline returned no results, trying direct search"
            )
            raise Exception("Standard pipeline returned no results")

    except Exception as pipeline_error:
        logger.warning(
            f"FilingChunkSearch: Standard pipeline search failed: {str(pipeline_error)}, trying direct search"
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
                logger.info("FilingChunkSearch direct search fallback successful")
                return SearchFilingChunksResponse.model_validate(raw_response)
            else:
                logger.error("FilingChunkSearch: All search methods failed")
                return _get_empty_filing_chunks_response(args.max_results)

        except Exception as direct_error:
            logger.error(
                f"FilingChunkSearch: Direct search also failed: {str(direct_error)}"
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
