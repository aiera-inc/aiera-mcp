#!/usr/bin/env python3

"""Utility functions for Aiera MCP tools."""

import re


# Mapping of commonly-used Bloomberg ticker aliases to the canonical ticker
# recognized by the Aiera platform. Applied after format normalization.
#
# Historical note: GOOGL:US → GOOG:US used to be aliased here because the
# equities table had a mis-mapped bloomberg_root on the Alphabet Class A
# record. That data was corrected upstream (see CORE-2761), so the alias
# now actively causes the bug it was meant to work around — resolving a
# genuine GOOGL:US request to the wrong Class C security. Left as an empty
# dict so the alias mechanism stays wired for future needs.
TICKER_ALIASES: dict[str, str] = {}


def _apply_ticker_alias(ticker: str) -> str:
    """Apply ticker alias mapping for a single normalized ticker."""
    return TICKER_ALIASES.get(ticker, ticker)


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

        return ",".join(_apply_ticker_alias(t) for t in reticker)

    # if a space was substituted over colon...
    elif ":" not in ticker and " " in ticker:
        ticker_parts = ticker.split()
        return _apply_ticker_alias(f"{ticker_parts[0]}:{ticker_parts[1]}")

    # default to US if ticker doesn't include country code...
    elif ":" not in ticker:
        return _apply_ticker_alias(f"{ticker}:US")

    return _apply_ticker_alias(ticker)


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

    if event_type.strip() not in [
        "earnings",
        "presentation",
        "shareholder_meeting",
        "investor_meeting",
        "special_situation",
    ]:
        event_type = "earnings"

    return event_type.strip()


def correct_transcript_section(section: str) -> str:
    """Ensure the transcript section is set correctly."""
    if section.strip() == "qa":
        section = "q_and_a"

    return section.strip()


def correct_provided_types(provided_types: str) -> str:
    """Ensure provided type lists have comma-separation and are properly formatted."""
    if "," not in provided_types and " " in provided_types:
        provided_types = ",".join(provided_types.split())

    # Clean up each type and rejoin with commas
    cleaned_types = [
        provided_type.strip() for provided_type in provided_types.split(",")
    ]
    return ",".join(cleaned_types)


# Matches a Bloomberg-style exchange suffix on a ticker token: ``MSFT:US``, ``HSBA:LN``,
# ``BHP:AU``. Two letters preceded by a colon, attached to a token of word characters.
# Restricted to two letters so we don't accidentally strip URLs (``http://``) or other
# colon-bearing text in a natural-language search string.
_TICKER_SUFFIX_RE = re.compile(r"(\b\w+):[A-Z]{2}\b")


def strip_ticker_exchange_suffix(text: str) -> str:
    """Remove Bloomberg-style ``:XX`` exchange suffixes from a free-text search string.

    The research index analyzer doesn't currently tokenize the colon cleanly, so a
    search string containing ``MSFT:US`` produces zero results on multiple providers
    even though ``MSFT`` alone returns a healthy match set. This helper strips the
    suffix defensively before the text is sent to ``find_research`` / ``search_research``
    so client templates that emit Bloomberg-formatted tickers don't silently fail.

    Only the two-letter exchange code is stripped (``:US``, ``:LN``, ``:AU``, etc.).
    Other colon-bearing content (URLs, dates, identifiers) is left untouched.
    """
    if not text:
        return text
    return _TICKER_SUFFIX_RE.sub(r"\1", text)
