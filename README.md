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
- **Company Documents**: Press releases, slide presentations, disclosures
- **SEC Filings**: Filing data and metadata
- **Search**: Semantic search within transcripts and SEC filing content
- **Transcrippets**: Create, manage, and retrieve transcript excerpts
- **Third Bridge**: Expert insight events

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

4. **Run standalone server**:
```bash
uv run entrypoint.py
```

## Usage

### As a Package

```python
import asyncio
from mcp.server.fastmcp import FastMCP
from aiera_mcp import register_aiera_tools

# Basic usage with AIERA_API_KEY environment variable
mcp = FastMCP("MyServer")
register_aiera_tools(mcp)

# For OAuth systems (e.g., aiera-public-mcp)
from your_auth_system import get_current_api_key
register_aiera_tools(mcp, get_current_api_key)

# Package integration with Pydantic validation
from aiera_mcp.tools import register_tools
register_tools(mcp)

# Selective tool registration - include only specific tools
register_tools(mcp, include_tools=['find_events', 'get_event'])

# Selective tool registration - exclude specific tools
register_tools(mcp, exclude_tools=['delete_transcrippet', 'create_transcrippet'])

# Or configure globally
from aiera_mcp import set_api_key_provider
set_api_key_provider(get_current_api_key)

# Or import individual functions
from aiera_mcp import find_events, make_aiera_request, correct_bloomberg_ticker
```

## Package Contents

### Tools
- **Events**: `find_events`, `get_event`, `get_upcoming_events`
- **Filings**: `find_filings`, `get_filing`
- **Equities**: `find_equities`, `get_equity_summaries`, `get_sectors_and_subsectors`
- **Indexes & Watchlists**: `get_available_indexes`, `get_index_constituents`, `get_available_watchlists`, `get_watchlist_constituents`
- **Company Documents**: `find_company_docs`, `get_company_doc`, `get_company_doc_categories`, `get_company_doc_keywords`
- **Search**: `search_transcripts`, `search_filings`, `search_filing_chunks`
- **Transcrippets**: `find_transcrippets`, `create_transcrippet`, `delete_transcrippet`
- **Third Bridge**: `find_third_bridge_events`, `get_third_bridge_event`

### Utilities
- **API Functions**: `make_aiera_request`
- **Data Correction**: `correct_bloomberg_ticker`, `correct_keywords`, `correct_categories`, `correct_provided_ids`, `correct_event_type`, `correct_transcript_section`
- **Registration**:
  - `register_aiera_tools` - Register all tools with any FastMCP server instance (for standalone server)
  - `register_tools` - Registry-based registration with Pydantic validation and selective filtering (for package integration)
- **Tool Discovery**:
  - `get_all_tool_names` - Get list of all available tool names
  - `get_categories` - Get all tool categories
  - `get_tools_by_category` - Filter tools by category
  - `get_tools_by_read_only` - Filter tools by read-only status
  - `get_destructive_tools` - Get all potentially destructive tools
- **Authentication**: `set_api_key_provider`, `get_api_key`, `clear_api_key_provider` - OAuth compatibility functions

### Constants
- `DEFAULT_PAGE_SIZE`, `DEFAULT_MAX_PAGE_SIZE`, `AIERA_BASE_URL`, `CITATION_PROMPT`
- `AVAILABLE_TOOLS` - List of all 24 available tool names

## Selective Tool Registration

The `register_aiera_tools` function supports optional `include` and `exclude` parameters to register only a subset of tools:

```python
from mcp.server.fastmcp import FastMCP
from aiera_mcp import register_aiera_tools, EVENT_TOOLS, THIRD_BRIDGE_TOOLS

mcp = FastMCP("MyServer")

# Register only event-related tools
register_aiera_tools(mcp, include=["find_events", "get_event", "get_upcoming_events"])

# Use predefined tool groups for convenience
register_aiera_tools(mcp, include=EVENT_TOOLS)

# Register all tools except Third Bridge
register_aiera_tools(mcp, exclude=THIRD_BRIDGE_TOOLS)

# Combine with OAuth authentication
from your_auth_system import get_current_api_key
register_aiera_tools(mcp, get_current_api_key, include=EVENT_TOOLS)
```

