#!/bin/bash

# Integration Test Runner Script
# Runs integration tests individually to avoid event loop conflicts

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Show help if requested
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    cat << EOF
🧪 Aiera MCP Integration Test Runner

USAGE:
    ./scripts/run_integration_tests.sh [OPTIONS]

OPTIONS:
    -h, --help      Show this help message
    -e, --extended  Run extended test suite (includes additional tests)

EXAMPLES:
    ./scripts/run_integration_tests.sh                    # Run core tests (9 tests)
    ./scripts/run_integration_tests.sh --extended         # Run extended suite (21 tests)

SETUP:
    Set your API key in a .env file:
    echo "export AIERA_API_KEY=your_api_key_here" > .env

REQUIREMENTS:
    - Valid Aiera API key
    - uv installed (Python package manager)
    - Internet connection

For detailed documentation, see INTEGRATION_TESTING.md
EOF
    exit 0
fi

echo -e "${BLUE}🧪 Aiera MCP Integration Test Runner${NC}"
echo "========================================="

# Check if API key is set
if [ -f ".env" ]; then
    echo -e "${YELLOW}📁 Loading API key from .env file...${NC}"
    source .env
fi

if [ -z "$AIERA_API_KEY" ]; then
    echo -e "${RED}❌ ERROR: AIERA_API_KEY not set${NC}"
    echo "Please set your API key:"
    echo "  export AIERA_API_KEY=your_api_key_here"
    echo "Or create a .env file with:"
    echo "  echo 'export AIERA_API_KEY=your_api_key_here' > .env"
    exit 1
fi

echo -e "${GREEN}✅ API key loaded (${AIERA_API_KEY:0:8}...${AIERA_API_KEY: -4})${NC}"
echo ""

# Function to run a single test
run_test() {
    local test_path="$1"
    local test_name="$2"

    echo -e "${BLUE}🔄 Running: ${test_name}${NC}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    # Get start time
    local start_time=$(date +%s)

    # Run the test and capture output
    if output=$(uv run pytest "$test_path" -v --no-header --tb=short 2>&1); then
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        if echo "$output" | grep -q "PASSED"; then
            echo -e "${GREEN}✅ PASSED: ${test_name} ${BLUE}(${duration}s)${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        elif echo "$output" | grep -q "SKIPPED"; then
            echo -e "${YELLOW}⏭️  SKIPPED: ${test_name} ${BLUE}(${duration}s)${NC}"
            local skip_reason=$(echo "$output" | grep -o "SKIPPED.*" | head -1 | cut -c1-80)
            echo -e "   ${YELLOW}Reason: ${skip_reason}${NC}"
            SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
        else
            echo -e "${RED}❌ UNKNOWN: ${test_name} ${BLUE}(${duration}s)${NC}"
            echo "$output"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))

        echo -e "${RED}❌ FAILED: ${test_name} ${BLUE}(${duration}s)${NC}"

        # Extract and show the most relevant error information
        if echo "$output" | grep -q "FAILURES"; then
            echo -e "${RED}   Error Details:${NC}"
            # Show the actual assertion error or exception
            local error_info=$(echo "$output" | sed -n '/FAILURES/,/short test summary/p' | head -15 | tail -n +2)
            echo "$error_info" | while IFS= read -r line; do
                if [[ $line =~ ^[[:space:]]*E[[:space:]] ]]; then
                    echo -e "   ${RED}${line}${NC}"
                elif [[ $line =~ ^[[:space:]]*\> ]]; then
                    echo -e "   ${BLUE}${line}${NC}"
                else
                    echo -e "   ${line}"
                fi
            done
        else
            # Show last few lines if no FAILURES section
            echo -e "${RED}   Error Output:${NC}"
            echo "$output" | tail -8 | while IFS= read -r line; do
                echo -e "   ${line}"
            done
        fi

        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    echo ""
    sleep 1  # Brief pause between tests to avoid rate limiting
}

# Core integration tests - most reliable
echo -e "${BLUE}📊 Running Core API Tests${NC}"
echo "========================"

# Events API tests
run_test "tests/integration/test_events_integration.py::TestEventsIntegration::test_find_events_with_ticker_filter" "Events: Find with ticker filter"
run_test "tests/integration/test_events_integration.py::TestEventsIntegration::test_get_upcoming_events_real_api" "Events: Get upcoming events"

