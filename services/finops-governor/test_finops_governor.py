"""
test_finops_governor.py — Tests for the FinOps Governor

Covers:
  - Budget status classification (GREEN/YELLOW/RED)
  - Service scale-down protection
  - Alert publishing
  - HTTP handler
"""

from __future__ import annotations

import json
from dataclasses import asdict
from unittest.mock import MagicMock, patch

import pytest

import finops_governor as gov


# ─── Budget Evaluation ─────────────────────────────────────────────────────────


class TestBudgetStatus:
    """Tests for budget status classification."""

    def test_green_under_warn(self):
        with patch.object(gov, "query_current_spend", return_value=100.0):
            report = gov.evaluate_budget()
        assert report.status == gov.BudgetStatus.GREEN
        assert report.utilization_pct == 20.0  # 100/500 * 100

    def test_yellow_at_warn(self):
        with patch.object(gov, "query_current_spend", return_value=400.0):
            with patch.object(gov, "publish_alert"):
                report = gov.evaluate_budget()
        assert report.status == gov.BudgetStatus.YELLOW
        assert report.utilization_pct == 80.0

    def test_red_over_halt(self):
        with (
            patch.object(gov, "query_current_spend", return_value=550.0),
            patch.object(gov, "publish_alert"),
            patch.object(gov, "scale_down_services", return_value=["database-events-handler"]),
        ):
            report = gov.evaluate_budget()
        assert report.status == gov.BudgetStatus.RED
        assert report.utilization_pct == 110.0

    def test_green_no_alert(self):
        with patch.object(gov, "query_current_spend", return_value=50.0):
            with patch.object(gov, "publish_alert") as mock_alert:
                gov.evaluate_budget()
        mock_alert.assert_not_called()

    def test_yellow_publishes_alert(self):
        with (
            patch.object(gov, "query_current_spend", return_value=450.0),
            patch.object(gov, "publish_alert") as mock_alert,
        ):
            gov.evaluate_budget()
        mock_alert.assert_called_once()

    def test_red_scales_down(self):
        with (
            patch.object(gov, "query_current_spend", return_value=600.0),
            patch.object(gov, "publish_alert"),
            patch.object(gov, "scale_down_services", return_value=["database-events-handler"]) as mock_scale,
        ):
            report = gov.evaluate_budget()
        mock_scale.assert_called_once_with(gov.SCALABLE_SERVICES)
        assert "database-events-handler" in report.services_scaled_down

    def test_zero_budget_no_division_error(self):
        with patch.object(gov, "BUDGET_MONTHLY_USD", 0):
            with patch.object(gov, "query_current_spend", return_value=0.0):
                report = gov.evaluate_budget()
        assert report.utilization_pct == 0


# ─── Service Protection ───────────────────────────────────────────────────────


class TestServiceProtection:
    """Tests for protected service enforcement."""

    def test_protected_services_never_scaled(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = gov.scale_down_services(["counselconduit", "headfade"])
        assert result == []
        mock_run.assert_not_called()

    def test_scalable_services_can_scale(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = gov.scale_down_services(["database-events-handler"])
        assert "database-events-handler" in result

    def test_mixed_services_only_scales_unprotected(self):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr="")
            result = gov.scale_down_services(
                ["counselconduit", "database-events-handler", "headfade"]
            )
        assert result == ["database-events-handler"]


# ─── Data Models ───────────────────────────────────────────────────────────────


class TestDataModels:
    """Tests for StrEnum and dataclass serialization."""

    def test_budget_status_enum_values(self):
        assert gov.BudgetStatus.GREEN == "GREEN"
        assert gov.BudgetStatus.YELLOW == "YELLOW"
        assert gov.BudgetStatus.RED == "RED"

    def test_cost_report_serialization(self):
        report = gov.CostReport(
            current_spend_usd=100.0,
            budget_usd=500.0,
            utilization_pct=20.0,
            status=gov.BudgetStatus.GREEN,
            timestamp="2026-05-08T00:00:00Z",
            services_scaled_down=[],
            alert_message="test",
        )
        data = asdict(report)
        assert data["status"] == "GREEN"
        serialized = json.dumps(data)
        assert "current_spend_usd" in serialized


# ─── HTTP Handler ──────────────────────────────────────────────────────────────


class TestHTTPHandler:
    """Tests for the handle_finops_check HTTP function."""

    def test_returns_200_with_report(self):
        with patch.object(gov, "query_current_spend", return_value=100.0):
            request = MagicMock()
            response, status = gov.handle_finops_check(request)
        assert status == 200
        body = json.loads(response)
        assert body["status"] == "GREEN"

    def test_returns_500_on_error(self):
        with patch.object(gov, "evaluate_budget", side_effect=RuntimeError("test")):
            request = MagicMock()
            response, status = gov.handle_finops_check(request)
        assert status == 500


# ─── Standalone Mode ──────────────────────────────────────────────────────────


class TestStandaloneMode:
    """Tests for the _run_standalone function."""

    def test_standalone_completes(self, capsys):
        with patch.object(gov, "query_current_spend", return_value=50.0):
            result = gov._run_standalone()
        captured = capsys.readouterr()
        assert "FinOps Governor" in captured.out
        assert "GREEN" in result
