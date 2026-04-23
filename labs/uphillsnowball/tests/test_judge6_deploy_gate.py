"""Tests for Judge6DeployGate — Wet Fleece / Dry Ground / Battle."""

from __future__ import annotations

import pytest

from src.governance.j6_csrmc_cato import (
    DeploymentPhase,
    Judge6DeployGate,
    PhaseResult,
)


class TestWetFleece:
    """Phase 1: Static analysis gate."""

    def test_clean_artifact_passes(self):
        """Clean artifact with metadata should pass Wet Fleece."""
        artifact = {
            "type": "CODE_MODIFICATION",
            "source": "Agent-1-Builder",
            "code": "def hello():\n    return 'world'",
        }
        result = Judge6DeployGate.wet_fleece(artifact)
        assert result.passed is True
        assert result.phase == DeploymentPhase.WET_FLEECE
        assert result.directive == "ADVANCE_TO_DRY_GROUND"

    def test_missing_type_fails(self):
        """Missing artifact type should fail."""
        artifact = {"source": "Builder", "code": ""}
        result = Judge6DeployGate.wet_fleece(artifact)
        assert result.passed is False
        assert "Missing artifact type" in result.findings[0]

    def test_eval_banned(self):
        """eval() should be detected and rejected."""
        artifact = {
            "type": "CODE_MODIFICATION",
            "source": "Builder",
            "code": "result = eval(user_input)",
        }
        result = Judge6DeployGate.wet_fleece(artifact)
        assert result.passed is False
        assert any("eval()" in f for f in result.findings)

    def test_exec_banned(self):
        """exec() should be detected and rejected."""
        artifact = {
            "type": "CODE_MODIFICATION",
            "source": "Builder",
            "code": "exec(compiled_code)",
        }
        result = Judge6DeployGate.wet_fleece(artifact)
        assert result.passed is False

    def test_os_system_banned(self):
        """os.system() should be detected and rejected."""
        artifact = {
            "type": "CODE_MODIFICATION",
            "source": "Builder",
            "code": "os.system('rm -rf /')",
        }
        result = Judge6DeployGate.wet_fleece(artifact)
        assert result.passed is False


class TestDryGround:
    """Phase 2: Sandbox test execution gate."""

    def test_all_tests_pass(self):
        """All tests passing should advance to Battle."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder"}
        test_results = {"passed": 42, "failed": 0, "error": 0, "execution_time_ms": 5000}
        result = Judge6DeployGate.dry_ground(artifact, test_results)
        assert result.passed is True
        assert result.directive == "ADVANCE_TO_BATTLE"

    def test_failed_tests_reject(self):
        """Failed tests should reject."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder"}
        test_results = {"passed": 40, "failed": 2, "error": 0, "execution_time_ms": 3000}
        result = Judge6DeployGate.dry_ground(artifact, test_results)
        assert result.passed is False
        assert "2 test(s) failed" in result.findings[0]

    def test_sla_violation_rejects(self):
        """Execution exceeding 40s SLA should reject."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder"}
        test_results = {"passed": 10, "failed": 0, "error": 0, "execution_time_ms": 50_000}
        result = Judge6DeployGate.dry_ground(artifact, test_results)
        assert result.passed is False
        assert "UCMJ SLA" in result.findings[0]

    def test_zero_tests_rejects(self):
        """Zero passing tests should reject."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder"}
        test_results = {"passed": 0, "failed": 0, "error": 0, "execution_time_ms": 100}
        result = Judge6DeployGate.dry_ground(artifact, test_results)
        assert result.passed is False


class TestBattle:
    """Phase 3: Full integration test gate."""

    def test_all_clear_deploys(self):
        """All checks passing should authorize deployment."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder"}
        integration = {
            "health_check": True,
            "smoke_tests_passed": 5,
            "smoke_tests_total": 5,
            "lighthouse_score": 95,
        }
        result = Judge6DeployGate.battle(artifact, integration)
        assert result.passed is True
        assert result.directive == "DEPLOY_TO_PRODUCTION"

    def test_health_check_fail_rejects(self):
        """Failed health check should reject."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder"}
        integration = {"health_check": False}
        result = Judge6DeployGate.battle(artifact, integration)
        assert result.passed is False

    def test_low_lighthouse_rejects(self):
        """Lighthouse score below 80 should reject."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder"}
        integration = {"health_check": True, "lighthouse_score": 55}
        result = Judge6DeployGate.battle(artifact, integration)
        assert result.passed is False


class TestRunGate:
    """Full 3-phase gate sequence."""

    def test_fail_fast_on_wet_fleece(self):
        """Should stop at Wet Fleece if it fails."""
        artifact = {"code": "eval('exploit')"}
        results = Judge6DeployGate.run_gate(artifact)
        assert len(results) == 1
        assert results[0].phase == DeploymentPhase.WET_FLEECE
        assert results[0].passed is False

    def test_full_pipeline_pass(self):
        """Should execute all 3 phases when all pass."""
        artifact = {"type": "CODE_MODIFICATION", "source": "Builder", "code": "pass"}
        test_results = {"passed": 10, "failed": 0, "error": 0, "execution_time_ms": 1000}
        integration = {"health_check": True, "smoke_tests_passed": 3, "smoke_tests_total": 3}
        results = Judge6DeployGate.run_gate(artifact, test_results, integration)
        assert len(results) == 3
        assert all(r.passed for r in results)
        assert results[-1].directive == "DEPLOY_TO_PRODUCTION"
