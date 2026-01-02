# Aiera API Responses

This document defines the possible results and fields from various endpoints of the Aiera REST API.

---

## /chat-support/find-equities

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

## /chat-support/equity-summaries

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

## /chat-support/find-events

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

## /chat-support/estimated-and-upcoming-events

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

### /chat-support/search/transcripts

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "result": [
      {
        "_score": FLOAT,
        "date": "ISO_DATETIME",
        "primary_company_id": INTEGER,
        "content_id": INTEGER,
        "transcript_event_id": INTEGER,
        "transcript_section": "STRING_OR_NULL",
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

## /chat-support/find-conferences

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

## /chat-support/find-filings

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

### /chat-support/search/filing-chunks

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": {
    "result": [
      {
        "_score": FLOAT,
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

## /chat-support/find-company-docs

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

## /chat-support/get-company-doc-categories

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

## /chat-support/get-company-doc-keywords

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

## /chat-support/find-third-bridge

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

## /chat-support/available-indexes

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

## /chat-support/index-constituents/<index>

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

## /chat-support/available-watchlists

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

## /chat-support/watchlist-constituents/<watchlist_id>

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

## /chat-support/get-sectors-and-subsectors

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

## /chat-support/get-financials

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": [
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
            "report_date": DATE,
            "period_duration": "STRING",
            "calendar_year": INTEGER,
            "calendar_quarter": INTEGER,
            "fiscal_year": INTEGER,
            "fiscal_quarter": INTEGER,
            "is_restated": BOOLEAN,
            "earnings_date": DATETIME,
            "filing_date": DATETIME,
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
                        "headers": LIST/NULL
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
                        "url_target": "STRING",
                      }
                    }
                }, ...
            ]
        }, ...
    ]
}
```

## /chat-support/get-ratios

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": [
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
            "report_date": DATE,
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
}
```

## /chat-support/get-segments-and-kpis

```json
{
  "instructions": ["STRING", "STRING", ... ],
  "response": [
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
            "report_date": DATE,
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
}
```
