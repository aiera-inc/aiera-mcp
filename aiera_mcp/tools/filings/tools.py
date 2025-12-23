#!/usr/bin/env python3

"""SEC filing tools for Aiera MCP."""

import logging
from datetime import datetime

from ..base import get_http_client, make_aiera_request
from ... import get_api_key
from .models import (
    FindFilingsArgs,
    GetFilingArgs,
    FindFilingsResponse,
    GetFilingResponse,
    FilingItem,
    FilingDetails,
    FilingSummary,
    CitationInfo,
    EquityInfo,
)

# Setup logging
logger = logging.getLogger(__name__)


async def find_filings(args: FindFilingsArgs) -> FindFilingsResponse:
    """Find SEC filings, filtered by a date range, and one of the following: ticker(s), watchlist, index, sector, or subsector; and (optionally) by a form number."""
    logger.info("tool called: find_filings")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )

    # Return the structured response that matches the actual API format
    # Parse individual filings to match new model structure
    if "response" in raw_response and "data" in raw_response["response"]:
        filings_data = []
        for filing_data in raw_response["response"]["data"]:
            # Parse dates safely
            filing_date = None
            period_end_date = None
            release_date = None
            arrival_date = None
            pulled_date = None

            try:
                if filing_data.get("filing_date"):
                    filing_date = datetime.fromisoformat(
                        filing_data["filing_date"].replace("Z", "+00:00")
                    ).date()
            except (ValueError, AttributeError):
                pass

            try:
                if filing_data.get("period_end_date"):
                    period_end_date = datetime.fromisoformat(
                        filing_data["period_end_date"].replace("Z", "+00:00")
                    ).date()
            except (ValueError, AttributeError):
                pass

            try:
                if filing_data.get("release_date"):
                    release_date = datetime.fromisoformat(
                        filing_data["release_date"].replace("Z", "+00:00")
                    ).date()
            except (ValueError, AttributeError):
                pass

            try:
                if filing_data.get("arrival_date"):
                    arrival_date = datetime.fromisoformat(
                        filing_data["arrival_date"].replace("Z", "+00:00")
                    ).date()
            except (ValueError, AttributeError):
                pass

            try:
                if filing_data.get("pulled_date"):
                    pulled_date = datetime.fromisoformat(
                        filing_data["pulled_date"].replace("Z", "+00:00")
                    ).date()
            except (ValueError, AttributeError):
                pass

            # Extract company info from equity field if available
            equity_info = None
            if "equity" in filing_data:
                equity_data = filing_data["equity"]
                if isinstance(equity_data, dict):
                    equity_info = {
                        "company_name": equity_data.get("name"),
                        "ticker": equity_data.get("bloomberg_ticker")
                        or equity_data.get("ticker"),
                    }

            # Create new filing structure matching the actual response
            parsed_filing = {
                "filing_id": filing_data.get("filing_id"),
                "title": filing_data.get("title", ""),
                "filing_date": filing_date,
                "period_end_date": period_end_date,
                "is_amendment": filing_data.get("is_amendment", 0),
                "equity": equity_info,
                "form_number": filing_data.get("form_number"),
                "form_name": filing_data.get("form_name"),
                "filing_organization": filing_data.get("filing_organization"),
                "filing_system": filing_data.get("filing_system"),
                "release_date": release_date,
                "arrival_date": arrival_date,
                "pulled_date": pulled_date,
                "json_synced": filing_data.get("json_synced"),
                "datafiles_synced": filing_data.get("datafiles_synced"),
                "summary": filing_data.get("summary"),
                "citation_information": filing_data.get("citation_information"),
            }
            filings_data.append(parsed_filing)

        raw_response["response"]["data"] = filings_data

    # Handle malformed responses gracefully
    try:
        return FindFilingsResponse.model_validate(raw_response)
    except Exception as e:
        logger.warning(f"Failed to parse API response: {e}")
        # Return empty response for malformed data
        return FindFilingsResponse(
            instructions=[], response={"data": [], "pagination": None}
        )


async def get_filing(args: GetFilingArgs) -> GetFilingResponse:
    """Retrieve an SEC filing, including a summary and other metadata."""
    logger.info("tool called: get_filing")

    # Get client and API key (no context needed for standard MCP)
    client = await get_http_client(None)
    api_key = get_api_key()

    params = args.model_dump(exclude_none=True)
    params["include_content"] = "true"

    # Handle special field mapping: filing_id -> filing_ids
    if "filing_id" in params:
        params["filing_ids"] = str(params.pop("filing_id"))

    raw_response = await make_aiera_request(
        client=client,
        method="GET",
        endpoint="/chat-support/find-filings",
        api_key=api_key,
        params=params,
    )

    # Transform raw response to structured format
    # Handle both old format (response.data) and new format (data directly)
    if "response" in raw_response:
        api_data = raw_response.get("response", {})
        filings_data = api_data.get("data", [])
        total_count = api_data.get("total", 0)
    else:
        # New API format with pagination object
        filings_data = raw_response.get("data", [])
        pagination = raw_response.get("pagination", {})
        total_count = pagination.get("total_count", len(filings_data))

    if not filings_data:
        raise ValueError(f"Filing not found: {args.filing_id}")

    filing_data = filings_data[0]  # Get the first (and should be only) filing

    # Parse dates safely
    filing_date = None
    period_end_date = None

    try:
        if filing_data.get("filing_date"):
            filing_date = datetime.fromisoformat(
                filing_data["filing_date"].replace("Z", "+00:00")
            ).date()
    except (ValueError, AttributeError):
        pass

    try:
        if filing_data.get("period_end_date"):
            period_end_date = datetime.fromisoformat(
                filing_data["period_end_date"].replace("Z", "+00:00")
            ).date()
    except (ValueError, AttributeError):
        pass

    # Build filing summary
    summary = None
    if (
        filing_data.get("summary")
        or filing_data.get("key_points")
        or filing_data.get("financial_highlights")
    ):
        summary = FilingSummary(
            summary=filing_data.get("summary"),
            key_points=filing_data.get("key_points", []),
            financial_highlights=filing_data.get("financial_highlights", {}),
        )

    # Build detailed filing
    # Handle API field mapping - get_filing returns different structure than find_filings
    equity_data = filing_data.get("equity", {})
    filing_details = FilingDetails(
        filing_id=filing_data.get("filing_id", 0),
        title=filing_data.get("title", ""),
        filing_date=filing_date,
        period_end_date=period_end_date,
        is_amendment=filing_data.get("is_amendment", 0),
        equity=(
            EquityInfo(
                company_name=equity_data.get("company_name", ""),
                ticker=equity_data.get("ticker", ""),
            )
            if equity_data
            else None
        ),
        form_number=filing_data.get("form_number", ""),
        form_name=filing_data.get("form_name", ""),
        summary=summary,
        content_preview=filing_data.get("content_preview"),
        document_count=filing_data.get("document_count", 1),
    )

    return GetFilingResponse(
        filing=filing_details,
        instructions=raw_response.get("instructions", []),
    )
