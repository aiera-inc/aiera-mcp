# Aiera MCP Tools API Documentation

This document provides comprehensive documentation for all Aiera MCP (Model Context Protocol) tools, including input parameters and expected output structures.

---

## Table of Contents

1. [Utility Tools](#utility-tools)
   - [ping](#ping)
   - [debug_auth](#debug_auth)
2. [Equity & Company Tools](#equity--company-tools)
   - [find_equities](#find_equities)
   - [get_equity_summaries](#get_equity_summaries)
3. [Event Tools](#event-tools)
   - [find_events](#find_events)
   - [get_event](#get_event)
   - [get_upcoming_events](#get_upcoming_events)
   - [find_conferences](#find_conferences)
4. [Transcript Search](#transcript-search)
   - [search_transcripts](#search_transcripts)
5. [Filing Tools](#filing-tools)
   - [find_filings](#find_filings)
   - [get_filing](#get_filing)
   - [search_filings](#search_filings)
6. [Company Document Tools](#company-document-tools)
   - [find_company_docs](#find_company_docs)
   - [get_company_doc](#get_company_doc)
   - [get_company_doc_categories](#get_company_doc_categories)
   - [get_company_doc_keywords](#get_company_doc_keywords)
7. [Third Bridge Expert Insights](#third-bridge-expert-insights)
   - [find_third_bridge_events](#find_third_bridge_events)
   - [get_third_bridge_event](#get_third_bridge_event)
8. [Research Tools](#research-tools)
   - [find_research](#find_research)
   - [get_research](#get_research)
   - [search_research](#search_research)
   - [get_research_providers](#get_research_providers)
   - [get_research_authors](#get_research_authors)
   - [get_research_asset_classes](#get_research_asset_classes)
   - [get_research_asset_types](#get_research_asset_types)
   - [get_research_subjects](#get_research_subjects)
   - [get_research_product_focuses](#get_research_product_focuses)
   - [get_research_discipline_types](#get_research_discipline_types)
   - [get_research_region_types](#get_research_region_types)
   - [get_research_country_codes](#get_research_country_codes)
9. [Financial Data Tools](#financial-data-tools)
   - [get_financials](#get_financials)
   - [get_ratios](#get_ratios)
   - [get_kpis_and_segments](#get_kpis_and_segments)
10. [Web Search Tools](#web-search-tools)
   - [trusted_web_search](#trusted_web_search)
11. [Reference Data Tools](#reference-data-tools)
   - [get_available_indexes](#get_available_indexes)
   - [get_index_constituents](#get_index_constituents)
   - [get_available_watchlists](#get_available_watchlists)
   - [get_watchlist_constituents](#get_watchlist_constituents)
   - [get_sectors_and_subsectors](#get_sectors_and_subsectors)

---

## Utility Tools

### ping

Simple ping test to verify server is running.

**Input Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| *(none)* | - | - | No parameters required |

**Output Structure:**
```json
{
  "status": "STRING",
  "server": "STRING",
  "timestamp": "STRING",
  "tools_loaded": INTEGER
}
```

---

### debug_auth

Debug authentication state and token information.

**Input Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| *(none)* | - | - | No parameters required |

**Output Structure:**
```json
{
  "auth_successful": BOOLEAN,
  "error": STRING | null,
  "token_type": "STRING",
  "has_api_key": BOOLEAN,
  "api_key_preview": "STRING",
  "claims_keys": ["STRING", ...],
  "user_id": "STRING",
  "environment": {
    "stage": "STRING",
    "lambda_mode": "STRING",
    "allow_env_key": "STRING"
  },
  "custom_claims": [STRING, ...],
  "has_custom_api_key": BOOLEAN
}
```

---

## Equity & Company Tools

### find_equities

Find companies and equities using various identifiers or search terms.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Free-text search term |
| bloomberg_ticker | string | no | null | Bloomberg ticker (comma-separated for multiple) |
| ticker | string | no | null | Standard ticker symbol |
| isin | string | no | null | ISIN identifier (comma-separated for multiple) |
| ric | string | no | null | Reuters Instrument Code (comma-separated for multiple) |
| permid | string | no | null | PermID identifier |
| sector_id | integer/string | no | null | Filter by sector ID. Use get_sectors_and_subsectors to find valid IDs |
| subsector_id | integer/string | no | null | Filter by subsector ID. Use get_sectors_and_subsectors to find valid IDs |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "data": [
      {
        "equity_id": INTEGER,
        "company_id": INTEGER,
        "name": "STRING",
        "bloomberg_ticker": "STRING",
        "sector_id": INTEGER,
        "subsector_id": INTEGER,
        "primary_equity": BOOLEAN,
        "created": "DATETIME_STRING",
        "modified": "DATETIME_STRING"
      }
    ],
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    }
  },
  "error": STRING | null
}
```

---

### get_equity_summaries

Retrieve detailed summaries about one or more equities.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| bloomberg_ticker | string | **yes** | - | Bloomberg ticker (comma-separated for multiple) |
| include_base_instructions | boolean | no | true | Include base instructions in response |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": [
    {
      "equity_id": INTEGER,
      "company_id": INTEGER,
      "name": "STRING",
      "bloomberg_ticker": "STRING",
      "sector_id": INTEGER,
      "subsector_id": INTEGER,
      "description": "STRING",
      "country": "STRING",
      "created": "DATETIME_STRING",
      "modified": "DATETIME_STRING",
      "status": "STRING",
      "leadership": [
        {
          "name": "STRING",
          "title": "STRING",
          "event_count": INTEGER,
          "last_event_date": "DATETIME_STRING"
        }
      ],
      "indices": ["STRING", ...],
      "confirmed_events": {
        "past": [
          {
            "event_id": INTEGER,
            "title": "STRING",
            "event_type": "STRING",
            "event_date": "DATETIME_STRING",
            "fiscal_quarter": INTEGER | null,
            "fiscal_year": INTEGER | null,
            "has_human_verified": BOOLEAN,
            "has_live_transcript": BOOLEAN,
            "has_audio": BOOLEAN,
            "summary": {
              "title": "STRING",
              "content": ["STRING", ...]
            },
            "citation_information": {
              "title": "STRING",
              "url": "STRING",
              "metadata": {
                "type": "STRING",
                "url_target": "STRING",
                "company_id": INTEGER,
                "event_id": INTEGER
              }
            }
          }
        ],
        "upcoming": [...]
      },
      "estimated_events": [
        {
          "estimate_id": INTEGER,
          "estimate_date": "DATETIME_STRING",
          "estimate_type": "STRING",
          "estimate_title": "STRING"
        }
      ]
    }
  ],
  "error": STRING | null
}
```

---

**Note:** For financial data tools (get_financials, get_ratios, get_kpis_and_segments), see the [Financial Data Tools](#financial-data-tools) section below.

---

## Event Tools

### find_events

Search for corporate events including earnings calls, investor presentations, and shareholder meetings.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **yes** | - | Start date (YYYY-MM-DD) |
| end_date | string | **yes** | - | End date (YYYY-MM-DD) |
| search | string | no | null | Search term to filter events by title |
| event_type | string | no | "earnings" | Event type: `earnings`, `presentation`, `investor_meeting`, `shareholder_meeting`, `special_situation` |
| bloomberg_ticker | string | no | null | Bloomberg ticker (comma-separated for multiple) |
| watchlist_id | integer/string | no | null | Filter by watchlist ID |
| index_id | integer/string | no | null | Filter by index ID |
| sector_id | integer/string | no | null | Filter by sector ID |
| subsector_id | integer/string | no | null | Filter by subsector ID |
| conference_id | integer/string | no | null | Filter by conference ID |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "data": [
      {
        "event_id": INTEGER,
        "title": "STRING",
        "event_type": "STRING",
        "event_date": "DATETIME_STRING",
        "equity": {
          "equity_id": INTEGER,
          "company_id": INTEGER,
          "name": "STRING",
          "bloomberg_ticker": "STRING",
          "sector_id": INTEGER,
          "subsector_id": INTEGER,
          "primary_equity": BOOLEAN
        },
        "event_category": "STRING",
        "expected_language": "STRING",
        "conference": {
          "conference_id": INTEGER | null,
          "conference_name": STRING | null
        },
        "summary": {
          "title": STRING | null,
          "summary": STRING | null
        },
        "citation_information": {
          "title": "STRING",
          "url": "STRING",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER,
            "transcript_item_id": INTEGER | null
          }
        },
        "transcripts": null | [...]
      }
    ],
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    }
  },
  "error": STRING | null
}
```

---

### get_event

Get detailed information about a specific event including full transcript.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| event_id | string | **yes** | - | The event ID to retrieve |
| transcript_section | string | no | null | Filter to specific section: `presentation` or `q_and_a` |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "data": [
      {
        "event_id": INTEGER,
        "title": "STRING",
        "event_type": "STRING",
        "event_date": "DATETIME_STRING",
        "equity": {...},
        "event_category": "STRING",
        "expected_language": "STRING",
        "conference": {...},
        "summary": {...} | null,
        "citation_information": {...} | null,
        "transcripts": [
          {
            "transcript_item_id": INTEGER,
            "transcript": "STRING",
            "timestamp": "DATETIME_STRING",
            "speaker": "STRING",
            "speaker_type": "STRING",
            "transcript_section": "STRING",
            "citation_information": {
              "title": "STRING",
              "url": "STRING",
              "metadata": {
                "type": "STRING",
                "url_target": "STRING",
                "company_id": INTEGER,
                "event_id": INTEGER,
                "transcript_item_id": INTEGER
              }
            }
          }
        ]
      }
    ],
    "pagination": {...}
  },
  "error": STRING | null
}
```

---

### get_upcoming_events

Get confirmed and estimated upcoming events within a date range.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **yes** | - | Start date (YYYY-MM-DD) |
| end_date | string | **yes** | - | End date (YYYY-MM-DD) |
| bloomberg_ticker | string | no* | null | Bloomberg ticker (comma-separated) |
| watchlist_id | integer/string | no* | null | Filter by watchlist ID |
| index_id | integer/string | no* | null | Filter by index ID |
| sector_id | integer/string | no* | null | Filter by sector ID |
| subsector_id | integer/string | no* | null | Filter by subsector ID |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

*At least one of bloomberg_ticker, watchlist_id, index_id, sector_id, or subsector_id is required.

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "estimates": [
      {
        "estimate_id": INTEGER,
        "equity": {
          "equity_id": INTEGER,
          "company_id": INTEGER,
          "name": "STRING",
          "bloomberg_ticker": "STRING",
          "sector_id": INTEGER,
          "subsector_id": INTEGER,
          "primary_equity": BOOLEAN | null
        },
        "estimate": {
          "call_type": "STRING",
          "call_date": "DATETIME_STRING",
          "title": "STRING"
        },
        "actual": {...} | null,
        "citation_information": {...}
      }
    ],
    "actuals": [...]
  },
  "error": STRING | null
}
```

---

### find_conferences

Search for conferences by date range.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **yes** | - | Start date (YYYY-MM-DD) |
| end_date | string | **yes** | - | End date (YYYY-MM-DD) |
| search | string | no | null | Search term to filter conferences by title |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "data": [
      {
        "conference_id": INTEGER,
        "title": "STRING",
        "event_count": INTEGER,
        "start_date": "DATETIME_STRING",
        "end_date": "DATETIME_STRING",
        "citation_information": {
          "title": "STRING",
          "url": "STRING",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "conference_id": INTEGER
          }
        }
      }
    ],
    "pagination": {...}
  },
  "error": STRING | null
}
```

---

## Transcript Search

### search_transcripts

Semantic search within specific transcript events using embedding-based matching.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query_text | string | **yes** | - | Search query text |
| equity_ids | array[integer] | no | null | List of equity IDs to filter search |
| event_ids | array[integer] | no | null | List of event IDs to search within |
| event_type | string | no | "earnings" | Event type filter |
| transcript_section | string | no | "" | Filter by section: `presentation` or `q_and_a` |
| start_date | string | no | "" | Start date filter (YYYY-MM-DD) |
| end_date | string | no | "" | End date filter (YYYY-MM-DD) |
| size | integer | no | 20 | Number of results per page (max 250) |
| search_after | array | no | null | Cursor for pagination. Pass `next_search_after` from a previous response to fetch the next page. |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "error": STRING | null,
  "response": {
    "result": [
      {
        "score": FLOAT,
        "date": "DATETIME_STRING",
        "primary_company_id": INTEGER,
        "transcript_item_id": INTEGER,
        "transcript_event_id": INTEGER,
        "transcript_section": "STRING",
        "speaker_name": "STRING",
        "speaker_title": "STRING",
        "text": "STRING",
        "primary_equity_id": INTEGER,
        "title": "STRING",
        "citation_information": {
          "title": "STRING",
          "url": "STRING",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER,
            "transcript_item_id": INTEGER
          }
        }
      }
    ],
    "pagination": {
      "total": INTEGER,
      "page_size": INTEGER,
      "has_next_page": BOOLEAN,
      "next_search_after": [FLOAT, INTEGER] | null
    }
  }
}
```

---

## Filing Tools

### find_filings

Find SEC filings filtered by date range and optional filters.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **yes** | - | Start date (YYYY-MM-DD) |
| end_date | string | **yes** | - | End date (YYYY-MM-DD) |
| search | string | no | null | Search term to filter filings |
| bloomberg_ticker | string | no | null | Bloomberg ticker (comma-separated) |
| form_number | string | no | null | SEC form number (e.g., "10-K", "8-K", "10-Q") |
| watchlist_id | integer/string | no | null | Filter by watchlist ID |
| index_id | integer/string | no | null | Filter by index ID |
| sector_id | integer/string | no | null | Filter by sector ID |
| subsector_id | integer/string | no | null | Filter by subsector ID |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "data": [
      {
        "filing_id": INTEGER,
        "title": "STRING",
        "filing_date": "DATETIME_STRING" | null,
        "period_end_date": "DATETIME_STRING",
        "is_amendment": INTEGER,
        "equity": {
          "equity_id": INTEGER,
          "company_id": INTEGER,
          "name": "STRING",
          "bloomberg_ticker": "STRING",
          "sector_id": INTEGER,
          "subsector_id": INTEGER
        },
        "form_number": "STRING",
        "form_name": "STRING",
        "filing_organization": "STRING",
        "filing_system": "STRING",
        "release_date": "DATETIME_STRING",
        "arrival_date": "DATETIME_STRING",
        "pulled_date": "DATETIME_STRING",
        "json_synced": BOOLEAN,
        "datafiles_synced": BOOLEAN,
        "summary": ["STRING", ...] | null,
        "content_raw": STRING | null,
        "citation_information": {...}
      }
    ],
    "pagination": {...}
  },
  "error": STRING | null
}
```

---

### get_filing

Get detailed information about a specific SEC filing.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| filing_id | string | **yes** | - | The filing ID to retrieve |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "error": STRING | null,
  "filing": {
    "filing_id": INTEGER,
    "title": "STRING",
    "filing_date": "DATETIME_STRING" | null,
    "period_end_date": "DATETIME_STRING",
    "is_amendment": INTEGER,
    "equity": {...},
    "form_number": "STRING",
    "form_name": "STRING",
    "filing_organization": STRING | null,
    "filing_system": STRING | null,
    "release_date": STRING | null,
    "arrival_date": STRING | null,
    "pulled_date": STRING | null,
    "json_synced": BOOLEAN | null,
    "datafiles_synced": BOOLEAN | null,
    "summary": {
      "summary": "STRING",
      "key_points": [...],
      "financial_highlights": {...}
    },
    "content_raw": STRING | null,
    "citation_information": {...} | null,
    "content_preview": STRING | null,
    "document_count": INTEGER
  }
}
```

---

### search_filings

Semantic search within SEC filing document chunks using embedding-based matching.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query_text | string | **yes** | - | Search query text |
| equity_ids | array[integer] | no | null | List of equity IDs to filter search |
| filing_ids | array[string] | no | null | List of filing IDs to search within |
| filing_type | string | no | "" | Filter by filing type |
| start_date | string | no | "" | Start date filter |
| end_date | string | no | "" | End date filter |
| size | integer | no | 20 | Number of results per page (max 250) |
| search_after | array | no | null | Cursor for pagination. Pass `next_search_after` from a previous response to fetch the next page. |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "error": STRING | null,
  "response": {
    "result": [
      {
        "score": FLOAT,
        "date": "DATE_STRING",
        "metadata": {
          "page_number": INTEGER,
          "doc_page": INTEGER | null
        },
        "primary_company_id": INTEGER,
        "content_id": INTEGER,
        "filing_id": "STRING",
        "company_common_name": "STRING",
        "filing_type": "STRING",
        "primary_equity_id": INTEGER,
        "text": "STRING",
        "title": "STRING",
        "citation_information": {...}
      }
    ],
    "pagination": {
      "total": INTEGER,
      "page_size": INTEGER,
      "has_next_page": BOOLEAN,
      "next_search_after": [FLOAT, INTEGER] | null
    }
  }
}
```

---

## Company Document Tools

### find_company_docs

Find company-published documents (press releases, annual reports, etc.).

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **yes** | - | Start date (YYYY-MM-DD) |
| end_date | string | **yes** | - | End date (YYYY-MM-DD) |
| search | string | no | null | Search term to filter docs by title or category |
| bloomberg_ticker | string | no | null | Bloomberg ticker (comma-separated) |
| categories | string | no | null | Document categories (comma-separated): `press_release`, `annual_report`, `earnings_release`, `slide_presentation`, `compliance`, `disclosure`, etc. |
| keywords | string | no | null | Keywords to filter by |
| exclude_categories | string | no | null | Comma-separated category names to exclude from results |
| exclude_keywords | string | no | null | Comma-separated keywords to exclude from results |
| watchlist_id | integer/string | no | null | Filter by watchlist ID |
| index_id | integer/string | no | null | Filter by index ID |
| sector_id | integer/string | no | null | Filter by sector ID |
| subsector_id | integer/string | no | null | Filter by subsector ID |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "error": STRING | null,
  "response": {
    "pagination": {...},
    "data": [
      {
        "doc_id": INTEGER,
        "company": {
          "company_id": INTEGER,
          "name": "STRING"
        },
        "publish_date": "DATE_STRING" | null,
        "category": "STRING" | null,
        "title": "STRING" | null,
        "source_url": "STRING",
        "summary": ["STRING", ...] | null,
        "keywords": ["STRING", ...] | null,
        "processed": "DATETIME_STRING" | null,
        "created": "DATETIME_STRING",
        "modified": "DATETIME_STRING",
        "content_raw": STRING | null,
        "citation_information": {...}
      }
    ]
  }
}
```

---

### get_company_doc

Get detailed information about a specific company document.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| company_doc_ids | string | **yes** | - | Document ID(s) to retrieve |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "error": STRING | null,
  "document": {
    "doc_id": INTEGER,
    "company": {...},
    "publish_date": "DATE_STRING",
    "category": "STRING",
    "title": "STRING",
    "source_url": "STRING",
    "summary": ["STRING", ...],
    "keywords": ["STRING", ...],
    "processed": "DATETIME_STRING",
    "created": "DATETIME_STRING",
    "modified": "DATETIME_STRING",
    "content_raw": "STRING",
    "citation_information": {...},
    "attachments": [...] | null
  }
}
```

---

### get_company_doc_categories

Retrieve all available document categories for filtering.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter categories |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": [...],
  "error": STRING | null,
  "pagination": {...},
  "data": {
    "CATEGORY_NAME": INTEGER,  // category name -> document count
    ...
  }
}
```

---

### get_company_doc_keywords

Retrieve all available keywords for filtering company documents.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter keywords |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": [...],
  "error": STRING | null,
  "pagination": {...},
  "data": {
    "KEYWORD": INTEGER,  // keyword -> document count
    ...
  }
}
```

---

## Third Bridge Expert Insights

### find_third_bridge_events

Find expert insight events from Third Bridge.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | **yes** | - | Start date (YYYY-MM-DD) |
| end_date | string | **yes** | - | End date (YYYY-MM-DD) |
| search | string | no | null | Search term to filter content by title or description |
| bloomberg_ticker | string | no | null | Bloomberg ticker (comma-separated) |
| watchlist_id | integer/string | no | null | Filter by watchlist ID |
| index_id | integer/string | no | null | Filter by index ID |
| sector_id | integer/string | no | null | Filter by sector ID |
| subsector_id | integer/string | no | null | Filter by subsector ID |
| content_type | string | no | null | Filter by content type: `FORUM`, `PRIMER`, or `COMMUNITY` |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "error": STRING | null,
  "response": {
    "pagination": {...},
    "data": [
      {
        "event_id": "STRING",
        "content_type": "STRING",
        "call_date": "DATETIME_STRING",
        "title": "STRING",
        "language": "STRING",
        "agenda": ["STRING", ...],
        "insights": [...] | null,
        "transcripts": [...] | null,
        "citation_information": {...}
      }
    ]
  }
}
```

---

### get_third_bridge_event

Get detailed information about a specific Third Bridge expert insight event.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| thirdbridge_event_id | string | **yes** | - | Third Bridge event ID |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "error": STRING | null,
  "event": {
    "event_id": "STRING",
    "content_type": "STRING",
    "call_date": "DATETIME_STRING",
    "title": "STRING",
    "language": "STRING",
    "agenda": ["STRING", ...],
    "insights": [...] | null,
    "citation_information": {...} | null,
    "transcripts": [
      {
        "start_ms": INTEGER,
        "duration_ms": INTEGER,
        "transcript": "STRING",
        "citation_information": {...}
      }
    ]
  }
}
```

---

## Research Tools

### find_research

Find research reports filtered by optional author IDs, provider IDs, regions, countries, and date range. Uses the `/find-research` endpoint with cursor-based pagination.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| start_date | string | no | null | Start date (YYYY-MM-DD). Defaults to 52 weeks ago on the server |
| end_date | string | no | null | End date (YYYY-MM-DD). Defaults to now on the server |
| author_ids | array[string] | no | null | List of author person IDs to filter by |
| aiera_provider_ids | array[string] | no | null | List of Aiera provider IDs to filter by |
| regions | array[string] | no | null | List of regions to filter by (e.g., ['Americas', 'EMEA']) |
| countries | array[string] | no | null | List of country codes to filter by (e.g., ['US', 'GB']) |
| asset_classes | array[string] | no | null | List of asset classes to filter by. Obtain valid values from get_research_asset_classes (e.g., ['Equity', 'Fixed Income']) |
| asset_types | array[string] | no | null | List of asset types to filter by. Obtain valid values from get_research_asset_types (e.g., ['Common Stock', 'Corporate Bond']) |
| subjects | array[string] | no | null | List of subjects to filter by. Obtain valid values from get_research_subjects (e.g., ['Technology', 'Healthcare']) |
| product_focuses | array[string] | no | null | List of product focus values to filter by. Obtain valid values from get_research_product_focuses (e.g., ['Equity Research', 'Credit Research']) |
| discipline_types | array[string] | no | null | List of discipline types to filter by. Obtain valid values from get_research_discipline_types (e.g., ['Fundamental', 'Quantitative']) |
| search | string | no | null | Free-text search term. Matches against title, abstract, and description of research reports |
| search_after | array | no | null | Cursor for pagination. Pass `next_search_after` from a previous response to fetch the next page |
| page_size | integer/string | no | 50 | Number of items per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "result": [
      {
        "research_id": "STRING",
        "document_id": "STRING",
        "aiera_provider_id": "STRING",
        "title": "STRING",
        "abstract": STRING | null,
        "published_datetime": "DATETIME_STRING",
        "organization_name": "STRING",
        "organization_type": "STRING",
        "product_category": "STRING",
        "product_focus": "STRING",
        "language": "STRING",
        "page_count": INTEGER,
        "subjects": ["STRING", ...],
        "asset_classes": ["STRING", ...],
        "asset_types": ["STRING", ...],
        "authors": [
          {
            "name": "STRING",
            "author_id": "STRING"
          }
        ],
        "regions": [],
        "countries": [
          {
            "code": "STRING",
            "primary_indicator": BOOLEAN
          }
        ],
        "citation_information": {
          "title": "STRING",
          "url": "STRING",
          "metadata": {
            "type": "research",
            "url_target": "aiera",
            "document_id": "STRING"
          }
        }
      }
    ],
    "pagination": {
      "total": INTEGER,
      "page_size": INTEGER,
      "has_next_page": BOOLEAN,
      "next_search_after": [STRING, STRING] | null
    }
  },
  "error": STRING | null
}
```

---

### get_research

Get detailed information about a specific research report including summary, metadata, authors, and content. Uses the `/find-research` endpoint with `research_id` and `include_content=true`.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| document_id | string | **yes** | - | The research report document ID to retrieve. Obtain from find_research or search_research results |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "result": [
      {
        "research_id": "STRING",
        "document_id": "STRING",
        "aiera_provider_id": "STRING",
        "title": "STRING",
        "abstract": STRING | null,
        "published_datetime": "DATETIME_STRING",
        "organization_name": "STRING",
        "organization_type": "STRING",
        "product_category": "STRING",
        "product_focus": "STRING",
        "language": "STRING",
        "page_count": INTEGER,
        "subjects": ["STRING", ...],
        "asset_classes": ["STRING", ...],
        "asset_types": ["STRING", ...],
        "authors": [
          {
            "name": "STRING",
            "author_id": "STRING"
          }
        ],
        "regions": [],
        "countries": [
          {
            "code": "STRING",
            "primary_indicator": BOOLEAN
          }
        ],
        "content": ["STRING", ...] | null,
        "citation_information": {
          "title": "STRING",
          "url": "STRING",
          "metadata": {
            "type": "research",
            "url_target": "aiera",
            "document_id": "STRING"
          }
        }
      }
    ]
  },
  "error": STRING | null
}
```

---

### search_research

Semantic search within research content for specific topics, analyses, or insights using embedding-based matching.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query_text | string | **yes** | - | Search query text |
| document_ids | array[string] | no | null | List of document IDs to search within. Obtain from find_research results |
| author_ids | array[string] | no | null | List of author person IDs to filter by |
| aiera_provider_ids | array[string] | no | null | List of Aiera provider IDs to filter by |
| asset_classes | array[string] | no | null | List of asset classes to filter by. Obtain valid values from get_research_asset_classes (e.g., ['Equity', 'Fixed Income']) |
| asset_types | array[string] | no | null | List of asset types to filter by. Obtain valid values from get_research_asset_types (e.g., ['Common Stock', 'Corporate Bond']) |
| start_date | string | no | "" | Start date filter (YYYY-MM-DD) |
| end_date | string | no | "" | End date filter (YYYY-MM-DD) |
| size | integer | no | 20 | Number of results per page (max 250) |
| search_after | array | no | null | Cursor for pagination. Pass `next_search_after` from a previous response to fetch the next page. |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "result": [
      {
        "score": FLOAT,
        "organization_name": "STRING",
        "title": "STRING",
        "research_id": "STRING",
        "document_id": "STRING",
        "chunk_id": "STRING",
        "published_datetime": "DATETIME_STRING",
        "text": "STRING",
        "page": INTEGER,
        "aiera_provider_id": "STRING",
        "authors": [
          {
            "name": "STRING",
            "author_id": "STRING"
          }
        ],
        "citation_information": {
          "title": "STRING",
          "url": "STRING",
          "metadata": {
            "type": "research",
            "url_target": "STRING",
            "document_id": "STRING",
            "page": INTEGER
          }
        }
      }
    ],
    "pagination": {
      "total": INTEGER,
      "page_size": INTEGER,
      "has_next_page": BOOLEAN,
      "next_search_after": [FLOAT, "STRING"] | null
    }
  },
  "error": STRING | null
}
```

---

### get_research_providers

Retrieve all available research providers with their IDs, names, and descriptions. Used to find valid provider IDs for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| search | string | no | null | Search term to filter providers by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": {
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    },
    "data": [
      {
        "provider_id": "STRING",
        "provider_name": "STRING",
        "doc_count": INTEGER
      }
    ]
  },
  "error": STRING | null
}
```

---

### get_research_authors

Search for research authors by name or provider. Returns author IDs and display names. Used to find valid author_ids for filtering find_research and search_research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter authors by display name |
| provider_id | string | no | null | Filter authors by Aiera provider ID. Obtain provider IDs from get_research_providers results |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "author_id": "STRING",
      "name": "STRING"
    }
  ],
  "error": STRING | null
}
```

---

### get_research_asset_classes

Retrieve all available research asset classes with their names and document counts. Used to find valid asset class values for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter asset classes by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "asset_class": "STRING",
      "doc_count": INTEGER
    }
  ],
  "error": STRING | null
}
```

---

### get_research_asset_types

Retrieve all available research asset types with their names and document counts. Used to find valid asset type values for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter asset types by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "asset_type": "STRING",
      "doc_count": INTEGER
    }
  ],
  "error": STRING | null
}
```

---

### get_research_subjects

Retrieve all available research subjects with their names and document counts. Used to find valid subject values for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter subjects by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "subject": "STRING",
      "doc_count": INTEGER
    }
  ],
  "error": STRING | null
}
```

---

### get_research_product_focuses

Retrieve all available research product focus values with their names and document counts. Used to find valid product focus values for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter product focuses by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "product_focus": "STRING",
      "doc_count": INTEGER
    }
  ],
  "error": STRING | null
}
```

---

### get_research_discipline_types

Retrieve all available research discipline types with their names and document counts. Used to find valid discipline type values for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter discipline types by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "discipline_type": "STRING",
      "doc_count": INTEGER
    }
  ],
  "error": STRING | null
}
```

---

### get_research_region_types

Retrieve all available research region types with their names and document counts. Used to find valid region type values for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter region types by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "region": "STRING",
      "doc_count": INTEGER
    }
  ],
  "error": STRING | null
}
```

---

### get_research_country_codes

Retrieve all available research country codes with their names and document counts. Used to find valid country code values for filtering research tools.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter country codes by name |
| page | integer/string | no | 1 | Page number for pagination |
| page_size | integer/string | no | 50 | Results per page (1-100) |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "country_code": "STRING",
      "doc_count": INTEGER
    }
  ],
  "error": STRING | null
}
```

---

## Financial Data Tools

### get_financials

Retrieve financial statement data for a company. Available statement types include Income Statement (revenue, costs, operating income, net income, EPS), Balance Sheet (assets, liabilities, equity, cash position, debt), and Cash Flow Statement (operating cash flow, CapEx, free cash flow, financing activities).

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| bloomberg_ticker | string | **yes** | - | Bloomberg ticker in 'TICKER:COUNTRY' format (e.g., 'AAPL:US') |
| source | string | **yes** | - | Financial statement type: `income-statement`, `balance-sheet`, or `cash-flow-statement` |
| calendar_year | integer | **yes** | - | Calendar year for the financial data |
| source_type | string | no | "standardized" | Data format: `as-reported` (original filings) or `standardized` (normalized data) |
| period | string | no | "annual" | Reporting period: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| calendar_quarter | integer | no | null | Calendar quarter (1-4). Required for quarterly periods |
| ratio_id | string | no | null | Specific ratio ID to filter |
| metric_id | string | no | null | Specific metric ID to filter |
| metric_type | string | no | null | Metric type filter |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": [
    {
      "equity": {
        "equity_id": INTEGER,
        "company_id": INTEGER,
        "name": "STRING",
        "bloomberg_ticker": "STRING",
        "sector_id": INTEGER,
        "subsector_id": INTEGER
      },
      "periods": [
        {
          "period_type": "STRING",
          "report_date": "DATE_STRING",
          "period_duration": "STRING",
          "calendar_year": INTEGER,
          "calendar_quarter": INTEGER | null,
          "fiscal_year": INTEGER,
          "fiscal_quarter": INTEGER | null,
          "is_restated": BOOLEAN | null,
          "earnings_date": "DATETIME_STRING" | null,
          "filing_date": "DATETIME_STRING" | null,
          "metrics": [
            {
              "metric": {
                "metric_name": "STRING",
                "metric_format": "STRING" | null,
                "is_point_in_time": BOOLEAN | null,
                "is_currency": BOOLEAN | null,
                "is_per_share": BOOLEAN | null,
                "is_key_metric": BOOLEAN | null,
                "is_total": BOOLEAN | null,
                "headers": ["STRING", ...]
              },
              "metric_value": FLOAT | null,
              "metric_unit": "STRING" | null,
              "metric_currency": "STRING" | null,
              "metric_is_calculated": BOOLEAN | null,
              "citation_information": {...} | null
            }
          ]
        }
      ]
    }
  ],
  "error": STRING | null
}
```

---

### get_ratios

Retrieve financial ratios for a company, including profitability ratios (ROE, ROA, profit margins), liquidity ratios (current ratio, quick ratio), valuation ratios (P/E, P/B, EV/EBITDA), and leverage ratios (debt-to-equity, interest coverage).

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| bloomberg_ticker | string | **yes** | - | Bloomberg ticker in 'TICKER:COUNTRY' format (e.g., 'AAPL:US') |
| calendar_year | integer | **yes** | - | Calendar year for the ratio data |
| period | string | no | "annual" | Reporting period: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| calendar_quarter | integer | no | null | Calendar quarter (1-4). Required for quarterly periods |
| ratio_id | string | no | null | Specific ratio ID to filter |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": [
    {
      "equity": {
        "equity_id": INTEGER,
        "company_id": INTEGER,
        "name": "STRING",
        "bloomberg_ticker": "STRING",
        "sector_id": INTEGER,
        "subsector_id": INTEGER
      },
      "periods": [
        {
          "period_type": "STRING",
          "report_date": "DATE_STRING",
          "period_duration": "STRING",
          "calendar_year": INTEGER,
          "calendar_quarter": INTEGER | null,
          "fiscal_year": INTEGER,
          "fiscal_quarter": INTEGER | null,
          "ratios": [
            {
              "ratio_id": "STRING",
              "ratio": "STRING",
              "ratio_category": "STRING",
              "ratio_value": FLOAT | null
            }
          ]
        }
      ]
    }
  ],
  "error": STRING | null
}
```

---

### get_kpis_and_segments

Retrieve KPIs (Key Performance Indicators) and business segment data for a company. KPIs include subscriber counts, unit sales, average selling prices, same-store sales, etc. Segments provide revenue and metrics broken down by business unit, geography, or product line. These metrics are company-specific and vary by industry.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| bloomberg_ticker | string | **yes** | - | Bloomberg ticker in 'TICKER:COUNTRY' format (e.g., 'AAPL:US') |
| calendar_year | integer | **yes** | - | Calendar year for the KPI and segment data |
| period | string | no | "annual" | Reporting period: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| calendar_quarter | integer | no | null | Calendar quarter (1-4). Required for quarterly periods |
| metric_id | string | no | null | Specific metric ID to filter |
| metric_type | string | no | null | Metric type filter |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": [
    {
      "equity": {
        "equity_id": INTEGER,
        "company_id": INTEGER,
        "name": "STRING",
        "bloomberg_ticker": "STRING",
        "sector_id": INTEGER,
        "subsector_id": INTEGER
      },
      "periods": [
        {
          "period_type": "STRING",
          "report_date": "DATE_STRING",
          "period_duration": "STRING",
          "calendar_year": INTEGER,
          "calendar_quarter": INTEGER | null,
          "fiscal_year": INTEGER,
          "fiscal_quarter": INTEGER | null,
          "kpi": [
            {
              "metric_id": "STRING",
              "metric_name": "STRING",
              "metric_format": "STRING" | null,
              "is_currency": BOOLEAN | null,
              "is_important": BOOLEAN | null,
              "metric_value": FLOAT | null
            }
          ],
          "segment": [
            {
              "metric_id": "STRING",
              "metric_name": "STRING",
              "metric_format": "STRING" | null,
              "is_currency": BOOLEAN | null,
              "is_important": BOOLEAN | null,
              "metric_value": FLOAT | null
            }
          ]
        }
      ]
    }
  ],
  "error": STRING | null
}
```

---

## Web Search Tools

### trusted_web_search

Search the web using only trusted/approved domains relevant to financial professionals. By default, searches across trusted sources including cnbc.com, bloomberg.com, reuters.com, wsj.com, apnews.com, and other Aiera-approved domains.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | **yes** | - | The search query to find relevant news and articles from trusted financial sources |
| allowed_domains | string | no | null | Comma-separated list of allowed domains to restrict search results (e.g., 'cnbc.com,reuters.com'). If omitted, will use Aiera's curated list of trusted domains |
| include_base_instructions | boolean | no | true | Include base instructions |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt for context |
| self_identification | string | no | null | Self-identified information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": ["STRING", ...],
  "response": [
    {
      "title": "STRING",
      "snippet": "STRING",
      "score": FLOAT,
      "citation_information": {
        "title": "STRING",
        "url": "STRING",
        "metadata": {
          "type": "web_result",
          "url_target": "external"
        }
      }
    }
  ],
  "error": STRING | null
}
```

---

## Reference Data Tools

### get_available_indexes

Retrieve all available stock market indices with their IDs.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": [...] | null,
  "response": [
    {
      "index_id": INTEGER,
      "name": "STRING",
      "short_name": "STRING"
    }
  ],
  "error": STRING | null
}
```

---

### get_index_constituents

Get all equities within a specific stock market index.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| index | string/integer | **yes** | - | Index ID or short name |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "data": [
    {
      "equity_id": INTEGER,
      "company_id": INTEGER,
      "name": "STRING",
      "bloomberg_ticker": "STRING",
      "sector_id": INTEGER,
      "subsector_id": INTEGER,
      "primary_equity": BOOLEAN | null,
      "created": "DATETIME_STRING",
      "modified": "DATETIME_STRING"
    }
  ],
  "pagination": {...}
}
```

---

### get_available_watchlists

Retrieve all available watchlists with their IDs.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "instructions": [...] | null,
  "response": [
    {
      "watchlist_id": INTEGER,
      "name": "STRING",
      "type": "STRING"
    }
  ],
  "error": STRING | null
}
```

---

### get_watchlist_constituents

Get all equities within a specific watchlist.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| watchlist_id | string/integer | **yes** | - | Watchlist ID |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "data": [
    {
      "equity_id": INTEGER,
      "company_id": INTEGER,
      "name": "STRING",
      "bloomberg_ticker": "STRING",
      "sector_id": INTEGER,
      "subsector_id": INTEGER,
      "primary_equity": BOOLEAN,
      "created": "DATETIME_STRING",
      "modified": "DATETIME_STRING"
    }
  ],
  "pagination": {...}
}
```

---

### get_sectors_and_subsectors

Retrieve all available sectors and subsectors with their IDs.

**Input Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | no | null | Search term to filter |
| page | integer/string | no | 1 | Page number |
| page_size | integer/string | no | 50 | Results per page |
| exclude_instructions | boolean | no | false | Exclude all instructions in response |
| originating_prompt | string | no | null | Original user prompt |
| self_identification | string | no | null | Self-identied information about the user/server/session, used for tracking purposes |

**Output Structure:**
```json
{
  "response": [
    {
      "sector_id": INTEGER,
      "name": "STRING",
      "gics_code": "STRING",
      "subsectors": [
        {
          "subsector_id": INTEGER,
          "name": "STRING",
          "gics_code": "STRING",
          "gics_industry_code": "STRING"
        }
      ]
    }
  ]
}
```

---

## Common Response Elements

### Instructions Array
Most responses include an `instructions` array with guidance for handling the data:
```json
{
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **DAY, MONTH DD, YYYY**...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ]
}
```

### Citation Information Object
Most data items include citation information for proper attribution:
```json
{
  "citation_information": {
    "title": "STRING",
    "url": "STRING",
    "metadata": {
      "type": "STRING",  // "event", "filing", "company_doc", "conference", "company", "research"
      "url_target": "STRING",  // "aiera" or "external"
      "company_id": INTEGER,
      "event_id": INTEGER | null,
      "transcript_item_id": INTEGER | null,
      "filing_id": INTEGER | null,
      "content_id": INTEGER | null,
      "company_doc_id": INTEGER | null,
      "conference_id": INTEGER | null,
      "research_id": STRING | null
    }
  }
}
```

### Pagination Object
List endpoints return pagination information:
```json
{
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  }
}
```

---

## Event Types Reference

| event_type            | Description                                       |
|-----------------------|---------------------------------------------------|
| `earnings`            | Earnings calls and quarterly results              |
| `presentation`        | Investor presentations and conference calls       |
| `investor_meeting`    | Investor meetings and analyst days                |
| `shareholder_meeting` | Annual/special shareholder meetings               |
| `special_situation`   | M&A announcements and other corporate actions     |
