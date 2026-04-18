"""
Tests for the Rich Hickey refactored layers.py subpackage.

Validates that the barrel exports and submodule decomposition
maintain backward compatibility and structural integrity.
"""

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Ensure the pnkln package is importable from its actual location
PNKLN_ROOT = Path(__file__).resolve().parents[2] / "apps" / "aiyou_stack" / "aiyou-fastapi-services" / "apps"


@pytest.fixture(autouse=True)
def patch_sys_path():
    """Add the pnkln apps directory to sys.path for import resolution."""
    path_str = str(PNKLN_ROOT)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
    # Mock numpy since it may not be installed in the test venv
    if "numpy" not in sys.modules:
        sys.modules["numpy"] = MagicMock()
    yield
    if path_str in sys.path:
        sys.path.remove(path_str)


def _clear_pnkln_cache():
    """Flush cached pnkln modules for clean re-import."""
    for key in list(sys.modules.keys()):
        if key.startswith("pnkln"):
            del sys.modules[key]


class TestSubmoduleExistence:
    """Verify all expected submodules exist and are importable."""

    # judge.py depends on src.kosmos.doctrine (not yet built),
    # so it's excluded from structural import tests
    SELF_CONTAINED_MODULES = [
        "pnkln.governance.judge_architecture.models",
        "pnkln.governance.judge_architecture.regulatory",
        "pnkln.governance.judge_architecture.infrastructure",
        "pnkln.governance.judge_architecture.product",
        "pnkln.governance.judge_architecture.analytics",
        "pnkln.governance.judge_architecture.monitor",
        "pnkln.governance.judge_architecture.formatter",
    ]

    @pytest.mark.parametrize("module_name", SELF_CONTAINED_MODULES)
    def test_submodule_importable(self, module_name):
        """Each refactored submodule must be importable."""
        _clear_pnkln_cache()
        mod = importlib.import_module(module_name)
        assert mod is not None


class TestModelIntegrity:
    """Verify the Decision model is structurally sound."""

    def test_decision_instantiation(self):
        """Decision dataclass must be instantiable with its actual fields."""
        _clear_pnkln_cache()
        from pnkln.governance.judge_architecture.models import Decision

        d = Decision(
            id="TEST-001",
            type="procurement",
            description="A test decision for structural validation",
            risk_level="low",
        )
        assert d.id == "TEST-001"
        assert d.type == "procurement"

    def test_decision_has_expected_fields(self):
        """Decision must have its documented fields."""
        _clear_pnkln_cache()
        import dataclasses

        from pnkln.governance.judge_architecture.models import Decision

        field_names = [f.name for f in dataclasses.fields(Decision)]
        assert "id" in field_names
        assert "type" in field_names
        assert "description" in field_names
        assert "risk_level" in field_names


class TestInfrastructureOptimizer:
    """Verify the infrastructure optimizer logic."""

    def test_route_nvidia_for_low_latency(self):
        """Low-latency recsys should route to nvidia_blackwell."""
        _clear_pnkln_cache()
        from pnkln.governance.judge_architecture.infrastructure import (
            InfrastructureOptimizer,
        )

        optimizer = InfrastructureOptimizer()
        slo = MagicMock()
        slo.p95_latency = 100
        result = optimizer.route_workload("recsys_inference", slo)
        assert result == "nvidia_blackwell"

    def test_route_aws_for_batch(self):
        """Batch training should route to aws_trainium2."""
        _clear_pnkln_cache()
        from pnkln.governance.judge_architecture.infrastructure import (
            InfrastructureOptimizer,
        )

        optimizer = InfrastructureOptimizer()
        result = optimizer.route_workload("batch_training", MagicMock())
        assert result == "aws_trainium2"

    def test_route_azure_for_burst(self):
        """Burst capacity should route to azure_maia."""
        _clear_pnkln_cache()
        from pnkln.governance.judge_architecture.infrastructure import (
            InfrastructureOptimizer,
        )

        optimizer = InfrastructureOptimizer()
        result = optimizer.route_workload("burst_capacity", MagicMock())
        assert result == "azure_maia"

    def test_route_default_fallback(self):
        """Unknown workload types should fallback to default."""
        _clear_pnkln_cache()
        from pnkln.governance.judge_architecture.infrastructure import (
            InfrastructureOptimizer,
        )

        optimizer = InfrastructureOptimizer()
        result = optimizer.route_workload("unknown_type", MagicMock())
        assert result == "default_neuron_onnx"

    def test_cost_savings_projection(self):
        """Savings projection must return correct structure and math."""
        _clear_pnkln_cache()
        from pnkln.governance.judge_architecture.infrastructure import (
            InfrastructureOptimizer,
        )

        optimizer = InfrastructureOptimizer()
        result = optimizer.project_savings(100000, {"nvidia": 0.4, "aws": 0.45, "azure": 0.15})
        assert "gross_savings" in result
        assert "complexity_cost" in result
        assert "net_savings" in result
        assert result["net_savings"] == result["gross_savings"] - result["complexity_cost"]
        assert result["gross_savings"] == 25000.0  # 25% of 100k
        assert result["complexity_cost"] == 5000.0  # 5% of 100k


class TestSupplyChainSecurityGate:
    """Verify the supply chain security gate."""

    @pytest.mark.asyncio
    async def test_validate_returns_low_risk(self):
        """Default validation should return low risk."""
        _clear_pnkln_cache()
        from pnkln.governance.judge_architecture.infrastructure import (
            SupplyChainSecurityGate,
        )

        gate = SupplyChainSecurityGate()
        result = await gate.validate()
        assert result["risk_score"] == "L"
        assert result["slsa_provenance_verified"] is True
        assert result["cve_vulnerabilities"] == []
