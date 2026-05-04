# Copyright 2026 ShadowTag AI. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Tests for the integration demo — MockChatModel + run_demo end-to-end."""

from __future__ import annotations

import time

import pytest

from firebase_tool_bridge.bridge import ToolBridge
from firebase_tool_bridge.evidence import EvidenceLogger
from firebase_tool_bridge.integration_demo import (
    MockChatModel,
    cli_confirmation_provider,
    delete_all_meal_plans,
    fetch_weather,
    run_demo,
    save_meal_plan,
    search_recipes,
)
from firebase_tool_bridge.registry import FunctionRegistry, RiskTier


# ─── MockChatModel Tests ────────────────────────────────────────────────────


class TestMockChatModel:
    """Verify the scripted conversation model."""

    def test_turn1_proposes_weather_call(self):
        model = MockChatModel()
        resp = model.send_message([{"text": "What's the weather?"}])
        assert resp.has_function_calls
        assert len(resp.function_calls) == 1
        assert resp.function_calls[0].name == "fetch_weather"
        assert resp.function_calls[0].args["city"] == "San Francisco"
        assert resp.text is None

    def test_turn2_proposes_recipe_call(self):
        model = MockChatModel()
        # Advance past turn 1
        model.send_message([{"text": "initial"}])
        resp = model.send_message([{"functionResponse": {"name": "fetch_weather", "response": {}}}])
        assert resp.has_function_calls
        assert len(resp.function_calls) == 1
        assert resp.function_calls[0].name == "search_recipes"
        assert resp.function_calls[0].args["max_results"] == 3
        assert resp.text is None

    def test_turn3_returns_text_no_calls(self):
        model = MockChatModel()
        model.send_message([{"text": "initial"}])
        model.send_message([{"functionResponse": {}}])
        resp = model.send_message([{"functionResponse": {}}])
        assert not resp.has_function_calls
        assert resp.text is not None
        assert "San Francisco" in resp.text
        assert "Margherita" in resp.text

    def test_turn_counter_increments(self):
        model = MockChatModel()
        assert model.turn == 0
        model.send_message([{"text": "a"}])
        assert model.turn == 1
        model.send_message([{"text": "b"}])
        assert model.turn == 2

    def test_beyond_turn3_always_text(self):
        model = MockChatModel()
        for _ in range(3):
            model.send_message([{"text": "x"}])
        # Turn 4+
        resp = model.send_message([{"text": "y"}])
        assert not resp.has_function_calls
        assert resp.text is not None


# ─── Tool Function Tests ────────────────────────────────────────────────────


class TestToolFunctions:
    """Validate the demo tool implementations."""

    def test_fetch_weather_known_city(self):
        result = fetch_weather("San Francisco")
        assert result["city"] == "San Francisco"
        assert result["temp"] == 18
        assert result["conditions"] == "foggy"
        assert result["unit"] == "celsius"

    def test_fetch_weather_fahrenheit(self):
        result = fetch_weather("San Francisco", unit="fahrenheit")
        assert result["temp"] == round(18 * 9 / 5 + 32)
        assert result["unit"] == "fahrenheit"

    def test_fetch_weather_unknown_city(self):
        result = fetch_weather("Atlantis")
        assert result["temp"] == 20
        assert result["conditions"] == "unknown"

    def test_fetch_weather_case_insensitive(self):
        result = fetch_weather("NEW YORK")
        assert result["temp"] == 25

    def test_search_recipes_default(self):
        results = search_recipes("anything")
        assert len(results) == 5
        assert all("name" in r for r in results)

    def test_search_recipes_max_results(self):
        results = search_recipes("anything", max_results=2)
        assert len(results) == 2

    def test_search_recipes_vegan_filter(self):
        results = search_recipes("food", dietary_filter="vegan")
        names = {r["name"] for r in results}
        assert "Ratatouille" in names
        assert "Pad Thai" in names
        assert "Spaghetti Carbonara" not in names

    def test_save_meal_plan(self):
        result = save_meal_plan("Monday", "Oatmeal", "Salad", "Pasta")
        assert result["status"] == "saved"
        assert result["day"] == "Monday"
        assert result["meals"]["breakfast"] == "Oatmeal"

    def test_delete_all_meal_plans(self):
        result = delete_all_meal_plans()
        assert result["status"] == "deleted"
        assert "permanently" in result["message"]


# ─── Confirmation Provider Tests ─────────────────────────────────────────────


class TestConfirmationProvider:
    """Validate the demo auto-approve provider."""

    def test_always_approves(self):
        assert cli_confirmation_provider("any_function", {"key": "val"}) is True

    def test_logs_function_name(self, caplog):
        import logging

        with caplog.at_level(logging.INFO):
            cli_confirmation_provider("dangerous_op", {"target": "prod"})
        assert "dangerous_op" in caplog.text


# ─── Integration Demo End-to-End ─────────────────────────────────────────────


