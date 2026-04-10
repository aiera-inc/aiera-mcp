#!/usr/bin/env python3

"""Common utility tools for Aiera MCP."""

import logging

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    GetGrammarTemplateArgs,
    GetGrammarTemplateResponse,
    GetCoreInstructionsArgs,
    GetCoreInstructionsResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


async def get_grammar_template(
    args: GetGrammarTemplateArgs,
) -> GetGrammarTemplateResponse:
    """Retrieve a grammar template for tailored response guidance."""
    logger.info("tool called: get_grammar_template")

    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-grammar-template",
        api_key=api_key,
        params=params,
    )

    response = GetGrammarTemplateResponse.model_validate(raw_response)
    return response


async def get_core_instructions(
    args: GetCoreInstructionsArgs,
) -> GetCoreInstructionsResponse:
    """Retrieve core instructions for working with Aiera tools and data."""
    logger.info("tool called: get_core_instructions")

    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/get-core-instructions",
        api_key=api_key,
        params=params,
    )

    response = GetCoreInstructionsResponse.model_validate(raw_response)
    return response
