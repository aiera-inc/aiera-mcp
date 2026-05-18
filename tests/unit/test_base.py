#!/usr/bin/env python3

"""Unit tests for make_aiera_request retry and timeout behavior."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from aiera_mcp.tools.base import make_aiera_request


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
