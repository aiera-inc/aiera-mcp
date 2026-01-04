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

## POST /search/{index}

Executes a raw OpenSearch query against the specified index.

**Path Parameters:**

| Parameter  | Type   | Description                                                                                                                       |
|------------|--------|-----------------------------------------------------------------------------------------------------------------------------------|
| `index`    | string | Index to search. Valid values: `events`, `transcripts`, `filings`, `filing-chunks`, `attachments`, `company_docs`, `third_bridge` |

**Request Body (JSON):**

The request body should contain a valid OpenSearch query object. Special parameters can be included at the top level:

| Parameter                   | Type    | Default  | Description                   |
|-----------------------------|---------|----------|-------------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions     |
| `originating_prompt`        | string  | -        | Original prompt               |
| `self_identification`       | string  | -        | Caller identifier             |

**Response:**

Response varies by index type:

### /search/transcripts

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "result": [
      {
        "score": FLOAT,
        "date": "ISO_DATETIME",
        "primary_company_id": INTEGER,
        "content_id": INTEGER,
        "transcript_event_id": INTEGER,
        "transcript_section": "STRING_OR_NULL",
        "speaker_name": "STRING_OR_NULL",
        "speaker_title": "STRING_OR_NULL",
        "text": "STRING",
        "primary_equity_id": INTEGER,
        "title": "STRING",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER,
            "transcript_item_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

### /search/events

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "result": [
      {
        "score": FLOAT,
        "date": "ISO_DATETIME",
        "primary_company_id": INTEGER,
        "content_id": INTEGER,
        "text": "STRING",
        "primary_equity_id": INTEGER,
        "title": "STRING",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

### /search/filing-chunks

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "result": [
      {
        "score": FLOAT,
        "date": "ISO_DATE",
        "primary_company_id": INTEGER,
        "content_id": INTEGER,
        "filing_id": INTEGER,
        "company_common_name": "STRING",
        "filing_type": "STRING",
        "primary_equity_id": INTEGER,
        "text": "STRING",
        "title": "STRING",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "filing_id": INTEGER,
            "content_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

### /search/filings

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "result": [
      {
        "score": FLOAT,
        "date": "ISO_DATE",
        "primary_company_id": INTEGER,
        "content_id": INTEGER,
        "filing_id": INTEGER,
        "company_common_name": "STRING",
        "filing_type": "STRING",
        "primary_equity_id": INTEGER,
        "text": "STRING",
        "title": "STRING",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "filing_id": INTEGER,
            "content_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

### /search/attachments

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "result": [
      {
        "score": FLOAT,
        "date": "ISO_DATETIME",
        "primary_company_id": INTEGER,
        "content_id": INTEGER,
        "event_id": INTEGER,
        "attachment_type": "STRING",
        "text": "STRING",
        "primary_equity_id": INTEGER,
        "title": "STRING",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "event_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

---

## GET /get-financials

Retrieves financial statement data for the specified company.

**Query Parameters:**

| Parameter                   | Type    | Default        | Description                                                                          |
|-----------------------------|---------|----------------|--------------------------------------------------------------------------------------|
| `include_base_instructions` | boolean | `true`         | Include base instructions                                                            |
| `originating_prompt`        | string  | -              | Original prompt                                                                      |
| `self_identification`       | string  | -              | Caller identifier                                                                    |
| `bloomberg_ticker`          | string  | -              | Bloomberg ticker symbol                                                              |
| `source`                    | string  | **required**   | Financial statement type: `income-statement`, `balance-sheet`, `cash-flow-statement` |
| `source_type`               | string  | `standardized` | Data format: `as-reported`, `standardized`                                           |
| `period`                    | string  | `annual`       | Period type: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest`            |
| `fiscal_year`               | string  | -              | Fiscal year                                                                          |
| `fiscal_quarter`            | string  | -              | Fiscal quarter                                                                       |
| `calendar_year`             | string  | **required**   | Calendar year (e.g., `2024`)                                                         |
| `calendar_quarter`          | string  | -              | Calendar quarter (e.g., `Q1`)                                                        |
| `ratio_id`                  | string  | -              | Specific ratio ID                                                                    |
| `metric_id`                 | string  | -              | Specific metric ID                                                                   |
| `metric_type`               | string  | -              | Metric type filter                                                                   |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
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
          "report_date": "DATE",
          "period_duration": "STRING",
          "calendar_year": INTEGER,
          "calendar_quarter": INTEGER,
          "fiscal_year": INTEGER,
          "fiscal_quarter": INTEGER,
          "is_restated": BOOLEAN,
          "earnings_date": "DATETIME",
          "filing_date": "DATETIME",
          "metrics": [
            {
              "metric": {
                "metric_name": "STRING",
                "metric_format": "STRING",
                "is_point_in_time": BOOLEAN,
                "is_currency": BOOLEAN,
                "is_per_share": BOOLEAN,
                "is_key_metric": BOOLEAN,
                "is_total": BOOLEAN,
                "headers": "LIST_OR_NULL"
              },
              "metric_value": INTEGER,
              "metric_unit": "STRING",
              "metric_currency": "STRING",
              "metric_is_calculated": BOOLEAN,
              "citation_information": {
                "title": "STRING",
                "url": "URL",
                "metadata": {
                  "type": "STRING",
                  "url_target": "STRING"
                }
              }
            }, ...
          ]
        }, ...
      ]
    }, ...
  ]
}
```

---

## GET /get-ratios

Retrieves financial ratios for the specified company.

**Query Parameters:**

| Parameter                   | Type    | Default      | Description                                                               |
|-----------------------------|---------|--------------|---------------------------------------------------------------------------|
| `include_base_instructions` | boolean | `true`       | Include base instructions                                                 |
| `originating_prompt`        | string  | -            | Original prompt                                                           |
| `self_identification`       | string  | -            | Caller identifier                                                         |
| `bloomberg_ticker`          | string  | -            | Bloomberg ticker symbol                                                   |
| `period`                    | string  | `annual`     | Period type: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| `calendar_year`             | string  | **required** | Calendar year                                                             |
| `calendar_quarter`          | string  | -            | Calendar quarter                                                          |
| `ratio_id`                  | string  | -            | Specific ratio ID to filter                                               |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
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
          "report_date": "DATE",
          "period_duration": "STRING",
          "calendar_year": INTEGER,
          "calendar_quarter": INTEGER,
          "fiscal_year": INTEGER,
          "fiscal_quarter": INTEGER,
          "ratios": [
            {
              "ratio_id": "STRING",
              "ratio": "STRING",
              "ratio_category": "STRING",
              "ratio_value": FLOAT
            }, ...
          ]
        }, ...
      ]
    }, ...
  ]
}
```

---

## GET /get-segments-and-kpis

Retrieves segment data and KPIs for the specified company.

**Query Parameters:**

| Parameter                   | Type    | Default      | Description                                                               |
|-----------------------------|---------|--------------|---------------------------------------------------------------------------|
| `include_base_instructions` | boolean | `true`       | Include base instructions                                                 |
| `originating_prompt`        | string  | -            | Original prompt                                                           |
| `self_identification`       | string  | -            | Caller identifier                                                         |
| `bloomberg_ticker`          | string  | -            | Bloomberg ticker symbol                                                   |
| `period`                    | string  | `annual`     | Period type: `annual`, `quarterly`, `semi-annual`, `ltm`, `ytd`, `latest` |
| `calendar_year`             | string  | **required** | Calendar year                                                             |
| `calendar_quarter`          | string  | -            | Calendar quarter                                                          |
| `metric_id`                 | string  | -            | Specific metric ID                                                        |
| `metric_type`               | string  | -            | Metric type filter                                                        |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
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
          "report_date": "DATE",
          "period_duration": "STRING",
          "calendar_year": INTEGER,
          "calendar_quarter": INTEGER,
          "fiscal_year": INTEGER,
          "fiscal_quarter": INTEGER,
          "kpi": [
            {
              "metric_id": "STRING",
              "metric_name": "STRING",
              "metric_format": "STRING",
              "is_currency": BOOLEAN,
              "is_important": BOOLEAN,
              "metric_value": INTEGER
            }, ...
          ],
          "segment": [
            {
              "metric_id": "STRING",
              "metric_name": "STRING",
              "metric_format": "STRING",
              "is_currency": BOOLEAN,
              "is_important": BOOLEAN,
              "metric_value": INTEGER
            }, ...
          ]
        }, ...
      ]
    }, ...
  ]
}
```

---

## GET /available-watchlists

Returns the list of watchlists available to the authenticated user.

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                |
|-----------------------------|---------|----------|----------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions  |
| `originating_prompt`        | string  | -        | Original prompt            |
| `self_identification`       | string  | -        | Caller identifier          |
| `search`                    | string  | -        | Search term                |
| `page`                      | integer | `1`      | Page number                |
| `page_size`                 | integer | `50`     | Results per page (max 100) |

**Response:**

```json
{
  "response": [
    {
      "watchlist_id": INTEGER,
      "name": "STRING",
      "type": "STRING"
    }, ...
  ]
}
```

---

## GET /watchlist-constituents/{watchlist_id}

Returns the equities contained in a specific watchlist.

**Path Parameters:**

| Parameter      | Type    | Description             |
|----------------|---------|-------------------------|
| `watchlist_id` | integer | The ID of the watchlist |

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                |
|-----------------------------|---------|----------|----------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions  |
| `originating_prompt`        | string  | -        | Original prompt            |
| `self_identification`       | string  | -        | Caller identifier          |
| `search`                    | string  | -        | Search term                |
| `page`                      | integer | `1`      | Page number                |
| `page_size`                 | integer | `50`     | Results per page (max 100) |

**Response:**

```json
{
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "equity_id": INTEGER,
      "company_id": INTEGER,
      "name": "STRING",
      "bloomberg_ticker": "STRING",
      "sector_id": INTEGER,
      "subsector_id": INTEGER,
      "primary_equity": BOOLEAN,
      "created": "ISO_DATETIME",
      "modified": "ISO_DATETIME"
    }, ...
  ]
}
```

---

## GET /available-indexes

Returns the list of available market indices.

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                |
|-----------------------------|---------|----------|----------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions  |
| `originating_prompt`        | string  | -        | Original prompt            |
| `self_identification`       | string  | -        | Caller identifier          |
| `search`                    | string  | -        | Search term                |
| `page`                      | integer | `1`      | Page number                |
| `page_size`                 | integer | `50`     | Results per page (max 100) |

**Response:**

```json
{
  "response": [
    {
      "index_id": INTEGER,
      "name": "STRING",
      "short_name": "STRING"
    }, ...
  ]
}
```

---

## GET /index-constituents/{index}

Returns the equities contained in a specific market index.

**Path Parameters:**

| Parameter  | Type           | Description                           |
|------------|----------------|---------------------------------------|
| `index`    | string/integer | Index ID, short name, or display name |

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                |
|-----------------------------|---------|----------|----------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions  |
| `originating_prompt`        | string  | -        | Original prompt            |
| `self_identification`       | string  | -        | Caller identifier          |
| `search`                    | string  | -        | Search term                |
| `page`                      | integer | `1`      | Page number                |
| `page_size`                 | integer | `50`     | Results per page (max 100) |

**Response:**

```json
{
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": [
    {
      "equity_id": INTEGER,
      "company_id": INTEGER,
      "name": "STRING",
      "bloomberg_ticker": "STRING",
      "sector_id": INTEGER,
      "sub_sector_id": INTEGER,
      "primary_equity": BOOLEAN,
      "created": "ISO_DATETIME",
      "modified": "ISO_DATETIME"
    }, ...
  ]
}
```

---

## GET /estimated-and-upcoming-events

Returns estimated future events and confirmed upcoming events for specified equities.

**Query Parameters:**

| Parameter                   | Type     | Default       | Description                        |
|-----------------------------|----------|---------------|------------------------------------|
| `include_base_instructions` | boolean  | `true`        | Include base instructions          |
| `originating_prompt`        | string   | -             | Original prompt                    |
| `self_identification`       | string   | -             | Caller identifier                  |
| `search`                    | string   | -             | Search term to filter events       |
| `bloomberg_ticker`          | string   | -             | Bloomberg ticker symbol            |
| `equity_ids`                | string   | -             | Comma-separated list of equity IDs |
| `index_id`                  | integer  | -             | Filter by market index             |
| `watchlist_id`              | integer  | -             | Filter by user watchlist           |
| `sector_id`                 | integer  | -             | Filter by GICS sector              |
| `subsector_id`              | integer  | -             | Filter by GICS subsector           |
| `start_date`                | datetime | now           | Start of date range (ISO 8601)     |
| `end_date`                  | datetime | now + 8 weeks | End of date range (ISO 8601)       |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
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
          "subsector_id": INTEGER
        },
        "estimate": {
          "call_type": "STRING",
          "call_date": "ISO_DATETIME",
          "title": "STRING"
        },
        "actual": {
          "scheduled_audio_call_id": INTEGER,
          "call_type": "STRING",
          "call_date": "ISO_DATETIME",
          "title": "STRING",
          "url": "URL"
        },
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER
          }
        }
      },
      {
        "estimate_id": INTEGER,
        "equity": {
          "equity_id": INTEGER,
          "company_id": INTEGER,
          "name": "STRING",
          "bloomberg_ticker": "STRING",
          "sector_id": INTEGER,
          "subsector_id": INTEGER
        },
        "estimate": {
          "call_type": "STRING",
          "call_date": "ISO_DATETIME",
          "title": "STRING"
        },
        "actual": NULL,
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER
          }
        }
      }, ...
    ],
    "actuals": [
      {
        "event_id": INTEGER,
        "equity": {
          "equity_id": INTEGER,
          "company_id": INTEGER,
          "name": "STRING",
          "bloomberg_ticker": "STRING",
          "sector_id": INTEGER,
          "subsector_id": INTEGER
        },
        "call_type": "STRING",
        "call_date": "ISO_DATETIME",
        "title": "STRING",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

---

## GET /find-events

Searches for events with optional transcript inclusion.

**Query Parameters:**

| Parameter                   | Type     | Default       | Description                                                |
|-----------------------------|----------|---------------|------------------------------------------------------------|
| `include_base_instructions` | boolean  | `true`        | Include base instructions                                  |
| `originating_prompt`        | string   | -             | Original prompt                                            |
| `self_identification`       | string   | -             | Caller identifier                                          |
| `bloomberg_ticker`          | string   | -             | Bloomberg ticker symbol                                    |
| `sector_id`                 | integer  | -             | Filter by GICS sector                                      |
| `subsector_id`              | integer  | -             | Filter by GICS subsector                                   |
| `index_id`                  | integer  | -             | Filter by market index                                     |
| `watchlist_id`              | integer  | -             | Filter by user watchlist                                   |
| `conference_id`             | integer  | -             | Filter by conference/event group                           |
| `event_id`                  | integer  | -             | Single event ID to retrieve                                |
| `event_ids`                 | string   | -             | Comma-separated list of event IDs                          |
| `event_type`                | string   | -             | Comma-separated event types (e.g., `earnings`, `guidance`) |
| `start_date`                | datetime | now - 2 weeks | Start of date range                                        |
| `end_date`                  | datetime | now + 2 weeks | End of date range (max 8 weeks out)                        |
| `include_transcripts`       | boolean  | `false`       | Include transcript content                                 |
| `event_category`            | string   | -             | Filter by category: `expert_insights`, `thirdbridge`       |
| `transcript_section`        | string   | -             | Filter transcript by section: `q_and_a`, `presentation`    |
| `page`                      | integer  | `1`           | Page number                                                |
| `page_size`                 | integer  | `50`          | Results per page (max 100)                                 |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    },
    "data": [
      {
        "event_id": INTEGER,
        "equity": {
          "equity_id": INTEGER,
          "company_id": INTEGER,
          "name": "STRING",
          "bloomberg_ticker": "STRING",
          "sector_id": INTEGER,
          "subsector_id": INTEGER,
          "primary_equity": BOOLEAN
        },
        "title": "STRING",
        "event_type": "STRING",
        "event_date": "ISO_DATETIME",
        "event_category": "STRING",
        "expected_language": "STRING",
        "conference": {
          "conference_id": INTEGER_OR_NULL,
          "conference_name": "STRING_OR_NULL"
        },
        "summary": {
          "title": "STRING",
          "summary": ["STRING", ...]
        },
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER
          }
        },
        "transcripts": [
          {
            "transcript_item_id": INTEGER,
            "transcript": "STRING",
            "timestamp": "ISO_DATETIME",
            "speaker": "STRING",
            "speaker_type": "STRING",
            "transcript_section": "STRING_OR_NULL",
            "citation_information": {
              "title": "STRING",
              "url": "URL",
              "metadata": {
                "type": "STRING",
                "url_target": "STRING",
                "company_id": INTEGER,
                "event_id": INTEGER,
                "transcript_item_id": INTEGER
              }
            }
          }, ...
        ]
      }, ...
    ]
  }
}
```

Note: The `transcripts` array is only included when `include_transcripts=true`. When transcripts are included, the `summary` field will be `null`.

---

## GET /find-conferences

Searches for investment conferences and event groups.

**Query Parameters:**

| Parameter                   | Type     | Default       | Description                |
|-----------------------------|----------|---------------|----------------------------|
| `include_base_instructions` | boolean  | `true`        | Include base instructions  |
| `originating_prompt`        | string   | -             | Original prompt            |
| `self_identification`       | string   | -             | Caller identifier          |
| `start_date`                | datetime | now - 2 weeks | Start of date range        |
| `end_date`                  | datetime | now + 2 weeks | End of date range          |
| `page`                      | integer  | `1`           | Page number                |
| `page_size`                 | integer  | `50`          | Results per page (max 100) |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    },
    "data": [
      {
        "conference_id": INTEGER,
        "title": "STRING",
        "event_count": INTEGER,
        "start_date": "ISO_DATETIME",
        "end_date": "ISO_DATETIME",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "conference_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

---

## GET /equity-summaries

Returns comprehensive summary information for specified equities including leadership, indices, events, and estimates.

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                            |
|-----------------------------|---------|----------|----------------------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions              |
| `originating_prompt`        | string  | -        | Original prompt                        |
| `self_identification`       | string  | -        | Caller identifier                      |
| `bloomberg_ticker`          | string  | -        | Bloomberg ticker symbol                |
| `equity_ids`                | string  | -        | Comma-separated list of equity IDs     |
| `index_id`                  | integer | -        | Filter by market index                 |
| `watchlist_id`              | integer | -        | Filter by user watchlist               |
| `lookback`                  | integer | `90`     | Number of days to look back for events |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
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
      "created": "ISO_DATETIME",
      "modified": "ISO_DATETIME",
      "status": "STRING",
      "leadership": [
        {
          "name": "STRING",
          "title": "STRING",
          "event_count": INTEGER,
          "last_event_date": "ISO_DATETIME"
        }, ...
      ],
      "indices": ["STRING", "STRING", ...],
      "confirmed_events": {
        "past": [
          {
            "event_id": INTEGER,
            "title": "STRING",
            "event_type": "STRING",
            "event_date": "ISO_DATETIME",
            "fiscal_quarter": INTEGER,
            "fiscal_year": INTEGER,
            "has_human_verified": BOOLEAN,
            "has_live_transcript": BOOLEAN,
            "has_audio": BOOLEAN,
            "summary": {
              "title": "STRING",
              "content": ["STRING", ...]
            },
            "citation_information": {
              "title": "STRING",
              "url": "URL",
              "metadata": {
                "type": "STRING",
                "url_target": "STRING",
                "company_id": INTEGER,
                "event_id": INTEGER
              }
            }
          }, ...
        ],
        "upcoming": [
          {
            "event_id": INTEGER,
            "title": "STRING",
            "event_type": "STRING",
            "event_date": "ISO_DATETIME",
            "fiscal_quarter": INTEGER,
            "fiscal_year": INTEGER,
            "citation_information": {
              "title": "STRING",
              "url": "URL",
              "metadata": {
                "type": "STRING",
                "url_target": "STRING",
                "company_id": INTEGER,
                "event_id": INTEGER
              }
            }
          }, ...
        ]
      },
      "estimated_events": [
        {
          "estimate_id": INTEGER,
          "estimate_date": "ISO_DATETIME",
          "estimate_type": "STRING",
          "estimate_title": "STRING"
        }, ...
      ]
    }
  ]
}
```

