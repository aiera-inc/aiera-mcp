# Aiera MCP Test Suite

This directory contains comprehensive unit and integration tests for all Aiera MCP tools.

## 📁 Directory Structure

```
tests/
├── conftest.py                    # Global test configuration and fixtures
├── fixtures/                     # Test data and API response samples
│   └── api_responses.json        # Sample API responses for testing
├── unit/                         # Unit tests with mocked dependencies
│   ├── conftest.py              # Unit test specific fixtures
│   ├── test_events/             # Events domain tests
│   ├── test_filings/            # SEC filings tests
│   ├── test_equities/           # Equities and company metadata tests
│   ├── test_company_docs/       # Company documents tests
│   ├── test_third_bridge/       # Third Bridge expert events tests
│   └── test_transcrippets/      # Transcrippets tests
├── integration/                  # Integration tests with real API
│   ├── conftest.py              # Integration test fixtures
│   ├── test_events_integration.py
│   ├── test_filings_integration.py
│   ├── test_equities_integration.py
│   ├── test_company_docs_integration.py
│   ├── test_third_bridge_integration.py
│   └── test_transcrippets_integration.py
└── README.md                    # This file
```

## 🏷️ Test Categories

### Unit Tests (`@pytest.mark.unit`)
- **Fast execution** (< 1 second per test)
- **Mocked dependencies** (no real API calls)
- **Comprehensive coverage** of all code paths
- **Model validation** and edge cases
- **Error handling** scenarios

### Integration Tests (`@pytest.mark.integration`)
- **Real API calls** to Aiera endpoints
- **Requires valid API key** via `AIERA_API_KEY` environment variable
- **Rate limited** to avoid API quota issues
- **End-to-end testing** of tool functionality
- **Marked as slow** (`@pytest.mark.slow`)

### Model Tests
- **Pydantic model validation**
- **Field serialization/deserialization**
- **JSON schema generation**
- **Type validation and error handling**

### Tool Tests
- **Function behavior testing**
- **API request/response handling**
- **Data transformation logic**
- **Citation generation**

## 🚀 Running Tests

### Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and virtual environments.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies and set up virtual environment
uv sync

# Install development dependencies
uv add --dev pytest pytest-asyncio pytest-cov pytest-xdist pytest-httpx
```

### Quick Start (with uv)

```bash
# Run all tests (unit only, no API key needed)
make test-unit

# Run with coverage
make test-coverage

# Run specific domain
make test-domain DOMAIN=events

# Run integration tests (using .env file - recommended)
source .env && make test-integration

# Or run integration tests (with inline API key)
make test-integration AIERA_API_KEY=your-api-key
```

### Using Test Runner Script with uv

```bash
# All unit tests
uv run python scripts/run_tests.py --type=unit --verbose

# Integration tests (using .env file - recommended)
source .env && uv run python scripts/run_tests.py --type=integration

# Or integration tests (with inline API key)
AIERA_API_KEY=your-key uv run python scripts/run_tests.py --type=integration

# Specific domain
uv run python scripts/run_tests.py --domain=events --verbose

# Fast tests only
uv run python scripts/run_tests.py --type=fast

# With coverage
uv run python scripts/run_tests.py --coverage

# Parallel execution (faster)
uv run python scripts/run_tests.py --type=unit --parallel=4
```

### Direct Pytest Usage with uv

```bash
# Unit tests only
uv run pytest tests/unit -v

# Integration tests (with API key)
AIERA_API_KEY=your-key uv run pytest tests/integration -v

# Specific test file
uv run pytest tests/unit/test_events/test_tools.py -v

# Specific test function
uv run pytest tests/unit/test_events/test_tools.py::TestFindEvents::test_find_events_success -v

# With markers
uv run pytest -m "unit and not slow" -v
uv run pytest -m "integration and requires_api_key" -v

# Run tests with coverage
uv run pytest tests/unit --cov=aiera_mcp --cov-report=html -v

# Parallel execution for faster testing
uv run pytest tests/unit -n auto -v
```

### Alternative: Traditional pip/venv

If you prefer not to use uv:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .

# Run tests
python scripts/run_tests.py --type=unit --verbose
pytest tests/unit -v
```

## 🔧 Test Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AIERA_API_KEY` | Valid Aiera API key | Integration tests only |
| `RUN_EXPENSIVE_TESTS` | Enable expensive/slow tests | Optional |

#### Using .env File (Recommended)

The easiest way to provide your API key is via a `.env` file in the project root:

```bash
# Create .env file with your API key
echo "export AIERA_API_KEY=your-api-key-here" > .env

# Run integration tests using the .env file
source .env && make test-integration

# Or use the provided script
./run_integration_tests.sh
```

### Pytest Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.unit` | Unit tests (mocked) |
| `@pytest.mark.integration` | Integration tests (real API) |
| `@pytest.mark.requires_api_key` | Requires valid API key |
| `@pytest.mark.slow` | Slow-running tests |

### Configuration File

See `pytest.ini` for global configuration:
- Async mode enabled
- Test discovery patterns
- Marker definitions
- Warning filters

## 🧪 Test Patterns

### Unit Test Pattern

```python
@pytest.mark.unit
class TestToolName:
    @pytest.mark.asyncio
    async def test_success_case(self, mock_http_dependencies, api_responses):
        """Test successful API response handling."""
        # Setup mock
        mock_http_dependencies['mock_make_request'].return_value = api_responses["success"]

        # Execute
        result = await tool_function(args)

        # Verify
        assert isinstance(result, ExpectedResponseType)
        assert result.field == expected_value
```

### Integration Test Pattern

