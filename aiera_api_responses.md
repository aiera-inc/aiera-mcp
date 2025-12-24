# Aiera API Responses

This document defines the possible results and fields from various endpoints of the Aiera REST API.

---

## /chat-support/find-equities

```json
{
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions..."
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "pagination": {
      "total_count": 16639,
      "current_page": 1,
      "total_pages": 333,
      "page_size": 50
    },
    "data": [
      {
        "equity_id": 22685,
        "company_id": 7501,
        "name": "SAMSUNG ELECTRONICS CO LTD /FI",
        "bloomberg_ticker": "005935:KS",
        "sector_id": 5,
        "subsector_id": 73,
        "primary_equity": false,
        "created": "2021-05-21T20:05:09",
        "modified": "2025-10-30T03:35:03"
      },
      {
        "equity_id": 21477,
        "company_id": 2304,
        "name": "ECOPETROL S.A.",
        "bloomberg_ticker": "ECOPETL:CB",
        "sector_id": 12,
        "subsector_id": 150,
        "primary_equity": false,
        "created": "2021-02-09T22:16:30",
        "modified": "2025-11-15T13:03:52"
      }, ...
    ]
  }
}
```

## /chat-support/equity-summaries

```json
{
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions..."
  ],
  "response": [
    {
      "equity_id": 1,
      "company_id": 1,
      "name": "AMAZON COM INC",
      "bloomberg_ticker": "AMZN:US",
      "sector_id": 1,
      "subsector_id": 259,
      "description": "Amazon.com, Inc. engages in the retail sale of consumer products and subscriptions in North America and internationally. It operates through three segments: North America, International, and Amazon Web Services. The company also manufactures and sells electronic devices, including Kindle, Fire tablets, Fire TVs, Rings, and Echo and other devices.",
      "country": "United States of America",
      "created": "2017-06-01T00:00:00",
      "modified": "2025-12-23T18:01:27",
      "status": "active",
      "leadership": [
        {
          "name": "Andrew R. Jassy",
          "title": "CEO of Amazon Web Services Inc.",
          "event_count": 8,
          "last_event_date": "2025-10-30T17:00:00"
        },
        {
          "name": "Brian T. Olsavsky",
          "title": "Chief Financial Officer & Senior Vice President",
          "event_count": 8,
          "last_event_date": "2025-10-30T17:00:00"
        }, ...
      ],
      "indices": ["S&P 100", "S&P 500", "Russell 3000", "Russell 1000"],
      "confirmed_events": {
        "past": [
          {
            "event_id": 2819716,
            "title": "Q3 2025 Amazon.com Inc Earnings Call",
            "event_type": "earnings",
            "event_date": "2025-10-30T17:00:00",
            "fiscal_quarter": 3,
            "fiscal_year": 2025,
            "has_human_verified": true,
            "has_live_transcript": true,
            "has_audio": true,
            "summary": {
              "title": "Amazon's Future: Andrew Jassy on Capacity Expansion, AI Innovations...",
              "content": ["...detailed summary..."]
            },
            "citation_information": {
                "title": "Q3 2025 CBAK Energy Technology Inc Earnings Call",
                "url": "https://dashboard.aiera.com/companies/279/activity/transcripts?tabs[0]=evt%7C2826481",
                "metadata": {
                    "type": "event",
                    "url_target": "aiera",
                    "company_id": 279,
                    "event_id": 2826481
                }
             }
          }, ...
        ],
        "upcoming": [
          {
            "event_id": 2831731,
            "title": "CBAK Energy Technology Inc Annual Shareholders Meeting",
            "event_type": "shareholder_meeting",
            "event_date": "2025-12-28T21:00:00",
            "fiscal_quarter": null,
            "fiscal_year": null,
            "citation_information": {
                "title": "CBAK Energy Technology Inc Annual Shareholders Meeting",
                "url": "https://dashboard.aiera.com/companies/279/activity/transcripts?tabs[0]=evt%7C2831731",
                "metadata": {
                    "type": "event",
                    "url_target": "aiera",
                    "company_id": 279,
                    "event_id": 2831731
                }
            }
          }, ...
        ]
      },
      "estimated_events": [
        {
          "estimate_id": 18803,
          "estimate_date": "2026-02-05T17:00:00",
          "estimate_type": "earnings",
          "estimate_title": "Q4 Earnings Call"
        },
        {
          "estimate_id": 18804,
          "estimate_date": "2026-04-30T17:00:00",
          "estimate_type": "earnings",
          "estimate_title": "Q1 Earnings Call"
        }, ...
      ]
    }
  ]
}
```