---

## GET /find-filings

Searches for SEC filings and regulatory documents.

**Query Parameters:**

| Parameter                   | Type     | Default        | Description                                       |
|-----------------------------|----------|----------------|---------------------------------------------------|
| `include_base_instructions` | boolean  | `true`         | Include base instructions                         |
| `originating_prompt`        | string   | -              | Original prompt                                   |
| `self_identification`       | string   | -              | Caller identifier                                 |
| `search`                    | string   | -              | Search term to filter filings                     |
| `bloomberg_ticker`          | string   | -              | Bloomberg ticker symbol                           |
| `sector_id`                 | integer  | -              | Filter by GICS sector                             |
| `subsector_id`              | integer  | -              | Filter by GICS subsector                          |
| `watchlist_id`              | integer  | -              | Filter by user watchlist                          |
| `index_id`                  | integer  | -              | Filter by market index                            |
| `filing_id`                 | integer  | -              | Single filing ID to retrieve                      |
| `filing_ids`                | string   | -              | Comma-separated list of filing IDs                |
| `form_number`               | string   | -              | Filter by form type (e.g., `10-K`, `10-Q`, `8-K`) |
| `start_date`                | datetime | now - 12 weeks | Start of date range                               |
| `end_date`                  | datetime | now            | End of date range                                 |
| `include_delisted`          | boolean  | `true`         | Include filings from delisted companies           |
| `include_content`           | boolean  | `false`        | Include raw filing content                        |
| `company_rollup`            | boolean  | `true`         | Roll up to company level                          |
| `page`                      | integer  | `1`            | Page number                                       |
| `page_size`                 | integer  | `50`           | Results per page (max 100)                        |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    },
    "data": [
      {
        "filing_id": INTEGER,
        "equity": {
          "equity_id": INTEGER,
          "company_id": INTEGER,
          "name": "STRING",
          "bloomberg_ticker": "STRING",
          "sector_id": INTEGER,
          "subsector_id": INTEGER
        },
        "title": "STRING",
        "form_number": "STRING",
        "form_name": "STRING",
        "filing_organization": "STRING",
        "filing_system": "STRING",
        "is_amendment": INTEGER,
        "period_end_date": "ISO_DATETIME",
        "release_date": "ISO_DATETIME",
        "arrival_date": "ISO_DATETIME",
        "pulled_date": "ISO_DATETIME",
        "json_synced": BOOLEAN,
        "datafiles_synced": BOOLEAN,
        "summary": ["STRING", ...],
        "content_raw": "STRING_OR_NULL",
        "datafiles": [
          {
            "description": "STRING",
            "file_type": "STRING",
            "content_raw": "STRING"
          }, ...
        ],
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "filing_id": INTEGER,
            "content_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

Note: `content_raw` and `datafiles` are only included when `include_content=true`.

---

## GET /find-company-docs

Searches for company documents (investor presentations, annual reports, etc.).

**Query Parameters:**

| Parameter                   | Type     | Default       | Description                               |
|-----------------------------|----------|---------------|-------------------------------------------|
| `include_base_instructions` | boolean  | `true`        | Include base instructions                 |
| `originating_prompt`        | string   | -             | Original prompt                           |
| `self_identification`       | string   | -             | Caller identifier                         |
| `start_date`                | datetime | now - 4 weeks | Start of date range                       |
| `end_date`                  | datetime | now           | End of date range                         |
| `categories`                | string   | -             | Comma-separated category names to include |
| `exclude_categories`        | string   | -             | Comma-separated category names to exclude |
| `keywords`                  | string   | -             | Comma-separated keywords to include       |
| `exclude_keywords`          | string   | -             | Comma-separated keywords to exclude       |
| `bloomberg_ticker`          | string   | -             | Bloomberg ticker symbol                   |
| `sector_id`                 | integer  | -             | Filter by GICS sector                     |
| `subsector_id`              | integer  | -             | Filter by GICS subsector                  |
| `watchlist_id`              | integer  | -             | Filter by user watchlist                  |
| `index_id`                  | integer  | -             | Filter by market index                    |
| `company_doc_id`            | integer  | -             | Single document ID to retrieve            |
| `company_doc_ids`           | string   | -             | Comma-separated list of document IDs      |
| `include_delisted`          | boolean  | `true`        | Include docs from delisted companies      |
| `include_content`           | boolean  | `false`       | Include raw document content              |
| `company_rollup`            | boolean  | `true`        | Roll up to company level                  |
| `page`                      | integer  | `1`           | Page number                               |
| `page_size`                 | integer  | `50`          | Results per page (max 100)                |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    },
    "data": [
      {
        "doc_id": INTEGER,
        "company": {
          "company_id": INTEGER,
          "name": "STRING"
        },
        "publish_date": "ISO_DATE",
        "category": "STRING",
        "title": "STRING",
        "source_url": "URL",
        "summary": ["STRING", ...],
        "keywords": ["STRING", ...],
        "processed": "ISO_DATETIME",
        "created": "ISO_DATETIME",
        "modified": "ISO_DATETIME",
        "content_raw": "STRING_OR_NULL",
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "company_doc_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

Note: `content_raw` is only included when `include_content=true`.

---

## GET /find-equities

Searches for equities/companies in the Aiera database.

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                        |
|-----------------------------|---------|----------|------------------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions          |
| `originating_prompt`        | string  | -        | Original prompt                    |
| `self_identification`       | string  | -        | Caller identifier                  |
| `bloomberg_ticker`          | string  | -        | Bloomberg ticker symbol            |
| `sector_id`                 | string  | -        | Filter by GICS sector              |
| `subsector_id`              | string  | -        | Filter by GICS subsector           |
| `search`                    | string  | -        | Search by company name or ticker   |
| `include_inactive`          | boolean | `false`  | Include inactive/delisted equities |
| `page`                      | integer | `1`      | Page number                        |
| `page_size`                 | integer | `50`     | Results per page (max 100)         |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    },
    "data": [
      {
        "equity_id": INTEGER,
        "company_id": INTEGER,
        "name": "STRING",
        "bloomberg_ticker": "STRING",
        "sector_id": INTEGER,
        "subsector_id": INTEGER,
        "primary_equity": BOOLEAN,
        "created": "ISO_DATETIME",
        "modified": "ISO_DATETIME"
      }, ...
    ]
  }
}
```

---

## GET /get-sectors-and-subsectors

Returns the complete list of GICS sectors and subsectors.

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                |
|-----------------------------|---------|----------|----------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions  |
| `originating_prompt`        | string  | -        | Original prompt            |
| `self_identification`       | string  | -        | Caller identifier          |
| `search`                    | string  | -        | Search term                |
| `page`                      | integer | `1`      | Page number                |
| `page_size`                 | integer | `50`     | Results per page (max 100) |

**Response:**

```json
{
  "response": [
    {
      "sector_id": INTEGER,
      "gics_code": "STRING",
      "name": "STRING",
      "subsectors": [
        {
          "subsector_id": INTEGER,
          "gics_code": "STRING",
          "gics_industry_code": "STRING",
          "name": "STRING"
        }, ...
      ]
    }, ...
  ]
}
```

---

## GET /get-company-doc-categories

Returns available company document categories with counts.

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                |
|-----------------------------|---------|----------|----------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions  |
| `originating_prompt`        | string  | -        | Original prompt            |
| `self_identification`       | string  | -        | Caller identifier          |
| `search`                    | string  | -        | Search/filter categories   |
| `page`                      | integer | `1`      | Page number                |
| `page_size`                 | integer | `50`     | Results per page (max 100) |

**Response:**

```json
{
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": {
    "CATEGORY_NAME": INTEGER,
    "CATEGORY_NAME": INTEGER,
    ...
  }
}
```

---

## GET /get-company-doc-keywords

Returns available company document keywords with counts.

**Query Parameters:**

| Parameter                   | Type    | Default  | Description                |
|-----------------------------|---------|----------|----------------------------|
| `include_base_instructions` | boolean | `true`   | Include base instructions  |
| `originating_prompt`        | string  | -        | Original prompt            |
| `self_identification`       | string  | -        | Caller identifier          |
| `search`                    | string  | -        | Search/filter keywords     |
| `page`                      | integer | `1`      | Page number                |
| `page_size`                 | integer | `50`     | Results per page (max 100) |

**Response:**

```json
{
  "pagination": {
    "total_count": INTEGER,
    "current_page": INTEGER,
    "total_pages": INTEGER,
    "page_size": INTEGER
  },
  "data": {
    "KEYWORD": INTEGER,
    "KEYWORD": INTEGER,
    ...
  }
}
```

---

## GET /find-third-bridge

Searches for Third Bridge expert content (forums, primers, community).

**Query Parameters:**

| Parameter                   | Type     | Default               | Description                                    |
|-----------------------------|----------|-----------------------|------------------------------------------------|
| `include_base_instructions` | boolean  | `true`                | Include base instructions                      |
| `originating_prompt`        | string   | -                     | Original prompt                                |
| `self_identification`       | string   | -                     | Caller identifier                              |
| `search`                    | string   | -                     | Search term to filter content                  |
| `bloomberg_ticker`          | string   | -                     | Bloomberg ticker symbol                        |
| `sector_id`                 | integer  | -                     | Filter by GICS sector                          |
| `subsector_id`              | integer  | -                     | Filter by GICS subsector                       |
| `index_id`                  | integer  | -                     | Filter by market index                         |
| `watchlist_id`              | integer  | -                     | Filter by user watchlist                       |
| `event_id`                  | string   | -                     | Single Third Bridge event ID                   |
| `event_ids`                 | string   | -                     | Comma-separated list of event IDs              |
| `start_date`                | datetime | now - 4 weeks         | Start of date range                            |
| `end_date`                  | datetime | now (max 8 weeks out) | End of date range                              |
| `include_transcripts`       | boolean  | `false`               | Include transcript content                     |
| `content_type`              | string   | -                     | Filter by type: `FORUM`, `PRIMER`, `COMMUNITY` |
| `page`                      | integer  | `1`                   | Page number                                    |
| `page_size`                 | integer  | `50`                  | Results per page (max 100)                     |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "pagination": {
      "total_count": INTEGER,
      "current_page": INTEGER,
      "total_pages": INTEGER,
      "page_size": INTEGER
    },
    "data": [
      {
        "event_id": "STRING",
        "content_type": "STRING",
        "call_date": "ISO_DATETIME",
        "title": "STRING",
        "language": "STRING",
        "agenda": ["STRING", ...],
        "insights": ["STRING", ...],
        "transcripts": [
          {
            "start_ms": INTEGER,
            "duration_ms": INTEGER,
            "transcript": "STRING",
            "citation_information": {
              "title": "STRING",
              "url": "URL",
              "metadata": {
                "type": "STRING",
                "url_target": "STRING",
                "company_id": INTEGER,
                "event_id": INTEGER,
                "transcript_item_id": INTEGER
              }
            }
          }, ...
        ],
        "citation_information": {
          "title": "STRING",
          "url": "URL",
          "metadata": {
            "type": "STRING",
            "url_target": "STRING",
            "company_id": INTEGER,
            "event_id": INTEGER
          }
        }
      }, ...
    ]
  }
}
```

Note: `transcripts` array is only included when `include_transcripts=true`. When transcripts are not included, `citation_information` is included at the event level.

---

## POST /search-company-news

Searches company investor relations news pages using external search.

**Query Parameters:**

| Parameter                   | Type    | Default      | Description               |
|-----------------------------|---------|--------------|---------------------------|
| `include_base_instructions` | boolean | `true`       | Include base instructions |
| `originating_prompt`        | string  | -            | Original prompt           |
| `self_identification`       | string  | -            | Caller identifier         |
| `search`                    | string  | **required** | Search query for news     |
| `bloomberg_ticker`          | string  | -            | Bloomberg ticker symbol   |
| `sector_id`                 | integer | -            | Filter by GICS sector     |
| `subsector_id`              | integer | -            | Filter by GICS subsector  |
| `index_id`                  | integer | -            | Filter by market index    |
| `watchlist_id`              | integer | -            | Filter by user watchlist  |

**Response:**

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": [
    {
      "title": "STRING",
      "snippet": "STRING",
      "score": FLOAT,
      "citation_information": {
        "title": "STRING",
        "url": "URL",
        "metadata": {
          "type": "STRING",
          "url_target": "STRING"
        }
      }
    }, ...
  ]
}
```

---

## Notes

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
