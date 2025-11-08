# Integration Testing Guide

This document provides guidance for running integration tests against the real Aiera API.

## Setup

1. **API Key**: Set your Aiera API key in the environment:
   ```bash
   export AIERA_API_KEY=your_api_key_here
   ```
   Or create a `.env` file:
   ```bash
   echo "export AIERA_API_KEY=your_api_key_here" > .env
   source .env
   ```

2. **Dependencies**: Install test dependencies:
   ```bash
   uv sync --dev
   ```

## Running Integration Tests

### Using the Test Runner Script (Recommended)

The easiest way to run integration tests is using the provided script:

```bash
# Run core integration tests (9 essential tests)
./scripts/run_integration_tests.sh

# Run extended test suite (includes additional tests)
./scripts/run_integration_tests.sh --extended
```

The script automatically:
- ✅ Loads API key from `.env` file
- ✅ Runs tests individually to avoid event loop conflicts
- ✅ Provides colored output with clear pass/fail status
- ✅ Shows execution timing for each test
- ✅ Enhanced error reporting with detailed failure information
- ✅ Includes rate limiting between tests (1s pause)
- ✅ Shows summary statistics with pass/fail/skip counts
- ✅ Provides troubleshooting tips on failures

### Individual Tests (Manual)

Due to pytest-asyncio event loop lifecycle limitations, running multiple integration tests in the same session may cause event loop closure errors. **Run tests individually for best results:**

```bash
# Individual test examples
source .env && uv run pytest tests/integration/test_events_integration.py::TestEventsIntegration::test_find_events_real_api -v
source .env && uv run pytest tests/integration/test_filings_integration.py::TestFilingsIntegration::test_find_filings_real_api -v
source .env && uv run pytest tests/integration/test_transcrippets_integration.py::TestTranscrippetsIntegration::test_find_transcrippets_real_api -v
```

### Test Categories

```bash
# Run all events integration tests (one at a time)
source .env && uv run pytest tests/integration/test_events_integration.py -k "test_find_events_real_api" -v

# Run all filings integration tests (one at a time)
source .env && uv run pytest tests/integration/test_filings_integration.py -k "test_find_filings_real_api" -v

# Run all transcrippets integration tests (one at a time)
source .env && uv run pytest tests/integration/test_transcrippets_integration.py -k "test_find_transcrippets_real_api" -v
```

## Known Issues

### Event Loop Closure Errors

**Problem**: When running multiple integration tests in the same pytest session, you may encounter:
```
RuntimeError: Event loop is closed
```

**Root Cause**: This is a known issue with pytest-asyncio and httpx/httpcore when multiple async tests share HTTP client connections. The event loop gets closed during test cleanup while HTTP connections are still being closed.

**Workaround**: Run integration tests individually rather than in batches.

**Status**: Tests work perfectly when run individually. This is a testing infrastructure limitation, not a problem with the actual MCP tools.

## Test Structure

Integration tests are organized by API category:

- `test_events_integration.py` - Events API tests
- `test_filings_integration.py` - SEC filings API tests
- `test_transcrippets_integration.py` - Transcrippets API tests
- `test_equities_integration.py` - Equities and sectors API tests
- `test_company_docs_integration.py` - Company documents API tests
- `test_third_bridge_integration.py` - Third Bridge events API tests

## Rate Limiting

Integration tests include automatic rate limiting (1 request per second) to avoid hitting API limits. Tests will automatically pause between API calls.

## Test Data

Tests use realistic date ranges and ticker symbols that should have data available:

- **Tickers**: AAPL:US, MSFT:US, GOOGL:US, TSLA:US, AMZN:US
- **Date Ranges**: Q3/Q4 2023 earnings seasons, Q1 2024
- **Form Types**: 10-K, 10-Q, 8-K for SEC filings

## Timeout Configuration

Integration tests use extended timeouts to handle API latency:
- **Connection timeout**: 10 seconds
- **Read timeout**: 60 seconds
- **Total timeout**: 60 seconds

This resolves the 504 Gateway Timeout errors that were occurring with shorter timeout values.

## Success Criteria

A successful integration test run should:
1. ✅ Connect to the Aiera API with valid authentication
2. ✅ Receive 200 OK responses (not 504 timeouts)
3. ✅ Parse response data into proper Pydantic models
4. ✅ Generate valid citations with public URLs where applicable
5. ✅ Handle edge cases like empty results gracefully

## Troubleshooting

### 504 Gateway Timeout
- **Solution**: Timeout values have been increased to 60 seconds
- **Status**: Resolved in recent updates

### Field Mapping Issues
- **Example**: `title=None` in transcrippets
- **Solution**: Tests now accept either `title` or `event_title` as valid
- **Status**: Resolved for known cases

### Event Loop Errors
- **Solution**: Run tests individually
- **Status**: Known limitation, documented above