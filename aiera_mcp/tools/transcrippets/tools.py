#!/usr/bin/env python3

"""Transcrippet tools for Aiera MCP."""

import logging
from typing import Any, Dict
from datetime import datetime

from .models import (
    FindTranscrippetsArgs,
    CreateTranscrippetArgs,
    DeleteTranscrippetArgs,
    FindTranscrippetsResponse,
    CreateTranscrippetResponse,
    DeleteTranscrippetResponse,
    TranscrippetItem,
    TranscrippetDetails
)
from ..base import get_http_client, get_api_key_from_context, make_aiera_request
from ..common.models import CitationInfo

# Setup logging
logger = logging.getLogger(__name__)


async def find_transcrippets(args: FindTranscrippetsArgs) -> FindTranscrippetsResponse:
    """Find and retrieve Transcrippets™, filtered by various identifiers and date ranges."""
    logger.info("tool called: find_transcrippets")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/transcrippets/",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Note: Transcrippets API returns data differently than other endpoints
    transcrippets_data = raw_response.get("response", [])
    if not isinstance(transcrippets_data, list):
        transcrippets_data = []

    transcrippets = []
    citations = []

    for transcrippet_data in transcrippets_data:
        # Parse created date safely
        created_date = None
        try:
            if transcrippet_data.get("created_date"):
                created_date = datetime.fromisoformat(transcrippet_data["created_date"].replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pass

        # Generate public URL (preserving original logic)
        public_url = f"https://public.aiera.com/shared/transcrippet.html?id={transcrippet_data.get('transcrippet_guid')}"

        transcrippet_item = TranscrippetItem(
            transcrippet_id=str(transcrippet_data.get("transcrippet_id", "")),
            public_url=public_url,
            title=transcrippet_data.get("title"),
            company_name=transcrippet_data.get("company_name"),
            event_title=transcrippet_data.get("event_title"),
            transcript_preview=transcrippet_data.get("transcript_preview"),
            created_date=created_date
        )
        transcrippets.append(transcrippet_item)

        # Add citation with public URL
        citations.append(CitationInfo(
            title=transcrippet_data.get("title", f"Transcrippet {transcrippet_data.get('transcrippet_id', '')}"),
            url=public_url,
            timestamp=created_date
        ))

    return FindTranscrippetsResponse(
        transcrippets=transcrippets,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def create_transcrippet(args: CreateTranscrippetArgs) -> CreateTranscrippetResponse:
    """Create a new Transcrippet™ from an event transcript segment."""
    logger.info("tool called: create_transcrippet")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    data = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/transcrippets/create",
        api_key=api_key,
        data=data,
    )

    # Transform raw response to structured format
    transcrippet_data = raw_response.get("response", {})
    if not isinstance(transcrippet_data, dict):
        raise ValueError("Failed to create transcrippet")

    # Parse created date safely
    created_date = None
    try:
        if transcrippet_data.get("created_date"):
            created_date = datetime.fromisoformat(transcrippet_data["created_date"].replace("Z", "+00:00"))
        else:
            created_date = datetime.now()
    except (ValueError, AttributeError):
        created_date = datetime.now()

    # Generate public URL (preserving original logic)
    public_url = f"https://public.aiera.com/shared/transcrippet.html?id={transcrippet_data.get('transcrippet_guid')}"

    # Build detailed transcrippet
    transcrippet_details = TranscrippetDetails(
        transcrippet_id=str(transcrippet_data.get("transcrippet_id", "")),
        public_url=public_url,
        title=transcrippet_data.get("title"),
        company_name=transcrippet_data.get("company_name"),
        event_title=transcrippet_data.get("event_title"),
        transcript_preview=transcrippet_data.get("transcript_preview"),
        created_date=created_date,
        transcript_text=transcrippet_data.get("transcript_text", ""),
        audio_url=transcrippet_data.get("audio_url"),
        speaker_name=transcrippet_data.get("speaker_name"),
        start_time=transcrippet_data.get("start_time"),
        end_time=transcrippet_data.get("end_time")
    )

    # Build citation
    citations = [CitationInfo(
        title=transcrippet_data.get("title", f"Transcrippet {transcrippet_data.get('transcrippet_id', '')}"),
        url=public_url,
        timestamp=created_date
    )]

    return CreateTranscrippetResponse(
        transcrippet=transcrippet_details,
        instructions=raw_response.get("instructions", []),
        citation_information=citations
    )


async def delete_transcrippet(args: DeleteTranscrippetArgs) -> DeleteTranscrippetResponse:
    """Delete a Transcrippet™ by its ID."""
    logger.info("tool called: delete_transcrippet")

    # Get context from FastMCP instance
    from ...server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    try:
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint=f"/transcrippets/{args.transcrippet_id}/delete",
            api_key=api_key,
            params=params,
        )

        # Check if deletion was successful
        success = True
        message = "Transcrippet deleted successfully"

        # If there's an error in the response, mark as failed
        if "error" in raw_response:
            success = False
            message = raw_response.get("error", "Deletion failed")
        elif raw_response.get("response", {}).get("error"):
            success = False
            message = raw_response["response"].get("error", "Deletion failed")

        return DeleteTranscrippetResponse(
            success=success,
            message=message,
            instructions=raw_response.get("instructions", []),
            citation_information=[]
        )

    except Exception as e:
        return DeleteTranscrippetResponse(
            success=False,
            message=f"Failed to delete transcrippet: {str(e)}",
            instructions=[],
            citation_information=[]
        )


# Legacy registration functions removed - all tools now registered via registry