## /chat-support/find-events

```json
{
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "pagination": {
      "total_count": 2,
      "current_page": 1,
      "total_pages": 1,
      "page_size": 2
    },
    "data": [
      {
        "event_id": 2819716,
        "equity": {
          "equity_id": 1,
          "company_id": 1,
          "name": "AMAZON COM INC",
          "bloomberg_ticker": "AMZN:US",
          "sector_id": 1,
          "subsector_id": 259,
          "primary_equity": true
        },
        "title": "Q3 2025 Amazon.com Inc Earnings Call",
        "event_type": "earnings",
        "event_date": "2025-10-30T17:00:00",
        "event_category": "standard",
        "expected_language": "en",
        "conference": {
          "conference_id": null,
          "conference_name": null
        },
        "summary": {
          "title": null,
          "summary": null
        },
        "citation_information": {
          "title": "Q3 2025 Amazon.com Inc Earnings Call",
          "url": "https://dashboard.aiera.com/companies/1/activity/transcripts?tabs[0]=evt%7C2819716",
          "metadata": {
            "type": "event",
            "url_target": "aiera",
            "company_id": 1,
            "event_id": 2819716
          }
        }
      },
      {
        "event_id": 2734016,
        "equity": {
          "equity_id": 1,
          "company_id": 1,
          "name": "AMAZON COM INC",
          "bloomberg_ticker": "AMZN:US",
          "sector_id": 1,
          "subsector_id": 259,
          "primary_equity": true
        },
        "title": "Q2 2025 Amazon.com Inc Earnings Call",
        "event_type": "earnings",
        "event_date": "2025-07-31T17:00:00",
        "event_category": "standard",
        "expected_language": "en",
        "conference": {
          "conference_id": null,
          "conference_name": null
        },
        "summary": {
          "title": "Amazon's Q2 2025: Strong Revenue Growth, AI Innovations, and Record-Breaking Prime Day Performance",
          "summary": [
            "Amazon reported Q2 2025 revenue of $167.7 billion, up 12% year-over-year, with operating income of $19.2 billion. AWS grew 17.5% to a $123 billion annualized run rate. The company highlighted advancements in AI, including the Trainium2 chip and new services like Amazon Bedrock and Agent Core. Prime Day set new records, and delivery speeds improved with 30% more same-day or next-day deliveries. Advertising revenue grew 22% to $15.7 billion. Key partnerships were announced with Roku and Disney for advertising. Amazon Pharmacy grew 50% year-over-year. Q3 guidance projects net sales between $174-179.5 billion and operating income of $15.5-20.5 billion. Leadership expressed optimism about future growth, particularly in cloud services and AI, while noting ongoing investments in infrastructure and technology to support long-term expansion."
          ]
        },
        "citation_information": {
          "title": "Q2 2025 Amazon.com Inc Earnings Call",
          "url": "https://dashboard.aiera.com/companies/1/activity/transcripts?tabs[0]=evt%7C2734016",
          "metadata": {
            "type": "event",
            "url_target": "aiera",
            "company_id": 1,
            "event_id": 2819716
          }
        },
        "transcripts": [
          {
            "transcript_item_id": 182926099,
            "transcript": "Will be against our results for the comparable period of 2024...",
            "timestamp": "2025-07-31T17:02:01",
            "start_ms": 240,
            "duration_ms": 47760,
            "speaker": "Dave Fildes",
            "speaker_type": "final",
            "created": "2025-12-11T23:16:44",
            "modified": "2025-12-12T00:38:43",
            "transcript_section": "presentation",
            "transcript_version": 3,
            "citation_information": {
              "title": "Q2 2025 Amazon.com Inc Earnings Call",
              "url": "https://dashboard.aiera.com/companies/1/activity/transcripts?tabs[0]=evt%7C2734016%7Ctext%7C182926099",
              "metadata": {
                "type": "event",
                "url_target": "aiera",
                "company_id": 1,
                "event_id": 2734016,
                "transcript_item_id": 182926099
              }
            }
          }, ...
        ]
      }
    ]
  }
}
```

## /chat-support/estimated-and-upcoming-events

