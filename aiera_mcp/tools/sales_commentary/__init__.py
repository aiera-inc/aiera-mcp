#!/usr/bin/env python3

"""Sales commentary domain for Aiera MCP (CORE-4827)."""

from .tools import (
    find_sales_commentary,
    get_sales_commentary,
    report_sales_commentary_usage,
)
from .models import (
    FindSalesCommentaryArgs,
    GetSalesCommentaryArgs,
    ReportSalesCommentaryUsageArgs,
    FindSalesCommentaryResponse,
    GetSalesCommentaryResponse,
    ReportSalesCommentaryUsageResponse,
)

__all__ = [
    # Tools
    "find_sales_commentary",
    "get_sales_commentary",
    "report_sales_commentary_usage",
    # Parameter models
    "FindSalesCommentaryArgs",
    "GetSalesCommentaryArgs",
    "ReportSalesCommentaryUsageArgs",
    # Response models
    "FindSalesCommentaryResponse",
    "GetSalesCommentaryResponse",
    "ReportSalesCommentaryUsageResponse",
]
