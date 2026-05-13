#!/usr/bin/env python3

"""Unit tests for server-level functionality."""

import pytest

from aiera_mcp.server import get_instructions, server


@pytest.mark.unit
class TestGetInstructions:
    def test_returns_non_empty_string(self):
        result = get_instructions()
        assert isinstance(result, str)
        assert result.strip()

    def test_mentions_required_bootstrap_tools(self):
        result = get_instructions()
        assert "get_core_instructions" in result
        assert "get_grammar_template" in result

    def test_includes_current_date(self):
        from datetime import datetime

        result = get_instructions()
        assert datetime.now().strftime("%B") in result
        assert str(datetime.now().year) in result

    def test_wired_into_mcp_server(self):
        assert server.instructions
        assert "get_core_instructions" in server.instructions
        assert "get_grammar_template" in server.instructions
