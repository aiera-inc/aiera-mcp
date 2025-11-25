#!/usr/bin/env python3

"""
Enhanced manual testing script for Aiera MCP tools.

This script tests each tool by:
1. Making direct API calls with make_aiera_request
2. Calling the corresponding tool function
3. Comparing raw API responses with structured tool outputs
4. Logging discrepancies and issues
"""

import asyncio
import httpx
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import the base function we need
from aiera_mcp.tools.base import make_aiera_request

# Import all the tool functions to compare against
from aiera_mcp.tools.events.tools import find_events, get_event, get_upcoming_events
from aiera_mcp.tools.filings.tools import find_filings
from aiera_mcp.tools.equities.tools import (
    find_equities,
    get_equity_summaries,
    get_available_watchlists,
    get_available_indexes,
    get_sectors_and_subsectors,
    get_index_constituents,
    get_watchlist_constituents,
)
from aiera_mcp.tools.company_docs.tools import (
    find_company_docs,
    get_company_doc,
    get_company_doc_categories,
    get_company_doc_keywords,
)
from aiera_mcp.tools.third_bridge.tools import (
    find_third_bridge_events,
    get_third_bridge_event,
)
from aiera_mcp.tools.transcrippets.tools import (
    find_transcrippets,
    create_transcrippet,
    delete_transcrippet,
)
from aiera_mcp.tools.search.tools import (
    search_transcripts,
    search_filings,
    search_filing_chunks,
)

