#!/usr/bin/env python3

"""Unit tests for get_api_key() provider behavior — log noise reduction."""

import logging

import pytest

from aiera_mcp import clear_api_key_provider, get_api_key, set_api_key_provider


@pytest.mark.unit
class TestGetApiKeyProviderLogging:
    def teardown_method(self):
        clear_api_key_provider()

    def test_unauthenticated_provider_error_logs_warning_without_traceback(
        self, caplog
    ):
        def provider():
            raise ValueError(
                "No user API key in request context — request is unauthenticated"
            )

        set_api_key_provider(provider)

        with (
            caplog.at_level(logging.WARNING),
            pytest.raises(
                ValueError, match="Failed to get API key from configured provider"
            ),
        ):
            get_api_key()

        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        warning_records = [r for r in caplog.records if r.levelno == logging.WARNING]

        assert not error_records, "should not log at ERROR for unauth case"
        assert any(
            "No user API key in request context" in r.getMessage()
            for r in warning_records
        )
        assert all(r.exc_info is None for r in warning_records)

    def test_unexpected_provider_error_still_logs_with_traceback(self, caplog):
        def provider():
            raise RuntimeError("something genuinely broken")

        set_api_key_provider(provider)

        with (
            caplog.at_level(logging.ERROR),
            pytest.raises(
                ValueError, match="Failed to get API key from configured provider"
            ),
        ):
            get_api_key()

        error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
        assert error_records, "unexpected exceptions should still log ERROR"
        assert any(
            r.exc_info is not None for r in error_records
        ), "unexpected exceptions should keep their traceback"

    def test_successful_provider_does_not_log_error_or_warning(self, caplog):
        def provider():
            return "abc123"

        set_api_key_provider(provider)

        with caplog.at_level(logging.WARNING):
            result = get_api_key()

        assert result == "abc123"
        assert not any(r.levelno >= logging.WARNING for r in caplog.records)