```json
{
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "estimates": [
      {
        "estimate_id": 20876,
        "equity": {
          "equity_id": 514,
          "company_id": 1326,
          "name": "Wells Fargo & Co",
          "bloomberg_ticker": "WFC:US",
          "sector_id": 8,
          "subsector_id": 94
        },
        "estimate": {
          "call_type": "earnings",
          "call_date": "2026-01-14T10:00:00",
          "title": "Q4 Earnings Call"
        },
        "actual": {
          "scheduled_audio_call_id": 2688304,
          "call_type": "earnings",
          "call_date": "2026-01-15T10:00:00",
          "title": "Q4 2025 Wells Fargo & Co Earnings Call",
          "url": "https://dashboard.aiera.com/companies/1326/calendar?tabs[0]=evt%7C2688304"
        },
        "citation_information": {
          "title": "Q4 2025 Wells Fargo & Co Earnings Call",
          "url": "https://dashboard.aiera.com/companies/1326/activity/transcripts?tabs[0]=evt%7C2688304",
          "metadata": {
            "type": "event",
            "url_target": "aiera",
            "company_id": 1326,
            "event_id": 2688304
          }
        }
      },
      {
        "estimate_id": 20880,
        "equity": {
          "equity_id": 514,
          "company_id": 1326,
          "name": "Wells Fargo & Co",
          "bloomberg_ticker": "WFC:US",
          "sector_id": 8,
          "subsector_id": 94
        },
        "estimate": {
          "call_type": "presentation",
          "call_date": "2026-02-15T08:00:00",
          "title": "Financial Services Conference"
        },
        "actual": null,
        "citation_information": {
          "title": "Financial Services Conference",
          "url": "https://dashboard.aiera.com/companies/1326/activity",
          "metadata": {
            "type": "company",
            "url_target": "aiera",
            "company_id": 1326
          }
        }
      }, ...
    ],
    "actuals": [
      {
        "event_id": 2820054,
        "equity": {
          "equity_id": 514,
          "company_id": 1326,
          "name": "Wells Fargo & Co",
          "bloomberg_ticker": "WFC:US",
          "sector_id": 8,
          "subsector_id": 94
        },
        "call_type": "earnings_release",
        "call_date": "2026-01-14T07:00:00",
        "title": "Wells Fargo & Company to Report Q4, 2025 Results on Jan 14, 2026",
        "citation_information": {
          "title": "Wells Fargo & Company to Report Q4, 2025 Results on Jan 14, 2026",
          "url": "https://dashboard.aiera.com/companies/1326/activity/transcripts?tabs[0]=evt%7C2820054",
          "metadata": {
            "type": "event",
            "url_target": "aiera",
            "company_id": 1326,
            "event_id": 2820054
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
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "result": [
      {
        "_score": 9.457697,
        "date": "2022-04-28T17:30:00",
        "primary_company_id": 1,
        "content_id": 182846708,
        "transcript_event_id": 2108591,
        "transcript_section": null,
        "text": "Inflation has been in both periods. Inflation was in the transportation costs, especially in wage inflation last year. It remains there. It's been amplified a bit by the fuel costs following the Ukraine conflict, which has happened since we last spoke. It's more a factor of that those costs will now, we believe, persist a little longer than we were hoping at the beginning of the year...",
        "primary_equity_id": 1,
        "title": "Q1 2022 Amazon.com Inc Earnings Call",
        "citation_information": {
          "title": "Q1 2022 Amazon.com Inc Earnings Call",
          "url": "https://dashboard.aiera.com/companies/1/activity/transcripts?tabs[0]=evt%7C2108591%7Ctext%7C182846708",
          "metadata": {
            "type": "event",
            "url_target": "aiera",
            "company_id": 1,
            "event_id": 2108591,
            "transcript_item_id": 182846708
          }
        }
      },
      {
        "_score": 8.921383,
        "date": "2022-04-28T17:30:00",
        "primary_company_id": 1,
        "content_id": 182846689,
        "transcript_event_id": 2108591,
        "transcript_section": null,
        "text": "What you're seeing there in the growth in shipping costs versus the unit growth, a little bit on the unit side, but it's essentially a factor of inflation and productivity that I've mentioned to you on the component that hits in the transportation area.",
        "primary_equity_id": 1,
        "title": "Q1 2022 Amazon.com Inc Earnings Call",
        "citation_information": {
          "title": "Q1 2022 Amazon.com Inc Earnings Call",
          "url": "https://dashboard.aiera.com/companies/1/activity/transcripts?tabs[0]=evt%7C2108591%7Ctext%7C182846689",
          "metadata": {
            "type": "event",
            "url_target": "aiera",
            "company_id": 1,
            "event_id": 2108591,
            "transcript_item_id": 182846689
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
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "pagination": {
      "total_count": 15,
      "current_page": 1,
      "total_pages": 1,
      "page_size": 15
    },
    "data": [
      {
        "conference_id": 36743,
        "title": "TD Cowen Global Mining Conference",
        "event_count": 2,
        "start_date": "2026-01-28T09:10:00",
        "end_date": "2026-01-28T09:10:00",
        "citation_information": {
          "title": "TD Cowen Global Mining Conference",
          "url": "https://dashboard.aiera.com/conferences/36743",
          "metadata": {
            "type": "conference",
            "url_target": "aiera",
            "conference_id": 36743
          }
        }
      },
      {
        "conference_id": 36747,
        "title": "CIBC Western Institutional Investor Conference",
        "event_count": 2,
        "start_date": "2026-01-22T17:00:00",
        "end_date": "2026-01-22T17:00:00",
        "citation_information": {
          "title": "CIBC Western Institutional Investor Conference",
          "url": "https://dashboard.aiera.com/conferences/36747",
          "metadata": {
            "type": "conference",
            "url_target": "aiera",
            "conference_id": 36747
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
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "pagination": {
      "total_count": 97,
      "current_page": 1,
      "total_pages": 2,
      "page_size": 50
    },
    "data": [
      {
        "filing_id": 8587883,
        "equity": {
          "equity_id": 26058,
          "company_id": 1,
          "name": "AMAZON COM INC",
          "bloomberg_ticker": "AMZ:GR",
          "sector_id": 1,
          "subsector_id": 259
        },
        "title": "AMAZON COM INC - 4",
        "form_number": "4",
        "form_name": "Statement of Changes in Beneficial Ownership",
        "filing_organization": "sec",
        "filing_system": "edgar",
        "is_amendment": 0,
        "period_end_date": "2025-12-01T00:00:00",
        "release_date": "2025-12-03T17:00:17",
        "arrival_date": "2025-12-23T20:00:08",
        "pulled_date": "2025-12-23T20:02:53",
        "json_synced": false,
        "datafiles_synced": false,
        "summary": ["...summary text..."],
        "citation_information": {
          "title": "AMAZON COM INC - 4",
          "url": "https://dashboard.aiera.com/companies/1/activity/filings?tabs[0]=fl%7C28259872",
          "metadata": {
            "type": "filing",
            "url_target": "aiera",
            "company_id": 1,
            "filing_id": 8587883,
            "content_id": 28259872
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
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "result": [
      {
        "_score": 12.584471,
        "date": "2023-04-12",
        "primary_company_id": 1,
        "content_id": 21687400,
        "filing_id": 7046270,
        "company_common_name": "Amazon",
        "filing_type": "DEF14A",
        "primary_equity_id": 1,
        "text": "| Aspect | Details |\n|---|---|\n| Notable contextual data | The discussion highlights a historically high CEO-to-median-pay ratio among S&P 500 companies in 2021, with CEO pay largely in restricted stock and no performance criteria, underscoring concerns about pay inflation and alignment with broader employee pay practices |",
        "title": "Amazon.com Inc - DEF 14A",
        "citation_information": {
          "title": "Amazon.com Inc - DEF 14A",
          "url": "https://dashboard.aiera.com/companies/1/activity/filings?tabs[0]=fl%7C21687400",
          "metadata": {
            "type": "filing",
            "url_target": "aiera",
            "company_id": 1,
            "filing_id": 7046270,
            "content_id": 21687400
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
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "pagination": {
      "total_count": 417,
      "current_page": 1,
      "total_pages": 9,
      "page_size": 50
    },
    "data": [
      {
        "doc_id": 5488573,
        "company": {
          "company_id": 1,
          "name": "Amazon"
        },
        "publish_date": "2025-12-19",
        "category": "press_release",
        "title": "United Rentals Scales AI-Powered Manual Assist Application on AWS to Speed Equipment Repairs",
        "source_url": "https://press.aboutamazon.com/aws/2025/12/united-rentals-scales-ai-applications-with-aws",
        "summary": [
          "The document announces that United Rentals has expanded enterprise-wide adoption of Manual Assist AI, a web-based application built on Amazon Web Services (AWS) that provides AI-powered diagnostics and instant access to thousands of equipment manufacturer manuals for service teams. The application now supports more than 4,000 monthly users, helping technicians quickly locate relevant manuals, summarize procedures, and identify the most important technical details to accelerate troubleshooting and repairs.",
          "Manual Assist AI, developed in collaboration with AWS using services including Amazon Bedrock and Amazon OpenSearch, is designed to reduce the time required to find critical service information, enabling faster, more accurate maintenance both in the shop and in the field. United Rentals highlights that the tool improves fleet utilization by getting equipment back into service more quickly, aligning with its broader strategy to use generative AI to expand employee capacity and increase customer value.",
          "AWS underscores the partnership as an example of how AI can enhance productivity and safety across industries, while United Rentals positions Manual Assist AI as part of its Worksite Performance Solutions innovation strategy. This strategy emphasizes digital tools, advanced equipment technologies, and data analytics aimed at improving project efficiency, safety, and overall worksite performance. The release also provides background on United Rentals' global footprint, fleet size, and market indices membership, along with investor relations contact information."
        ],
        "keywords": [
          "generative ai",
          "ai-powered diagnostics",
          "manual assist ai",
          "equipment manuals",
          "field service",
          "technician productivity",
          "equipment downtime",
          "fleet utilization",
          "cloud infrastructure",
          "amazon bedrock",
          "amazon opensearch",
          "digital tools",
          "worksite performance solutions",
          "project efficiency",
          "jobsite productivity",
          "predictive maintenance",
          "troubleshooting",
          "service procedures",
          "industrial equipment",
          "rental equipment operations"
        ],
        "processed": "2025-12-20T00:03:06",
        "created": "2025-12-20T00:02:33",
        "modified": "2025-12-20T23:26:34",
        "citation_information": {
          "title": "United Rentals Scales AI-Powered Manual Assist Application on AWS to Speed Equipment Repairs",
          "url": "https://press.aboutamazon.com/aws/2025/12/united-rentals-scales-ai-applications-with-aws",
          "metadata": {
            "type": "company_doc",
            "url_target": "external",
            "company_id": 1,
            "company_doc_id": 5488573
          }
        }
      },
      {
        "doc_id": 5488573,
        "company": {
          "company_id": 1,
          "name": "Amazon"
        },
        "publish_date": "2025-12-19",
        "category": "press_release",
        "title": "United Rentals Scales AI-Powered Manual Assist Application on AWS to Speed Equipment Repairs",
        "source_url": "https://press.aboutamazon.com/aws/2025/12/united-rentals-scales-ai-applications-with-aws",
        "summary": [
          "The document announces that United Rentals has expanded enterprise-wide adoption of Manual Assist AI, a web-based application built on Amazon Web Services (AWS) that provides AI-powered diagnostics and instant access to thousands of equipment manufacturer manuals for service teams. The application now supports more than 4,000 monthly users, helping technicians quickly locate relevant manuals, summarize procedures, and identify the most important technical details to accelerate troubleshooting and repairs.",
          "Manual Assist AI, developed in collaboration with AWS using services including Amazon Bedrock and Amazon OpenSearch, is designed to reduce the time required to find critical service information, enabling faster, more accurate maintenance both in the shop and in the field. United Rentals highlights that the tool improves fleet utilization by getting equipment back into service more quickly, aligning with its broader strategy to use generative AI to expand employee capacity and increase customer value.",
          "AWS underscores the partnership as an example of how AI can enhance productivity and safety across industries, while United Rentals positions Manual Assist AI as part of its Worksite Performance Solutions innovation strategy. This strategy emphasizes digital tools, advanced equipment technologies, and data analytics aimed at improving project efficiency, safety, and overall worksite performance. The release also provides background on United Rentals' global footprint, fleet size, and market indices membership, along with investor relations contact information."
        ],
        "keywords": [
          "generative ai",
          "ai-powered diagnostics",
          "manual assist ai",
          "equipment manuals",
          "field service",
          "technician productivity",
          "equipment downtime",
          "fleet utilization",
          "cloud infrastructure",
          "amazon bedrock",
          "amazon opensearch",
          "digital tools",
          "worksite performance solutions",
          "project efficiency",
          "jobsite productivity",
          "predictive maintenance",
          "troubleshooting",
          "service procedures",
          "industrial equipment",
          "rental equipment operations"
        ],
        "processed": "2025-12-20T00:03:06",
        "created": "2025-12-20T00:02:33",
        "modified": "2025-12-20T23:26:34",
        "content_raw": "December 18, 2025 Amazon Business Prime Offers Small and Midsize Businesses Even More Value with New Benefits from Intuit QuickBooks, CrowdStrike, and Gusto Business Prime customers have access to exclusive benefits with Intuit QuickBooks, CrowdStrike, and Gusto to support their financial management, cybersecurity, and Human Resources needs Expanded benefits can help SMBs save nearly $1,000 per year, streamline operations, and simplify business buying Savings build on Business Prime's value, joining member benefits like fast, free shipping, Spend Visibility, Guided Buying, and flexible payment SEATTLE--(BUSINESS WIRE)-- Today Amazon (NASDAQ: AMZN) announced that Amazon Business has added even more value to the Business Prime membership program with benefits from Intuit QuickBooks, CrowdStrike, and Gusto that help small and midsize business customers save time and money. Amazon Business tailors the best of Amazon—everyday low prices, vast selection, and a convenient shopping and delivery experience—alongside a diverse supplier network, a reliable global logistics system, adaptable workflow features, and intelligent automation tools to meet the needs of organizations of all sizes, including hundreds of thousands of small businesses worldwide. The Business Prime membership enhances this value proposition by offering organizations even more benefits, including access to fast, free shipping on millions of items, along with powerful analytics and spending controls that optimize the management of decentralized purchasing. With three new collaborations offering benefits in financial management, cybersecurity, and HR, Business Prime has never been more valuable for \"Small business owners wear a lot of hats — accountant, HR manager, IT lead — sometimes all before lunch,\" said Todd Heimes, VP at Amazon Business. \"We're thrilled to introduce new Business Prime benefits that help them work smarter, save money, and get back to what they love most — running their business.\" Simplify Finances with Intuit QuickBooks\n\nQuickBooks brings industry-leading financial management tools to Business Prime members at a fraction of the cost, which includes a direct integration that enables small business customers to seamlessly automate purchase reconciliation and categorization. Coming in 2026, this benefit gives Business Prime members access to QuickBooks Online Simple Start for just $180 per year — a 60% discount off the regular $456 MSRP . With QuickBooks, millions of small businesses manage their finances end- to-end including automating payments, getting paid faster, paying employees, and seamlessly reconciling their books. This benefit is best suited for small businesses that want to simplify business operations, gain visibility into cash flow, and streamline financial management. It's available to Business Prime members in the U.S. who are new QuickBooks Online subscribers and maintain an active Business Prime Essentials subscription. Business Prime members can redeem this exclusive offer through their Business Prime benefits page and complete a simple activation process on Intuit's website. Once enrolled, members can manage their business while continuing to enjoy their discounted rate for the duration of the promotion period. Protect Your Business with Free Enterprise-Grade Cybersecurity Business Prime members on the Essentials plan and above now receive access to CrowdStrike Falcon Go at no additional cost — bringing the power of the industry's leading cybersecurity platform to small and midsize businesses. Falcon Go delivers AI-native protection designed to stop breaches, providing world-class prevention against ransomware, malware, and modern cyberattacks for organizations that often lack dedicated security teams. Falcon Go delivers the same industry-leading speed, efficacy, and AI- powered detection that protect the world's largest enterprises. This benefit, valued at $59 per device annually, removes financial and operational barriers by giving SMBs effortless access to enterprise-grade protection through the Amazon Business Prime membership. The offer is available to Business Prime members in the U.S. who do not already have a CrowdStrike account and maintain an active Business Prime account. Business Prime Duo members receive 50% off the standard Falcon Go rate. Members can activate their cybersecurity benefit directly through their Business Prime benefits page and complete a quick setup experience on CrowdStrike's website. Once enabled, Falcon Go immediately provides AI-powered protection that helps businesses defend against evolving threats and keep operations running securely. Streamline HR and Payroll with Gusto Business Prime members in the U.S. also now receive 70% off their first 12 months of Gusto's comprehensive payroll and HR platform. Available immediately, this benefit gives members access to Gusto's all-in-one\n\nsystem for hiring, onboarding, payroll, and benefits administration — helping business owners save time, stay compliant with company policies, and reduce manual work. Trusted by more than 400,000 businesses nationwide, Gusto is best suited for small businesses looking to automate payroll, simplify HR management, and drive compliance with federal and state regulations. The offer is available to members without an existing Gusto account and requires an active Business Prime membership to Members can redeem this offer through their Business Prime benefits page and complete the activation process on Gusto's website. Once enrolled, members gain access to automated payroll runs, built-in tax filing, and benefits management tools that help save hours each week and allow them to focus more on growing their business. After the 12- month promotional period, standard pricing applies. When Prime Means Business With yearly savings of nearly $1,000, fast delivery speeds, and significant membership engagement, Business Prime continues to demonstrate its value as an essential tool for business customers worldwide. Business Prime members also have access to enhanced shipping benefits including Amazon Day, which consolidates eligible deliveries to a single day each week. Last year, Business Prime members saved more than $750 million globally in shipping fees, and nearly 50% of global orders and over 70% of U.S. Business Prime orders arrived the same day or next day in the last Small business customers in the U.S. can take advantage of additional savings opportunities through  Business Prime Rewards  which offers up to 4% back on brands by Amazon. Customers can also enjoy savings from the Amazon Business Prime American Express Card  and Prime-exclusive From Solopreneurs to Fortune 500: Amazon Business Provides Value, Selection, and Convenience Since launching in the U.S. in 2015, Amazon Business has empowered businesses of all sizes through unmatched selection, deep discounts, and smart capabilities. Today, Amazon Business continues to be a priority for the company, driving over $35 billion in annualized gross sales, with strong adoption and positive feedback from customers. Amazon Business actively serves more than eight million organizations globally, excluding emerging geographies. Procurement and business leaders benefit from convenient shipping options on hundreds of millions of supplies across categories like office, IT, janitorial, and food service, along with business- tailored features including a curated site experience, Business Prime, business-only pricing and selection, single- or multi-user business accounts, approval workflows, purchasing system integrations, payment solutions, tax exemptions, and dedicated customer support. Working closely with customers to understand their business buying challenges, Amazon Business continues to develop new technologies that\n\nmake it easy for organizations and administrators to define, meet, and proactively measure progress toward their purchasing budgets and goals. Amazon Business is now a strategic partner to businesses in 11 countries including Australia, Canada, France, Germany, India, Italy, Japan, Mexico, Spain, the United Kingdom, and the United States. Visit the Amazon Business website  to learn more. Amazon.com, Inc. Media Hotline Amazon-pr@amazon.com www.amazon.com/pr Source: Amazon.com, Inc.",
        "citation_information": {
          "title": "United Rentals Scales AI-Powered Manual Assist Application on AWS to Speed Equipment Repairs",
          "url": "https://press.aboutamazon.com/aws/2025/12/united-rentals-scales-ai-applications-with-aws",
          "metadata": {
            "type": "company_doc",
            "url_target": "external",
            "company_id": 1,
            "company_doc_id": 5488573
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
    "total_count": 5163,
    "current_page": 1,
    "total_pages": 259,
    "page_size": 20
  },
  "data": {
    "announcement": 828592,
    "press_release": 440360,
    "slide_presentation": 333390,
    "earnings_release": 303698,
    "sec_filing": 247404,
    "financial_report": 84214,
    "other": 81464,
    "annual_report": 69484,
    "transcript": 21255,
    "sustainability_report": 11007,
    "corporate_governance": 9610,
    "management_discussion_and_analysis": 8595,
    "proxy_statement": 7293,
    "product": 7106,
    "shareholder_letter": 6159,
    "research_report": 5350,
    "investor_presentation": 5188,
    "certification": 5134,
    "datasheet": 4843,
    "policy_document": 4527
  }
}
```

