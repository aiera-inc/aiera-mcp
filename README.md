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

# Aiera MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that provides access to [Aiera](https://www.aiera.com) financial data API through an LLM-friendly interface.

## Overview

This server exposes Aiera API endpoints as MCP tools, providing access to comprehensive financial data including:

- Events (calendar, transcripts, and metadata)
- Company information (symbology, summaries, etc)
- Company documents (press releases, slide presentations, disclosures, etc)
- Filings (SEC filings and related metadata)

## Installation

### Prerequisites

- Python 3.10+
- An Aiera API key
- [Astral UV](https://docs.astral.sh/uv/getting-started/installation/)
  - For existing installs, check that you have a version that supports the `uvx` command.

### Claude Desktop

1. Follow the [Claude Desktop MCP installation instructions](https://modelcontextprotocol.io/quickstart/user) to complete the initial installation and find your configuration file.
1. Use the following example as reference to add Aiera's MCP server.
Make sure you complete the various fields.
    1. Path find your path to `uvx`, run `which uvx` in your terminal.
    2. Replace `<your_api_key_here>` with your actual Aiera API key.
    3. Replace `<your_directory>` with your home directory path, e.g., `/home/username` (Mac/Linux) or `C:\Users\username` (Windows).

<details>
  <summary>claude_desktop_config.json</summary>

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

## Available Tools

This MCP server implements most Aiera API endpoints as tools, including:

- `find_events` - Retrieve events, filtered by ticker(s), date range, and (optionally) by event type.
- `get_upcoming_events` - Retrieve confirmed and estimated upcoming events.
- `find_filings` - Retrieve SEC filings, filtered by ticker(s) and a date range, and (optionally) by form number
- `get_filing_text` - Retrieve the raw content for a single SEC filing.
- `find_equities` - Retrieve equities, filtered by various identifiers, such as ticker(s) or RIC, or by a search term.
- `get_equity_summaries` - Retrieve detailed summary information about one or more equities.
- `find_company_docs` - Retrieve documents that have been published on company IR websites.
- `get_company_doc_text` - Retrieve the raw content for a single company document.
- And many more...

## Links
- [Aiera REST Documentation](https://rest.aiera.com)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

## Privacy Policy

This MCP server interacts with Aiera's API to fetch financial data. All data requests are subject to Aiera's privacy policy and terms of service.

- **Aiera Privacy Policy**: https://aiera.com/privacy-policy/
- **Data Handling**: This server does not store or cache any user data. All requests are proxied directly to Aiera's API.
- **API Key**: Your Aiera API key is used only for authenticating requests to their API.