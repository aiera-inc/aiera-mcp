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
uv sync  # or pip install -e .
```

2. **Set up environment variables**:
```bash
export AIERA_API_KEY="your-aiera-api-key"
```

3. **Run standalone server**:
```bash
uv run entrypoint.py
```

## Usage

### As a Package

```python
import asyncio
from mcp.server.fastmcp import FastMCP
from aiera_mcp import register_aiera_tools

# Create MCP server and register all Aiera tools
mcp = FastMCP("MyServer")
register_aiera_tools(mcp)

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
- **Third Bridge**: `find_third_bridge_events`, `get_third_bridge_event`

### Utilities
- **API Functions**: `make_aiera_request`
- **Data Correction**: `correct_bloomberg_ticker`, `correct_keywords`, `correct_categories`, `correct_provided_ids`, `correct_event_type`, `correct_transcript_section`
- **Registration**: `register_aiera_tools` - Register all tools with any FastMCP server instance

### Constants
- `DEFAULT_PAGE_SIZE`, `DEFAULT_MAX_PAGE_SIZE`, `AIERA_BASE_URL`, `CITATION_PROMPT`

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

## Usage Examples

Once integrated, you can prompt Claude to access Aiera data:

```
Get the latest earnings call transcript for Apple Inc. and summarize key points
```

## Key Features

- **Comprehensive API Coverage**: Implements most Aiera API endpoints as MCP tools
- **Flexible Integration**: Use as a standalone server or integrate as a Python package
- **Data Validation**: Built-in utilities for correcting tickers, keywords, and other parameters
- **Easy Registration**: Single function to register all tools with any MCP server
- **Development Ready**: Full development environment with testing and linting tools

Some endpoints may require special permissions. Contact your Aiera representative for more details.

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