## /chat-support/get-company-doc-keywords

```json
{
  "pagination": {
    "total_count": 1703856,
    "current_page": 1,
    "total_pages": 170386,
    "page_size": 10
  },
  "data": {
    "financial results": 343826,
    "financial performance": 274544,
    "financial statements": 223534,
    "sustainability": 185838,
    "corporate governance": 182635,
    "risk management": 157447,
    "earnings": 153799,
    "cash flow": 146470,
    "net income": 139432,
    "revenue": 134810
  }
}
```

## /chat-support/find-third-bridge

```json
{
  "instructions": [
    "This data is provided for institutional finance professionals...",
    "The current date is **Monday, December 22, 2025**, and the current time is **11:04 AM**...",
    "Questions about guidance will always require the transcript...",
    "Answers to guidance questions should focus on management commentary...",
    "Some endpoints may require specific permissions...",
    "IMPORTANT: when referencing this data in a response, ALWAYS include inline citations..."
  ],
  "response": {
    "pagination": {
      "total_count": 13,
      "current_page": 1,
      "total_pages": 1,
      "page_size": 13
    },
    "data": [
      {
        "event_id": "46abc016e6da845a6459e80a200341c5",
        "content_type": "COMMUNITY",
        "call_date": "2025-04-23T19:00:00",
        "title": "Robotic Delivery Market - Senior Executive, Sales & Operations Planning at Amazon.com Inc",
        "language": "eng",
        "agenda": ["...agenda text..."],
        "insights": ["...insights text..."],
        "citation_information": {
          "title": "Robotic Delivery Market - Senior Executive, Sales & Operations Planning at Amazon.com Inc",
          "url": "https://dashboard.aiera.com/companies/1/calendar?tabs[0]=evt%7C2833969",
          "metadata": {
            "type": "event",
            "url_target": "aiera",
            "company_id": 1,
            "event_id": 2833969
          }
        }
      },
      {
        "event_id": "46abc016e6da845a6459e80a200341c5",
        "content_type": "COMMUNITY",
        "call_date": "2025-04-23T19:00:00",
        "title": "Robotic Delivery Market - Senior Executive, Sales & Operations Planning at Amazon.com Inc",
        "language": "eng",
        "agenda": ["...agenda text..."],
        "insights": ["...insights text..."],
        "transcripts": [
          {
            "start_ms": 155000,
            "duration_ms": 60000,
            "transcript": "We're just trying to make sure that we understand the split correctly...",
            "citation_information": {
              "title": "AI Infrastructure Industry - Amazon & Nvidia...",
              "url": "https://dashboard.aiera.com/companies/1/calendar?tabs[0]=evt%7C2820893%7Ctext%7C179195065",
              "metadata": {
                "type": "event",
                "url_target": "aiera",
                "company_id": 1,
                "event_id": 2820893,
                "transcript_item_id": 179195065
              }
            }
          }, ...
        ]
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
      "index_id": 3,
      "name": "Dow Jones Industrial Average",
      "short_name": "DJIA"
    },
    {
      "index_id": 8,
      "name": "Russell 1000",
      "short_name": "RUSSELL1000"
    },
    {
      "index_id": 7,
      "name": "Russell 2000",
      "short_name": "RUSSELL2000"
    },
    {
      "index_id": 6,
      "name": "Russell 3000",
      "short_name": "RUSSELL3000"
    },
    {
      "index_id": 1,
      "name": "S&P 100",
      "short_name": "SP100"
    },
    {
      "index_id": 2,
      "name": "S&P 500",
      "short_name": "SP500"
    }
  ]
}
```

