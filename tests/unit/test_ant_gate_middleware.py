# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Unit tests for AntGateMiddleware.

Tests the middleware that injects USER_TYPE into request state, ensuring:
- Default behavior (external) when ENABLE_ANT_GATE is not set
- Ant detection via X-ShadowTag-Ant-Gate header
- Feature flag gating (ENABLE_ANT_GATE env var)
- Response header injection for ant users
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure repo root is importable
import sys
from pathlib import Path

_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from apps.counselconduit.api.middleware_ant import AntGateMiddleware


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_request(headers: dict[str, str] | None = None) -> MagicMock:
    """Create a mock Starlette Request with optional headers."""
    request = MagicMock()
    request.state = MagicMock()
    # Starlette headers are case-insensitive Mapping
    _headers = {k.lower(): v for k, v in (headers or {}).items()}
    request.headers = MagicMock()
    request.headers.get = lambda key, default=None: _headers.get(key.lower(), default)
    return request


def _make_response(status_code: int = 200) -> MagicMock:
    """Create a mock Response."""
    response = MagicMock()
    response.status_code = status_code
    response.headers = {}
    return response


# ── Tests: Default Behavior ──────────────────────────────────────────────


class TestAntGateMiddlewareDefault:
    """Test AntGateMiddleware when ENABLE_ANT_GATE is not set (default off)."""

    @pytest.mark.asyncio
    async def test_user_type_defaults_to_external(self) -> None:
        """Without ENABLE_ANT_GATE, user_type should always be 'external'."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request()
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {}, clear=False):
            # Ensure ENABLE_ANT_GATE is not set
            os.environ.pop("ENABLE_ANT_GATE", None)
            result = await middleware.dispatch(request, call_next)

        assert request.state.user_type == "external"
        assert "X-Ant-Gate-Active" not in result.headers

    @pytest.mark.asyncio
    async def test_ant_header_ignored_when_flag_off(self) -> None:
        """X-ShadowTag-Ant-Gate header is ignored when feature flag is off."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request({"X-ShadowTag-Ant-Gate": "true"})
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": "false"}):
            result = await middleware.dispatch(request, call_next)

        assert request.state.user_type == "external"


# ── Tests: Feature Flag Enabled ──────────────────────────────────────────


class TestAntGateMiddlewareEnabled:
    """Test AntGateMiddleware when ENABLE_ANT_GATE is enabled."""

    @pytest.mark.asyncio
    async def test_ant_user_type_set_with_header(self) -> None:
        """When flag is on and header is present, user_type should be 'ant'."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request({"X-ShadowTag-Ant-Gate": "true"})
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": "true"}):
            result = await middleware.dispatch(request, call_next)

        assert request.state.user_type == "ant"
        assert result.headers["X-Ant-Gate-Active"] == "true"

    @pytest.mark.asyncio
    async def test_external_when_no_header(self) -> None:
        """When flag is on but no header, user_type should be 'external'."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request()
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": "true"}):
            result = await middleware.dispatch(request, call_next)

        assert request.state.user_type == "external"
        assert "X-Ant-Gate-Active" not in result.headers

    @pytest.mark.asyncio
    async def test_header_value_case_insensitive(self) -> None:
        """X-ShadowTag-Ant-Gate header value should be case-insensitive."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request({"X-ShadowTag-Ant-Gate": "TRUE"})
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": "1"}):
            result = await middleware.dispatch(request, call_next)

        assert request.state.user_type == "ant"

    @pytest.mark.asyncio
    async def test_invalid_header_value(self) -> None:
        """Invalid header value should not trigger ant mode."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request({"X-ShadowTag-Ant-Gate": "maybe"})
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": "true"}):
            await middleware.dispatch(request, call_next)

        assert request.state.user_type == "external"


# ── Tests: Feature Flag Variants ─────────────────────────────────────────


class TestAntGateFeatureFlagVariants:
    """Test various truthy/falsy values for ENABLE_ANT_GATE."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", ["true", "1", "t", "y", "yes", "TRUE", "True", "YES"])
    async def test_truthy_values_enable_gate(self, value: str) -> None:
        """All truthy variants should enable the ant gate."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request({"X-ShadowTag-Ant-Gate": "true"})
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": value}):
            await middleware.dispatch(request, call_next)

        assert request.state.user_type == "ant"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("value", ["false", "0", "no", "n", "off", ""])
    async def test_falsy_values_disable_gate(self, value: str) -> None:
        """Falsy variants should keep the ant gate disabled."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request({"X-ShadowTag-Ant-Gate": "true"})
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": value}):
            await middleware.dispatch(request, call_next)

        assert request.state.user_type == "external"


# ── Tests: Response Header ───────────────────────────────────────────────


class TestAntGateResponseHeaders:
    """Test response header injection behavior."""

    @pytest.mark.asyncio
    async def test_ant_response_header_set(self) -> None:
        """Ant users should get X-Ant-Gate-Active response header."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request({"X-ShadowTag-Ant-Gate": "true"})
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": "true"}):
            result = await middleware.dispatch(request, call_next)

        assert result.headers["X-Ant-Gate-Active"] == "true"

    @pytest.mark.asyncio
    async def test_external_no_ant_header(self) -> None:
        """External users should NOT get X-Ant-Gate-Active response header."""
        middleware = AntGateMiddleware(app=MagicMock())
        request = _make_request()
        response = _make_response()

        async def call_next(_req):
            return response

        with patch.dict(os.environ, {"ENABLE_ANT_GATE": "true"}):
            result = await middleware.dispatch(request, call_next)

        assert "X-Ant-Gate-Active" not in result.headers
