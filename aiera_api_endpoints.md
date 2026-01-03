# Aiera Chat Support API Endpoints

This document describes all available endpoints in the Chat Support API (`/chat-support/`) and their input parameters.

---

## Common Parameters

The following parameters are shared across most endpoints:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Whether to include base instructions in the response |
| `originating_prompt` | string | - | The original prompt that triggered this request |
| `self_identification` | string | - | Identifier for the calling system/agent |

---

## GET /get-instructions/{instruction_type}

Retrieves instructions of a specific type for use with MCP/AI agents.

**Path Parameters:**

| Parameter | Type | Description                                                      |
|-----------|------|------------------------------------------------------------------|
| `instruction_type` | string | The type of instructions to retrieve (citations, base, guidance) |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |

---

## POST /search/{index}

Executes a raw OpenSearch query against the specified index.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | string | Index to search. Valid values: `events`, `transcripts`, `filings`, `filing-chunks`, `attachments`, `company_docs`, `third_bridge` |

**Request Body (JSON):**

The request body should contain a valid OpenSearch query object. Special parameters can be included at the top level:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `query` | object | - | OpenSearch query body |
| `size` | integer | `100` | Number of results (max 250) |
| `from` | integer | `0` | Offset for pagination |
| `min_score` | float | `0.2` | Minimum relevance score |
| `_source` | array | `[]` | Fields to include in response |

---

## GET /get-financials

Retrieves financial statement data for the specified company.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `source` | string | **required** | Financial statement type: `income-statement`, `balance-sheet`, `cash-flow-statement` |
| `source_type` | string | `standardized` | Data format: `as-reported`, `standardized` |
| `period` | string | `annual` | Period type: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| `fiscal_year` | string | - | Fiscal year |
| `fiscal_quarter` | string | - | Fiscal quarter |
| `calendar_year` | string | **required** | Calendar year (e.g., `2024`) |
| `calendar_quarter` | string | - | Calendar quarter (e.g., `Q1`) |
| `ratio_id` | string | - | Specific ratio ID |
| `metric_id` | string | - | Specific metric ID |
| `metric_type` | string | - | Metric type filter |

---

## GET /get-ratios

Retrieves financial ratios for the specified company.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `period` | string | `annual` | Period type: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| `calendar_year` | string | **required** | Calendar year |
| `calendar_quarter` | string | - | Calendar quarter |
| `ratio_id` | string | - | Specific ratio ID to filter |

---

## GET /get-segments-and-kpis

Retrieves segment data and KPIs for the specified company.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `period` | string | `annual` | Period type: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| `calendar_year` | string | **required** | Calendar year |
| `calendar_quarter` | string | - | Calendar quarter |
| `metric_id` | string | - | Specific metric ID |
| `metric_type` | string | - | Metric type filter |

---

## GET /available-watchlists

Returns the list of watchlists available to the authenticated user.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /watchlist-constituents/{watchlist_id}

Returns the equities contained in a specific watchlist.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `watchlist_id` | integer | The ID of the watchlist |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /available-indexes

Returns the list of available market indices.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /index-constituents/{index}

Returns the equities contained in a specific market index.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `index` | string/integer | Index ID, short name, or display name |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /estimated-and-upcoming-events

Returns estimated future events and confirmed upcoming events for specified equities.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term to filter events |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `equity_ids` | string | - | Comma-separated list of equity IDs |
| `index_id` | integer | - | Filter by market index |
| `watchlist_id` | integer | - | Filter by user watchlist |
| `sector_id` | integer | - | Filter by GICS sector |
| `subsector_id` | integer | - | Filter by GICS subsector |
| `start_date` | datetime | now | Start of date range (ISO 8601) |
| `end_date` | datetime | now + 8 weeks | End of date range (ISO 8601) |

---

## GET /find-events

Searches for events with optional transcript inclusion.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term to filter events by title |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `sector_id` | integer | - | Filter by GICS sector |
| `subsector_id` | integer | - | Filter by GICS subsector |
| `index_id` | integer | - | Filter by market index |
| `watchlist_id` | integer | - | Filter by user watchlist |
| `conference_id` | integer | - | Filter by conference/event group |
| `event_id` | integer | - | Single event ID to retrieve |
| `event_ids` | string | - | Comma-separated list of event IDs |
| `event_type` | string | - | Comma-separated event types (e.g., `earnings`, `guidance`) |
| `start_date` | datetime | now - 2 weeks | Start of date range |
| `end_date` | datetime | now + 2 weeks | End of date range (max 8 weeks out) |
| `include_transcripts` | boolean | `false` | Include transcript content |
| `event_category` | string | - | Filter by category: `expert_insights`, `thirdbridge` |
| `transcript_section` | string | - | Filter transcript by section: `q_and_a`, `presentation` |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /find-conferences

Searches for investment conferences and event groups.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `start_date` | datetime | now - 2 weeks | Start of date range |
| `end_date` | datetime | now + 2 weeks | End of date range |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /equity-summaries

Returns comprehensive summary information for specified equities including leadership, indices, events, and estimates.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `equity_ids` | string | - | Comma-separated list of equity IDs |
| `index_id` | integer | - | Filter by market index |
| `watchlist_id` | integer | - | Filter by user watchlist |
| `lookback` | integer | `90` | Number of days to look back for events |

---

## GET /find-filings