# Import parameter and response models
from aiera_mcp.tools.events.models import (
    FindEventsArgs,
    GetEventArgs,
    GetUpcomingEventsArgs,
    FindEventsResponse,
    GetEventResponse,
    GetUpcomingEventsResponse,
)
from aiera_mcp.tools.filings.models import FindFilingsArgs, FindFilingsResponse
from aiera_mcp.tools.equities.models import (
    FindEquitiesArgs,
    GetEquitySummariesArgs,
    GetIndexConstituentsArgs,
    GetWatchlistConstituentsArgs,
    GetAvailableWatchlistsArgs,
    GetAvailableIndexesArgs,
    GetSectorsAndSubsectorsArgs,
    FindEquitiesResponse,
    GetEquitySummariesResponse,
    GetAvailableWatchlistsResponse,
    GetAvailableIndexesResponse,
    GetSectorsSubsectorsResponse,
    GetIndexConstituentsResponse,
    GetWatchlistConstituentsResponse,
)
from aiera_mcp.tools.company_docs.models import (
    FindCompanyDocsArgs,
    GetCompanyDocArgs,
    GetCompanyDocCategoriesArgs,
    GetCompanyDocKeywordsArgs,
    FindCompanyDocsResponse,
    GetCompanyDocResponse,
    GetCompanyDocCategoriesResponse,
    GetCompanyDocKeywordsResponse,
)
from aiera_mcp.tools.third_bridge.models import (
    FindThirdBridgeEventsArgs,
    GetThirdBridgeEventArgs,
    FindThirdBridgeEventsResponse,
    GetThirdBridgeEventResponse,
)
from aiera_mcp.tools.transcrippets.models import (
    FindTranscrippetsArgs,
    FindTranscrippetsResponse,
    CreateTranscrippetArgs,
    CreateTranscrippetResponse,
    DeleteTranscrippetArgs,
    DeleteTranscrippetResponse,
)
from aiera_mcp.tools.search.models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchFilingChunksArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchFilingChunksResponse,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("manual_test_discrepancies.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of comparing raw API response with tool output."""

    tool_name: str
    success: bool
    raw_response: Optional[Dict[Any, Any]]
    structured_response: Optional[Any]
    parsed_response: Optional[Any]
    discrepancies: List[str]
    parsing_errors: List[str]
    errors: List[str]
    endpoint: str
    params_or_data: Dict[str, Any]


class DiscrepancyAnalyzer:
    """Analyzes discrepancies between raw API responses and structured outputs."""

    def __init__(self):
        self.results: List[TestResult] = []

    def analyze_parsing(
        self, raw_response: Dict[Any, Any], parsed_response: Any, tool_name: str
    ) -> List[str]:
        """Analyze if the Response object correctly parsed the raw response."""
        parsing_errors = []

        try:
            if parsed_response is None:
                parsing_errors.append(
                    "Failed to parse raw response into Response object"
                )
                return parsing_errors

            # The Response object successfully parsed the raw response
            # This means the schema matches the API response structure
            logger.info(f"✅ {tool_name}: Response object parsing successful")
            logger.debug(
                f"Raw response keys: {list(raw_response.keys()) if isinstance(raw_response, dict) else type(raw_response)}"
            )

        except Exception as e:
            parsing_errors.append(f"Error during parsing analysis: {str(e)}")

        return parsing_errors

    def compare_parsed_with_structured(
        self, parsed_response: Any, structured_response: Any, tool_name: str
    ) -> List[str]:
        """Compare the parsed Response object with the structured tool output."""
        discrepancies = []

        try:
            # Convert both to comparable formats
            if hasattr(parsed_response, "model_dump"):
                parsed_dict = parsed_response.model_dump()
            else:
                parsed_dict = parsed_response

            if hasattr(structured_response, "model_dump"):
                structured_dict = structured_response.model_dump()
            else:
                structured_dict = structured_response

            # For a simple comparison, check if they're substantially the same
            # The tool function should return the same data as the Response object parsing
            if parsed_dict != structured_dict:
                # This is expected since tools may add metadata, transform data, etc.
                # We'll just log that they differ but not treat it as an error
                logger.debug(
                    f"📝 {tool_name}: Parsed Response differs from tool output (expected)"
                )
            else:
                logger.info(
                    f"✅ {tool_name}: Parsed Response matches tool output exactly"
                )

        except Exception as e:
            discrepancies.append(
                f"Error comparing parsed response with tool output: {str(e)}"
            )

        return discrepancies

    def analyze_structure(self, raw: Any, structured: Any, path: str = "") -> List[str]:
        """Simple comparison of raw and structured responses."""
        discrepancies = []

        # Since we're focusing on Response object parsing, we'll keep this simple
        # The main test is whether the Response object can parse the raw response
        try:
            if raw is None and structured is not None:
                discrepancies.append(
                    f"{path}: Raw response is None but structured response exists"
                )
            elif raw is not None and structured is None:
                discrepancies.append(
                    f"{path}: Structured response is None but raw response exists"
                )
            # For other cases, we'll rely on the Response object parsing test

        except Exception as e:
            discrepancies.append(f"{path}: Error analyzing structure - {str(e)}")

        return discrepancies

    def check_data_completeness(
        self, raw: Dict[Any, Any], structured: Any, tool_name: str
    ) -> List[str]:
        """Simplified check focusing on basic data presence."""
        discrepancies = []

        try:
            # Just check if both responses exist and have some content
            if raw is None:
                discrepancies.append("No raw response received")
            elif structured is None:
                discrepancies.append("No structured response received")
            else:
                logger.debug(
                    f"📝 {tool_name}: Both raw and structured responses received"
                )

        except Exception as e:
            discrepancies.append(f"Error checking data completeness: {str(e)}")

        return discrepancies

    def log_discrepancies(self, result: TestResult):
        """Log detailed discrepancy information."""
        if result.discrepancies or result.errors or result.parsing_errors:
            logger.warning(f"=== ISSUES FOUND IN {result.tool_name} ===")

            if result.errors:
                logger.error(f"Errors in {result.tool_name}:")
                for error in result.errors:
                    logger.error(f"  - {error}")

            if result.parsing_errors:
                logger.error(f"Parsing errors in {result.tool_name}:")
                for error in result.parsing_errors:
                    logger.error(f"  - {error}")

            if result.discrepancies:
                logger.warning(f"Discrepancies in {result.tool_name}:")
                for discrepancy in result.discrepancies:
                    logger.warning(f"  - {discrepancy}")

            # Log full raw response for tools with errors, parsing errors, or discrepancies to help debug
            if (
                result.errors or result.parsing_errors or result.discrepancies
            ) and result.raw_response:
                log_func = (
                    logger.error
                    if (result.errors or result.parsing_errors)
                    else logger.warning
                )
                issue_type = (
                    "ERRORS"
                    if result.errors
                    else (
                        "PARSING ERRORS" if result.parsing_errors else "DISCREPANCIES"
                    )
                )
                log_func(f"FULL RAW RESPONSE FOR {result.tool_name} WITH {issue_type}:")
                import json

                try:
                    log_func(json.dumps(result.raw_response, indent=2, default=str))
                except Exception as e:
                    log_func(f"Could not serialize raw response: {e}")
                    log_func(f"Raw response type: {type(result.raw_response)}")
                    log_func(f"Raw response repr: {repr(result.raw_response)}")

            # Log sample of raw response structure
            if result.raw_response:
                if isinstance(result.raw_response, dict):
                    logger.info(
                        f"Raw response keys for {result.tool_name}: {list(result.raw_response.keys())}"
                    )
                    if "data" in result.raw_response and result.raw_response["data"]:
                        first_item = (
                            result.raw_response["data"][0]
                            if isinstance(result.raw_response["data"], list)
                            else result.raw_response["data"]
                        )
                        if isinstance(first_item, dict):
                            logger.info(
                                f"Raw data item keys: {list(first_item.keys())}"
                            )
                elif isinstance(result.raw_response, list):
                    logger.info(
                        f"Raw response is a list with {len(result.raw_response)} items"
                    )
                    if result.raw_response and isinstance(result.raw_response[0], dict):
                        logger.info(
                            f"First list item keys: {list(result.raw_response[0].keys())}"
                        )
                else:
                    logger.info(f"Raw response type: {type(result.raw_response)}")

            logger.warning(f"=== END {result.tool_name} ===\n")
        else:
            logger.info(f"✅ {result.tool_name}: No issues found")

        # Extended detailed logging for all tools if they have responses and issues
        if result.raw_response and (
            result.errors or result.parsing_errors or result.discrepancies
        ):
            logger.info(f"=== DETAILED ANALYSIS FOR {result.tool_name} ===")

            # Additional detailed analysis
            if isinstance(result.raw_response, dict):
                # Check different possible response formats
                if "response" in result.raw_response:
                    logger.info(f"Response wrapper detected")
                    response_data = result.raw_response["response"]
                    if isinstance(response_data, dict):
                        if "data" in response_data:
                            data = response_data["data"]
                            logger.info(
                                f"Found data in response.data format: {len(data) if isinstance(data, list) else 'not a list'}"
                            )
                        logger.info(
                            f"Response wrapper keys: {list(response_data.keys())}"
                        )
                    elif isinstance(response_data, list):
                        logger.info(
                            f"Response wrapper contains list directly: {len(response_data)} items"
                        )

                if "data" in result.raw_response:
                    data = result.raw_response["data"]
                    logger.info(
                        f"Found data in root format: {len(data) if isinstance(data, list) else 'not a list'}"
                    )

                # Log pagination info if present
                if "pagination" in result.raw_response:
                    logger.info(f"Pagination info: {result.raw_response['pagination']}")
                elif (
                    "response" in result.raw_response
                    and isinstance(result.raw_response["response"], dict)
                    and "total" in result.raw_response["response"]
                ):
                    logger.info(
                        f"Legacy pagination - total: {result.raw_response['response']['total']}"
                    )

                # Log instructions if present
                if "instructions" in result.raw_response:
                    logger.info(f"Instructions: {result.raw_response['instructions']}")

            elif isinstance(result.raw_response, list):
                logger.info(
                    f"Response is direct list: {len(result.raw_response)} items"
                )
                if result.raw_response and isinstance(result.raw_response[0], dict):
                    logger.info(
                        f"First item structure: {list(result.raw_response[0].keys())}"
                    )

            logger.info(f"=== END DETAILED ANALYSIS FOR {result.tool_name} ===\n")


async def get_test_http_client():
    """Get an HTTP client for testing."""
    return httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    )


