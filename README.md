<a href="https://www.aiera.com">
  <div align="center">
    <picture>
        <source media="(prefers-color-scheme: light)" srcset="assets/aiera_logo_lightmode.png">
        <source media="(prefers-color-scheme: dark)" srcset="assets/aiera_logo_darkmode.jpeg">
        <img alt="Aiera logo" src="assets/aiera_logo_darkmode.jpeg" height="100">
    </picture>
  </div>
</a>
<br>

> [!IMPORTANT]
> :test_tube: This project is experimental and could be subject to breaking changes.

# Aiera MCP Tools

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) package that provides access to [Aiera](https://www.aiera.com) financial data. This repository contains both a standalone MCP server and a reusable Python package.

## Overview

This package exposes Aiera API endpoints as MCP tools, providing access to comprehensive financial data including:

- **Events**: Calendar events, transcripts, and metadata
- **Company Information**: Symbology, summaries, sectors, and watchlists
- **Company Documents**: Press releases, slide presentations, disclosures, etc.
- **SEC Filings**: Filing data and metadata
- **Financials**: Income statements, balance sheets, and cash flow statements
- **Third Bridge**: Expert insight events
- **Search**: Semantic search within transcripts, SEC filing content, company documents, etc.
- **Transcrippets**: Create, manage, and retrieve transcript excerpts

## Installation

### Option 1: As a Python Package (Recommended)

Install directly from GitHub:

```bash
pip install git+https://github.com/aiera-inc/aiera-mcp.git
```

Or add to your `pyproject.toml`:

```toml
dependencies = [
    "aiera-mcp-tools @ git+https://github.com/aiera-inc/aiera-mcp.git@main",
]
```

### Option 2: Local Development

1. **Clone and install**:
```bash
git clone https://github.com/aiera-inc/aiera-mcp.git
cd aiera-mcp
uv sync --group dev  # Install with dev dependencies
```

2. **Set up pre-commit hooks** (recommended for development):
```bash
uv run pre-commit install
```

3. **Set up environment variables**:
```bash
export AIERA_API_KEY="your-aiera-api-key"
```

Alternatively, create a `.env` file in the project root (see [Configuration](#configuration) section below).

4. **Run standalone server**:
```bash
uv run entrypoint.py
```

## Configuration

The package uses Pydantic BaseSettings for configuration management. All settings can be configured via environment variables or a `.env` file.

### Available Settings

| Setting                   | Environment Variable             | Default                         | Description                      |
|---------------------------|----------------------------------|---------------------------------|----------------------------------|
| Base URL                  | `AIERA_BASE_URL`                 | `https://premium.aiera.com/api` | Aiera API base URL               |
| API Key                   | `AIERA_API_KEY`                  | None                            | Your Aiera API key (required)    |
| Page Size                 | `DEFAULT_PAGE_SIZE`              | `50`                            | Default number of items per page |
| Max Page Size             | `DEFAULT_MAX_PAGE_SIZE`          | `100`                           | Maximum allowed page size        |
| HTTP Timeout              | `HTTP_TIMEOUT`                   | `30.0`                          | Request timeout in seconds       |
| Max Keepalive Connections | `HTTP_MAX_KEEPALIVE_CONNECTIONS` | `10`                            | Maximum keepalive connections    |
| Max Connections           | `HTTP_MAX_CONNECTIONS`           | `20`                            | Maximum total connections        |
| Keepalive Expiry          | `HTTP_KEEPALIVE_EXPIRY`          | `30.0`                          | Keepalive expiry time in seconds |
| Log Level                 | `LOG_LEVEL`                      | `INFO`                          | Logging level                    |

### Using a .env File

Create a `.env` file in your project root (use `.env.example` as a template):

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
AIERA_API_KEY=your-api-key-here
AIERA_BASE_URL=https://premium.aiera.com/api  # Optional: override default
DEFAULT_PAGE_SIZE=100  # Optional: override default
```

### Programmatic Configuration

Access and modify settings programmatically:

```python
from aiera_mcp import get_settings, reload_settings

# Get current settings
settings = get_settings()
logger.debug(f"Base URL: {settings.aiera_base_url}")
logger.debug(f"Page Size: {settings.default_page_size}")

# Reload settings from environment (useful for testing)
reload_settings()
```

### Custom Settings Instance

For advanced use cases, you can create a custom settings instance:

```python
from aiera_mcp.config import AieraSettings

# Create settings with custom values
custom_settings = AieraSettings(
    aiera_base_url="https://custom.aiera.com/api",
    default_page_size=100,
    http_timeout=60.0
)
```

## Usage

### As a Package

```python
from aiera_mcp import register_aiera_tools, set_api_key_provider

# Basic usage with AIERA_API_KEY environment variable
# Returns the tool registry dictionary
tools = register_aiera_tools()

# For OAuth systems (e.g., aiera-public-mcp)
from your_auth_system import get_current_api_key
tools = register_aiera_tools(api_key_provider=get_current_api_key)

# Or configure API key provider globally
set_api_key_provider(get_current_api_key)

# Import individual tool functions directly
from aiera_mcp import find_events, make_aiera_request, correct_bloomberg_ticker
```

## Package Contents

### Tools
- **Events**: `find_events`, `find_conferences`, `get_event`, `get_upcoming_events`
- **Filings**: `find_filings`, `get_filing`
- **Company Documents**: `find_company_docs`, `get_company_doc`, `get_company_doc_categories`, `get_company_doc_keywords`
- **Third Bridge**: `find_third_bridge_events`, `get_third_bridge_event`
- **Search**: `search_transcripts`, `search_filings`
- **Equities**: `find_equities`, `get_equity_summaries`, `get_sectors_and_subsectors`, `get_financials`
- **Indexes & Watchlists**: `get_available_indexes`, `get_index_constituents`, `get_available_watchlists`, `get_watchlist_constituents`
- **Transcrippets**: `find_transcrippets`, `create_transcrippet`, `delete_transcrippet`

### Utilities
- **API Functions**: `make_aiera_request`
- **Registration**: `register_aiera_tools` - Configure API key provider and get tool registry
- **Authentication**: `set_api_key_provider`, `get_api_key`, `clear_api_key_provider` - OAuth compatibility functions

### Configuration
- `get_settings`, `reload_settings`, `AieraSettings` - Configuration management functions (see [Configuration](#configuration))
- `DEFAULT_PAGE_SIZE`, `DEFAULT_MAX_PAGE_SIZE`, `AIERA_BASE_URL` - Constants (loaded from settings, can be overridden via environment variables)
- `AVAILABLE_TOOLS` - List of all 24 available tool names

## Prerequisites

- Python 3.11 or higher
- An Aiera API key
- [Astral UV](https://docs.astral.sh/uv/getting-started/installation/) (for development)

## Claude Desktop Configuration

### Option 1: Using the Standalone Server

1. Follow the [Claude Desktop MCP installation instructions](https://modelcontextprotocol.io/quickstart/user) and find your configuration file.
2. Use the following configuration:
   - Replace `<your_api_key_here>` with your actual Aiera API key
   - Replace `<your_directory>` with your home directory path

<details>
  <summary>claude_desktop_config.json (Standalone Server)</summary>

```json
{
    "mcpServers": {
        "Aiera MCP": {
           "command": "uv",
           "args": [
               "run",
               "--with",
               "git+https://github.com/aiera-inc/aiera-mcp.git",
               "aiera-mcp"
            ],
            "env": {
               "AIERA_API_KEY": "<your_api_key_here>"
            }
        }
    }
}
```
</details>

### Option 2: Using Local Installation

<details>
  <summary>claude_desktop_config.json (Local Installation)</summary>

```json
{
    "mcpServers": {
        "Aiera MCP": {
           "command": "<your_directory>/.local/bin/uv",
           "args": [
               "run",
               "--directory",
               "<your_directory>/aiera-mcp",
               "python",
               "entrypoint.py"
            ],
            "env": {
               "AIERA_API_KEY": "<your_api_key_here>"
            }
        }
    }
}
```
</details>

## Usage Examples

Once integrated, you can prompt Claude to access Aiera data:

```
Get the latest earnings call transcript for Apple Inc. and summarize key points
```

## Key Features

- **Comprehensive API Coverage**: Implements most Aiera API endpoints as MCP tools
- **Flexible Integration**: Use as a standalone server or integrate as a Python package
- **OAuth Compatible**: Seamlessly integrates with OAuth authentication systems (e.g., aiera-public-mcp)
- **Multi-Authentication**: Supports both environment variables and OAuth providers
- **Data Validation**: Built-in utilities for correcting tickers, keywords, and other parameters
- **Type Safety**: Pydantic-based parameter validation with automatic schema generation
- **Registry Pattern**: Centralized tool metadata and configuration management
- **Development Ready**: Full development environment with testing and linting tools

Some endpoints may require special permissions. Contact your Aiera representative for more details.

## Authentication

This package supports two authentication methods:

### Environment Variable (Default)
```bash
export AIERA_API_KEY="your-aiera-api-key"
```

### OAuth Integration
For OAuth systems like aiera-public-mcp:
```python
from aiera_mcp import register_aiera_tools
from your_oauth_system import get_current_api_key

register_aiera_tools(api_key_provider=get_current_api_key)
```

The package automatically handles API key resolution with fallback from OAuth provider to environment variable.

## Testing

### Manual Integration Testing

Since integration tests have been removed, use the manual testing script to validate the MCP tools against the real Aiera API.

**Setup:**
```bash
# Set up API key
export AIERA_API_KEY="your_api_key_here"
```

**Manual Testing Script:**
```bash
# Test all available tools
AIERA_API_KEY=your_api_key_here uv run python scripts/manual_test.py

# Test specific tool categories
AIERA_API_KEY=your_api_key_here uv run python scripts/manual_test.py find_events
AIERA_API_KEY=your_api_key_here uv run python scripts/manual_test.py find_filings
AIERA_API_KEY=your_api_key_here uv run python scripts/manual_test.py create_transcrippet
```

The manual test script:
- Makes direct API calls and compares them with tool outputs
- Tests each tool function individually
- Logs discrepancies and issues to help with debugging
- Provides comprehensive validation of tool behavior

## Development

### Version Management

This package uses automatic semantic versioning based on Git tags:

**Creating a Release:**
```bash
# 1. Ensure all changes are committed and pushed
git add . && git commit -m "Prepare release"

# 2. Create and push a version tag
git tag v1.2.3  # Use semantic versioning
git push origin v1.2.3

# 3. Create GitHub release (optional but recommended)
gh release create v1.2.3 --generate-notes
```

**Version Formats:**
- Released versions: `1.2.3` (from Git tags like `v1.2.3`)
- Development versions: `1.2.4.dev5+g1a2b3c4` (auto-generated from commits)

The package version is automatically determined from Git history using `hatch-vcs`.

### Pre-commit Hooks

This project uses pre-commit for code quality:

```bash
# Install hooks (one time setup)
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

## Links
- [Aiera REST Documentation](https://rest.aiera.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Privacy Policy

This MCP server interacts with Aiera's API to fetch relevant financial data.
All data requests are subject to Aiera's privacy policy and terms of service, and require an active account.

- **Aiera Privacy Policy**: https://aiera.com/privacy-policy/
- **Data Handling**: This server does not store or cache any user data.
- **API Key**: Your Aiera API key is used only for authenticating requests to their API.
