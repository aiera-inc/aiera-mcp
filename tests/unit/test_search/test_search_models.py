#!/usr/bin/env python3

"""Unit tests for search models."""

import pytest
from pydantic import ValidationError

from aiera_mcp.tools.search.models import (
    SearchTranscriptsArgs,
    SearchFilingsArgs,
    SearchResearchArgs,
    SearchCompanyDocsArgs,
    SearchThirdbridgeArgs,
    SearchTranscriptsResponse,
    SearchFilingsResponse,
    SearchResearchResponse,
    SearchCompanyDocsResponse,
    SearchThirdbridgeResponse,
)


@pytest.mark.unit
class TestSearchTranscriptsArgs:
    """Test SearchTranscriptsArgs model."""

    def test_valid_search_transcripts_args(self):
        """Test valid SearchTranscriptsArgs creation."""
        args = SearchTranscriptsArgs(
            query_text="earnings guidance",
            event_ids=[1, 2, 3],
            equity_ids=[100, 200],
            start_date="2024-01-01",
            end_date="2024-12-31",
            transcript_section="q_and_a",
            event_type="earnings",
            size=25,
        )

        assert args.query_text == "earnings guidance"
        assert args.event_ids == [1, 2, 3]
        assert args.equity_ids == [100, 200]
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.transcript_section == "q_and_a"
        assert args.event_type == "earnings"
        assert args.size == 25
        assert args.search_after is None

    def test_search_transcripts_args_defaults(self):
        """Test SearchTranscriptsArgs default values."""
        args = SearchTranscriptsArgs(
            query_text="test query",
            event_ids=[1],
            equity_ids=[1],
        )

        assert args.start_date == ""
        assert args.end_date == ""
        assert args.transcript_section == ""
        assert args.event_type == "earnings"
        assert args.size == 25
        assert args.search_after is None
        assert args.originating_prompt is None
        assert args.include_base_instructions is True
        assert args.exclude_instructions is False

    def test_search_transcripts_args_with_originating_prompt(self):
        """Test SearchTranscriptsArgs with originating_prompt field."""
        args = SearchTranscriptsArgs(
            query_text="earnings",
            event_ids=[1],
            equity_ids=[1],
            originating_prompt="What did management say about inflation?",
            include_base_instructions=False,
        )

        assert args.originating_prompt == "What did management say about inflation?"
        assert args.include_base_instructions is False

    def test_search_transcripts_args_required_fields(self):
        """Test that query_text is required."""
        # query_text is required
        with pytest.raises(ValidationError):
            SearchTranscriptsArgs()

        # event_ids and equity_ids have default values (None)
        args = SearchTranscriptsArgs(query_text="test")
        assert args.query_text == "test"
        assert args.event_ids is None
        assert args.equity_ids is None


