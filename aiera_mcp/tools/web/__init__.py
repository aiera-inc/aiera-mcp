#!/usr/bin/env python3

"""Web domain for Aiera MCP."""

from .tools import trusted_web_search
from .models import (
    TrustedWebSearchArgs,
    TrustedWebSearchResponse,
)

__all__ = [
    # Tools
    "trusted_web_search",
    # Parameter models
    "TrustedWebSearchArgs",
    # Response models
    "TrustedWebSearchResponse",
]
