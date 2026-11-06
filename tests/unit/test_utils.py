#!/usr/bin/env python3

"""Unit tests for the Bloomberg ticker input-correction helper."""

import pytest

from aiera_mcp.tools.company_docs.models import FindCompanyDocsArgs
from aiera_mcp.tools.equities.models import FindEquitiesArgs, GetEquitySummariesArgs
from aiera_mcp.tools.events.models import FindEventsArgs
from aiera_mcp.tools.filings.models import FindFilingsArgs
from aiera_mcp.tools.third_bridge.models import FindThirdBridgeEventsArgs
from aiera_mcp.tools.utils import correct_bloomberg_ticker

DATE_RANGE = {"start_date": "2023-10-01", "end_date": "2023-10-31"}


@pytest.mark.unit
class TestCorrectBloombergTicker:
    """Test Bloomberg ticker format correction."""

    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("AAPL:US", "AAPL:US"),
            ("AAPL", "AAPL:US"),
            ("MSFT US", "MSFT:US"),
            ("MSFT US Equity", "MSFT:US"),
            ("GOOGL:US", "GOOG:US"),
            ("AAPL,MSFT", "AAPL:US,MSFT:US"),
            ("AAPL:US,MSFT:US,GOOGL:US", "AAPL:US,MSFT:US,GOOG:US"),
            ("MSFT US,AAPL US", "MSFT:US,AAPL:US"),
        ],
    )
    def test_already_supported_formats(self, ticker, expected):
        """Formats the corrector already handled keep their result."""
        assert correct_bloomberg_ticker(ticker) == expected

    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("AAPL, MSFT", "AAPL:US,MSFT:US"),
            ("AAPL:US, MSFT:US", "AAPL:US,MSFT:US"),
            ("AAPL , MSFT", "AAPL:US,MSFT:US"),
            ("MSFT US, AAPL US", "MSFT:US,AAPL:US"),
            ("AAPL:US , GOOGL:US", "AAPL:US,GOOG:US"),
        ],
    )
    def test_spaces_around_separators(self, ticker, expected):
        """A space after the comma is the natural way to write a list."""
        assert correct_bloomberg_ticker(ticker) == expected

    @pytest.mark.parametrize("ticker", ["AAPL ", " AAPL", "  AAPL  "])
    def test_padded_single_ticker(self, ticker):
        """Surrounding whitespace on a lone ticker is trimmed, not indexed."""
        assert correct_bloomberg_ticker(ticker) == "AAPL:US"

    def test_alias_applies_to_padded_token(self):
        """The alias map keys on the trimmed ticker."""
        assert correct_bloomberg_ticker("AAPL:US, GOOGL:US") == "AAPL:US,GOOG:US"

    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("AAPL,,MSFT", "AAPL:US,MSFT:US"),
            ("AAPL, ,MSFT", "AAPL:US,MSFT:US"),
            ("AAPL,MSFT,", "AAPL:US,MSFT:US"),
            ("", ""),
            ("   ", ""),
        ],
    )
    def test_empty_tokens_are_dropped(self, ticker, expected):
        """Empty segments must not become a bare ':US' filter."""
        assert correct_bloomberg_ticker(ticker) == expected


@pytest.mark.unit
class TestBloombergTickerValidatorAcrossTools:
    """The corrector runs as a before-validator on every ticker-aware tool."""

    @pytest.mark.parametrize(
        "args_model,extra_args",
        [
            (FindEventsArgs, DATE_RANGE),
            (FindFilingsArgs, DATE_RANGE),
            (FindCompanyDocsArgs, DATE_RANGE),
            (FindEquitiesArgs, {}),
            (GetEquitySummariesArgs, {}),
            (FindThirdBridgeEventsArgs, {}),
        ],
    )
    def test_spaced_ticker_list_is_corrected(self, args_model, extra_args):
        """A comma-and-space list is accepted rather than raising."""
        args = args_model(bloomberg_ticker="AAPL, MSFT", **extra_args)

        assert args.bloomberg_ticker == "AAPL:US,MSFT:US"

    def test_padded_ticker_is_corrected(self):
        """Leading and trailing whitespace is tolerated on a single ticker."""
        args = FindEquitiesArgs(bloomberg_ticker=" AAPL ")

        assert args.bloomberg_ticker == "AAPL:US"
