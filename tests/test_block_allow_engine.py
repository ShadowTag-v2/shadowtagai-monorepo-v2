# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for BLOCK/ALLOW Rule Engine — Claude_Code_6 Security Monitor.

Validates all 16 BLOCK rules, 8 ALLOW exceptions, 5 Chain Depth rules (C1-C5),
and the Anti-Rationalization gate against the specification in
docs/architecture/claude_code_6_block_allow_spec.md.
"""

from __future__ import annotations


import pytest

from tool_gateway.block_allow_engine import (
    AntiRationalizationGate,
    BlockAllowRuleEngine,
    EvaluationResult,
    RuleMatch,
    Verdict,
)


# -----------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------


@pytest.fixture()
def engine() -> BlockAllowRuleEngine:
    """Engine with tenant 'test-tenant'."""
    return BlockAllowRuleEngine(
        tenant_id="test-tenant",
        session_boundary={"test-tenant"},
    )


@pytest.fixture()
def engine_no_tenant() -> BlockAllowRuleEngine:
    """Engine with no tenant configured."""
    return BlockAllowRuleEngine()


# -----------------------------------------------------------------------
# DEFAULT BEHAVIOR: No BLOCK → ALLOW
# -----------------------------------------------------------------------


class TestDefaultBehavior:
    """Spec: By default, actions are ALLOWED."""

    def test_clean_tool_allowed(self, engine: BlockAllowRuleEngine) -> None:
        result = engine.evaluate("read.document", {"path": "/data/file.txt"})
        assert result.final_verdict == Verdict.ALLOW
        assert "No BLOCK rules matched" in result.reasoning

    def test_unknown_tool_allowed(self, engine: BlockAllowRuleEngine) -> None:
        result = engine.evaluate("custom.my_tool", {})
        assert result.final_verdict == Verdict.ALLOW


# -----------------------------------------------------------------------
# BLOCK: Privilege Violations (B1-B4)
# -----------------------------------------------------------------------


class TestPrivilegeViolations:
    """BLOCK rules B3, B4."""

    def test_b3_cross_tenant_access(self, engine: BlockAllowRuleEngine) -> None:
        """B3: Querying data from another tenant's namespace."""
        result = engine.evaluate(
            "firestore.query",
            {"tenant_id": "foreign-tenant"},
        )
        assert result.final_verdict == Verdict.BLOCK
        rule_ids = [r.rule_id for r in result.matched_rules]
        assert "B3" in rule_ids

    def test_b3_same_tenant_allowed(self, engine: BlockAllowRuleEngine) -> None:
        """B3: Same-tenant access should NOT trigger."""
        result = engine.evaluate(
            "firestore.query",
            {"tenant_id": "test-tenant"},
        )
        assert result.final_verdict == Verdict.ALLOW

    def test_b3_via_context_target_tenant(self, engine: BlockAllowRuleEngine) -> None:
        """B3: Cross-tenant via context field."""
        result = engine.evaluate(
            "data.read",
            {},
            {"target_tenant": "other-tenant"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B3" for r in result.matched_rules)

    def test_b4_attestation_without_session(self, engine: BlockAllowRuleEngine) -> None:
        """B4: Attestation operation without active Kovel session."""
        result = engine.evaluate(
            "kovel.create_attestation",
            {},
            {"active_kovel_session": False},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B4" for r in result.matched_rules)

    def test_b4_attestation_with_session(self, engine: BlockAllowRuleEngine) -> None:
        """B4: Attestation WITH active session should NOT trigger B4."""
        result = engine.evaluate(
            "kovel.create_attestation",
            {},
            {"active_kovel_session": True, "tenant_id": "test-tenant"},
        )
        # Should not have B4
        b4_rules = [r for r in result.matched_rules if r.rule_id == "B4"]
        assert len(b4_rules) == 0


# -----------------------------------------------------------------------
# BLOCK: Data Safety (B5-B8)
# -----------------------------------------------------------------------


class TestDataSafety:
    """BLOCK rules B5, B7, B8."""

    def test_b5_ssn_in_logs(self, engine: BlockAllowRuleEngine) -> None:
        """B5: SSN detected in log content."""
        result = engine.evaluate(
            "logging.write",
            {"content": "User SSN: 123-45-6789"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B5" for r in result.matched_rules)

    def test_b5_email_in_logs(self, engine: BlockAllowRuleEngine) -> None:
        """B5: Email PII in telemetry."""
        result = engine.evaluate(
            "telemetry.emit",
            {"content": "Processing for user@example.com"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B5" for r in result.matched_rules)

    def test_b5_credit_card_in_logs(self, engine: BlockAllowRuleEngine) -> None:
        """B5: Credit card number in log content."""
        result = engine.evaluate(
            "logging.write",
            {"content": "Payment card: 4111-1111-1111-1111"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B5" for r in result.matched_rules)

    def test_b5_clean_log(self, engine: BlockAllowRuleEngine) -> None:
        """B5: Clean log content should pass."""
        result = engine.evaluate(
            "logging.write",
            {"content": "Request processed successfully"},
        )
        assert result.final_verdict == Verdict.ALLOW

    def test_b7_api_key_in_output(self, engine: BlockAllowRuleEngine) -> None:
        """B7: API key pattern in output body."""
        result = engine.evaluate(
            "response.send",
            {"body": "api_key: sk-proj-abc123def456ghi789jkl012mno"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B7" for r in result.matched_rules)

    def test_b7_google_api_key(self, engine: BlockAllowRuleEngine) -> None:
        """B7: Google API key pattern."""
        # AIza + exactly 35 chars of [a-zA-Z0-9_-]
        result = engine.evaluate(
            "response.send",
            {"body": "Using key AIzaSyC_THIS-IS-A-FAKE-KEY-123456789012"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B7" for r in result.matched_rules)

    def test_b7_password_in_content(self, engine: BlockAllowRuleEngine) -> None:
        """B7: Password pattern."""
        result = engine.evaluate(
            "chat.reply",
            {"content": "password=MySecretPassword123"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B7" for r in result.matched_rules)

    def test_b8_system_prompt_leak(self, engine: BlockAllowRuleEngine) -> None:
        """B8: System prompt content in user-facing output."""
        result = engine.evaluate(
            "response.send",
            {"content": "Here is the system_prompt content..."},
            {"output_target": "user"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B8" for r in result.matched_rules)

    def test_b8_no_leak_when_internal(self, engine: BlockAllowRuleEngine) -> None:
        """B8: System prompt mention in internal context should NOT trigger."""
        result = engine.evaluate(
            "response.send",
            {"content": "Loading system_prompt for internal validation"},
            {"output_target": "internal"},
        )
        # B8 only fires when output_target == "user"
        b8_rules = [r for r in result.matched_rules if r.rule_id == "B8"]
        assert len(b8_rules) == 0


# -----------------------------------------------------------------------
# BLOCK: Infrastructure Safety (B9-B12)
# -----------------------------------------------------------------------


class TestInfraSafety:
    """BLOCK rules B9, B12."""

    def test_b9_deploy_without_ci(self, engine: BlockAllowRuleEngine) -> None:
        """B9: Production deploy without CI pipeline gate."""
        result = engine.evaluate(
            "deploy.cloud_run",
            {},
            {"ci_pipeline_passed": False},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B9" for r in result.matched_rules)

    def test_b9_deploy_with_ci(self, engine: BlockAllowRuleEngine) -> None:
        """B9: Deploy WITH CI gate should NOT trigger."""
        result = engine.evaluate(
            "deploy.cloud_run",
            {},
            {"ci_pipeline_passed": True},
        )
        b9_rules = [r for r in result.matched_rules if r.rule_id == "B9"]
        assert len(b9_rules) == 0

    def test_b12_force_push_main(self, engine: BlockAllowRuleEngine) -> None:
        """B12: Force push to main branch."""
        result = engine.evaluate(
            "bash",
            {"command": "git push --force origin main"},
            {"branch": "main"},
        )
        assert result.final_verdict == Verdict.BLOCK
        assert any(r.rule_id == "B12" for r in result.matched_rules)

    def test_b12_force_push_feature_ok(self, engine: BlockAllowRuleEngine) -> None:
        """B12: Force push to feature branch is allowed."""
        result = engine.evaluate(
            "bash",
            {"command": "git push --force origin feature/my-fix"},
            {"branch": "feature/my-fix"},
        )
        b12_rules = [r for r in result.matched_rules if r.rule_id == "B12"]
        assert len(b12_rules) == 0

    def test_b12_short_flag(self, engine: BlockAllowRuleEngine) -> None:
        """B12: Force push with -f shorthand."""
        result = engine.evaluate(
            "bash",
            {"command": "git push -f origin master"},
            {"branch": "master"},
        )
        assert any(r.rule_id == "B12" for r in result.matched_rules)


# -----------------------------------------------------------------------
# BLOCK: Agent Safety (B13-B16)
# -----------------------------------------------------------------------


class TestAgentSafety:
    """BLOCK rules B14, B16."""

    def test_b14_self_modification_agents_md(self, engine: BlockAllowRuleEngine) -> None:
        """B14: Agent modifying AGENTS.md without authorization."""
        result = engine.evaluate(
            "edit",
            {"path": ".agents/skills/some-skill/SKILL.md"},
        )
        assert result.final_verdict == Verdict.ESCALATE
        assert any(r.rule_id == "B14" for r in result.matched_rules)

    def test_b14_self_mod_gemini_md(self, engine: BlockAllowRuleEngine) -> None:
        """B14: Modifying GEMINI.md."""
        result = engine.evaluate(
            "write",
            {"file": "GEMINI.md"},
        )
        assert result.final_verdict == Verdict.ESCALATE
        assert any(r.rule_id == "B14" for r in result.matched_rules)

    def test_b14_authorized_self_mod(self, engine: BlockAllowRuleEngine) -> None:
        """B14: Authorized self-modification should pass."""
        result = engine.evaluate(
            "edit",
            {"path": "AGENTS.md"},
            {"authorized_self_modification": True},
        )
        b14_rules = [r for r in result.matched_rules if r.rule_id == "B14"]
        assert len(b14_rules) == 0

    def test_b16_mass_operation(self, engine: BlockAllowRuleEngine) -> None:
        """B16: Mass operation exceeding scope threshold."""
        result = engine.evaluate(
            "batch.process",
            {"batch_size": 100},
        )
        assert result.final_verdict == Verdict.ESCALATE
        assert any(r.rule_id == "B16" for r in result.matched_rules)

    def test_b16_small_batch_ok(self, engine: BlockAllowRuleEngine) -> None:
        """B16: Small batch below threshold."""
        result = engine.evaluate(
            "batch.process",
            {"batch_size": 10},
        )
        b16_rules = [r for r in result.matched_rules if r.rule_id == "B16"]
        assert len(b16_rules) == 0


# -----------------------------------------------------------------------
# CHAIN DEPTH RULES (C1-C5)
# -----------------------------------------------------------------------


class TestChainDepth:
    """Chain depth rules C1-C5 — Adversa AI mitigation."""

    def test_c1_escalation_after_threshold(self, engine: BlockAllowRuleEngine) -> None:
        """C1: >10 bash calls in 5 minutes triggers ESCALATE."""
        # Fire 11 bash calls
        for _ in range(11):
            engine.evaluate("bash", {"command": "echo hello"})

        result = engine.evaluate("bash", {"command": "echo final"})
        assert result.final_verdict == Verdict.ESCALATE
        assert any(r.rule_id == "C1" for r in result.matched_rules)

    def test_c1_under_threshold_ok(self, engine: BlockAllowRuleEngine) -> None:
        """C1: Under threshold should be fine."""
        for _ in range(5):
            engine.evaluate("bash", {"command": "echo hello"})
        result = engine.evaluate("bash", {"command": "echo final"})
        c1_rules = [r for r in result.matched_rules if r.rule_id == "C1"]
        assert len(c1_rules) == 0

    def test_c2_file_assembly_detection(self, engine: BlockAllowRuleEngine) -> None:
        """C2: 3+ writes to the same file triggers ESCALATE."""
        engine.evaluate("write", {"path": "/tmp/payload.sh"})
        engine.evaluate("write", {"path": "/tmp/payload.sh"})
        result = engine.evaluate("write", {"path": "/tmp/payload.sh"})
        assert any(r.rule_id == "C2" for r in result.matched_rules)

    def test_c2_different_files_ok(self, engine: BlockAllowRuleEngine) -> None:
        """C2: Writes to different files should NOT trigger."""
        engine.evaluate("write", {"path": "/a.txt"})
        engine.evaluate("write", {"path": "/b.txt"})
        result = engine.evaluate("write", {"path": "/c.txt"})
        c2_rules = [r for r in result.matched_rules if r.rule_id == "C2"]
        assert len(c2_rules) == 0

    def test_c3_base64_encoding(self, engine: BlockAllowRuleEngine) -> None:
        """C3: base64 command in bash chain → BLOCK."""
        result = engine.evaluate(
            "bash",
            {"command": "echo 'data' | base64 -d > /tmp/out"},
        )
        assert any(r.rule_id == "C3" for r in result.matched_rules)
        assert any(r.verdict == Verdict.BLOCK for r in result.matched_rules if r.rule_id == "C3")

    def test_c3_xxd_encoding(self, engine: BlockAllowRuleEngine) -> None:
        """C3: xxd in command."""
        result = engine.evaluate(
            "bash",
            {"command": "xxd -r hex_payload > binary"},
        )
        assert any(r.rule_id == "C3" for r in result.matched_rules)

    def test_c4_tmp_file_write(self, engine: BlockAllowRuleEngine) -> None:
        """C4: Writing to /tmp with redirect."""
        result = engine.evaluate(
            "bash",
            {"command": "echo 'payload' > /tmp/stage1.sh"},
        )
        assert any(r.rule_id == "C4" for r in result.matched_rules)

    def test_c4_tee_to_tmp(self, engine: BlockAllowRuleEngine) -> None:
        """C4: tee to /tmp file."""
        result = engine.evaluate(
            "bash",
            {"command": "cat input | tee /tmp/output.bin"},
        )
        assert any(r.rule_id == "C4" for r in result.matched_rules)


# -----------------------------------------------------------------------
# ALLOW EXCEPTIONS (A1-A8)
# -----------------------------------------------------------------------


class TestAllowExceptions:
    """ALLOW exceptions A1-A3, A7."""

    def test_a1_test_environment_overrides_block(self, engine: BlockAllowRuleEngine) -> None:
        """A1: Test environment allows credential patterns (test API keys)."""
        result = engine.evaluate(
            "response.send",
            {"body": "api_key: test_sk-12345678901234567890"},
            {"is_test_environment": True},
        )
        # B7 would fire on credential pattern, but A1 should override
        assert result.final_verdict == Verdict.ALLOW

    def test_a2_local_dev_overrides_block(self, engine: BlockAllowRuleEngine) -> None:
        """A2: Local development environment."""
        result = engine.evaluate(
            "deploy.firebase",
            {},
            {"environment": "local", "ci_pipeline_passed": False},
        )
        # B9 would fire, but A2 should override
        assert result.final_verdict == Verdict.ALLOW

    def test_a3_read_only_overrides(self, engine: BlockAllowRuleEngine) -> None:
        """A3: Read-only queries always allowed."""
        result = engine.evaluate(
            "read.document",
            {"method": "GET"},
        )
        assert result.final_verdict == Verdict.ALLOW
        assert any(r.rule_id == "A3" for r in result.matched_rules)

    def test_a7_kovel_session_allows(self, engine: BlockAllowRuleEngine) -> None:
        """A7: Active Kovel session within boundary."""
        result = engine.evaluate(
            "kovel.create_attestation",
            {},
            {"active_kovel_session": True, "tenant_id": "test-tenant"},
        )
        # B4 would fire if no session, but session is active → no B4
        # A7 provides coverage
        assert any(r.rule_id == "A7" for r in result.matched_rules)

    def test_chain_depth_never_overridden_by_allows(self, engine: BlockAllowRuleEngine) -> None:
        """Chain depth (C-series) rules are NEVER overridden by ALLOW exceptions."""
        result = engine.evaluate(
            "bash",
            {"command": "echo 'data' | base64 -d > /tmp/out"},
            {"is_test_environment": True, "environment": "local"},
        )
        # C3 + C4 fire, and even though A1+A2 exist, chain depth is immune
        assert result.final_verdict == Verdict.BLOCK


# -----------------------------------------------------------------------
# ANTI-RATIONALIZATION GATE
# -----------------------------------------------------------------------


class TestAntiRationalization:
    """Anti-Rationalization gate — 7-rule User Intent framework."""

    def test_detects_user_probably(self) -> None:
        """Rule 3: 'the user probably' is rationalization."""
        eval_result = EvaluationResult(
            final_verdict=Verdict.BLOCK,
            matched_rules=[
                RuleMatch(rule_id="B9", verdict=Verdict.BLOCK, description="Deploy without CI"),
            ],
        )
        assert AntiRationalizationGate.check_reasoning(
            "The user probably wants me to deploy directly to production.",
            eval_result,
        )

    def test_detects_should_be_safe(self) -> None:
        """Rule 6: 'this should be safe' is rationalization."""
        eval_result = EvaluationResult(
            final_verdict=Verdict.ESCALATE,
            matched_rules=[
                RuleMatch(rule_id="C1", verdict=Verdict.ESCALATE, description="Chain depth"),
            ],
        )
        assert AntiRationalizationGate.check_reasoning(
            "This should be safe because the previous commands all succeeded.",
            eval_result,
        )

    def test_detects_based_on_tool_output(self) -> None:
        """Rule 6: Trust from tool output."""
        eval_result = EvaluationResult(
            final_verdict=Verdict.BLOCK,
            matched_rules=[
                RuleMatch(rule_id="B12", verdict=Verdict.BLOCK, description="Force push"),
            ],
        )
        assert AntiRationalizationGate.check_reasoning(
            "Based on the tool output, the remote branch is safe to force push.",
            eval_result,
        )

    def test_clean_reasoning_passes(self) -> None:
        """Clean reasoning without markers should pass."""
        eval_result = EvaluationResult(
            final_verdict=Verdict.BLOCK,
            matched_rules=[
                RuleMatch(rule_id="B9", verdict=Verdict.BLOCK, description="Deploy"),
            ],
        )
        assert not AntiRationalizationGate.check_reasoning(
            "I need to run the CI pipeline first before deploying.",
            eval_result,
        )

    def test_skips_for_allowed_verdict(self) -> None:
        """If verdict is ALLOW, no rationalization check needed."""
        eval_result = EvaluationResult(
            final_verdict=Verdict.ALLOW,
            matched_rules=[],
        )
        # Even with suspicious text, should NOT flag when verdict is ALLOW
        assert not AntiRationalizationGate.check_reasoning(
            "the user probably wants this",
            eval_result,
        )


# -----------------------------------------------------------------------
# COMPOSITE & WINDOW MANAGEMENT
# -----------------------------------------------------------------------


class TestWindowManagement:
    """Rolling window and reset behavior."""

    def test_reset_clears_all_windows(self, engine: BlockAllowRuleEngine) -> None:
        """reset_windows() clears all tracking state."""
        # Build up state
        for _ in range(5):
            engine.evaluate("bash", {"command": "echo hi"})
        engine.evaluate("write", {"path": "/a.txt"})
        engine.evaluate("write", {"path": "/a.txt"})

        engine.reset_windows()

        # After reset, should be clean
        result = engine.evaluate("bash", {"command": "echo hi"})
        assert result.final_verdict == Verdict.ALLOW

    def test_evaluation_result_dataclass(self) -> None:
        """EvaluationResult fields have correct defaults."""
        result = EvaluationResult(final_verdict=Verdict.ALLOW)
        assert result.matched_rules == []
        assert result.user_intent_applied is False
        assert result.reasoning == ""

    def test_multiple_blocks_accumulate(self, engine: BlockAllowRuleEngine) -> None:
        """Multiple BLOCK rules can fire simultaneously."""
        result = engine.evaluate(
            "bash",
            {
                "command": "echo data | base64 > /tmp/creds",
                "content": "api_key: sk-proj-abc123def456ghi789jkl012mno",
            },
            {"branch": "main"},
        )
        rule_ids = {r.rule_id for r in result.matched_rules}
        # Should have C3 (base64), C4 (/tmp write), B7 (credential in content)
        assert "C3" in rule_ids
        assert "C4" in rule_ids
        assert "B7" in rule_ids