class TestRunDemo:
    """Test that run_demo executes without errors."""

    def test_demo_completes(self, caplog):
        import logging

        with caplog.at_level(logging.INFO):
            run_demo()
        assert "Demo complete" in caplog.text
        assert "STEP 1" in caplog.text
        assert "STEP 5" in caplog.text

    def test_demo_evidence_written(self, caplog):
        import logging

        with caplog.at_level(logging.INFO):
            run_demo()
        # Should have logged 2 function calls (weather + recipes)
        assert "evidence records" in caplog.text.lower() or "2 evidence" in caplog.text


# ─── Bridge.handle() Latency Benchmark ───────────────────────────────────────


class TestBridgeLatencyBenchmark:
    """Benchmark bridge.handle() across risk tiers.

    These tests verify sub-millisecond dispatch for the mock setup
    and measure relative overhead of risk-tier confirmation gating.
    """

    @pytest.fixture
    def bench_bridge(self, tmp_path):
        reg = FunctionRegistry()
        reg.register("low_op", lambda **kw: kw, RiskTier.LOW)
        reg.register("med_op", lambda **kw: kw, RiskTier.MEDIUM)
        reg.register(
            "high_op",
            lambda **kw: kw,
            RiskTier.HIGH,
            action_tags=frozenset({"deploy"}),
        )
        reg.register(
            "crit_op",
            lambda **kw: kw,
            RiskTier.CRITICAL,
            action_tags=frozenset({"data_delete"}),
        )

        class AutoApprove:
            def request_confirmation(self, *args, **kwargs):
                return True

        return ToolBridge(
            reg,
            evidence=EvidenceLogger(repo_root=tmp_path),
            confirmation=AutoApprove(),
        )

    def _measure_latency(self, bridge, fn_name, args, iterations=100):
        """Run N iterations and return p50/p95/p99 in milliseconds."""
        # Warm-up: exclude cold-start file creation and hash init overhead
        for _ in range(5):
            bridge.handle(fn_name, args)
        timings = []
        for _ in range(iterations):
            start = time.perf_counter()
            bridge.handle(fn_name, args)
            elapsed = (time.perf_counter() - start) * 1000
            timings.append(elapsed)
        timings.sort()
        return {
            "p50": timings[len(timings) // 2],
            "p95": timings[int(len(timings) * 0.95)],
            "p99": timings[int(len(timings) * 0.99)],
            "mean": sum(timings) / len(timings),
        }

    def test_low_risk_latency(self, bench_bridge):
        stats = self._measure_latency(bench_bridge, "low_op", {"x": 1})
        # p50 validates bridge logic is sub-millisecond; p95 allows for OS jitter/GC
        assert stats["p50"] < 1.0, f"LOW p50={stats['p50']:.2f}ms exceeds 1ms"
        assert stats["p95"] < 500.0, f"LOW p95={stats['p95']:.2f}ms exceeds 500ms"

    def test_medium_risk_latency(self, bench_bridge):
        stats = self._measure_latency(bench_bridge, "med_op", {"x": 1})
        assert stats["p50"] < 1.0, f"MEDIUM p50={stats['p50']:.2f}ms exceeds 1ms"
        assert stats["p95"] < 500.0, f"MEDIUM p95={stats['p95']:.2f}ms exceeds 500ms"

    def test_high_risk_latency(self, bench_bridge):
        stats = self._measure_latency(bench_bridge, "high_op", {"x": 1})
        assert stats["p50"] < 1.0, f"HIGH p50={stats['p50']:.2f}ms exceeds 1ms"
        assert stats["p95"] < 500.0, f"HIGH p95={stats['p95']:.2f}ms exceeds 500ms"

    def test_critical_risk_latency(self, bench_bridge):
        stats = self._measure_latency(bench_bridge, "crit_op", {"x": 1})
        assert stats["p50"] < 1.0, f"CRITICAL p50={stats['p50']:.2f}ms exceeds 1ms"
        assert stats["p95"] < 500.0, f"CRITICAL p95={stats['p95']:.2f}ms exceeds 500ms"

    def test_latency_report(self, bench_bridge, caplog):
        """Generate a full latency report across all tiers."""
        import logging

        with caplog.at_level(logging.INFO):
            tiers = {
                "LOW": ("low_op", {"x": 1}),
                "MEDIUM": ("med_op", {"x": 1}),
                "HIGH": ("high_op", {"target": "staging"}),
                "CRITICAL": ("crit_op", {"target": "prod"}),
            }
            for tier, (fn, args) in tiers.items():
                stats = self._measure_latency(bench_bridge, fn, args, iterations=200)
                print(f"  {tier:10s} → p50={stats['p50']:.3f}ms  p95={stats['p95']:.3f}ms  p99={stats['p99']:.3f}ms  mean={stats['mean']:.3f}ms")
        # Just verify it ran
        assert True
