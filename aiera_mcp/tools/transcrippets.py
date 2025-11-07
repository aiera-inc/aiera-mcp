#!/usr/bin/env python3

"""Transcrippet tools for Aiera MCP."""

import logging
from typing import Any, Dict

from .base import get_http_client, get_api_key_from_context, make_aiera_request
from .params import FindTranscrippetsArgs, CreateTranscrippetArgs, DeleteTranscrippetArgs

# Setup logging
logger = logging.getLogger(__name__)


async def find_transcrippets(args: FindTranscrippetsArgs) -> Dict[str, Any]:
    """Find and retrieve Transcrippets™, filtered by various identifiers and date ranges."""
    logger.info("tool called: find_transcrippets")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

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


async def create_transcrippet(args: CreateTranscrippetArgs) -> Dict[str, Any]:
    """Create a new Transcrippet™ from an event transcript segment."""
    logger.info("tool called: create_transcrippet")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    data = args.model_dump(exclude_none=True)

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


async def delete_transcrippet(args: DeleteTranscrippetArgs) -> Dict[str, Any]:
    """Delete a Transcrippet™ by its ID."""
    logger.info("tool called: delete_transcrippet")

    # Get context from FastMCP instance
    from ..server import mcp
    ctx = mcp.get_context()
    client = await get_http_client(ctx)
    api_key = await get_api_key_from_context(ctx)

    params = args.model_dump(exclude_none=True)

    return await make_aiera_request(
        client=client,
        method="POST",
        endpoint=f"/transcrippets/{args.transcrippet_id}/delete",
        api_key=api_key,
        params=params,
    )


# Legacy registration functions removed - all tools now registered via registry
