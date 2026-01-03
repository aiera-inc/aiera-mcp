#!/usr/bin/env python3

"""Instructions tools for Aiera MCP."""

import logging

from .models import (
    GetInstructionsArgs,
    GetInstructionsResponse,
)
from ..base import get_http_client, make_aiera_request
from ... import get_api_key

# Setup logging
logger = logging.getLogger(__name__)


async def get_instructions(args: GetInstructionsArgs) -> GetInstructionsResponse:
    """Retrieve instructions of a specific type for use with MCP/AI agents."""
    logger.info(f"tool called: get_instructions (type={args.instruction_type})")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    # Build params, excluding instruction_type which goes in the path
    params = args.model_dump(exclude_none=True, exclude={"instruction_type"})

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint=f"/chat-support/get-instructions/{args.instruction_type}",
        api_key=api_key,
        params=params,
    )

    # Return the structured response directly
    response = GetInstructionsResponse.model_validate(raw_response)
    return response
