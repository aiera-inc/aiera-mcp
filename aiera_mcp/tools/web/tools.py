#!/usr/bin/env python3

"""Web tools for Aiera MCP."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    TrustedWebSearchArgs,
    TrustedWebSearchResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def trusted_web_search(args: TrustedWebSearchArgs) -> TrustedWebSearchResponse:
    """Search the web using only trusted/approved financial news domains."""
    logger.info("tool called: trusted_web_search")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/trusted-web",
        api_key=api_key,
        params=params,
    )

    response = TrustedWebSearchResponse.model_validate(raw_response)
    if args.exclude_instructions:
        response.instructions = []
    return response
