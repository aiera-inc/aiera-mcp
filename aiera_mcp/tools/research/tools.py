#!/usr/bin/env python3

"""Research tools for Aiera MCP."""

import logging
import asyncio

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    FindResearchArgs,
    GetResearchArgs,
    FindResearchResponse,
    GetResearchResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_research(args: FindResearchArgs) -> FindResearchResponse:
    """Find research reports using semantic search with embedding-based matching.

    Uses the post_filter approach to avoid "hybrid query must be a top level query" errors,
    similar to the opensearch-mcp-server-py implementation. This tool uses the
    ext.ml_inference.query_text pattern to automatically generate embeddings
    from the query text using the configured embedding pipeline.
    """
    logger.info("tool called: find_research")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    must_clauses = []

    # add date range filter...
    if args.start_date:
        range = {"gte": args.start_date}
        if args.end_date:
            range["lte"] = args.end_date

        must_clauses.append({"range": {"date": range}})

    # add asset classes filter...
    if args.asset_classes:
        must_clauses.append({"terms": {"asset_classes": args.asset_classes}})

    # add asset types filter...
    if args.asset_types:
        must_clauses.append({"terms": {"asset_types": args.asset_types}})

    # add author filter...
    if args.author_ids:
        must_clauses.append({"terms": {"authors.person_id": args.author_ids}})

    # add aiera provider ID filter...
    if args.aiera_provider_ids:
        must_clauses.append({"terms": {"aiera_provider_id": args.aiera_provider_ids}})

    k_value = 40
    if must_clauses:
        k_value = 400  # Increased for filters

    if k_value > 10000:
        k_value = 10000

    query_text = args.search or ""

    # first, try ML-based search...
    query = {
        "query": {
            "hybrid": {
                "queries": [
                    {
                        "neural": {
                            "embedding_384": {
                                "query_text": query_text,
                                "k": k_value,
                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": query_text,
                            "fields": ["synopsis", "description", "title"],
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
        "size": 20,
        "search_pipeline": "hybrid_search_pipeline",
        "include_base_instructions": args.include_base_instructions,
        "originating_prompt": args.originating_prompt,
        "self_identification": args.self_identification,
    }

    # Try ML-inference search...
    try:
        raw_response = await asyncio.wait_for(
            make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/research",
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
            logger.info("find_research ML inference successful")
            response = FindResearchResponse.model_validate(raw_response)
            if args.exclude_instructions:
                response.instructions = []
            return response

    except asyncio.TimeoutError:
        logger.warning(
            "find_research: ML inference timed out, falling back to standard search"
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
                                    "text": {
                                        "query": query_text,
                                        "boost": 2.0,
                                    }
                                }
                            },
                            {
                                "multi_match": {
                                    "query": query_text,
                                    "fields": ["synopsis", "description", "title"],
                                    "type": "best_fields",
                                    "boost": 1.5,
                                }
                            },
                        ],
                    }
                },
                "size": 20,
                "include_base_instructions": args.include_base_instructions,
                "originating_prompt": args.originating_prompt,
                "self_identification": args.self_identification,
            }

            raw_response = await make_aiera_request(
                client=client,
                method="POST",
                endpoint="/chat-support/search/research",
                api_key=api_key,
                params={},
                data=query,
            )

            if raw_response and "response" in raw_response:
                logger.info("find_research standard pipeline search successful")
                response = FindResearchResponse.model_validate(raw_response)
                if args.exclude_instructions:
                    response.instructions = []
                return response

        except Exception as pipeline_error:
            logger.info(
                f"find_research: Standard pipeline search failed: {str(pipeline_error)}"
            )

    # if failed, send empty response...
    return _get_empty_find_research_response()


def _get_empty_find_research_response() -> FindResearchResponse:
    """Return empty response structure for find research."""
    return FindResearchResponse(
        instructions=[],
        response={"result": []},
    )


async def get_research(args: GetResearchArgs) -> GetResearchResponse:
    """Retrieve a research report, including summary and other metadata."""
    logger.info("tool called: get_research")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-research",
        api_key=api_key,
        params=params,
    )

    response = GetResearchResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
