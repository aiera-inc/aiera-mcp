#!/usr/bin/env python3

"""Utility functions for Aiera MCP tools."""


def correct_bloomberg_ticker(ticker: str) -> str:
    """Ensure bloomberg ticker is in the correct format (ticker:country_code)."""
    if "," in ticker:
        tickers = ticker.split(",")
        reticker = []
        for ticker in tickers:
            # if a space was substituted over colon...
            if ":" not in ticker and " " in ticker:
                ticker_parts = ticker.split()
                reticker.append(f"{ticker_parts[0]}:{ticker_parts[1]}")

            # default to US if ticker doesn't include country code...
            elif ":" not in ticker:
                reticker.append(f"{ticker}:US")

            else:
                reticker.append(ticker)

        return ",".join(reticker)

    # if a space was substituted over colon...
    elif ":" not in ticker and " " in ticker:
        ticker_parts = ticker.split()
        return f"{ticker_parts[0]}:{ticker_parts[1]}"

    # default to US if ticker doesn't include country code...
    elif ":" not in ticker:
        return f"{ticker}:US"

    return ticker


def correct_keywords(keywords: str) -> str:
    """Ensure keywords have comma-separation."""
    if "," not in keywords and " " in keywords and len(keywords.split()) > 3:
        return ",".join(keywords.split())

    return keywords


def correct_categories(categories: str) -> str:
    """Ensure categories have comma-separation."""
    if "," not in categories and " " in categories:
        return ",".join(categories.split())

    return categories


def correct_provided_ids(provided_ids: str) -> str:
    """Ensure provided ID lists have comma-separation."""
    if "," not in provided_ids and " " in provided_ids:
        corrected = []
        for provided_id in provided_ids.split(","):
            corrected.append(provided_id.strip())

        return ",".join(corrected)

    return provided_ids


def correct_event_type(event_type: str) -> str:
    """Ensure event type is set correctly."""
    if event_type.strip() == "conference":
        event_type = "presentation"
    elif event_type.strip() == "m&a":
        event_type = "special_situation"

    if event_type.strip() not in ["earnings", "presentation", "shareholder_meeting", "investor_meeting", "special_situation"]:
        event_type = "earnings"

    return event_type.strip()


def correct_transcript_section(section: str) -> str:
    """Ensure the transcript section is set correctly."""
    if section.strip() == "qa":
        section = "q_and_a"

    return section.strip()