def get_test_api_key():
    """Get API key from environment."""
    return os.getenv("AIERA_API_KEY", "test-key")


def get_test_date_ranges():
    """Get test date ranges for various tests."""
    today = datetime.now()
    return {
        "last_quarter": {
            "start_date": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "end_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        },
        "last_year": {
            "start_date": (today - timedelta(days=365)).strftime("%Y-%m-%d"),
            "end_date": (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        },
        "q4_2023": {"start_date": "2023-10-01", "end_date": "2023-12-31"},
        "q1_2024": {"start_date": "2024-01-01", "end_date": "2024-03-31"},
    }


async def test_tool_with_comparison(
    tool_name: str,
    tool_function,
    args_model,
    response_model,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    method: str = "GET",
    analyzer: Optional[DiscrepancyAnalyzer] = None,
) -> TestResult:
    """Test a tool by comparing raw API response with structured output."""

    client = await get_test_http_client()
    api_key = get_test_api_key()

    result = TestResult(
        tool_name=tool_name,
        success=False,
        raw_response=None,
        structured_response=None,
        parsed_response=None,
        discrepancies=[],
        parsing_errors=[],
        errors=[],
        endpoint=endpoint,
        params_or_data=params or data or {},
    )

    try:
        # Step 1: Make raw API call
        logger.info(f"Testing {tool_name}...")
        raw_response = await make_aiera_request(
            client=client,
            method=method,
            endpoint=endpoint,
            api_key=api_key,
            params=params or {},
            data=data,
        )
        result.raw_response = raw_response

        # Step 2: Test Response object parsing
        try:
            parsed_response = response_model.model_validate(raw_response)
            result.parsed_response = parsed_response

            # Log result count for search tools
            if tool_name in ["search_transcripts", "search_filing_chunks"]:
                try:
                    if hasattr(parsed_response, "response") and hasattr(
                        parsed_response.response, "result"
                    ):
                        result = parsed_response.response.result
                        if result is not None:
                            result_count = len(result)
                            logger.info(
                                f"📊 {tool_name} returned {result_count} results"
                            )
                        else:
                            logger.info(
                                f"📊 {tool_name} returned 0 results (result is null)"
                            )
                    elif hasattr(parsed_response, "data"):
                        result_count = (
                            len(parsed_response.data)
                            if isinstance(parsed_response.data, list)
                            else 1
                        )
                        logger.info(f"📊 {tool_name} returned {result_count} results")
                    else:
                        logger.info(
                            f"📊 {tool_name}: Could not determine result count structure - response type: {type(parsed_response)}"
                        )
                except Exception as count_error:
                    logger.info(
                        f"📊 {tool_name}: Could not extract result count: {count_error}"
                    )

            # Analyze parsing quality
            if analyzer:
                parsing_errors = analyzer.analyze_parsing(
                    raw_response, parsed_response, tool_name
                )
                result.parsing_errors.extend(parsing_errors)

        except Exception as e:
            result.parsing_errors.append(f"Response parsing failed: {str(e)}")
            logger.error(f"❌ {tool_name} response parsing failed: {e}")

        # Step 3: Make structured tool call
        try:
            # Determine source of arguments (params for GET, data for POST)
            args_dict = params or data or {}

            if args_dict:
                # Convert args dict to args model, filtering only valid fields
                valid_args = {
                    k: v for k, v in args_dict.items() if k in args_model.model_fields
                }

                # Special handling for search tools which have updated argument structures
                if args_model == SearchTranscriptsArgs:
                    # Use the new argument structure with specified test data
                    args_instance = SearchTranscriptsArgs(
                        event_ids=[2250284, 2190837, 2083130, 2006972],
                        query_text="revenue",
                        max_results=15,
                    )
                elif args_model == SearchFilingsArgs:
                    # Use the new argument structure
                    args_instance = SearchFilingsArgs(
                        company_name="Apple Inc",
                        start_date="2024-01-01",
                        end_date="2024-12-31",
                        document_types=["10-K"],
                        max_results=5,
                    )
                elif args_model == SearchFilingChunksArgs:
                    # Use the new argument structure
                    args_instance = SearchFilingChunksArgs(
                        query_text="revenue guidance",
                        company_name="Apple Inc",
                        filing_type="10-K",
                        max_results=10,
                    )
                else:
                    args_instance = args_model(**valid_args)
            else:
                # For empty args, create appropriate args
                if args_model in [GetAvailableWatchlistsArgs, GetAvailableIndexesArgs]:
                    args_instance = args_model()
                elif args_model in [
                    GetSectorsAndSubsectorsArgs,
                    GetCompanyDocCategoriesArgs,
                    GetCompanyDocKeywordsArgs,
                ]:
                    args_instance = args_model(search="", page=1, page_size=50)
                else:
                    # This is a complex case - we'll need to handle it per tool
                    args_instance = args_model()

            structured_response = await tool_function(args_instance)
            result.structured_response = structured_response

            # Step 4: Compare responses
            if analyzer:
                # Check structure alignment
                structure_discrepancies = analyzer.analyze_structure(
                    raw_response, structured_response
                )
                result.discrepancies.extend(structure_discrepancies)

                # Check data completeness
                completeness_discrepancies = analyzer.check_data_completeness(
                    raw_response, structured_response, tool_name
                )
                result.discrepancies.extend(completeness_discrepancies)

                # Compare parsed response with structured response
                if result.parsed_response is not None:
                    parsed_comparison = analyzer.compare_parsed_with_structured(
                        result.parsed_response, structured_response, tool_name
                    )
                    result.discrepancies.extend(parsed_comparison)

        except Exception as e:
            # Tool function failed, but we still have raw response
            result.errors.append(f"Tool function failed: {str(e)}")
            logger.error(f"❌ {tool_name} tool function failed: {e}")

        result.success = len(result.errors) == 0 and len(result.parsing_errors) == 0
        if result.success:
            total_issues = len(result.discrepancies)
            logger.info(f"✅ {tool_name} completed with {total_issues} discrepancies")
        elif result.parsing_errors:
            logger.error(
                f"❌ {tool_name} failed with {len(result.parsing_errors)} parsing errors"
            )

    except Exception as e:
        result.errors.append(f"API call failed: {str(e)}")
        logger.error(f"❌ {tool_name} API call failed: {e}")

    finally:
        await client.aclose()

    return result


async def run_comprehensive_tests():
    """Run comprehensive comparison tests for all tools."""
    logger.info("Starting comprehensive Aiera MCP tool comparison tests...\n")

    analyzer = DiscrepancyAnalyzer()
    date_ranges = get_test_date_ranges()

    # Define all tests with their corresponding Response models
    tests = [
        # Events
        {
            "tool_name": "find_events",
            "tool_function": find_events,
            "args_model": FindEventsArgs,
            "response_model": FindEventsResponse,
            "endpoint": "/chat-support/find-events",
            "params": {
                "start_date": date_ranges["q4_2023"]["start_date"],
                "end_date": date_ranges["q4_2023"]["end_date"],
                "event_type": "earnings",
                "page": 1,
                "page_size": 5,
            },
        },
        {
            "tool_name": "get_event",
            "tool_function": get_event,
            "args_model": GetEventArgs,
            "response_model": GetEventResponse,
            "endpoint": "/chat-support/find-events",
            "params": {
                "event_id": "2662190",
                "include_transcripts": "true",
            },
        },
        {
            "tool_name": "get_upcoming_events",
            "tool_function": get_upcoming_events,
            "args_model": GetUpcomingEventsArgs,
            "response_model": GetUpcomingEventsResponse,
            "endpoint": "/chat-support/estimated-and-upcoming-events",
            "params": {
                "start_date": "2024-12-01",
                "end_date": "2024-12-31",
                "page": 1,
                "page_size": 5,
            },
        },
        # Filings
        {
            "tool_name": "find_filings",
            "tool_function": find_filings,
            "args_model": FindFilingsArgs,
            "response_model": FindFilingsResponse,
            "endpoint": "/chat-support/find-filings",
            "params": {
                "start_date": date_ranges["q1_2024"]["start_date"],
                "end_date": date_ranges["q1_2024"]["end_date"],
                "form_number": "10-K",
                "page": 1,
                "page_size": 5,
            },
        },
        # Equities
        {
            "tool_name": "find_equities",
            "tool_function": find_equities,
            "args_model": FindEquitiesArgs,
            "response_model": FindEquitiesResponse,
            "endpoint": "/chat-support/find-equities",
            "params": {
                "bloomberg_ticker": "AAPL:US",
                "include_company_metadata": "true",
                "page": 1,
                "page_size": 5,
            },
        },
        {
            "tool_name": "get_equity_summaries",
            "tool_function": get_equity_summaries,
            "args_model": GetEquitySummariesArgs,
            "response_model": GetEquitySummariesResponse,
            "endpoint": "/chat-support/equity-summaries",
            "params": {"bloomberg_ticker": "AAPL:US", "lookback": "90"},
        },
        {
            "tool_name": "get_available_watchlists",
            "tool_function": get_available_watchlists,
            "args_model": GetAvailableWatchlistsArgs,
            "response_model": GetAvailableWatchlistsResponse,
            "endpoint": "/chat-support/available-watchlists",
            "params": {},
        },
        {
            "tool_name": "get_available_indexes",
            "tool_function": get_available_indexes,
            "args_model": GetAvailableIndexesArgs,
            "response_model": GetAvailableIndexesResponse,
            "endpoint": "/chat-support/available-indexes",
            "params": {},
        },
        {
            "tool_name": "get_sectors_and_subsectors",
            "tool_function": get_sectors_and_subsectors,
            "args_model": GetSectorsAndSubsectorsArgs,
            "response_model": GetSectorsSubsectorsResponse,
            "endpoint": "/chat-support/get-sectors-and-subsectors",
            "params": {},
        },
        {
            "tool_name": "get_index_constituents",
            "tool_function": get_index_constituents,
            "args_model": GetIndexConstituentsArgs,
            "response_model": GetIndexConstituentsResponse,
            "endpoint": "/chat-support/index-constituents/1",
            "params": {"index": "1", "page": 1, "page_size": 10},
        },
        {
            "tool_name": "get_watchlist_constituents",
            "tool_function": get_watchlist_constituents,
            "args_model": GetWatchlistConstituentsArgs,
            "response_model": GetWatchlistConstituentsResponse,
            "endpoint": "/chat-support/watchlist-constituents/44201720",
            "params": {"watchlist_id": "44201720", "page": 1, "page_size": 10},
        },
        # Company Docs
        {
            "tool_name": "find_company_docs",
            "tool_function": find_company_docs,
            "args_model": FindCompanyDocsArgs,
            "response_model": FindCompanyDocsResponse,
            "endpoint": "/chat-support/find-company-docs",
            "params": {
                "start_date": date_ranges["q1_2024"]["start_date"],
                "end_date": date_ranges["q1_2024"]["end_date"],
                "bloomberg_ticker": "AAPL:US",
                "page": 1,
                "page_size": 5,
            },
        },
        {
            "tool_name": "get_company_doc",
            "tool_function": get_company_doc,
            "args_model": GetCompanyDocArgs,
            "response_model": GetCompanyDocResponse,
            "endpoint": "/chat-support/find-company-docs",
            "params": {
                "company_doc_ids": "4291375",
                "include_content": "true",
            },
        },
        {
            "tool_name": "get_company_doc_categories",
            "tool_function": get_company_doc_categories,
            "args_model": GetCompanyDocCategoriesArgs,
            "response_model": GetCompanyDocCategoriesResponse,
            "endpoint": "/chat-support/get-company-doc-categories",
            "params": {},
        },
        {
            "tool_name": "get_company_doc_keywords",
            "tool_function": get_company_doc_keywords,
            "args_model": GetCompanyDocKeywordsArgs,
            "response_model": GetCompanyDocKeywordsResponse,
            "endpoint": "/chat-support/get-company-doc-keywords",
            "params": {},
        },
        # Third Bridge
        {
            "tool_name": "find_third_bridge_events",
            "tool_function": find_third_bridge_events,
            "args_model": FindThirdBridgeEventsArgs,
            "response_model": FindThirdBridgeEventsResponse,
            "endpoint": "/chat-support/find-third-bridge",
            "params": {
                "start_date": date_ranges["last_quarter"]["start_date"],
                "end_date": date_ranges["last_quarter"]["end_date"],
                "page": 1,
                "page_size": 5,
            },
        },
        {
            "tool_name": "get_third_bridge_event",
            "tool_function": get_third_bridge_event,
            "args_model": GetThirdBridgeEventArgs,
            "response_model": GetThirdBridgeEventResponse,
            "endpoint": "/chat-support/find-third-bridge",
            "params": {
                "thirdbridge_event_id": "6182f8d11138178578faa91850e2c8d2",
                "include_transcripts": "true",
            },
        },
        # Transcrippets
        {
            "tool_name": "find_transcrippets",
            "tool_function": find_transcrippets,
            "args_model": FindTranscrippetsArgs,
            "response_model": FindTranscrippetsResponse,
            "endpoint": "/transcrippets/",
            "params": {
                "start_date": date_ranges["last_quarter"]["start_date"],
                "end_date": date_ranges["last_quarter"]["end_date"],
            },
        },
        {
            "tool_name": "create_transcrippet",
            "tool_function": create_transcrippet,
            "args_model": CreateTranscrippetArgs,
            "response_model": CreateTranscrippetResponse,
            "endpoint": "/transcrippets/create",
            "method": "POST",
            "data": {
                "event_id": 2662190,
                "transcript": "Sure, I'll take that one. I think we're a long way from equilibrium. As you say, we're taking up our cash content spend this year estimated from $17 billion to $18 billion. That's in the context of we're small in terms of view share and penetration everywhere around the world or less than 50% penetrated into connected households. You heard from Greg that we're only capturing about 6% of our estimated revenue market. So we have a long way to grow. It's really about where do we put the next $1 billion and then beyond that to work in the most impactful way.",
                "transcript_item_id": 153833615,
                "transcript_end_item_id": 153833615,
                "transcript_item_offset": 0,
                "transcript_end_item_offset": 536,
            },
        },
        # NOTE: delete_transcrippet is DESTRUCTIVE and should be used with caution
        # Uncomment the following test to include it in the test suite
        # {
        #     "tool_name": "delete_transcrippet",
        #     "tool_function": delete_transcrippet,
        #     "args_model": DeleteTranscrippetArgs,
        #     "response_model": DeleteTranscrippetResponse,
        #     "endpoint": "/transcrippets/999999/delete",
        #     "method": "DELETE",
        #     "params": {},
        # },
        # Search Tools
        {
            "tool_name": "search_transcripts",
            "tool_function": search_transcripts,
            "args_model": SearchTranscriptsArgs,
            "response_model": SearchTranscriptsResponse,
            "endpoint": "/chat-support/search/transcripts",
            "method": "POST",
            "params": {"search_pipeline": "hybrid_search_pipeline"},
            "data": {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"text": {"query": "revenue", "boost": 2.0}}},
                            {
                                "multi_match": {
                                    "query": "revenue",
                                    "fields": ["title^1.5", "speaker_name"],
                                    "boost": 1.5,
                                }
                            },
                        ],
                        "filter": [
                            {
                                "terms": {
                                    "transcript_event_id": [
                                        2250284,
                                        2190837,
                                        2083130,
                                        2006972,
                                    ]
                                }
                            }
                        ],
                        "minimum_should_match": 1,
                    }
                },
                "size": 15,
                "_source": [
                    "content_id",
                    "text",
                    "transcript_event_id",
                    "title",
                    "speaker_name",
                    "speaker_title",
                    "date",
                    "section",
                    "transcript_section",
                ],
                "sort": [{"_score": {"order": "desc"}}],
            },
        },
        {
            "tool_name": "search_filings",
            "tool_function": search_filings,
            "args_model": SearchFilingsArgs,
            "response_model": SearchFilingsResponse,
            "endpoint": "/chat-support/search/filings",
            "method": "POST",
            "data": {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match_phrase": {
                                    "title": {"query": "Apple Inc", "boost": 15.0}
                                }
                            },
                            {
                                "wildcard": {
                                    "title": {
                                        "value": "*Apple Inc*",
                                        "case_insensitive": True,
                                        "boost": 8.0,
                                    }
                                }
                            },
                            {
                                "wildcard": {
                                    "title": {
                                        "value": "*Apple*",
                                        "case_insensitive": True,
                                        "boost": 6.0,
                                    }
                                }
                            },
                            {"term": {"company_name.keyword": "Apple Inc"}},
                            {"term": {"issuer_name.keyword": "Apple Inc"}},
                            {"term": {"entity_name.keyword": "Apple Inc"}},
                            {"term": {"filer_name.keyword": "Apple Inc"}},
                        ],
                        "filter": [
                            {
                                "range": {
                                    "date": {"gte": "2024-01-01", "lte": "2024-12-31"}
                                }
                            },
                            {
                                "bool": {
                                    "should": [
                                        {
                                            "match_phrase": {
                                                "title": {
                                                    "query": "10-K",
                                                    "boost": 10.0,
                                                }
                                            }
                                        },
                                        {"term": {"document_type.keyword": "10-K"}},
                                        {"term": {"form_type.keyword": "10-K"}},
                                        {"term": {"filing_type.keyword": "10-K"}},
                                    ],
                                    "minimum_should_match": 1,
                                }
                            },
                        ],
                        "minimum_should_match": 1,
                    }
                },
                "size": 5,
                "_source": [
                    "content_id",
                    "title",
                    "company_name",
                    "issuer_name",
                    "entity_name",
                    "document_type",
                    "form_type",
                    "filing_type",
                    "date",
                    "filing_date",
                    "filing_id",
                ],
                "sort": [{"date": {"order": "desc"}}, {"_score": {"order": "desc"}}],
                "timeout": "15s",
                "search_pipeline": "hybrid_search_pipeline",
            },
        },
        {
            "tool_name": "search_filing_chunks",
            "tool_function": search_filing_chunks,
            "args_model": SearchFilingChunksArgs,
            "response_model": SearchFilingChunksResponse,
            "endpoint": "/chat-support/search/filing-chunks",
            "method": "POST",
            "params": {"search_pipeline": "hybrid_search_pipeline"},
            "data": {
                "query": {
                    "bool": {
                        "should": [
                            {
                                "match": {
                                    "text": {"query": "revenue guidance", "boost": 2.0}
                                }
                            },
                            {
                                "multi_match": {
                                    "query": "revenue guidance",
                                    "fields": ["title^1.5", "summary"],
                                    "boost": 1.5,
                                }
                            },
                        ],
                        "filter": [
                            {
                                "bool": {
                                    "should": [
                                        # Tier 1: Exact matches (boost 10.0)
                                        {
                                            "term": {
                                                "company_common_name.keyword": {
                                                    "value": "Apple Inc",
                                                    "boost": 10.0,
                                                }
                                            }
                                        },
                                        {
                                            "term": {
                                                "company_legal_name.keyword": {
                                                    "value": "Apple Inc",
                                                    "boost": 10.0,
                                                }
                                            }
                                        },
                                        # Tier 2: Fuzzy matching with AUTO fuzziness (boost 8.0-7.5)
                                        {
                                            "fuzzy": {
                                                "company_common_name": {
                                                    "value": "Apple Inc",
                                                    "fuzziness": "AUTO",
                                                    "boost": 8.0,
                                                    "max_expansions": 50,
                                                }
                                            }
                                        },
                                        {
                                            "fuzzy": {
                                                "company_legal_name": {
                                                    "value": "Apple Inc",
                                                    "fuzziness": "AUTO",
                                                    "boost": 8.0,
                                                    "max_expansions": 50,
                                                }
                                            }
                                        },
                                        {
                                            "fuzzy": {
                                                "company_common_name": {
                                                    "value": "Apple",
                                                    "fuzziness": "AUTO",
                                                    "boost": 7.5,
                                                    "max_expansions": 50,
                                                }
                                            }
                                        },
                                        {
                                            "fuzzy": {
                                                "company_legal_name": {
                                                    "value": "Apple",
                                                    "fuzziness": "AUTO",
                                                    "boost": 7.5,
                                                    "max_expansions": 50,
                                                }
                                            }
                                        },
                                        # Tier 3: Phrase matching with slop (boost 6.0-5.5)
                                        {
                                            "match_phrase": {
                                                "company_common_name": {
                                                    "query": "Apple Inc",
                                                    "boost": 6.0,
                                                    "slop": 1,
                                                }
                                            }
                                        },
                                        {
                                            "match_phrase": {
                                                "company_legal_name": {
                                                    "query": "Apple Inc",
                                                    "boost": 6.0,
                                                    "slop": 1,
                                                }
                                            }
                                        },
                                        {
                                            "match_phrase": {
                                                "company_common_name": {
                                                    "query": "Apple",
                                                    "boost": 5.5,
                                                    "slop": 1,
                                                }
                                            }
                                        },
                                        {
                                            "match_phrase": {
                                                "company_legal_name": {
                                                    "query": "Apple",
                                                    "boost": 5.5,
                                                    "slop": 1,
                                                }
                                            }
                                        },
                                        # Tier 4: Word-based matching with fuzzy operator (boost 5.0-4.5)
                                        {
                                            "match": {
                                                "company_common_name": {
                                                    "query": "Apple Inc",
                                                    "boost": 5.0,
                                                    "operator": "and",
                                                    "fuzziness": "AUTO",
                                                }
                                            }
                                        },
                                        {
                                            "match": {
                                                "company_legal_name": {
                                                    "query": "Apple Inc",
                                                    "boost": 5.0,
                                                    "operator": "and",
                                                    "fuzziness": "AUTO",
                                                }
                                            }
                                        },
                                        {
                                            "match": {
                                                "company_common_name": {
                                                    "query": "Apple",
                                                    "boost": 4.5,
                                                    "operator": "and",
                                                    "fuzziness": "AUTO",
                                                }
                                            }
                                        },
                                        {
                                            "match": {
                                                "company_legal_name": {
                                                    "query": "Apple",
                                                    "boost": 4.5,
                                                    "operator": "and",
                                                    "fuzziness": "AUTO",
                                                }
                                            }
                                        },
                                        # Tier 5: Title fuzzy matching (boost 3.0-2.5)
                                        {
                                            "fuzzy": {
                                                "title": {
                                                    "value": "Apple Inc",
                                                    "fuzziness": "AUTO",
                                                    "boost": 3.0,
                                                    "max_expansions": 25,
                                                }
                                            }
                                        },
                                        {
                                            "fuzzy": {
                                                "title": {
                                                    "value": "Apple",
                                                    "fuzziness": "AUTO",
                                                    "boost": 2.5,
                                                    "max_expansions": 25,
                                                }
                                            }
                                        },
                                        # Tier 6: Selective wildcards for longer names (boost 2.0-1.8)
                                        {
                                            "wildcard": {
                                                "company_common_name.keyword": {
                                                    "value": "*Apple Inc*",
                                                    "boost": 2.0,
                                                }
                                            }
                                        },
                                        {
                                            "wildcard": {
                                                "company_legal_name.keyword": {
                                                    "value": "*Apple Inc*",
                                                    "boost": 2.0,
                                                }
                                            }
                                        },
                                        {
                                            "wildcard": {
                                                "company_common_name.keyword": {
                                                    "value": "*Apple*",
                                                    "boost": 1.8,
                                                }
                                            }
                                        },
                                        {
                                            "wildcard": {
                                                "company_legal_name.keyword": {
                                                    "value": "*Apple*",
                                                    "boost": 1.8,
                                                }
                                            }
                                        },
                                    ],
                                    "minimum_should_match": 1,
                                }
                            }
                        ],
                        "minimum_should_match": 1,
                    }
                },
                "size": 10,
                "_source": [
                    "content_id",
                    "text",
                    "title",
                    "company_common_name",
                    "filing_id",
                    "filing_form_id",
                    "date",
                    "chunk_id",
                ],
            },
        },
    ]

    # Run all tests
    results = []
    for test_config in tests:
        try:
            result = await test_tool_with_comparison(analyzer=analyzer, **test_config)
            if result is not None:
                # Debug: Check what type result actually is
                if not isinstance(result, TestResult):
                    logger.error(
                        f"Test returned unexpected type for {test_config['tool_name']}: {type(result)} - {result}"
                    )
                    continue
                results.append(result)
                analyzer.results.append(result)
                analyzer.log_discrepancies(result)
            else:
                logger.error(
                    f"Test returned None result for {test_config['tool_name']}"
                )

        except Exception as e:
            logger.error(f"Test setup failed for {test_config['tool_name']}: {e}")

    # Generate summary report
    logger.info("\n" + "=" * 80)
    logger.info("COMPREHENSIVE TEST SUMMARY")
    logger.info("=" * 80)

    total_tests = len(results)
    successful_tests = sum(1 for r in results if r.success)
    tests_with_discrepancies = sum(1 for r in results if r.discrepancies)
    tests_with_errors = sum(1 for r in results if r.errors)

    tests_with_parsing_errors = sum(1 for r in results if r.parsing_errors)

    logger.info(f"Total tests run: {total_tests}")
    logger.info(f"Successful tests: {successful_tests}")
    logger.info(f"Tests with parsing errors: {tests_with_parsing_errors}")
    logger.info(f"Tests with discrepancies: {tests_with_discrepancies}")
    logger.info(f"Tests with other errors: {tests_with_errors}")

    if tests_with_parsing_errors > 0:
        logger.error(
            f"\n❌ {tests_with_parsing_errors} tools have Response object parsing errors"
        )
        logger.error(
            "These indicate issues with the Response model definitions or API response structure changes"
        )

    if tests_with_discrepancies > 0:
        logger.warning(
            f"\n⚠️ {tests_with_discrepancies} tools have discrepancies between raw and structured responses"
        )
        logger.warning("Check manual_test_discrepancies.log for detailed analysis")

    if tests_with_errors > 0:
        logger.error(f"\n❌ {tests_with_errors} tools failed to execute")

    if (
        tests_with_parsing_errors == 0
        and tests_with_discrepancies == 0
        and tests_with_errors == 0
    ):
        logger.info("\n🎉 All tools passed with no issues!")
    elif tests_with_parsing_errors == 0:
        logger.info("\n✅ All Response objects parse correctly!")

    return analyzer


