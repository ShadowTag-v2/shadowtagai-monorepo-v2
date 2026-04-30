# Copyright (c) 2026 ShadowTag, Inc. All rights reserved.

"""Tests for evaluation_bridge.bridge module."""

from __future__ import annotations

from pathlib import Path

import pytest

from evaluation_bridge.bridge import (
    EvaluationBridge,
    EvaluationConfig,
    EvaluationResult,
    GateResult,
    GateType,
    GATE_ORDER,
)


class TestGateType:
    def test_order(self) -> None:
        assert GATE_ORDER == [GateType.BUILD, GateType.TEST, GateType.LINT, GateType.MERGE]

    def test_string_enum(self) -> None:
        assert GateType.BUILD == "build"


class TestGateResult:
    def test_defaults(self) -> None:
        g = GateResult(gate=GateType.TEST, passed=True)
        assert g.exit_code == 0
        assert g.duration_ms == 0.0


class TestEvaluationResult:
    def test_to_dict(self) -> None:
        r = EvaluationResult(session_id="dr-test")
        r.gates.append(GateResult(gate=GateType.BUILD, passed=True))
        d = r.to_dict()
        assert d["session_id"] == "dr-test"
        assert len(d["gates"]) == 1


class TestEvaluationConfig:
    def test_defaults(self) -> None:
        cfg = EvaluationConfig()
        assert "pytest" in cfg.test_command
        assert cfg.fail_fast is True
        assert cfg.auto_merge_on_pass is True


class TestEvaluationBridge:
    @pytest.mark.asyncio
    async def test_all_gates_pass(self, tmp_path: Path) -> None:
        config = EvaluationConfig(
            build_command="echo build-ok",
            test_command="echo test-ok",
            lint_command="echo lint-ok",
            auto_merge_on_pass=True,
        )
        bridge = EvaluationBridge(workspace_root=tmp_path, config=config)
        result = await bridge.evaluate(session_id="dr-pass")
        assert result.all_passed is True
        assert len(result.gates) >= 3  # build + test + lint (+ merge)

    @pytest.mark.asyncio
    async def test_fail_fast_on_build(self, tmp_path: Path) -> None:
        config = EvaluationConfig(
            build_command="exit 1",
            test_command="echo should-not-run",
            lint_command="echo should-not-run",
            fail_fast=True,
        )
        bridge = EvaluationBridge(workspace_root=tmp_path, config=config)
        result = await bridge.evaluate(session_id="dr-fail")
        assert result.all_passed is False
        assert len(result.gates) == 1  # only build ran
        assert result.gates[0].gate == GateType.BUILD

    @pytest.mark.asyncio
    async def test_single_gate(self, tmp_path: Path) -> None:
        config = EvaluationConfig()
        bridge = EvaluationBridge(workspace_root=tmp_path, config=config)
        gate = await bridge.run_single_gate(
            session_id="dr-single",
            gate_type=GateType.BUILD,
            command="echo single-ok",
        )
        assert gate.passed is True
        assert gate.gate == GateType.BUILD
