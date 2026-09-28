#!/usr/bin/env python3

"""Unit tests for argument coercion/validation on the events, equities,
company-docs and search arg models: list/string coercion, company_type,
conference_id, and equity_ids handling."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.company_docs.models import FindCompanyDocsArgs
from aiera_mcp.tools.events.models import FindEventsArgs
from aiera_mcp.tools.equities.models import FindEquitiesArgs
from aiera_mcp.tools.search.models import SearchTranscriptsArgs

DATES = {"start_date": "2026-01-01", "end_date": "2026-03-01"}


@pytest.mark.unit
class TestCompanyDocsListCoercion:
    def test_keywords_single_multiword_item_not_split(self):
        # Regression: a single multi-word keyword must NOT be split into pieces.
        a = FindCompanyDocsArgs(**DATES, keywords=["environmental social and governance"])
        assert a.keywords == "environmental social and governance"

    def test_categories_single_slug_passthrough(self):
        a = FindCompanyDocsArgs(**DATES, categories=["press_release"])
        assert a.categories == "press_release"

    def test_categories_list_joined(self):
        a = FindCompanyDocsArgs(**DATES, categories=["press_release", "annual_report"])
        assert a.categories == "press_release,annual_report"

    def test_categories_string_form(self):
        a = FindCompanyDocsArgs(**DATES, categories="press_release,annual_report")
        assert a.categories == "press_release,annual_report"

    def test_exclude_categories_accepts_list(self):
        a = FindCompanyDocsArgs(**DATES, exclude_categories=["press_release", "compliance"])
        assert a.exclude_categories == "press_release,compliance"

    def test_exclude_keywords_list_and_string(self):
        assert FindCompanyDocsArgs(**DATES, exclude_keywords=["ESG"]).exclude_keywords == "ESG"
        assert FindCompanyDocsArgs(**DATES, exclude_keywords="ESG,risk").exclude_keywords == "ESG,risk"


@pytest.mark.unit
class TestConferenceIdCoercion:
    def test_events_str_to_int(self):
        assert FindEventsArgs(**DATES, conference_id="12345").conference_id == 12345

    def test_events_rejects_name(self):
        with pytest.raises(ValidationError):
            FindEventsArgs(**DATES, conference_id="Barclays Global Consumer Conference")

    def test_search_str_to_int(self):
        assert SearchTranscriptsArgs(query_text="ai", conference_id="678").conference_id == 678

    def test_search_rejects_name(self):
        with pytest.raises(ValidationError):
            SearchTranscriptsArgs(query_text="ai", conference_id="some conference name")


@pytest.mark.unit
class TestCompanyTypeValidation:
    @pytest.mark.parametrize("val", ["corporate", "government", "regulatory"])
    def test_equities_valid(self, val):
        assert FindEquitiesArgs(search="Federal Reserve", company_type=val).company_type == val

    def test_equities_invalid(self):
        with pytest.raises(ValidationError):
            FindEquitiesArgs(search="x", company_type="bank")

    @pytest.mark.parametrize("val", ["corporate", "government", "regulatory"])
    def test_events_valid(self, val):
        assert FindEventsArgs(**DATES, company_type=val).company_type == val

    def test_events_invalid(self):
        with pytest.raises(ValidationError):
            FindEventsArgs(**DATES, company_type="bank")


@pytest.mark.unit
class TestEventsEquityIds:
    def test_comma_string(self):
        a = FindEventsArgs(**DATES, equity_ids="24829,25164", event_type="presentation")
        assert a.equity_ids == "24829,25164"

    def test_list_input(self):
        a = FindEventsArgs(**DATES, equity_ids=[24829, 25164], event_type="presentation")
        assert a.equity_ids == "24829,25164"

    def test_whitespace_stripped(self):
        a = FindEventsArgs(**DATES, equity_ids="24829, 25164")
        assert a.equity_ids == "24829,25164"

    def test_non_integer_rejected(self):
        with pytest.raises(ValidationError):
            FindEventsArgs(**DATES, equity_ids="abc")

    def test_none_omitted(self):
        assert FindEventsArgs(**DATES, equity_ids=None).equity_ids is None

    def test_empty_string_treated_as_absent(self):
        assert FindEventsArgs(**DATES, equity_ids="").equity_ids is None

    def test_comma_only_raises(self):
        # Must NOT collapse to "" (backend would return every event in the window).
        with pytest.raises(ValidationError):
            FindEventsArgs(**DATES, equity_ids=",")

    def test_empty_list_raises(self):
        with pytest.raises(ValidationError):
            FindEventsArgs(**DATES, equity_ids=[])


@pytest.mark.unit
class TestIncludeNonTradable:
    def test_defaults_false_and_settable(self):
        assert FindEquitiesArgs(search="Apple").include_non_tradable is False
        assert FindEquitiesArgs(search="Federal Reserve", include_non_tradable=True).include_non_tradable is True
