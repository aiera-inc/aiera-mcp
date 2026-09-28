#!/usr/bin/env python3

"""Tests for validators/behaviors added in the equity_ids / company_type /
conference_id / list-coercion PR (see review of aiera-inc/aiera-api#1377)."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.company_docs.models import FindCompanyDocsArgs
from aiera_mcp.tools.events.models import FindEventsArgs
from aiera_mcp.tools.equities.models import FindEquitiesArgs
from aiera_mcp.tools.search.models import SearchTranscriptsArgs

DATES = {"start_date": "2026-01-01", "end_date": "2026-03-01"}


@pytest.mark.unit
class TestCompanyDocsListCoercion:
    def test_single_multiword_list_item_not_split(self):
        # Regression: a single multi-word list item must NOT be split into pieces.
        a = FindCompanyDocsArgs(**DATES, keywords=["environmental social and governance"])
        assert a.keywords == "environmental social and governance"

    def test_categories_single_multiword_item_not_split(self):
        a = FindCompanyDocsArgs(**DATES, categories=["Investor Presentation"])
        assert a.categories == "Investor Presentation"

    def test_list_of_multiple_items_joined(self):
        a = FindCompanyDocsArgs(**DATES, categories=["press_release", "annual_report"])
        assert a.categories == "press_release,annual_report"

    def test_string_form_still_works(self):
        a = FindCompanyDocsArgs(**DATES, categories="press_release,annual_report")
        assert a.categories == "press_release,annual_report"

    def test_exclude_categories_accepts_list(self):
        a = FindCompanyDocsArgs(**DATES, exclude_categories=["press_release", "compliance"])
        assert a.exclude_categories == "press_release,compliance"

    def test_exclude_keywords_accepts_list_and_string(self):
        a = FindCompanyDocsArgs(**DATES, exclude_keywords=["ESG"])
        assert a.exclude_keywords == "ESG"
        b = FindCompanyDocsArgs(**DATES, exclude_keywords="ESG,risk")
        assert b.exclude_keywords == "ESG,risk"


@pytest.mark.unit
class TestConferenceIdCoercion:
    def test_events_conference_id_str_to_int(self):
        a = FindEventsArgs(**DATES, conference_id="12345")
        assert a.conference_id == 12345

    def test_events_conference_id_rejects_name(self):
        with pytest.raises(ValidationError):
            FindEventsArgs(**DATES, conference_id="Barclays Global Consumer Conference")

    def test_search_conference_id_str_to_int(self):
        a = SearchTranscriptsArgs(query_text="ai", conference_id="678")
        assert a.conference_id == 678

    def test_search_conference_id_rejects_name(self):
        with pytest.raises(ValidationError):
            SearchTranscriptsArgs(query_text="ai", conference_id="some conference name")


@pytest.mark.unit
class TestCompanyTypeValidation:
    @pytest.mark.parametrize("val", ["corporate", "government", "regulatory"])
    def test_equities_company_type_valid(self, val):
        assert FindEquitiesArgs(search="Federal Reserve", company_type=val).company_type == val

    def test_equities_company_type_invalid(self):
        with pytest.raises(ValidationError):
            FindEquitiesArgs(search="x", company_type="bank")

    @pytest.mark.parametrize("val", ["corporate", "government", "regulatory"])
    def test_events_company_type_valid(self, val):
        assert FindEventsArgs(**DATES, company_type=val).company_type == val

    def test_events_company_type_invalid(self):
        with pytest.raises(ValidationError):
            FindEventsArgs(**DATES, company_type="bank")


@pytest.mark.unit
class TestEventsEquityIds:
    def test_equity_ids_accepted(self):
        a = FindEventsArgs(**DATES, equity_ids="24829,25164", event_type="presentation")
        assert a.equity_ids == "24829,25164"

    def test_include_non_tradable_flag_present_on_equities(self):
        a = FindEquitiesArgs(search="Federal Reserve", include_non_tradable=True)
        assert a.include_non_tradable is True