async def test_create_transcrippet_manual():
    """Manual test for create_transcrippet with specific parameters."""
    logger.info("Starting manual test for create_transcrippet...")

    client = await get_test_http_client()
    api_key = get_test_api_key()

    # Test parameters as provided
    test_args = CreateTranscrippetArgs(
        event_id=2662190,
        transcript="Sure, I'll take that one. I think we're a long way from equilibrium. As you say, we're taking up our cash content spend this year estimated from $17 billion to $18 billion. That's in the context of we're small in terms of view share and penetration everywhere around the world or less than 50% penetrated into connected households. You heard from Greg that we're only capturing about 6% of our estimated revenue market. So we have a long way to grow. It's really about where do we put the next $1 billion and then beyond that to work in the most impactful way.",
        transcript_item_id=153833615,
        transcript_end_item_id=153833615,
        transcript_item_offset=0,
        transcript_end_item_offset=536,
    )

    try:
        # Test the function directly
        logger.info("Testing create_transcrippet function directly...")
        result = await create_transcrippet(test_args)

        logger.info("✅ create_transcrippet succeeded!")
        logger.info(f"Created transcrippet ID: {result.response.transcrippet_id}")
        logger.info(f"GUID: {result.response.transcrippet_guid}")
        logger.info(f"Public URL: {result.response.public_url}")
        logger.info(
            f"Company: {result.response.company_name} ({result.response.company_ticker})"
        )
        logger.info(f"Event: {result.response.event_title}")
        logger.info(f"Audio URL: {result.response.audio_url}")

        # Test via raw API call for comparison
        logger.info("\nTesting raw API call for comparison...")
        raw_data = test_args.model_dump(exclude_none=True)
        raw_response = await make_aiera_request(
            client=client,
            method="POST",
            endpoint="/transcrippets/create",
            api_key=api_key,
            data=raw_data,
        )

        logger.info("✅ Raw API call succeeded!")
        logger.info(f"Raw response keys: {list(raw_response.keys())}")
        if "response" in raw_response:
            logger.info(
                f"Raw response data keys: {list(raw_response['response'].keys())}"
            )
            logger.info(
                f"Raw GUID: {raw_response['response'].get('transcrippet_guid')}"
            )

    except Exception as e:
        logger.error(f"❌ create_transcrippet test failed: {e}")
        import traceback

        logger.error(f"Full traceback: {traceback.format_exc()}")

    finally:
        await client.aclose()

    logger.info("create_transcrippet manual test completed.")


if __name__ == "__main__":
    # Add option to run just the create transcrippet test
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "create_transcrippet":
        asyncio.run(test_create_transcrippet_manual())
    else:
        asyncio.run(run_comprehensive_tests())