```python
@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
class TestToolNameIntegration:
    @pytest.mark.asyncio
    async def test_real_api(self, integration_mcp_server, real_http_client, real_api_key, api_rate_limiter):
        """Test with real API."""
        await api_rate_limiter.wait()

        with patch('tool.module.mcp', integration_mcp_server), \
             patch('tool.module.get_http_client', return_value=real_http_client), \
             patch('tool.module.get_api_key', return_value=real_api_key):

            result = await tool_function(args)
            assert isinstance(result, ExpectedType)
```

## 📊 Coverage

Run tests with coverage reporting:

```bash
# Generate HTML coverage report
make test-coverage

# View coverage report
open htmlcov/index.html
```

Coverage targets:
- **Unit tests**: >95% code coverage
- **Integration tests**: End-to-end functionality validation
- **Models**: 100% validation coverage

## 🔄 Continuous Integration

### GitHub Actions

The project uses GitHub Actions for CI/CD:

- **Lint checks**: Code style, type checking, security scanning
- **Unit tests**: Run on multiple Python versions (3.9-3.12)
- **Integration tests**: Run on main branch pushes (when API key available)
- **Matrix testing**: Domain-specific test execution
- **Performance tests**: Benchmark slow operations

### Local Pre-commit

Set up pre-commit hooks:

```bash
pre-commit install
```

This will run linting and formatting checks before each commit.

## 🧩 Domain-Specific Testing

### Events Domain
- **3 tools**: find_events, get_event, get_upcoming_events
- **Key features**: Event type validation, date parsing, transcript sections
- **API patterns**: Standard pagination, field mapping (event_id → event_ids)

### Filings Domain
- **2 tools**: find_filings, get_filing
- **Key features**: SEC form types, amendment flags, content inclusion
- **API patterns**: Field mapping (filing_id → filing_ids)

### Equities Domain
- **7 tools**: Comprehensive equity data retrieval
- **Key features**: Market data, sectors/subsectors, indexes, watchlists
- **API patterns**: Complex data structures, multiple ID types

### Company Docs Domain
- **4 tools**: Document search and metadata
- **Key features**: Categories, keywords, search functionality
- **API patterns**: Standard CRUD operations

### Third Bridge Domain
- **2 tools**: Expert insight events
- **Key features**: Expert information, specialized event data
- **API patterns**: May have sparse data availability

### Transcrippets Domain
- **3 tools**: Create, read, delete transcript clips
- **Key features**: Public URL generation, GUID handling
- **API patterns**: Different response format (array vs response.data)

## 🛠️ Fixtures and Test Data

### Global Fixtures (`conftest.py`)

- `mock_mcp_context`: Mock MCP context
- `mock_http_client`: Mock HTTP client
- `sample_api_responses`: Sample API responses from fixtures
- `api_response_builder`: Helper for building test responses

### Unit Test Fixtures (`unit/conftest.py`)

- `mock_http_dependencies`: Complete HTTP mocking setup
- `mock_server_import`: Mock server imports
- Domain-specific response fixtures

### Integration Test Fixtures (`integration/conftest.py`)

- `real_api_key`: Validates API key availability
- `real_http_client`: Real HTTP client with timeouts
- `api_rate_limiter`: Rate limiting for API calls
- `sample_tickers`: Common tickers for testing

### Test Data (`fixtures/api_responses.json`)

Sample API responses for all domains:
- Success responses with realistic data
- Error responses for various scenarios
- Edge cases and data variations

## 🚨 Troubleshooting

### Common Issues

1. **API Key Missing**
   ```
   Solution: Set AIERA_API_KEY environment variable
   export AIERA_API_KEY=your-api-key-here
   ```

2. **Rate Limiting**
   ```
   Solution: Tests include automatic rate limiting
   Adjust api_rate_limiter in integration tests if needed
   ```

3. **Import Errors**
   ```
   Solution: Install in development mode
   pip install -e .
   ```

4. **Async Test Issues**
   ```
   Solution: Ensure pytest-asyncio is installed and asyncio_mode = auto in pytest.ini
   ```

### Running Subset of Tests

With uv:
```bash
# Only model tests
uv run pytest -k "test_models" -v

# Only successful cases
uv run pytest -k "success" -v

# Exclude slow tests
uv run pytest -m "not slow" -v

# Specific domain integration
uv run pytest tests/integration/test_events_integration.py -v

# Run tests in parallel for speed
uv run pytest tests/unit -n auto -v
```

Without uv:
```bash
# Only model tests
pytest -k "test_models" -v

# Only successful cases
pytest -k "success" -v

# Exclude slow tests
pytest -m "not slow" -v

# Specific domain integration
pytest tests/integration/test_events_integration.py -v
```

## 📈 Performance Considerations

- **Unit tests**: Should run in <30 seconds total
- **Integration tests**: May take several minutes due to API rate limiting
- **Parallel execution**: Unit tests support parallel execution (`-n auto`)
- **Rate limiting**: Integration tests are rate-limited to 1 call/second

## 🔒 Security

- **API keys**: Never commit API keys to version control
- **Test data**: Use realistic but non-sensitive test data
- **Secrets**: Store API keys in environment variables or CI secrets
- **Security scanning**: Bandit runs in CI to detect security issues

## 📝 Contributing

When adding new tests:

1. **Follow existing patterns** for consistency
2. **Add both unit and integration tests** for new tools
3. **Update fixtures** with new test data as needed
4. **Use appropriate markers** (`@pytest.mark.unit`, etc.)
5. **Include error cases** and edge conditions
6. **Document any special requirements** or setup needed

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio documentation](https://github.com/pytest-dev/pytest-asyncio)
- [Pydantic testing patterns](https://docs.pydantic.dev/latest/concepts/testing/)
- [httpx testing documentation](https://www.python-httpx.org/advanced/)
