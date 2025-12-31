#!/usr/bin/env python3

"""Transcrippet tools for Aiera MCP."""

import logging

from .models import (
    FindTranscrippetsArgs,
    CreateTranscrippetArgs,
    DeleteTranscrippetArgs,
    FindTranscrippetsResponse,
    CreateTranscrippetResponse,
    DeleteTranscrippetResponse,
    TranscrippetItem,
)
from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from ..common.models import CitationInfo

# Setup logging
logger = logging.getLogger(__name__)


async def find_transcrippets(args: FindTranscrippetsArgs) -> FindTranscrippetsResponse:
    """Find and retrieve Transcrippets™, filtered by various identifiers and date ranges."""
    logger.info("tool called: find_transcrippets")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/transcrippets/",
        api_key=api_key,
        params=params,
    )

    # Add public URLs to each transcrippet in the response
    if raw_response.get("response") and isinstance(raw_response["response"], list):
        for transcrippet in raw_response["response"]:
            if transcrippet.get("transcrippet_guid"):
                guid = transcrippet["transcrippet_guid"]
                transcrippet["public_url"] = (
                    f"https://public.aiera.com/shared/transcrippet.html?id={guid}"
                )

    # Return the structured response with the added public URLs
    response = FindTranscrippetsResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def create_transcrippet(
    args: CreateTranscrippetArgs,
) -> CreateTranscrippetResponse:
    """Create a new Transcrippet™ from an event transcript segment."""
    logger.info("tool called: create_transcrippet")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    data = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="POST",
        endpoint="/transcrippets/create",
        api_key=api_key,
        data=data,
    )

    # Add public URL to the response data before validation
    if raw_response.get("response") and raw_response["response"].get(
        "transcrippet_guid"
    ):
        guid = raw_response["response"]["transcrippet_guid"]
        raw_response["response"][
            "public_url"
        ] = f"https://public.aiera.com/shared/transcrippet.html?id={guid}"

    # Return the structured response with the added public URL
    response = CreateTranscrippetResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response


async def delete_transcrippet(
    args: DeleteTranscrippetArgs,
) -> DeleteTranscrippetResponse:
    """Delete a Transcrippet™ by its ID."""
    logger.info("tool called: delete_transcrippet")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

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

        response = DeleteTranscrippetResponse(
            success=success,
            message=message,
            instructions=raw_response.get("instructions", []),
        )
        if args.exclude_instructions:
            response.instructions = []
        return response

    except Exception as e:
        return DeleteTranscrippetResponse(
            success=False,
            message=f"Failed to delete transcrippet: {str(e)}",
            instructions=[],
        )


# Legacy registration functions removed - all tools now registered via registry