# Filings API tests
run_test "tests/integration/test_filings_integration.py::TestFilingsIntegration::test_find_filings_real_api" "Filings: Find filings"
run_test "tests/integration/test_filings_integration.py::TestFilingsIntegration::test_find_filings_different_form_types" "Filings: Different form types"

# Transcrippets API tests
run_test "tests/integration/test_transcrippets_integration.py::TestTranscrippetsIntegration::test_find_transcrippets_real_api" "Transcrippets: Find transcrippets"
run_test "tests/integration/test_transcrippets_integration.py::TestTranscrippetsIntegration::test_find_transcrippets_with_ticker_filter" "Transcrippets: With ticker filter"

# Additional tests if requested
if [ "$1" == "--extended" ] || [ "$1" == "-e" ]; then
    echo -e "${BLUE}🔍 Running Extended Tests${NC}"
    echo "========================="

    # More Events tests
    run_test "tests/integration/test_events_integration.py::TestEventsIntegration::test_events_pagination_integration" "Events: Pagination"
    run_test "tests/integration/test_events_integration.py::TestEventsIntegration::test_events_different_types_integration" "Events: Different types"
    run_test "tests/integration/test_events_integration.py::TestEventsIntegration::test_get_event_real_api" "Events: Get event details"

    # More Filings tests
    run_test "tests/integration/test_filings_integration.py::TestFilingsIntegration::test_filings_pagination_integration" "Filings: Pagination"
    run_test "tests/integration/test_filings_integration.py::TestFilingsIntegration::test_filings_citations_integration" "Filings: Citations"
    run_test "tests/integration/test_filings_integration.py::TestFilingsIntegration::test_find_filings_with_ticker_filter" "Filings: With ticker filter"

    # More Transcrippets tests
    run_test "tests/integration/test_transcrippets_integration.py::TestTranscrippetsIntegration::test_find_transcrippets_with_search" "Transcrippets: With search"
    run_test "tests/integration/test_transcrippets_integration.py::TestTranscrippetsIntegration::test_transcrippets_citations_integration" "Transcrippets: Citations"
    run_test "tests/integration/test_transcrippets_integration.py::TestTranscrippetsIntegration::test_transcrippets_public_url_format" "Transcrippets: URL format"

    # Company docs tests
    run_test "tests/integration/test_company_docs_integration.py::TestCompanyDocsIntegration::test_company_docs_citations_integration" "Company Docs: Citations"
    run_test "tests/integration/test_company_docs_integration.py::TestCompanyDocsIntegration::test_find_company_docs_with_search" "Company Docs: With search"

    # Equities tests
    run_test "tests/integration/test_equities_integration.py::TestEquitiesIntegration::test_equities_api_error_handling" "Equities: Error handling"
fi

# Error handling tests - these should work regardless of data
echo -e "${BLUE}🛡️  Running Error Handling Tests${NC}"
echo "================================="

run_test "tests/integration/test_events_integration.py::TestEventsIntegration::test_events_api_error_handling" "Events: Error handling"
run_test "tests/integration/test_filings_integration.py::TestFilingsIntegration::test_get_filing_invalid_id" "Filings: Invalid ID handling"
run_test "tests/integration/test_transcrippets_integration.py::TestTranscrippetsIntegration::test_transcrippets_api_error_handling" "Transcrippets: Error handling"

# Summary
echo ""
echo -e "${BLUE}📈 Test Summary${NC}"
echo "==============="
echo -e "Total Tests:   ${TOTAL_TESTS}"
echo -e "Passed:        ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed:        ${RED}${FAILED_TESTS}${NC}"
echo -e "Skipped:       ${YELLOW}${SKIPPED_TESTS}${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}💥 Some tests failed. Check the output above for details.${NC}"
    echo ""
    echo "💡 Troubleshooting tips:"
    echo "   • Verify your API key is valid and has proper permissions"
    echo "   • Check your internet connection"
    echo "   • Some tests may fail if the API has no data for the test parameters"
    echo "   • 504 timeouts may indicate API server load - try again later"
    exit 1
fi
