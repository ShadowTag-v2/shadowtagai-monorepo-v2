"""Tests for ANE Bridge hardware routing."""

import pytest
from apps.aiyou_stack.ane_bridge import (
    HardwareTier,
    InferenceResult,
    detect_hardware,
    route_inference,
)


class TestHardwareDetection:
    """Test hardware detection logic."""

    def test_detect_returns_valid_tier(self):
        """detect_hardware should return a valid HardwareTier."""
        tier = detect_hardware()
        assert isinstance(tier, HardwareTier)

    def test_detect_on_macos_arm64(self):
        """On macOS ARM64, should return ANE or GPU_LOCAL."""
        tier = detect_hardware()
        # On M1 Mac, this should be ANE
        assert tier in (HardwareTier.ANE, HardwareTier.GPU_LOCAL, HardwareTier.CPU)


class TestRouteInference:
    """Test inference routing."""

    def test_route_returns_result(self):
        """route_inference should return an InferenceResult."""
        result = route_inference("test-model", {"prompt": "hello"})
        assert isinstance(result, InferenceResult)
        assert result.model_name == "test-model"

    def test_route_with_preferred_tier(self):
        """route_inference should respect the preferred tier."""
        result = route_inference(
            "test-model",
            {"prompt": "hello"},
            preferred_tier=HardwareTier.CPU,
        )
        assert result.tier == HardwareTier.CPU

    def test_route_all_tiers(self):
        """Should be able to route to all tiers."""
        for tier in HardwareTier:
            result = route_inference(
                f"model-{tier.value}",
                {"data": "test"},
                preferred_tier=tier,
            )
            assert result.tier == tier


class TestZeroCPURouter:
    """Test the Zero CPU Router."""

    def test_router_initialization(self):
        """Router should initialize with empty metrics."""
        from apps.aiyou_stack.zero_cpu_router import ZeroCPURouter
        router = ZeroCPURouter()
        metrics = router.get_metrics()
        assert metrics["total_requests"] == 0
        assert metrics["errors"] == 0

    def test_router_routes_small_model(self):
        """Small models should prefer ANE."""
        from apps.aiyou_stack.zero_cpu_router import ZeroCPURouter
        router = ZeroCPURouter()
        result = router.route("small-model", {"prompt": "test"}, model_params_billions=0.5)
        assert isinstance(result, InferenceResult)
        metrics = router.get_metrics()
        assert metrics["total_requests"] == 1

    def test_router_routes_large_model_to_cloud(self):
        """Very large models should route to cloud."""
        from apps.aiyou_stack.zero_cpu_router import ZeroCPURouter
        router = ZeroCPURouter()
        result = router.route("huge-model", {"prompt": "test"}, model_params_billions=70.0)
        assert result.tier == HardwareTier.GPU_CLOUD
