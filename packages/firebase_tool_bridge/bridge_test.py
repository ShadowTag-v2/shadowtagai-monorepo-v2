# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tests for ToolBridge — the execution dispatch core."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from packages.firebase_tool_bridge.bridge import (
    BridgeResult,
    CallStatus,
    ConfirmationProvider,
    ToolBridge,
    _summarize_result,
)
from packages.firebase_tool_bridge.evidence import EvidenceLogger
from packages.firebase_tool_bridge.registry import FunctionRegistry, RiskTier


# --- Fixtures ---


def _echo(**kwargs):
    """Simple test function that echoes its arguments."""
    return kwargs


def _failing_fn(**kwargs):
    """Test function that always raises."""
    msg = "Intentional test failure"
    raise RuntimeError(msg)


def _adder(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


class DenyAllConfirmation(ConfirmationProvider):
    """Confirmation provider that always denies."""

    def request_confirmation(self, function_name, args, risk_tier, action_tags):
        return False


class ApproveAllConfirmation(ConfirmationProvider):
    """Confirmation provider that always approves."""

    def request_confirmation(self, function_name, args, risk_tier, action_tags):
        return True


@pytest.fixture
def tmp_repo(tmp_path):
    """Create a temporary repo root for evidence logging."""
    return tmp_path


@pytest.fixture
def registry():
    """Create a fresh function registry with test functions."""
    reg = FunctionRegistry()
    reg.register("echo", _echo, RiskTier.LOW, description="Echo args")
    reg.register("add", _adder, RiskTier.LOW, description="Add two numbers")
    reg.register(
        "deploy",
        _echo,
        RiskTier.HIGH,
        description="Deployment action",
        action_tags=frozenset({"deployment"}),
    )
    reg.register("fail", _failing_fn, RiskTier.LOW, description="Always fails")
    return reg


@pytest.fixture
def bridge(registry, tmp_repo):
    """Create a ToolBridge with auto-approve confirmation."""
    return ToolBridge(
        registry,
        evidence=EvidenceLogger(repo_root=tmp_repo),
        confirmation=ApproveAllConfirmation(),
        repo_root=tmp_repo,
    )


# --- Tests ---


class TestBridgeHandle:
    """Test the bridge.handle() dispatch method."""

    def test_successful_call(self, bridge):
        result = bridge.handle("echo", {"message": "hello"})
        assert result.status == CallStatus.SUCCESS
        assert result.result == {"message": "hello"}
        assert result.error is None

    def test_successful_add(self, bridge):
        result = bridge.handle("add", {"a": 3, "b": 7})
        assert result.status == CallStatus.SUCCESS
        assert result.result == 10

    def test_unregistered_function_rejected(self, bridge):
        result = bridge.handle("nonexistent", {"x": 1})
        assert result.status == CallStatus.REJECTED_UNREGISTERED
        assert "not registered" in result.error

    def test_empty_args_defaults(self, bridge):
        result = bridge.handle("echo")
        assert result.status == CallStatus.SUCCESS
        assert result.result == {}

    def test_function_error_captured(self, bridge):
        result = bridge.handle("fail", {})
        assert result.status == CallStatus.ERROR
        assert "RuntimeError" in result.error

    def test_confirmation_denied(self, registry, tmp_repo):
        deny_bridge = ToolBridge(
            registry,
            evidence=EvidenceLogger(repo_root=tmp_repo),
            confirmation=DenyAllConfirmation(),
        )
        result = deny_bridge.handle("deploy", {"target": "prod"})
        assert result.status == CallStatus.REJECTED_CONFIRMATION
        assert "denied" in result.error.lower()

    def test_confirmation_approved(self, bridge):
        result = bridge.handle("deploy", {"target": "staging"})
        assert result.status == CallStatus.SUCCESS


class TestBridgeResult:
    """Test BridgeResult serialization."""

    def test_success_response(self):
        br = BridgeResult(
            status=CallStatus.SUCCESS,
            function_name="test",
            result={"data": 42},
        )
        resp = br.to_function_response()
        assert resp == {"result": {"data": 42}}

    def test_error_response(self):
        br = BridgeResult(
            status=CallStatus.ERROR,
            function_name="test",
            error="Something broke",
        )
        resp = br.to_function_response()
        assert resp["error"] == "Something broke"
        assert resp["status"] == "error"

    def test_rejected_response(self):
        br = BridgeResult(
            status=CallStatus.REJECTED_UNREGISTERED,
            function_name="ghost",
        )
        resp = br.to_function_response()
        assert resp["status"] == "rejected_unregistered"


class TestBatchHandle:
    """Test batch dispatch."""

    def test_batch_all_succeed(self, bridge):
        calls = [
            ("echo", {"msg": "a"}),
            ("add", {"a": 1, "b": 2}),
        ]
        results = bridge.handle_batch(calls)
        assert len(results) == 2
        assert all(r.status == CallStatus.SUCCESS for r in results)

    def test_batch_mixed_results(self, bridge):
        calls = [
            ("echo", {"msg": "ok"}),
            ("nonexistent", {}),
            ("fail", {}),
        ]
        results = bridge.handle_batch(calls)
        assert results[0].status == CallStatus.SUCCESS
        assert results[1].status == CallStatus.REJECTED_UNREGISTERED
        assert results[2].status == CallStatus.ERROR


class TestEvidenceIntegration:
    """Test that evidence is actually written."""

    def test_evidence_file_created(self, bridge, tmp_repo):
        bridge.handle("echo", {"test": True})
        evidence_file = tmp_repo / ".agent" / "evidence" / "function_calls.ndjson"
        assert evidence_file.exists()

        lines = evidence_file.read_text().strip().split("\n")
        assert len(lines) >= 1

        record = json.loads(lines[-1])
        assert record["function_name"] == "echo"
        assert record["risk_tier"] == "low"
        assert record["success"] is True

    def test_rejected_call_logged(self, bridge, tmp_repo):
        bridge.handle("ghost_fn", {})
        evidence_file = tmp_repo / ".agent" / "evidence" / "function_calls.ndjson"
        lines = evidence_file.read_text().strip().split("\n")
        record = json.loads(lines[-1])
        assert record["success"] is False
        assert "unregistered" in record["execution_result_summary"]


class TestHooks:
    """Test pre/post hook mechanics."""

    def test_pre_hook_called(self, bridge):
        hook = MagicMock()
        bridge.add_pre_hook(hook)
        bridge.handle("echo", {"x": 1})
        hook.assert_called_once()

    def test_post_hook_called(self, bridge):
        hook = MagicMock()
        bridge.add_post_hook(hook)
        bridge.handle("echo", {"x": 1})
        hook.assert_called_once()

    def test_hook_failure_does_not_break_call(self, bridge):
        def bad_hook(*args):
            msg = "hook exploded"
            raise ValueError(msg)

        bridge.add_pre_hook(bad_hook)
        result = bridge.handle("echo", {"x": 1})
        assert result.status == CallStatus.SUCCESS


class TestSummarizeResult:
    """Test the _summarize_result utility."""

    def test_none(self):
        assert _summarize_result(None) == "None"

    def test_dict(self):
        assert "dict(2 keys" in _summarize_result({"a": 1, "b": 2})

    def test_list(self):
        assert _summarize_result([1, 2, 3]) == "list(3 items)"

    def test_short_string(self):
        assert _summarize_result("hello") == "str(5)"

    def test_int(self):
        assert _summarize_result(42) == "int=42"

    def test_bool(self):
        assert _summarize_result(True) == "bool=True"