## /chat-support/index-constituents/<index>

```json
{
  "pagination": {
    "total_count": 509,
    "current_page": 1,
    "total_pages": 11,
    "page_size": 50
  },
  "data": [
    {
      "equity_id": 355,
      "company_id": 4595,
      "name": "MICROSOFT CORP",
      "bloomberg_ticker": "MSFT:US",
      "sector_id": 5,
      "sub_sector_id": 84,
      "primary_equity": true,
      "created": "2017-07-06T00:00:00",
      "modified": "2025-12-19T14:15:59"
    }, ...
  ]
}
```

## /chat-support/available-watchlists

```json
{
  "response": [
    {
      "watchlist_id": 45245136,
      "name": "Primary",
      "type": "primary_watchlist"
    }
  ]
}
```

## /chat-support/watchlist-constituents/<watchlist_id>

```json
{
  "pagination": {
    "total_count": 8,
    "current_page": 1,
    "total_pages": 1,
    "page_size": 8
  },
  "data": [
    {
      "equity_id": 355,
      "company_id": 4595,
      "name": "MICROSOFT CORP",
      "bloomberg_ticker": "MSFT:US",
      "sector_id": 5,
      "subsector_id": 84,
      "primary_equity": true,
      "created": "2017-07-06T00:00:00",
      "modified": "2025-12-22T12:01:53"
    }, ...
  ]
}
```

## /chat-support/get-sectors-and-subsectors

```json
{
  "response": [
    {
      "sector_id": 1,
      "gics_code": "25",
      "name": "Consumer Discretionary",
      "subsectors": [
        {
          "subsector_id": 1,
          "gics_code": "25203010",
          "gics_industry_code": "252030",
          "name": "Apparel, Accessories & Luxury Goods"
        },
        {
          "subsector_id": 5,
          "gics_code": "25102010",
          "gics_industry_code": "251020",
          "name": "Automobile Manufacturers"
        }, ...
      ]
    }, ...
  ]
}
```