@pytest.mark.unit
class TestSearchFilingsArgs:
    """Test SearchFilingsArgs model."""

    def test_valid_search_filings_args(self):
        """Test valid SearchFilingsArgs creation."""
        args = SearchFilingsArgs(
            query_text="risk factors",
            equity_ids=[100, 200],
            filing_ids=["filing123", "filing456"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            filing_type="10-K",
            size=30,
        )

        assert args.query_text == "risk factors"
        assert args.equity_ids == [100, 200]
        assert args.filing_ids == ["filing123", "filing456"]
        assert args.start_date == "2024-01-01"
        assert args.end_date == "2024-12-31"
        assert args.filing_type == "10-K"
        assert args.size == 30

    def test_search_filings_args_defaults(self):
        """Test SearchFilingsArgs default values."""
        args = SearchFilingsArgs(
            query_text="test query",
            equity_ids=[1],
        )

        assert args.filing_ids is None
        assert args.start_date == ""
        assert args.end_date == ""
        assert args.filing_type == ""
        assert args.size == 25
        assert args.search_after is None

    def test_search_filings_args_required_fields(self):
        """Test that query_text is required."""
        with pytest.raises(ValidationError):
            SearchFilingsArgs()

        args = SearchFilingsArgs(query_text="test")
        assert args.query_text == "test"
        assert args.filing_ids is None
        assert args.equity_ids is None


@pytest.mark.unit
class TestSearchResearchArgs:
    """Test SearchResearchArgs model."""

    def test_valid_search_research_args(self):
        """Test valid SearchResearchArgs creation."""
        args = SearchResearchArgs(
            query_text="market trends",
            document_ids=["research123", "research456"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            author_ids=["12345"],
            aiera_provider_ids=["krypton"],
            asset_classes=["Equity"],
            asset_types=["Common Stock"],
            size=30,
        )

        assert args.query_text == "market trends"
        assert args.document_ids == ["research123", "research456"]
        assert args.author_ids == ["12345"]
        assert args.aiera_provider_ids == ["krypton"]
        assert args.asset_classes == ["Equity"]
        assert args.asset_types == ["Common Stock"]
        assert args.size == 30

    def test_search_research_args_defaults(self):
        """Test SearchResearchArgs default values."""
        args = SearchResearchArgs(query_text="test query")

        assert args.document_ids is None
        assert args.bloomberg_ticker is None
        assert args.start_date == ""
        assert args.end_date == ""
        assert args.author_ids is None
        assert args.aiera_provider_ids is None
        assert args.asset_classes is None
        assert args.asset_types is None
        assert args.size == 25

    def test_search_research_args_with_bloomberg_ticker(self):
        """Test SearchResearchArgs with bloomberg_ticker parameter."""
        args = SearchResearchArgs(
            query_text="price target changes",
            bloomberg_ticker="MA:US",
            start_date="2025-07-01",
            end_date="2025-12-31",
        )

        assert args.query_text == "price target changes"
        assert args.bloomberg_ticker == "MA:US"
        assert args.start_date == "2025-07-01"
        assert args.end_date == "2025-12-31"

    def test_search_research_args_required_fields(self):
        """Test that query_text is required."""
        with pytest.raises(ValidationError):
            SearchResearchArgs()

        args = SearchResearchArgs(query_text="test")
        assert args.query_text == "test"
        assert args.document_ids is None
        assert args.bloomberg_ticker is None


@pytest.mark.unit
class TestSearchResponses:
    """Test search response models with pass-through pattern."""

    def test_search_transcripts_response(self):
        """Test SearchTranscriptsResponse model with pass-through data."""
        response = SearchTranscriptsResponse(
            instructions=["Test instruction"],
            response={"result": [{"text": "test", "_score": 9.0}]},
        )

        assert response.response is not None
        assert len(response.response["result"]) == 1
        assert response.instructions == ["Test instruction"]

    def test_search_filings_response(self):
        """Test SearchFilingsResponse model with pass-through data."""
        response = SearchFilingsResponse(
            instructions=["Test instruction"],
            response={"result": [{"test": "data"}]},
        )

        assert response.response is not None
        assert len(response.response["result"]) == 1

    def test_search_response_empty_results(self):
        """Test search responses with empty results."""
        transcript_response = SearchTranscriptsResponse(
            instructions=[],
            response={"result": []},
        )
        assert transcript_response.response["result"] == []

        filing_response = SearchFilingsResponse(
            instructions=[],
            response={"result": []},
        )
        assert filing_response.response["result"] == []

    def test_search_research_response(self):
        """Test SearchResearchResponse model with pass-through data."""
        response = SearchResearchResponse(
            instructions=["Test instruction"],
            response={"result": [{"test": "data"}]},
        )

        assert response.response is not None
        assert len(response.response["result"]) == 1

    def test_search_response_null_response(self):
        """Test search responses with null response."""
        transcript_response = SearchTranscriptsResponse(
            instructions=[],
            response=None,
        )
        assert transcript_response.response is None

        filing_response = SearchFilingsResponse(
            instructions=[],
            response=None,
        )
        assert filing_response.response is None

        research_response = SearchResearchResponse(
            instructions=[],
            response=None,
        )
        assert research_response.response is None


@pytest.mark.unit
class TestSearchModelSerialization:
    """Test serialization of search models."""

    def test_search_transcripts_args_json_schema(self):
        """Test that SearchTranscriptsArgs generates valid JSON schema."""
        schema = SearchTranscriptsArgs.model_json_schema()

        assert "properties" in schema
        assert "query_text" in schema["properties"]
        assert "event_ids" in schema["properties"]
        assert "equity_ids" in schema["properties"]
        assert "size" in schema["properties"]
        assert "search_after" in schema["properties"]

    def test_search_filings_args_json_schema(self):
        """Test that SearchFilingsArgs generates valid JSON schema."""
        schema = SearchFilingsArgs.model_json_schema()

        assert "properties" in schema
        assert "query_text" in schema["properties"]
        assert "equity_ids" in schema["properties"]
        assert "filing_type" in schema["properties"]

    def test_search_research_args_json_schema(self):
        """Test that SearchResearchArgs generates valid JSON schema."""
        schema = SearchResearchArgs.model_json_schema()

        assert "properties" in schema
        assert "query_text" in schema["properties"]
        assert "document_ids" in schema["properties"]
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]
        assert "author_ids" in schema["properties"]
        assert "aiera_provider_ids" in schema["properties"]
        assert "asset_classes" in schema["properties"]
        assert "asset_types" in schema["properties"]
        assert "size" in schema["properties"]
        assert "search_after" in schema["properties"]


@pytest.mark.unit
class TestSearchCompanyDocsArgs:
    """Test SearchCompanyDocsArgs model."""

    def test_valid_search_company_docs_args(self):
        """Test valid SearchCompanyDocsArgs creation."""
        args = SearchCompanyDocsArgs(
            query_text="sustainability initiatives",
            company_doc_ids=[12345, 67890],
            company_ids=[1, 2],
            categories=["Investor Presentation"],
            keywords=["sustainability", "ESG"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            size=30,
        )

        assert args.query_text == "sustainability initiatives"
        assert args.company_doc_ids == [12345, 67890]
        assert args.company_ids == [1, 2]
        assert args.categories == ["Investor Presentation"]
        assert args.keywords == ["sustainability", "ESG"]
        assert args.size == 30

    def test_search_company_docs_args_defaults(self):
        """Test SearchCompanyDocsArgs default values."""
        args = SearchCompanyDocsArgs(query_text="test query")

        assert args.company_doc_ids is None
        assert args.company_ids is None
        assert args.categories is None
        assert args.keywords is None
        assert args.start_date == ""
        assert args.end_date == ""
        assert args.size == 25

    def test_search_company_docs_args_required_fields(self):
        """Test that query_text is required."""
        with pytest.raises(ValidationError):
            SearchCompanyDocsArgs()

        args = SearchCompanyDocsArgs(query_text="test")
        assert args.query_text == "test"

    def test_search_company_docs_args_json_schema(self):
        """Test that SearchCompanyDocsArgs generates valid JSON schema."""
        schema = SearchCompanyDocsArgs.model_json_schema()

        assert "properties" in schema
        assert "query_text" in schema["properties"]
        assert "company_doc_ids" in schema["properties"]
        assert "company_ids" in schema["properties"]
        assert "categories" in schema["properties"]
        assert "keywords" in schema["properties"]


@pytest.mark.unit
class TestSearchThirdbridgeArgs:
    """Test SearchThirdbridgeArgs model."""

    def test_valid_search_thirdbridge_args(self):
        """Test valid SearchThirdbridgeArgs creation."""
        args = SearchThirdbridgeArgs(
            query_text="semiconductor supply chain",
            company_ids=[1, 42],
            thirdbridge_ids=["TB-12345", "TB-67890"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            event_content_type="Interview",
            size=30,
        )

        assert args.query_text == "semiconductor supply chain"
        assert args.company_ids == [1, 42]
        assert args.thirdbridge_ids == ["TB-12345", "TB-67890"]
        assert args.event_content_type == "Interview"
        assert args.size == 30

    def test_search_thirdbridge_args_defaults(self):
        """Test SearchThirdbridgeArgs default values."""
        args = SearchThirdbridgeArgs(query_text="test query")

        assert args.company_ids is None
        assert args.thirdbridge_ids is None
        assert args.start_date == ""
        assert args.end_date == ""
        assert args.event_content_type == ""
        assert args.size == 25

    def test_search_thirdbridge_args_required_fields(self):
        """Test that query_text is required."""
        with pytest.raises(ValidationError):
            SearchThirdbridgeArgs()

        args = SearchThirdbridgeArgs(query_text="test")
        assert args.query_text == "test"

    def test_search_thirdbridge_args_json_schema(self):
        """Test that SearchThirdbridgeArgs generates valid JSON schema."""
        schema = SearchThirdbridgeArgs.model_json_schema()

        assert "properties" in schema
        assert "query_text" in schema["properties"]
        assert "company_ids" in schema["properties"]
        assert "thirdbridge_ids" in schema["properties"]
        assert "event_content_type" in schema["properties"]


@pytest.mark.unit
class TestNewSearchResponses:
    """Test new search response models with pass-through pattern."""

    def test_search_company_docs_response(self):
        """Test SearchCompanyDocsResponse model with pass-through data."""
        response = SearchCompanyDocsResponse(
            instructions=["Test instruction"],
            response={"result": [{"test": "data"}]},
        )

        assert response.response is not None
        assert len(response.response["result"]) == 1

    def test_search_thirdbridge_response(self):
        """Test SearchThirdbridgeResponse model with pass-through data."""
        response = SearchThirdbridgeResponse(
            instructions=["Test instruction"],
            response={"result": [{"test": "data"}]},
        )

        assert response.response is not None
        assert len(response.response["result"]) == 1

    def test_search_company_docs_response_null(self):
        """Test SearchCompanyDocsResponse with null response."""
        response = SearchCompanyDocsResponse(
            instructions=[],
            response=None,
        )
        assert response.response is None

    def test_search_thirdbridge_response_null(self):
        """Test SearchThirdbridgeResponse with null response."""
        response = SearchThirdbridgeResponse(
            instructions=[],
            response=None,
        )
        assert response.response is None
