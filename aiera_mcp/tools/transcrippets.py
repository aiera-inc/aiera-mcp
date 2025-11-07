#!/usr/bin/env python3

"""Transcrippet tools for Aiera MCP."""

import logging
from typing import Any, Dict, Optional

from mcp.server.fastmcp import FastMCP
from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .utils import correct_provided_ids

# Setup logging
logger = logging.getLogger(__name__)


async def find_transcrippets(
    transcrippet_id: Optional[str] = None,
    event_id: Optional[str] = None,
    equity_id: Optional[str] = None,
    speaker_id: Optional[str] = None,
    transcript_item_id: Optional[str] = None,
    created_start_date: Optional[str] = None,
    created_end_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Find and retrieve Transcrippets™, filtered by various identifiers and date ranges."""
    logger.info("tool called: find_transcrippets")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = {}

    if transcrippet_id:
        params["transcrippet_id"] = correct_provided_ids(transcrippet_id)

    if event_id:
        params["event_id"] = correct_provided_ids(event_id)

    if equity_id:
        params["equity_id"] = correct_provided_ids(equity_id)

    if speaker_id:
        params["speaker_id"] = correct_provided_ids(speaker_id)

    if transcript_item_id:
        params["transcript_item_id"] = correct_provided_ids(transcript_item_id)

    if created_start_date:
        params["created_start_date"] = created_start_date

    if created_end_date:
        params["created_end_date"] = created_end_date

    response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/transcrippets/",
        api_key=api_key,
        params=params,
    )

    # Filter response to only include public_url and transcrippet_id
    if "response" in response and isinstance(response["response"], list):
        filtered_transcrippets = []
        for transcrippet in response["response"]:
            filtered_item = {
                "transcrippet_id": transcrippet.get("transcrippet_id"),
                "public_url": f"https://public.aiera.com/shared/transcrippet.html?id={transcrippet.get('transcrippet_guid')}"
            }
            filtered_transcrippets.append(filtered_item)

        response["response"] = filtered_transcrippets

    return response


async def create_transcrippet(
    event_id: int,
    transcript: str,
    transcript_item_id: int,
    transcript_item_offset: int,
    transcript_end_item_id: int,
    transcript_end_item_offset: int,
    company_id: Optional[int] = None,
    equity_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Create a new Transcrippet™ from an event transcript segment."""
    logger.info("tool called: create_transcrippet")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    data = {
        "event_id": event_id,
        "transcript": transcript,
        "transcript_item_id": transcript_item_id,
        "transcript_item_offset": transcript_item_offset,
        "transcript_end_item_id": transcript_end_item_id,
        "transcript_end_item_offset": transcript_end_item_offset,
    }

    if company_id:
        data["company_id"] = company_id

    if equity_id:
        data["equity_id"] = equity_id

    response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/transcrippets/create",
        api_key=api_key,
        data=data,
    )

    # Filter response to only include public_url and transcrippet_id
    if "response" in response and isinstance(response["response"], dict):
        transcrippet = response["response"]
        filtered_transcrippet = {
            "transcrippet_id": transcrippet.get("transcrippet_id"),
            "public_url": f"https://public.aiera.com/shared/transcrippet.html?id={transcrippet.get('transcrippet_guid')}"
        }
        response["response"] = filtered_transcrippet

    return response


async def delete_transcrippet(transcrippet_id: str) -> Dict[str, Any]:
    """Delete a Transcrippet™ by its ID."""
    logger.info("tool called: delete_transcrippet")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    return await make_aiera_request(
        client=client,
        method="POST",
        endpoint=f"/transcrippets/{transcrippet_id}/delete",
        api_key=api_key,
        params={},
    )


def register_transcrippets_tools(mcp_server: FastMCP) -> None:
    """Register Transcrippet tools with FastMCP server."""

    @mcp_server.tool(
        name="find_transcrippets",
        description="Finds and retrieves Transcrippets™ using search filters.",
        annotations={
            "title": "Find Transcrippets",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def find_transcrippets_tool(
        transcrippet_id: Optional[str] = None,
        event_id: Optional[str] = None,
        equity_id: Optional[str] = None,
        speaker_id: Optional[str] = None,
        transcript_item_id: Optional[str] = None,
        created_start_date: Optional[str] = None,
        created_end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await find_transcrippets(transcrippet_id, event_id, equity_id, speaker_id, transcript_item_id, created_start_date, created_end_date)

    @mcp_server.tool(
        name="create_transcrippet",
        description="Creates a new Transcrippet™ from an event transcript segment.",
        annotations={
            "title": "Create Transcrippet",
            "readOnlyHint": True,
            "destructiveHint": False,
        }
    )
    async def create_transcrippet_tool(
        event_id: int,
        transcript: str,
        transcript_item_id: int,
        transcript_item_offset: int,
        transcript_end_item_id: int,
        transcript_end_item_offset: int,
        company_id: Optional[int] = None,
        equity_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        return await create_transcrippet(event_id, transcript, transcript_item_id, transcript_item_offset, transcript_end_item_id, transcript_end_item_offset, company_id, equity_id)

    @mcp_server.tool(
        name="delete_transcrippet",
        description="Deletes a Transcrippet™ by its ID.",
        annotations={
            "title": "Delete Transcrippet",
            "readOnlyHint": False,
            "destructiveHint": True,
        }
    )
    async def delete_transcrippet_tool(transcrippet_id: str) -> Dict[str, Any]:
        return await delete_transcrippet(transcrippet_id)