### Available Tool Groups

The package provides predefined tool groups for common use cases:

- **`EVENT_TOOLS`**: `["find_events", "get_event", "get_upcoming_events"]`
- **`FILING_TOOLS`**: `["find_filings", "get_filing"]`
- **`EQUITY_TOOLS`**: `["find_equities", "get_equity_summaries", "get_sectors_and_subsectors"]`
- **`INDEX_WATCHLIST_TOOLS`**: `["get_available_indexes", "get_index_constituents", "get_available_watchlists", "get_watchlist_constituents"]`
- **`COMPANY_DOC_TOOLS`**: `["find_company_docs", "get_company_doc", "get_company_doc_categories", "get_company_doc_keywords"]`
- **`SEARCH_TOOLS`**: `["search_transcripts", "search_filings", "search_filing_chunks"]`
- **`TRANSCRIPPET_TOOLS`**: `["find_transcrippets", "create_transcrippet", "delete_transcrippet"]`
- **`THIRD_BRIDGE_TOOLS`**: `["find_third_bridge_events", "get_third_bridge_event"]`
- **`AVAILABLE_TOOLS`**: Complete list of all 24 available tools

### Usage Examples

```python
# Register only core financial tools (events + filings + equities)
core_tools = EVENT_TOOLS + FILING_TOOLS + EQUITY_TOOLS
register_aiera_tools(mcp, include=core_tools)

# Register everything except Third Bridge (useful for basic subscriptions)
register_aiera_tools(mcp, exclude=THIRD_BRIDGE_TOOLS)

# Register only search/discovery tools
discovery_tools = ["find_events", "find_filings", "find_equities", "find_company_docs"]
register_aiera_tools(mcp, include=discovery_tools)
```

### Error Handling

The function validates tool names and provides helpful error messages:

```python
# This will raise ValueError: Unknown tools specified in 'include': ['nonexistent_tool']
register_aiera_tools(mcp, include=["nonexistent_tool"])

# This will raise ValueError: Cannot specify both 'include' and 'exclude' parameters
register_aiera_tools(mcp, include=EVENT_TOOLS, exclude=FILING_TOOLS)
```

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
               "--with",
               "mcp[cli]",
               "mcp",
               "run",
               "aiera_mcp/server.py"
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
               "--with",
               "mcp[cli]",
               "mcp",
               "run",
               "<your_directory>/aiera-mcp/aiera_mcp/server.py"
            ],
            "env": {
               "AIERA_API_KEY": "<your_api_key_here>"
            }
        }
    }
}
```
</details>

## Selective Tool Registration

The package supports selective registration to include or exclude specific tools:

```python
from aiera_mcp.tools import register_tools, get_all_tool_names, get_destructive_tools

# Get available tools
all_tools = get_all_tool_names()
print(f"Available tools: {all_tools}")

# Register only read-only tools (exclude destructive operations)
destructive_tools = list(get_destructive_tools().keys())
register_tools(mcp, exclude_tools=destructive_tools)

# Register only event-related tools
event_tools = ['find_events', 'get_event', 'get_upcoming_events']
register_tools(mcp, include_tools=event_tools)

# Error handling with suggestions
try:
    register_tools(mcp, include_tools=['find_event'])  # Typo
except ValueError as e:
    print(e)  # Will suggest: "Did you mean: find_event -> ['find_events', 'get_event']"
```

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
- **Selective Registration**: Include or exclude specific tools, with intelligent error handling and suggestions
- **Tool Discovery**: Helper functions to explore available tools by category, permissions, and functionality
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
from your_oauth_system import get_current_api_key
register_aiera_tools(mcp, get_current_api_key)
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
