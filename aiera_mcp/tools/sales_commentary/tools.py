#!/usr/bin/env python3

"""Sales commentary tools for Aiera MCP (CORE-4827)."""

import logging

from ..base import get_http_client, make_aiera_request
from ..utils import strip_ticker_exchange_suffix
from ... import get_api_key
from .models import (
    FindSalesCommentaryArgs,
    GetSalesCommentaryArgs,
    ReportSalesCommentaryUsageArgs,
    FindSalesCommentaryResponse,
    GetSalesCommentaryResponse,
    ReportSalesCommentaryUsageResponse,
)

logger = logging.getLogger(__name__)

FIND_ENDPOINT = "/chat-support/find-sales-commentary"
READERSHIP_ENDPOINT = "/chat-support/report-readership"


async def find_sales_commentary(args: FindSalesCommentaryArgs) -> FindSalesCommentaryResponse:
    """Find sales commentary emails with filter-based discovery and cursor pagination."""
    logger.info("tool called: find_sales_commentary")

    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    # Same analyzer caveat as research: a Bloomberg exchange suffix in free text returns
    # nothing, so strip it before the request leaves.
    if params.get("search"):
        params["search"] = strip_ticker_exchange_suffix(params["search"])

    # Tool parameter names -> API parameter names (comma-separated strings)
    if "author_ids" in params:
        params["author_person_ids"] = ",".join(params.pop("author_ids"))

    if "aiera_provider_ids" in params:
        params["provider_ids"] = ",".join(params.pop("aiera_provider_ids"))

    for list_field in ("series", "subjects"):
        if list_field in params:
            params[list_field] = ",".join(params[list_field])

    if "search_after" in params:
        params["search_after"] = ",".join(str(v) for v in params["search_after"])

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint=FIND_ENDPOINT,
        api_key=api_key,
        params=params,
    )

    response = FindSalesCommentaryResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def get_sales_commentary(args: GetSalesCommentaryArgs) -> GetSalesCommentaryResponse:
    """Retrieve one sales commentary email including its body sections."""
    logger.info("tool called: get_sales_commentary")

    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint=FIND_ENDPOINT,
        api_key=api_key,
        params=params,
    )

    response = GetSalesCommentaryResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def report_sales_commentary_usage(
    args: ReportSalesCommentaryUsageArgs,
) -> ReportSalesCommentaryUsageResponse:
    """Report sales commentary emails that informed the final answer via the shared
    /chat-support/report-readership endpoint, tagged content_type="sales_commentary".
    ``access_type`` is fixed to ``summarize``; the model only supplies the ids."""
    logger.info("tool called: report_sales_commentary_usage")

    client = await get_http_client(None)
    api_key = get_api_key()

    raw_ids = [doc_id.strip() for doc_id in (args.document_ids or "").split(",")]
    ids = [doc_id for doc_id in raw_ids if doc_id]

    body = {
        "items": [
            {"research_id": doc_id, "access_type": "summarize", "content_type": "sales_commentary"}
            for doc_id in ids
        ],
    }

    params: dict = {}
    if args.self_identification:
        params["self_identification"] = args.self_identification

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint=READERSHIP_ENDPOINT,
        api_key=api_key,
        params=params or None,
        data=body,
    )

    response = ReportSalesCommentaryUsageResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
