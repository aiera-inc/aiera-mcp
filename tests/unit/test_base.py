#!/usr/bin/env python3

"""Unit tests for make_aiera_request retry and timeout behavior."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from aiera_mcp.tools.base import _redact_headers, _send_tool_log, make_aiera_request


def _ok_response(json_payload=None):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = json_payload or {"ok": True}
    response.text = '{"ok": true}'
    return response


@pytest.mark.unit
@pytest.mark.asyncio
class TestMakeAieraRequestRetries:
    async def test_succeeds_first_attempt(self):
        client = MagicMock()
        client.request = AsyncMock(return_value=_ok_response({"foo": "bar"}))

        result = await make_aiera_request(
            client=client,
            method="GET",
            endpoint="/test",
            api_key="key",
        )

        assert result == {"foo": "bar"}
        assert client.request.await_count == 1

    async def test_retries_on_connect_error_then_succeeds(self, monkeypatch):
        # No-op sleep so the test doesn't actually wait
        async def fast_sleep(_):
            return None

        monkeypatch.setattr("aiera_mcp.tools.base.asyncio.sleep", fast_sleep)

        client = MagicMock()
        client.request = AsyncMock(
            side_effect=[httpx.ConnectError("refused"), _ok_response()]
        )

        result = await make_aiera_request(
            client=client,
            method="GET",
            endpoint="/test",
            api_key="key",
        )

        assert result == {"ok": True}
        assert client.request.await_count == 2

    async def test_raises_after_max_connect_error_attempts(self, monkeypatch):
        async def fast_sleep(_):
            return None

        monkeypatch.setattr("aiera_mcp.tools.base.asyncio.sleep", fast_sleep)

        client = MagicMock()
        client.request = AsyncMock(side_effect=httpx.ConnectError("refused"))

        with pytest.raises(Exception, match="Network error calling Aiera API"):
            await make_aiera_request(
                client=client,
                method="GET",
                endpoint="/test",
                api_key="key",
            )

        assert client.request.await_count == 2

    async def test_timeout_does_not_retry(self):
        client = MagicMock()
        client.request = AsyncMock(side_effect=httpx.ReadTimeout("slow"))

        with pytest.raises(Exception, match="timed out"):
            await make_aiera_request(
                client=client,
                method="GET",
                endpoint="/test",
                api_key="key",
            )

        # Exactly one attempt — no retry on timeout
        assert client.request.await_count == 1

    async def test_timeout_message_includes_configured_timeout(self):
        from aiera_mcp.config import get_settings

        client = MagicMock()
        client.request = AsyncMock(side_effect=httpx.ReadTimeout("slow"))

        configured = get_settings().http_timeout

        with pytest.raises(Exception) as exc_info:
            await make_aiera_request(
                client=client,
                method="GET",
                endpoint="/test",
                api_key="key",
            )

        assert f"{configured}s" in str(exc_info.value)
        assert "heavy load" in str(exc_info.value)

    async def test_non_transient_request_error_does_not_retry(self):
        client = MagicMock()
        client.request = AsyncMock(
            side_effect=httpx.RemoteProtocolError("server disconnected")
        )

        with pytest.raises(Exception, match="Network error calling Aiera API"):
            await make_aiera_request(
                client=client,
                method="GET",
                endpoint="/test",
                api_key="key",
            )

        assert client.request.await_count == 1


@pytest.mark.unit
class TestRedactHeaders:
    def test_redacts_api_key(self):
        out = _redact_headers(
            {"X-API-Key": "sekret", "Content-Type": "application/json"}
        )
        assert out["X-API-Key"] == "***REDACTED***"
        assert out["Content-Type"] == "application/json"

    def test_redacts_authorization_and_cookie(self):
        out = _redact_headers(
            {"Authorization": "Bearer abc", "Cookie": "session=xyz", "User-Agent": "ua"}
        )
        assert out["Authorization"] == "***REDACTED***"
        assert out["Cookie"] == "***REDACTED***"
        assert out["User-Agent"] == "ua"

    def test_does_not_mutate_input(self):
        original = {"X-API-Key": "sekret"}
        _redact_headers(original)
        assert original["X-API-Key"] == "sekret"

    def test_case_insensitive_match(self):
        out = _redact_headers(
            {
                "x-api-key": "sekret-lower",
                "X-Api-Key": "sekret-mixed",
                "AUTHORIZATION": "Bearer xyz",
            }
        )
        assert out["x-api-key"] == "***REDACTED***"
        assert out["X-Api-Key"] == "***REDACTED***"
        assert out["AUTHORIZATION"] == "***REDACTED***"


@pytest.mark.unit
@pytest.mark.asyncio
class TestApiKeyNeverLogged:
    async def test_api_key_not_in_error_logs_on_timeout(self, caplog):
        import logging

        client = MagicMock()
        client.request = AsyncMock(side_effect=httpx.ReadTimeout("slow"))

        api_key = "this-key-must-not-leak-abc123"
        with caplog.at_level(logging.ERROR), pytest.raises(Exception):
            await make_aiera_request(
                client=client,
                method="GET",
                endpoint="/test",
                api_key=api_key,
            )

        full_log = "\n".join(record.getMessage() for record in caplog.records)
        assert api_key not in full_log
        assert "***REDACTED***" in full_log

    async def test_api_key_not_in_error_logs_on_connect_error(
        self, caplog, monkeypatch
    ):
        import logging

        async def fast_sleep(_):
            return None

        monkeypatch.setattr("aiera_mcp.tools.base.asyncio.sleep", fast_sleep)

        client = MagicMock()
        client.request = AsyncMock(side_effect=httpx.ConnectError("refused"))

        api_key = "this-key-must-not-leak-xyz456"
        with caplog.at_level(logging.ERROR), pytest.raises(Exception):
            await make_aiera_request(
                client=client,
                method="GET",
                endpoint="/test",
                api_key=api_key,
            )

        full_log = "\n".join(record.getMessage() for record in caplog.records)
        assert api_key not in full_log
        assert "***REDACTED***" in full_log

    async def test_api_key_not_in_error_logs_on_non_2xx(self, caplog):
        import logging

        bad_response = MagicMock()
        bad_response.status_code = 500
        bad_response.text = "boom"

        client = MagicMock()
        client.request = AsyncMock(return_value=bad_response)

        api_key = "this-key-must-not-leak-pqr789"
        with caplog.at_level(logging.ERROR), pytest.raises(Exception):
            await make_aiera_request(
                client=client,
                method="GET",
                endpoint="/test",
                api_key=api_key,
            )

        full_log = "\n".join(record.getMessage() for record in caplog.records)
        assert api_key not in full_log
        assert "***REDACTED***" in full_log


@pytest.mark.unit
@pytest.mark.asyncio
class TestSendToolLogAuthFailureIsSilent:
    """`_send_tool_log` runs as fire-and-forget telemetry. When the configured
    api_key provider raises (unauthenticated request reaches the tool layer),
    the log helper must NOT itself emit a warning/error or traceback — one
    misbehaving client otherwise multiplies each failed tool call into stacked
    duplicate errors in Datadog."""

    async def test_silent_when_api_key_provider_raises(self, caplog):
        import logging

        from aiera_mcp import clear_api_key_provider, set_api_key_provider

        def raising_provider():
            raise ValueError("No user API key in request context")

        set_api_key_provider(raising_provider)
        try:
            with caplog.at_level(logging.WARNING):
                await _send_tool_log(
                    tool_name="find_events",
                    parameters={"q": "x"},
                    response=None,
                    is_error=True,
                )
        finally:
            clear_api_key_provider()

        # `get_api_key` itself emits one concise warning for the unauth case
        # (by design — see aiera_mcp/__init__.py). We only care that the
        # telemetry helper doesn't pile on with its own "MCP tool log: failed"
        # error + traceback, which was producing 2-3x duplicate stacked
        # tracebacks per failed call.
        bad = [
            r
            for r in caplog.records
            if r.levelno >= logging.WARNING
            and r.name.startswith("aiera_mcp.tools.base")
        ]
        assert not bad, (
            "_send_tool_log should fail silently when the api-key provider "
            f"raises, got: {[r.getMessage() for r in bad]}"
        )