Searches for SEC filings and regulatory documents.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term to filter filings |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `sector_id` | integer | - | Filter by GICS sector |
| `subsector_id` | integer | - | Filter by GICS subsector |
| `watchlist_id` | integer | - | Filter by user watchlist |
| `index_id` | integer | - | Filter by market index |
| `filing_id` | integer | - | Single filing ID to retrieve |
| `filing_ids` | string | - | Comma-separated list of filing IDs |
| `form_number` | string | - | Filter by form type (e.g., `10-K`, `10-Q`, `8-K`) |
| `start_date` | datetime | now - 12 weeks | Start of date range |
| `end_date` | datetime | now | End of date range |
| `include_delisted` | boolean | `true` | Include filings from delisted companies |
| `include_content` | boolean | `false` | Include raw filing content |
| `company_rollup` | boolean | `true` | Roll up to company level |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /find-company-docs

Searches for company documents (investor presentations, annual reports, etc.).

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term to filter documents |
| `start_date` | datetime | now - 4 weeks | Start of date range |
| `end_date` | datetime | now | End of date range |
| `categories` | string | - | Comma-separated category names to include |
| `exclude_categories` | string | - | Comma-separated category names to exclude |
| `keywords` | string | - | Comma-separated keywords to include |
| `exclude_keywords` | string | - | Comma-separated keywords to exclude |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `permid` | string | - | PermID identifier |
| `sector_id` | integer | - | Filter by GICS sector |
| `subsector_id` | integer | - | Filter by GICS subsector |
| `watchlist_id` | integer | - | Filter by user watchlist |
| `index_id` | integer | - | Filter by market index |
| `company_doc_id` | integer | - | Single document ID to retrieve |
| `company_doc_ids` | string | - | Comma-separated list of document IDs |
| `include_delisted` | boolean | `true` | Include docs from delisted companies |
| `include_content` | boolean | `false` | Include raw document content |
| `company_rollup` | boolean | `true` | Roll up to company level |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /find-equities

Searches for equities/companies in the Aiera database.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `permid` | string | - | PermID identifier |
| `sector_id` | string | - | Filter by GICS sector |
| `subsector_id` | string | - | Filter by GICS subsector |
| `search` | string | - | Search by company name or ticker |
| `include_inactive` | boolean | `false` | Include inactive/delisted equities |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /get-sectors-and-subsectors

Returns the complete list of GICS sectors and subsectors.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /get-company-doc-categories

Returns available company document categories with counts.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search/filter categories |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /get-company-doc-keywords

Returns available company document keywords with counts.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search/filter keywords |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## GET /find-third-bridge

Searches for Third Bridge expert content (forums, primers, community).

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | - | Search term to filter content |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `sector_id` | integer | - | Filter by GICS sector |
| `subsector_id` | integer | - | Filter by GICS subsector |
| `index_id` | integer | - | Filter by market index |
| `watchlist_id` | integer | - | Filter by user watchlist |
| `event_id` | string | - | Single Third Bridge event ID |
| `event_ids` | string | - | Comma-separated list of event IDs |
| `start_date` | datetime | now - 4 weeks | Start of date range |
| `end_date` | datetime | now (max 8 weeks out) | End of date range |
| `include_transcripts` | boolean | `false` | Include transcript content |
| `content_type` | string | - | Filter by type: `FORUM`, `PRIMER`, `COMMUNITY` |
| `page` | integer | `1` | Page number |
| `page_size` | integer | `50` | Results per page (max 100) |

---

## POST /search-company-news

Searches company investor relations news pages using external search.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_base_instructions` | boolean | `true` | Include base instructions |
| `originating_prompt` | string | - | Original prompt |
| `self_identification` | string | - | Caller identifier |
| `search` | string | **required** | Search query for news |
| `bloomberg_ticker` | string | - | Bloomberg ticker symbol |
| `isin` | string | - | ISIN identifier |
| `permid` | string | - | PermID identifier |
| `ric` | string | - | Reuters Instrument Code |
| `ticker` | string | - | Local ticker symbol |
| `sector_id` | integer | - | Filter by GICS sector |
| `subsector_id` | integer | - | Filter by GICS subsector |
| `index_id` | integer | - | Filter by market index |
| `watchlist_id` | integer | - | Filter by user watchlist |

---

## Notes

### Equity Identification
Most endpoints support multiple ways to identify equities:
- `bloomberg_ticker`: Full Bloomberg ticker (e.g., `AAPL:US`)
- `ticker`: Local ticker symbol (e.g., `AAPL`)
- `isin`: International Securities Identification Number
- `ric`: Reuters Instrument Code
- `permid`: PermID identifier
- `equity_ids`: Comma-separated internal equity IDs

### Filtering by Groups
- `watchlist_id`: Filter to equities in a user's watchlist
- `index_id`: Filter to equities in a market index (e.g., S&P 500)
- `sector_id`: Filter by GICS sector
- `subsector_id`: Filter by GICS subsector

### Pagination
All paginated endpoints support:
- `page`: Page number (1-indexed)
- `page_size`: Results per page (default 50, max 100 for most endpoints)

### Date Formats
Date parameters accept ISO 8601 formatted strings (e.g., `2024-01-15T00:00:00Z` or `2024-01-15`).

### Authentication
All endpoints require authentication. Access to specific data sets may require additional permissions.
