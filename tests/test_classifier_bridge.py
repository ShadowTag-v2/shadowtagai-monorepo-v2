# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for the AGNT Classifier Bridge — ClassifiedGateway, MCP Policy, Diagnostics.

Covers:
    - MCP policy enforcement (denylist precedence, allowlist, reserved names)
    - ClassifiedGateway pipeline (allowlist → policy → classifier → fail-closed)
    - Telemetry accumulation
    - Diagnostics health checks
    - Edge cases and error paths

Reference: AGNT STATE B Spec P2.1, P2.3, P5.1, P6.1
"""

from __future__ import annotations

import pytest

from agnt_classifier.agnt_api import AGNTClassifier
from agnt_classifier.allowlist import (
    CLASSIFIER_REQUIRED,
    SAFE_ALLOWLIST,
    requires_classifier,
)
from agnt_classifier.bridge import (
    ClassifiedGateway,
    GatewayAction,
    GatewayResult,
    GatewayTelemetry,
)
from agnt_classifier.diagnostics import (
    ClassifierDiagnostics,
    DiagnosticCheck,
    DiagnosticStatus,
    run_classifier_diagnostics,
)
from agnt_classifier.mcp_policy import (
    MCPPolicyConfig,
    MCPServerInfo,
    PolicyEntry,
    PolicyEntryType,
    RESERVED_SERVER_NAMES,
    _command_arrays_match,
    _url_matches_pattern,
    filter_servers_by_policy,
    get_default_agnt_policy,
    is_mcp_server_allowed_by_policy,
    is_mcp_server_denied,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# § MCP Policy Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestPolicyEntry:
    """Tests for PolicyEntry factory methods."""

    def test_from_name(self):
        entry = PolicyEntry.from_name("firebase-mcp-server")
        assert entry.entry_type == PolicyEntryType.NAME
        assert entry.server_name == "firebase-mcp-server"
        assert entry.server_command == ()
        assert entry.server_url == ""

    def test_from_command_list(self):
        entry = PolicyEntry.from_command(["npx", "-y", "firebase-tools"])
        assert entry.entry_type == PolicyEntryType.COMMAND
        assert entry.server_command == ("npx", "-y", "firebase-tools")

    def test_from_command_tuple(self):
        entry = PolicyEntry.from_command(("node", "server.js"))
        assert entry.server_command == ("node", "server.js")

    def test_from_url(self):
        entry = PolicyEntry.from_url("https://mcp.example.com/v1/*")
        assert entry.entry_type == PolicyEntryType.URL
        assert entry.server_url == "https://mcp.example.com/v1/*"

    def test_frozen_immutability(self):
        entry = PolicyEntry.from_name("test")
        with pytest.raises(AttributeError):
            entry.server_name = "modified"  # type: ignore[misc]


class TestCommandArrayMatch:
    """Tests for _command_arrays_match."""

    def test_exact_match(self):
        assert _command_arrays_match(("node", "server.js"), ["node", "server.js"])

    def test_glob_executable(self):
        assert _command_arrays_match(("*/npx",), ["/usr/local/bin/npx"])

    def test_prefix_match(self):
        assert _command_arrays_match(("npx",), ["npx", "-y", "extra-arg"])

    def test_too_many_pattern_elements(self):
        assert not _command_arrays_match(("a", "b", "c"), ["a", "b"])

    def test_empty_pattern(self):
        assert not _command_arrays_match((), ["node"])

    def test_empty_actual(self):
        assert not _command_arrays_match(("node",), [])

    def test_arg_mismatch(self):
        assert not _command_arrays_match(("node", "server.js"), ["node", "other.js"])


class TestUrlMatchesPattern:
    """Tests for _url_matches_pattern."""

    def test_exact_match(self):
        assert _url_matches_pattern(
            "https://mcp.example.com/v1/api",
            "https://mcp.example.com/v1/api",
        )

    def test_glob_path(self):
        assert _url_matches_pattern(
            "https://mcp.example.com/v1/tools",
            "https://mcp.example.com/v1/*",
        )

    def test_scheme_mismatch(self):
        assert not _url_matches_pattern(
            "http://mcp.example.com/v1",
            "https://mcp.example.com/v1",
        )

    def test_host_mismatch(self):
        assert not _url_matches_pattern(
            "https://other.example.com/v1",
            "https://mcp.example.com/v1",
        )

    def test_port_mismatch(self):
        assert not _url_matches_pattern(
            "https://mcp.example.com:8080/v1",
            "https://mcp.example.com:9090/v1",
        )

    def test_default_path_glob(self):
        assert _url_matches_pattern(
            "https://mcp.example.com/anything",
            "https://mcp.example.com",
        )


class TestReservedNames:
    """Tests for reserved server name blocking."""

    def test_claude_in_chrome_is_reserved(self):
        assert "claude-in-chrome" in RESERVED_SERVER_NAMES

    def test_computer_use_is_reserved(self):
        assert "computer-use" in RESERVED_SERVER_NAMES

    def test_agnt_internal_is_reserved(self):
        assert "agnt-internal" in RESERVED_SERVER_NAMES

    def test_normal_name_is_not_reserved(self):
        assert "firebase-mcp-server" not in RESERVED_SERVER_NAMES


class TestIsMcpServerDenied:
    """Tests for is_mcp_server_denied."""

    def test_reserved_name_always_denied(self):
        policy = MCPPolicyConfig()
        denied, entry = is_mcp_server_denied("claude-in-chrome", None, policy)
        assert denied
        assert entry is not None

    def test_reserved_case_insensitive(self):
        policy = MCPPolicyConfig()
        denied, _ = is_mcp_server_denied("Claude-In-Chrome", None, policy)
        assert denied

    def test_explicit_denylist_name(self):
        policy = MCPPolicyConfig(denied_servers=[PolicyEntry.from_name("evil-server")])
        denied, entry = is_mcp_server_denied("evil-server", MCPServerInfo(name="evil-server"), policy)
        assert denied

    def test_denylist_command_match(self):
        policy = MCPPolicyConfig(denied_servers=[PolicyEntry.from_command(["malware", "--run"])])
        info = MCPServerInfo(name="x", command=["malware", "--run"])
        denied, _ = is_mcp_server_denied("x", info, policy)
        assert denied

    def test_denylist_url_match(self):
        policy = MCPPolicyConfig(denied_servers=[PolicyEntry.from_url("https://evil.com/*")])
        info = MCPServerInfo(name="x", url="https://evil.com/mcp")
        denied, _ = is_mcp_server_denied("x", info, policy)
        assert denied

    def test_not_denied(self):
        policy = MCPPolicyConfig()
        denied, _ = is_mcp_server_denied("firebase-mcp-server", MCPServerInfo(name="firebase-mcp-server"), policy)
        assert not denied


class TestIsMcpServerAllowedByPolicy:
    """Tests for is_mcp_server_allowed_by_policy — the core policy function."""

    def test_denylist_takes_precedence(self):
        """Denylist must beat allowlist — security-critical."""
        policy = MCPPolicyConfig(
            allowed_servers=[PolicyEntry.from_name("evil-server")],
            denied_servers=[PolicyEntry.from_name("evil-server")],
        )
        result = is_mcp_server_allowed_by_policy("evil-server", MCPServerInfo(name="evil-server"), policy)
        assert not result.allowed
        assert "denylist" in result.reason.lower()

    def test_no_allowlist_allows_all(self):
        policy = MCPPolicyConfig(allowed_servers=None)
        result = is_mcp_server_allowed_by_policy("any-server", MCPServerInfo(name="any-server"), policy)
        assert result.allowed

    def test_empty_allowlist_blocks_all(self):
        policy = MCPPolicyConfig(allowed_servers=[])
        result = is_mcp_server_allowed_by_policy("any-server", MCPServerInfo(name="any-server"), policy)
        assert not result.allowed

    def test_allowlist_name_match(self):
        policy = MCPPolicyConfig(allowed_servers=[PolicyEntry.from_name("my-server")])
        result = is_mcp_server_allowed_by_policy("my-server", MCPServerInfo(name="my-server"), policy)
        assert result.allowed

    def test_allowlist_no_match(self):
        policy = MCPPolicyConfig(allowed_servers=[PolicyEntry.from_name("my-server")])
        result = is_mcp_server_allowed_by_policy("other-server", MCPServerInfo(name="other-server"), policy)
        assert not result.allowed

    def test_allowlist_command_match(self):
        policy = MCPPolicyConfig(allowed_servers=[PolicyEntry.from_command(["npx", "firebase-tools"])])
        info = MCPServerInfo(name="firebase", command=["npx", "firebase-tools"])
        result = is_mcp_server_allowed_by_policy("firebase", info, policy)
        assert result.allowed

    def test_allowlist_command_no_match(self):
        policy = MCPPolicyConfig(allowed_servers=[PolicyEntry.from_command(["npx", "firebase-tools"])])
        info = MCPServerInfo(name="firebase", command=["npx", "other-tool"])
        result = is_mcp_server_allowed_by_policy("firebase", info, policy)
        assert not result.allowed

    def test_allowlist_url_match(self):
        policy = MCPPolicyConfig(allowed_servers=[PolicyEntry.from_url("https://mcp.example.com/*")])
        info = MCPServerInfo(name="remote", url="https://mcp.example.com/v1")
        result = is_mcp_server_allowed_by_policy("remote", info, policy)
        assert result.allowed

    def test_allowlist_url_no_match(self):
        policy = MCPPolicyConfig(allowed_servers=[PolicyEntry.from_url("https://mcp.example.com/*")])
        info = MCPServerInfo(name="remote", url="https://other.example.com/v1")
        result = is_mcp_server_allowed_by_policy("remote", info, policy)
        assert not result.allowed


class TestDefaultAgntPolicy:
    """Tests for get_default_agnt_policy."""

    def test_fleet_servers_allowed(self):
        policy = get_default_agnt_policy()
        fleet = [
            "StitchMCP",
            "chrome-devtools-mcp",
            "firebase-mcp-server",
            "google-developer-knowledge",
            "sequential-thinking",
        ]
        for name in fleet:
            info = MCPServerInfo(name=name)
            result = is_mcp_server_allowed_by_policy(name, info, policy)
            assert result.allowed, f"Fleet server '{name}' should be allowed"

    def test_reserved_names_blocked(self):
        policy = get_default_agnt_policy()
        for name in ["claude-in-chrome", "computer-use"]:
            info = MCPServerInfo(name=name)
            result = is_mcp_server_allowed_by_policy(name, info, policy)
            assert not result.allowed, f"Reserved '{name}' should be blocked"

    def test_unknown_server_blocked(self):
        policy = get_default_agnt_policy()
        info = MCPServerInfo(name="unknown-server")
        result = is_mcp_server_allowed_by_policy("unknown-server", info, policy)
        assert not result.allowed


class TestFilterServersByPolicy:
    """Tests for filter_servers_by_policy."""

    def test_mixed_servers(self):
        servers = {
            "firebase-mcp-server": MCPServerInfo(name="firebase-mcp-server"),
            "evil-server": MCPServerInfo(name="evil-server"),
        }
        policy = MCPPolicyConfig(
            allowed_servers=[PolicyEntry.from_name("firebase-mcp-server")],
            denied_servers=[PolicyEntry.from_name("evil-server")],
        )
        allowed, blocked = filter_servers_by_policy(servers, policy)
        assert "firebase-mcp-server" in allowed
        assert "evil-server" in blocked

    def test_empty_servers(self):
        allowed, blocked = filter_servers_by_policy({}, MCPPolicyConfig())
        assert allowed == {}
        assert blocked == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# § ClassifiedGateway Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestClassifiedGateway:
    """Tests for ClassifiedGateway pipeline."""

    @pytest.fixture()
    def gateway(self) -> ClassifiedGateway:
        return ClassifiedGateway()

    def test_allowlisted_tool_fast_path(self, gateway: ClassifiedGateway):
        """Allowlisted tools should skip classifier and policy."""
        result = gateway.evaluate("view_file")
        assert result.allowed
        assert result.action == GatewayAction.ALLOW_ALLOWLIST
        assert result.stage == 0

    def test_safe_command_allowed(self, gateway: ClassifiedGateway):
        """Known safe commands (echo) should pass two-stage classifier."""
        result = gateway.evaluate(
            "run_command",
            {"CommandLine": "echo hello"},
        )
        assert result.allowed
        assert result.action == GatewayAction.ALLOW_CLASSIFIER

    def test_dangerous_command_blocked(self, gateway: ClassifiedGateway):
        """Destructive commands must be blocked."""
        result = gateway.evaluate(
            "run_command",
            {"CommandLine": "rm -rf /"},
        )
        assert not result.allowed
        assert result.action == GatewayAction.BLOCK_CLASSIFIER

    def test_mcp_policy_blocks_denied_server(self, gateway: ClassifiedGateway):
        """MCP tools from denied servers must be blocked by policy."""
        result = gateway.evaluate(
            "mcp_tool_x",
            {},
            mcp_server_name="claude-in-chrome",
        )
        assert not result.allowed
        assert result.action == GatewayAction.BLOCK_POLICY

    def test_mcp_policy_allows_fleet_server(self, gateway: ClassifiedGateway):
        """MCP tools from fleet servers should pass policy check."""
        result = gateway.evaluate(
            "mcp_firebase-mcp-server_firebase_get_environment",
            {},
            mcp_server_name="firebase-mcp-server",
        )
        assert result.allowed

    def test_mcp_policy_blocks_unknown_server(self, gateway: ClassifiedGateway):
        """Unknown MCP servers should be blocked when allowlist is configured."""
        result = gateway.evaluate(
            "mcp_unknown_tool",
            {},
            mcp_server_name="unknown-server",
        )
        assert not result.allowed
        assert result.action == GatewayAction.BLOCK_POLICY

    def test_fail_closed_on_exception(self):
        """Any exception must result in BLOCK (fail-closed P5.1)."""

        class BrokenClassifier(AGNTClassifier):
            def classify(self, **kwargs):
                raise RuntimeError("Classifier crashed")

        gateway = ClassifiedGateway(classifier=BrokenClassifier())
        result = gateway.evaluate(
            "run_command",
            {"CommandLine": "echo test"},
        )
        assert not result.allowed
        assert result.action == GatewayAction.BLOCK_FAIL_CLOSED

    def test_duration_recorded(self, gateway: ClassifiedGateway):
        """All results should include positive duration_ms."""
        result = gateway.evaluate("view_file")
        assert result.duration_ms > 0

    def test_callback_invoked(self):
        """on_evaluation callback should fire for every evaluation."""
        results = []
        gateway = ClassifiedGateway(on_evaluation=results.append)
        gateway.evaluate("view_file")
        gateway.evaluate("list_dir")
        assert len(results) == 2

    def test_result_structure(self, gateway: ClassifiedGateway):
        """GatewayResult should have all required fields."""
        result = gateway.evaluate("view_file")
        assert isinstance(result, GatewayResult)
        assert isinstance(result.allowed, bool)
        assert isinstance(result.action, GatewayAction)
        assert isinstance(result.tool_id, str)
        assert result.tool_id == "view_file"


class TestGatewayTelemetry:
    """Tests for GatewayTelemetry accumulation."""

    def test_initial_state(self):
        t = GatewayTelemetry()
        assert t.total_evaluations == 0
        assert t.total_allowed == 0
        assert t.total_blocked == 0

    def test_record_allowed(self):
        t = GatewayTelemetry()
        t.record(
            GatewayResult(
                allowed=True,
                action=GatewayAction.ALLOW_ALLOWLIST,
                tool_id="view_file",
                duration_ms=1.0,
            )
        )
        assert t.total_evaluations == 1
        assert t.total_allowed == 1
        assert t.allowlist_hits == 1

    def test_record_blocked(self):
        t = GatewayTelemetry()
        t.record(
            GatewayResult(
                allowed=False,
                action=GatewayAction.BLOCK_CLASSIFIER,
                tool_id="run_command",
                duration_ms=5.0,
            )
        )
        assert t.total_blocked == 1
        assert t.classifier_blocks == 1

    def test_avg_latency(self):
        t = GatewayTelemetry()
        t.record(
            GatewayResult(
                allowed=True,
                action=GatewayAction.ALLOW_ALLOWLIST,
                tool_id="t1",
                duration_ms=2.0,
            )
        )
        t.record(
            GatewayResult(
                allowed=True,
                action=GatewayAction.ALLOW_CLASSIFIER,
                tool_id="t2",
                duration_ms=4.0,
            )
        )
        assert t.avg_latency_ms == pytest.approx(3.0)

    def test_to_dict_keys(self):
        t = GatewayTelemetry()
        d = t.to_dict()
        expected_keys = {
            "total_evaluations",
            "total_allowed",
            "total_blocked",
            "total_fail_closed",
            "allowlist_hits",
            "classifier_allows",
            "classifier_blocks",
            "policy_blocks",
            "avg_latency_ms",
        }
        assert set(d.keys()) == expected_keys


class TestGatewaySummary:
    """Tests for gateway.get_summary()."""

    def test_summary_structure(self):
        gw = ClassifiedGateway()
        gw.evaluate("view_file")
        summary = gw.get_summary()
        assert "policy" in summary
        assert "telemetry" in summary
        assert summary["policy"]["has_allowlist"] is True
        assert summary["telemetry"]["total_evaluations"] == 1


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# § Allowlist Edge Cases
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestAllowlistEdgeCases:
    """Edge cases for allowlist integration."""

    def test_no_overlap_between_safe_and_classifier_required(self):
        """SAFE_ALLOWLIST and CLASSIFIER_REQUIRED must be disjoint."""
        overlap = SAFE_ALLOWLIST & CLASSIFIER_REQUIRED
        assert overlap == set(), f"Overlap detected: {overlap}"

    def test_dangerous_tools_not_in_allowlist(self):
        dangerous = {"run_command", "write_to_file", "send_command_input"}
        leaked = dangerous & SAFE_ALLOWLIST
        assert leaked == set(), f"Dangerous tools in allowlist: {leaked}"

    def test_requires_classifier_for_write(self):
        assert requires_classifier("write_to_file")

    def test_requires_classifier_for_run_command(self):
        assert requires_classifier("run_command")

    def test_not_requires_classifier_for_view(self):
        assert not requires_classifier("view_file")

    def test_unknown_tool_requires_classifier(self):
        assert requires_classifier("totally_unknown_tool_xyz")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# § Diagnostics Tests
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestClassifierDiagnostics:
    """Tests for ClassifierDiagnostics health check suite."""

    def test_run_all_returns_checks(self):
        diag = ClassifierDiagnostics()
        checks = diag.run_all()
        assert len(checks) == 6
        assert all(isinstance(c, DiagnosticCheck) for c in checks)

    def test_all_checks_have_names(self):
        diag = ClassifierDiagnostics()
        checks = diag.run_all()
        names = {c.name for c in checks}
        expected = {
            "classifier_import",
            "classifier_function",
            "allowlist_sanity",
            "policy_config",
            "gateway_pipeline",
            "telemetry_catalog",
        }
        assert names == expected

    def test_all_checks_pass(self):
        diag = ClassifierDiagnostics()
        checks = diag.run_all()
        for check in checks:
            assert check.status in {
                DiagnosticStatus.PASS,
                DiagnosticStatus.WARN,
            }, f"Check '{check.name}' failed: {check.message}"

    def test_check_duration_positive(self):
        diag = ClassifierDiagnostics()
        checks = diag.run_all()
        for check in checks:
            assert check.duration_ms >= 0, f"Negative duration on '{check.name}'"


class TestRunClassifierDiagnostics:
    """Tests for the convenience function."""

    def test_structured_report(self):
        report = run_classifier_diagnostics()
        assert "overall" in report
        assert "passed" in report
        assert "warned" in report
        assert "failed" in report
        assert "total" in report
        assert "checks" in report
        assert report["total"] == 6

    def test_no_failures(self):
        report = run_classifier_diagnostics()
        assert report["failed"] == 0, "Diagnostics failed: " + ", ".join(c["message"] for c in report["checks"] if c["status"] == "fail")
